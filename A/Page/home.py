import pandas as pd
from datetime import timedelta
from A.database.MySQLDatabase import MySQLDatabase

class Home:
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

    def merge_three_data(self, threshold=10):
        """合并 merged_stock_data 表数据，并根据 latest_price 过滤数据"""
        print("开始获取数据...")

        # 获取 merged_stock_data 表数据
        merged_stock_data = self.fetch_data('merged_stock_data')
        if not merged_stock_data:
            print("获取 merged_stock_data 失败")
            return None

        # 过滤数据：只保留 latest_price 小于 threshold 的记录
        filtered_data = [record for record in merged_stock_data if record['latest_price'] < threshold]

        # 将数据转换为 DataFrame 方便操作
        merged_df = pd.DataFrame(filtered_data)

        # 转换为字典格式
        merged_data = merged_df.to_dict(orient='records')
        return merged_data

    def close(self):
        """关闭数据库连接"""
        self.db.close()
