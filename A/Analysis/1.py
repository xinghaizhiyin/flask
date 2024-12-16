import pymysql
from A.database.MySQLTable import merged_columns  # 导入表结构

class StockDataMerger:
    def __init__(self, db_params):
        self.db_params = db_params
        self.db = None
        self.cursor = None
        self.merged_data = {}

    def connect(self):
        try:
            self.db = pymysql.connect(
                host=self.db_params['host'],
                user=self.db_params['user'],
                password=self.db_params['password'],
                database=self.db_params['database']
            )
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(f"数据库连接失败: {e}")
            raise

    def fetch_data(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"查询失败: {e}")
            return []

    def create_table_if_not_exists(self, table_name, columns):
        columns_str = ",\n".join([f"{col_name} {col_type}" for col_name, col_type in columns.items()])
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {columns_str}
        )
        """
        self.cursor.execute(create_table_query)
        self.db.commit()

    def insert_data(self, table_name, data):
        if not data:
            print("数据为空，跳过插入")
            return
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            update_part = ', '.join([f"{key} = VALUES({key})" for key in data.keys()])
            insert_query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_part}
            """
            self.cursor.execute(insert_query, tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(f"插入或更新数据失败: {e}")
            self.db.rollback()
        except Exception as e:
            print(f"发生未知错误: {e}")

    def merge_data(self, seven_day_data, thirty_day_data, ninety_day_data):
        all_stock_codes = set()
        for data in seven_day_data + thirty_day_data + ninety_day_data:
            all_stock_codes.add(data[1])  # 假设第二列是股票代码

        # 获取seven_day_data的data_write_time（假设是最后一列）
        data_write_time = seven_day_data[0][-1]  # 假设最后一列是data_write_time

        # 初始化合并数据字典
        self.merged_data = {code: {'stock_code': code, 'is_favorite': 0, 'data_write_time': data_write_time} for code in all_stock_codes}

        # 合并数据并计算价差
        self._merge_seven_day_data(seven_day_data)
        self._merge_thirty_day_data(thirty_day_data)
        self._merge_ninety_day_data(ninety_day_data)

    def _merge_seven_day_data(self, seven_day_data):
        for data in seven_day_data:
            stock_code = data[1]
            self.merged_data[stock_code].update({
                'stock_name': data[2],
                'latest_price': data[3],
                'latest_change_pct': data[4],
                'latest_amplitude_pct': data[5],
                'avg_days_7': data[6],
                'change_pct_7': data[7],
                'amplitude_pct_7': data[8],
                'min_days_7': data[9],
                'max_days_7': data[10],
                'down_count_7': data[11],
                'up_count_7': data[12],
            })

            # 计算7天价差（平均价减去最新价）
            avg_days_7 = data[6]
            latest_price = data[3]
            self.merged_data[stock_code]['price_diff_7'] = avg_days_7 - latest_price  # 平均价 - 最新价

    def _merge_thirty_day_data(self, thirty_day_data):
        for data in thirty_day_data:
            stock_code = data[1]
            self.merged_data[stock_code].update({
                'avg_days_30': data[6],
                'change_pct_30': data[7],
                'amplitude_pct_30': data[8],
                'min_days_30': data[9],
                'max_days_30': data[10],
                'down_count_30': data[11],
                'up_count_30': data[12]
            })

            # 计算30天价差（平均价减去最新价）
            avg_days_30 = data[6]
            latest_price = self.merged_data[stock_code].get('latest_price', 0)
            self.merged_data[stock_code]['price_diff_30'] = avg_days_30 - latest_price  # 平均价 - 最新价

    def _merge_ninety_day_data(self, ninety_day_data):
        for data in ninety_day_data:
            stock_code = data[1]
            self.merged_data[stock_code].update({
                'avg_days_90': data[6],
                'change_pct_90': data[7],
                'amplitude_pct_90': data[8],
                'min_days_90': data[9],
                'max_days_90': data[10],
                'down_count_90': data[11],
                'up_count_90': data[12]
            })

            # 计算90天价差（平均价减去最新价）
            avg_days_90 = data[6]
            latest_price = self.merged_data[stock_code].get('latest_price', 0)
            self.merged_data[stock_code]['price_diff_90'] = avg_days_90 - latest_price  # 平均价 - 最新价

    def insert_merged_data(self, table_name):
        for record in self.merged_data.values():
            self.insert_data(table_name, record)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()

# 使用StockDataMerger类
def process_and_insert_stock_data():
    db_params = {
        'host': 'localhost',
        'user': 'root',
        'password': 'admin',
        'database': 'stock'
    }

    # 初始化StockDataMerger实例
    stock_merger = StockDataMerger(db_params)
    stock_merger.connect()

    # 查询三个表的数据
    seven_day_query = "SELECT * FROM seven_day_data"
    thirty_day_query = "SELECT * FROM thirty_day_data"
    ninety_day_query = "SELECT * FROM ninety_day_data"

    seven_day_data = stock_merger.fetch_data(seven_day_query)
    thirty_day_data = stock_merger.fetch_data(thirty_day_query)
    ninety_day_data = stock_merger.fetch_data(ninety_day_query)

    # 合并数据
    stock_merger.merge_data(seven_day_data, thirty_day_data, ninety_day_data)

    # 创建合并表
    merged_table_name = 'merged_stock_data'
    stock_merger.create_table_if_not_exists(merged_table_name, merged_columns)

    # 插入合并后的数据
    stock_merger.insert_merged_data(merged_table_name)

    # 关闭数据库连接
    stock_merger.close()

# 调用函数来处理和插入数据
process_and_insert_stock_data()
