import akshare as ak
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from A.database.MySQLDatabase import MySQLDatabase  # 修改为正确的数据库模块导入
from A.database.MySQLTable import seven_day_columns, thirty_day_columns, ninety_day_columns  # 导入不同的表结构

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

def fetch_stock_data(stock_code, stock_name, start_date, end_date):
    """获取单只股票的历史数据"""
    try:
        # 获取指定股票的历史数据，直接使用股票代码（6位数字）
        stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date)
        if stock_data.empty:
            return None
        else:
            # 添加股票代码和名称
            stock_data["stock_code"] = stock_code
            stock_data["stock_name"] = stock_name

            return stock_data
    except Exception as e:
        print(f"Failed to fetch data for {stock_code}: {e}")
        return None

def prepare_data_for_insertion(stock_code, stock_name, stock_data, days=7):
    """准备N天数据插入数据库，默认N天为7天"""
    avg_days = stock_data['收盘'].tail(days).mean()  # N天平均收盘价
    change_pct = stock_data['涨跌幅'].tail(days).mean()  # N天涨跌幅平均值
    amplitude_pct = (stock_data['最高'].tail(days) - stock_data['最低'].tail(days)) / stock_data['最低'].tail(days) * 100  # N天振幅
    amplitude_pct = amplitude_pct.mean()  # 平均振幅
    min_days = stock_data['最低'].tail(days).min()  # N天内最低价格
    max_days = stock_data['最高'].tail(days).max()  # N天内最高价格
    down_count = (stock_data['涨跌幅'].tail(days) < 0).sum()  # N天下跌次数
    up_count = (stock_data['涨跌幅'].tail(days) > 0).sum()  # N天上涨次数
    latest_price = stock_data['收盘'].iloc[-1]  # 最新收盘价

    # 计算最新涨跌幅
    latest_change_pct = stock_data['涨跌幅'].iloc[-1]  # 最新涨跌幅（直接取最后一条数据的涨跌幅）

    # 计算最新振幅
    latest_amplitude_pct = (stock_data['最高'].iloc[-1] - stock_data['最低'].iloc[-1]) / stock_data['最低'].iloc[-1] * 100

    # 准备插入数据字典
    data = {
        'stock_code': stock_code,  # 股票代码
        'stock_name': stock_name,  # 股票名称
        'latest_price': latest_price,  # 最新收盘价
        'latest_change_pct': latest_change_pct,  # 最新涨跌幅
        'latest_amplitude_pct': latest_amplitude_pct,  # 最新振幅
        'avg_days': avg_days,  # N天平均收盘价
        'change_pct': change_pct,  # N天涨跌幅平均值
        'amplitude_pct': amplitude_pct,  # N天振幅平均值
        'min_days': min_days,  # N天最低价格
        'max_days': max_days,  # N天最高价格
        'down_count': down_count,  # N天下跌次数
        'up_count': up_count,  # N天上涨次数
        'data_write_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 数据写入时间
    }
    return data

def process_stock_code(stock_code, stock_name, db_params, days=7):
    """每个线程处理的单个股票代码，确保每个线程都能使用独立的数据库连接"""
    db = MySQLDatabase(**db_params)

    # 根据 days 选择对应的表结构
    if days == 7:
        db.create_table_if_not_exists("seven_day_data", seven_day_columns)
        table_name = "seven_day_data"
    elif days == 30:
        db.create_table_if_not_exists("thirty_day_data", thirty_day_columns)
        table_name = "thirty_day_data"
    elif days == 90:
        db.create_table_if_not_exists("ninety_day_data", ninety_day_columns)
        table_name = "ninety_day_data"
    else:
        raise ValueError("Invalid value for 'days'. It should be 7, 30, or 365.")

    try:
        end_date = pd.to_datetime('today').strftime('%Y%m%d')
        start_date = (pd.to_datetime('today') - pd.Timedelta(days=days)).strftime('%Y%m%d')

        stock_data = fetch_stock_data(stock_code, stock_name, start_date, end_date)

        if stock_data is not None and not stock_data.empty:
            data = prepare_data_for_insertion(stock_code, stock_name, stock_data, days)  # 传递days参数
            db.insert_data(table_name, data)  # 使用动态选择的表名
    finally:
        db.close()  # 确保每个线程结束后关闭数据库连接

def write_data_to_db(stock_dict, days=7):
    """获取N天数据并写入数据库"""
    try:
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(process_stock_code, stock_dict.keys(), stock_dict.values(), [db_params] * len(stock_dict),
                         [days] * len(stock_dict))  # 传递days参数

    except Exception as e:
        print(f"获取和写入{days}天数据失败: {e}")

def get_stock_codes():
    """获取沪深市场所有A股的股票代码，并剔除北交所股票（以 'bj' 开头）"""
    stock_list = ak.stock_zh_a_spot()

    stock_list['代码'] = stock_list['代码'].apply(lambda x: str(x).zfill(6))  # 格式化为6位数字
    stock_list = stock_list[~stock_list['代码'].str.startswith('bj')]  # 剔除北交所股票
    stock_list['代码'] = stock_list['代码'].apply(lambda x: x.lstrip('szsh'))  # 去掉前缀（'sz' 或 'sh'）

    stock_codes = stock_list['代码'].tolist()
    stock_names = stock_list['名称'].tolist()

    if len(stock_codes) != len(stock_names):
        print("警告：股票代码和名称的数量不一致！")
        return {}

    return dict(zip(stock_codes, stock_names))  # 返回股票代码与股票名称的字典

def main(days=7):
    """主函数"""
    stock_dict = get_stock_codes()
    write_data_to_db(stock_dict, days)

if __name__ == "__main__":
    main(days=7)
