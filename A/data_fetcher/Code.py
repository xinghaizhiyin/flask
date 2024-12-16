import akshare as ak
from datetime import datetime
from A.database.MySQLDatabase import MySQLDatabase  # 确保这个导入路径正确
from A.database.MySQLTable import stockcodes_columns  # 假设你已经定义了 stockcodes_columns

# 数据库连接参数
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'stock'
}

def fetch_and_insert_stock_codes(db_params, table_name, stockcodes_columns):
    """
    从AKShare获取沪深A股的股票代码，并插入到数据库指定的表中
    :param db_params: 数据库连接参数
    :param table_name: 数据库表名
    :param stockcodes_columns: 表结构
    """
    # 获取沪深市场所有A股的实时数据
    stock_list = ak.stock_zh_a_spot()

    # 提取股票代码并格式化为6位数字
    stock_codes = stock_list['代码'].apply(lambda x: str(x).zfill(6))  # 格式化股票代码为6位数字

    # 创建数据库连接并创建股票代码表（如果表不存在）
    db = MySQLDatabase(**db_params)  # 解包字典作为参数传递给构造函数
    db.create_table_if_not_exists(table_name, stockcodes_columns)  # 创建股票代码表（如果表不存在）

    # 定义插入股票代码的函数
    def insert_stock_codes(stock_codes):
        for stock_code in stock_codes:
            # 构建插入数据的字典
            data = {
                'stock_code': stock_code,  # 只插入股票代码
                'data_write_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间
            }
            # 执行插入操作
            db.insert_data(table_name, data)  # 假设表名为 stockcodes

    # 将股票代码插入数据库
    insert_stock_codes(stock_codes)

    # 关闭数据库连接
    db.close()

# 调用封装好的函数
fetch_and_insert_stock_codes(db_params, "stockcodes", stockcodes_columns)
