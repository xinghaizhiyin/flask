import akshare as ak
import pandas as pd
from datetime import datetime
from ..database.MySQLDatabase import MySQLDatabase  # 修改为正确的数据库模块导入
from ..database.MySQLTable import real_time_columns

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


def fetch_realtime_stock_data():
    """获取沪深A股实时数据"""
    try:
        stock_list = ak.stock_zh_a_spot()
        return stock_list
    except Exception as e:
        print(f"获取实时股票数据时发生错误: {e}")
        return None


def prepare_data_for_insertion(row):
    """准备数据插入数据库"""
    data = {
        'stock_code': row['代码'],  # 股票代码
        'stock_name': row['名称'],  # 股票名称
        'latest_price': row['最新价'],  # 最新价格
        'change_amt': row['涨跌额'],  # 涨跌额
        'change_pct': row['涨跌幅'],  # 涨跌幅
        'buy_price': row['买入'],  # 买入价
        'sell_price': row['卖出'],  # 卖出价
        'previous_close': row['昨收'],  # 昨收
        'today_open': row['今开'],  # 今开
        'highest_price': row['最高'],  # 最高价
        'lowest_price': row['最低'],  # 最低价
        'volume': row['成交量'],  # 成交量
        'amount': row['成交额'],  # 成交额
        'timestamp': row['时间戳'],  # 时间戳
        'data_write_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间
    }
    return data

def write_realtime_data_to_db():
    """获取实时数据并写入数据库"""
    try:
        # 获取实时股票数据
        stock_list = fetch_realtime_stock_data()

        if stock_list is not None and not stock_list.empty:
            # 创建数据库连接
            db = MySQLDatabase(**db_params)
            db.create_table_if_not_exists("real_time_data", real_time_columns)
            print("数据库表格已创建或已存在")

            # 将实时数据插入数据库
            for index, row in stock_list.iterrows():
                data = prepare_data_for_insertion(row)
                db.insert_data("real_time_data", data)

            db.close()
            print("实时数据已写入数据库。")
        else:
            print("没有获取到任何实时股票数据！")

    except Exception as e:
        print(f"获取和写入实时数据失败: {e}")


if __name__ == "__main__":
    write_realtime_data_to_db()
