import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import time
from A.database.MySQLDatabase import MySQLDatabase  # 修改为正确的数据库模块导入
from A.database.MySQLTable import seven_day_columns, thirty_day_columns, three_sixty_day_columns


# 设置 pandas 打印选项，确保显示完整数据
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.width', None)  # 自动调整宽度
pd.set_option('display.max_colwidth', None)  # 显示完整列内容

# 数据库连接参数
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'stock'
}


def get_date_range(days=7):
    """获取开始和结束日期，默认获取最近7天的数据（包括今天）"""
    end_date = datetime.today().strftime('%Y-%m-%d')  # 包括今天
    start_date = (datetime.today() - timedelta(days=days-1)).strftime('%Y-%m-%d')  # 包括今天及其前面6天
    return start_date, end_date


def fetch_stock_data(stock_code, stock_name, start_date, end_date):
    """获取单只股票的日线数据"""
    try:
        stock_data = ak.stock_zh_a_daily(symbol=stock_code, start_date=start_date, end_date=end_date)

        # 如果返回数据为空，直接返回 None
        if stock_data.empty:
            return None

        # 如果返回数据没有 'date' 列，直接返回 None
        if 'date' not in stock_data.columns:
            return None

        # 添加股票代码和名称
        stock_data['code'] = stock_code
        stock_data['name'] = stock_name
        return stock_data
    except Exception as e:
        print(f"获取股票数据时发生错误: {e}")
        return None


def get_all_stock_data(stock_list, start_date, end_date):
    """并发获取所有股票的日线数据"""
    all_stock_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for index, row in stock_list.iterrows():
            stock_code = row['代码']
            stock_name = row['名称']
            # 提交请求到线程池
            futures.append(executor.submit(fetch_stock_data, stock_code, stock_name, start_date, end_date))

        # 获取每个股票的数据
        for future in futures:
            stock_data = future.result()
            if stock_data is not None:
                all_stock_data.append(stock_data)

    # 将所有股票的数据合并为一个 DataFrame
    return pd.concat(all_stock_data, ignore_index=True) if all_stock_data else pd.DataFrame()


def prepare_data_for_insertion(row, prev_close=None, avg_7days=None, min_7days=None, max_7days=None):
    """准备数据插入数据库"""
    # 如果没有传入 prev_close，则默认涨跌幅为 None
    if prev_close is not None:
        change_pct = (row['close'] - prev_close) / prev_close * 100
    else:
        change_pct = None

    # 计算振幅（振幅的公式：高 - 低）/ 低
    amplitude_pct = (row['high'] - row['low']) / row['low'] * 100 if row['low'] != 0 else None

    # 计算市值
    market_cap = row['close'] * row['outstanding_share']  # 市值 = 收盘价 * 流通股本

    # 插入的数据
    data = {
        'stock_code': row['code'],  # 股票代码
        'stock_name': row['name'],  # 股票名称
        'date': row['date'],  # 日期
        'open': row['open'],  # 开盘价
        'high': row['high'],  # 最高价
        'low': row['low'],  # 最低价
        'close': row['close'],  # 最新收盘价
        'volume': row['volume'],  # 成交量
        'amount': row['amount'],  # 成交额
        'outstanding_share': row['outstanding_share'],  # 流通股本
        'turnover': row['turnover'],  # 换手率
        'market_cap': market_cap,  # 市值
        'change_pct': change_pct,  # 涨跌幅
        'amplitude_pct': amplitude_pct,  # 振幅
        'avg_7days': avg_7days,  # 7天收盘价平均值
        'min_7days': min_7days,  # 7天内最低收盘价
        'max_7days': max_7days,  # 7天内最高收盘价
        'data_write_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间
    }
    return data


def write_data():
    """获取数据并写入数据库"""
    try:
        # 获取今天的日期和7天前的日期（包括今天）
        start_date, end_date = get_date_range(days=7)

        # 获取沪深A股实时数据（包含股票代码、名称等）
        stock_list = ak.stock_zh_a_spot()
        print("获取股票列表：", stock_list)

        # 获取所有股票的日线数据
        all_stock_data = get_all_stock_data(stock_list, start_date, end_date)
        print("获取的股票数据：", all_stock_data)

        if not all_stock_data.empty:
            # 将 NaN 值替换为 None (即 NULL 在数据库中的表示)
            all_stock_data = all_stock_data.where(pd.notnull(all_stock_data), None)

            # 确保数据按日期排序
            all_stock_data['date'] = pd.to_datetime(all_stock_data['date'])
            all_stock_data = all_stock_data.sort_values(by='date')

            # 创建数据库连接
            db = MySQLDatabase(**db_params)
            db.create_table_if_not_exists("seven_data", seven_day_columns)
            print("创建数据库连接和表格")

            # 计算7天的平均收盘价、7天内最低价格、7天内最高价格（包含今天）
            all_stock_data['avg_7days'] = all_stock_data['close'].rolling(window=7, min_periods=1).mean()
            all_stock_data['min_7days'] = all_stock_data['low'].rolling(window=7, min_periods=1).min()
            all_stock_data['max_7days'] = all_stock_data['high'].rolling(window=7, min_periods=1).max()

            # 插入数据到数据库
            for index, row in all_stock_data.iterrows():
                # 获取前一天的收盘价 (可根据实际情况修改，例：从数据库获取前一天数据)
                prev_close = None  # 这里需要根据实际情况获取前一天的收盘价
                avg_7days = row['avg_7days']
                min_7days = row['min_7days']
                max_7days = row['max_7days']

                data = prepare_data_for_insertion(row, prev_close, avg_7days, min_7days, max_7days)
                db.insert_data("seven_data", data)

            db.close()
            print("数据已写入数据库。")
        else:
            print("没有获取到任何股票数据！")

    except Exception as e:
        print(f"数据获取和写入执行失败: {e}")



def main():
    """主函数"""
    # 记录程序开始时间
    start_time = time.time()

    # 执行数据获取和写入操作
    write_data()

    # 记录程序结束时间
    end_time = time.time()

    # 计算执行时间
    execution_time = end_time - start_time
    print(f"程序执行总时间: {execution_time:.2f} 秒")


if __name__ == "__main__":
    main()
