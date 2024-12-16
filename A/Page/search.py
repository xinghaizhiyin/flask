import pandas as pd
from datetime import timedelta
from A.database.MySQLDatabase import MySQLDatabase

class Search:
    def __init__(self, db_params):
        """初始化数据库连接"""
        self.db = MySQLDatabase(
            host=db_params['host'],
            user=db_params['user'],
            password=db_params['password'],
            database=db_params['database']
        )

    def fetch_data(self, table_name='real_time_data'):
        """获取指定表的数据，默认查询 real_time_data 表"""
        try:
            # 获取指定表的数据
            data = self.db.get_all_data(table_name)
        except Exception as e:
            print(f"查询失败: {e}")
            return None

        # 处理 Timedelta 和 Timestamp 类型的列，将其转换为字符串
        def convert_timedelta(value):
            if isinstance(value, timedelta):
                return str(value)  # 或者 return value.total_seconds()
            elif isinstance(value, pd.Timestamp):
                return value.strftime('%Y-%m-%d %H:%M:%S')  # 将 Timestamp 转换为字符串
            return value

        # 使用 map 替代 applymap，逐列应用转换
        for column in data.columns:
            if data[column].dtype == 'timedelta64[ns]':
                data[column] = data[column].map(convert_timedelta)
            elif data[column].dtype == 'datetime64[ns]':
                data[column] = data[column].map(convert_timedelta)

        # 转换为字典格式
        return data.to_dict(orient='records')

    def get_data_by_search(self, search_param):
        """根据 search_param（可能是 stock_code 或 stock_name）模糊查询数据"""
        try:
            # 使用封装好的方法执行模糊查询
            table_name = 'merged_stock_data'
            df = self.db.get_data_by_search(table_name, search_param)
            return df
        except Exception as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()  # 返回空 DataFrame，表示查询失败

    def get_favorites(self):
        """查询所有 is_favorite = 1 的记录"""
        try:
            table_name = 'merged_stock_data'

            df = self.db.get_favorites(table_name)
            return df  # 返回空 DataFrame
        except Exception as e:
            print(f"发生未知错误: {e}")
            return pd.DataFrame()  # 返回空 DataFrame

    def add_favorite_status(self, stock_code, is_favorite):
        """查询所有 is_favorite = 1 的记录"""
        try:
            df = self.db.update_favorite_status(stock_code, is_favorite)
            return df  # 返回空 DataFrame
        except Exception as e:
            print(f"发生未知错误: {e}")
            return pd.DataFrame()  # 返回空 DataFrame

    def close(self):
        """关闭数据库连接"""
        self.db.close()
