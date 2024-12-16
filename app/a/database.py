import pymysql
import pandas as pd

class MySQLDatabase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.db = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.db = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(f"数据库连接失败: {e}")
            raise

    def create_table_if_not_exists(self, table_name):
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            stock_code VARCHAR(10) UNIQUE,  -- 添加唯一约束
            stock_name VARCHAR(100),
            latest_price FLOAT,
            avg_1month FLOAT,
            avg_3months FLOAT,
            avg_1year FLOAT,
            avg_5days FLOAT,  -- 新增字段：最近五天的平均价
            down_count INT,  -- 新增字段：下跌的次数
            month_change_pct FLOAT,
            three_month_change_pct FLOAT,
            year_change_pct FLOAT,
            change_pct FLOAT,  -- 新增字段：涨跌幅
            amplitude_pct FLOAT,  -- 新增字段：振幅
            is_favorite TINYINT DEFAULT 0,  -- 新增字段：是否被收藏，默认为 0
            data_write_time DATETIME  -- 数据写入时间
        )
        """
        self.cursor.execute(create_table_query)
        self.db.commit()

    def insert_data(self, table_name, data):
        if not data:
            print("数据为空，跳过插入")
            return
        try:
            # 确保插入数据时列名与字典的键一致
            columns = ', '.join(data.keys())  # 获取字典中的键作为列名
            placeholders = ', '.join(['%s'] * len(data))  # 动态创建占位符

            # 构建更新部分的 SQL 字符串
            update_part = ', '.join([f"{key} = VALUES({key})" for key in data.keys()])

            # 处理 NaN 或 None 值，确保插入有效数据
            data = {key: (None if value != value else value) for key, value in data.items()}

            # 使用 INSERT ... ON DUPLICATE KEY UPDATE 语句
            insert_query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_part}
            """
            # 调用 execute 时，传递元组形式的数据
            self.cursor.execute(insert_query, tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(f"插入或更新数据失败: {e}")
            self.db.rollback()
        except Exception as e:
            print(f"发生未知错误: {e}")

    def query_stock_data(self, latest_price):
        """查询所有股票数据并按近一个月均价减去当前价格排序，去除最新价格为0的和价格高于给定最新价格的股票"""
        try:
            query = """
            SELECT stock_code, stock_name, latest_price, avg_5days, avg_1month, avg_3months, avg_1year, change_pct, amplitude_pct, down_count, data_write_time
            FROM stock_rankings
            """
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            # 将查询结果转换为 DataFrame
            df = pd.DataFrame(results,
                              columns=['stock_code', 'stock_name', 'latest_price', 'avg_5days', 'avg_1month', 'avg_3months', 'avg_1year',
                                       'change_pct', 'amplitude_pct','down_count', 'data_write_time'])

            # 转换无效时间值为 NaT
            df['data_write_time'] = pd.to_datetime(df['data_write_time'], errors='coerce')

            # 填充 NaT 为默认时间
            default_time = pd.to_datetime('2024-01-01 00:00:00')
            df['data_write_time'] = df['data_write_time'].fillna(default_time)

            # 去除无效的行
            df = df.dropna(subset=['stock_code', 'stock_name'])  # 如果有必要，去除包含NaN的行
            df = df.drop_duplicates(subset=['stock_code', 'stock_name'])  # 基于这些列去重

            # 去除最新价格为零的股票和价格高于给定最新价格的股票
            df = df[df['latest_price'] != 0]  # 剔除最新价格为0的股票
            df = df[df['latest_price'] <= latest_price]  # 剔除价格高于给定最新价格的股票

            # 计算近一个月均价与最新价格的差值
            df['PriceDifference'] = df['avg_1month'] - df['latest_price']

            # 保留两位小数
            df['PriceDifference'] = df['PriceDifference'].round(2)

            # 按价格差排序
            df_sorted = df.sort_values(by='PriceDifference', ascending=False)

            return df_sorted

        except pymysql.MySQLError as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()  # 返回空 DataFrame

    def search_stock_data(self, query=None):
        """
        模糊查询股票数据，只提供一个参数，优先查询第一个字段，如果查询不到再查询第二个字段
        :param query: 股票代码或股票名称
        :return: 查询结果的 DataFrame
        """
        try:
            # 初始化查询语句和参数
            query_sql = "SELECT * FROM stock_rankings WHERE 1=1"
            params = []

            # 优先使用股票代码查询
            query_sql += " AND stock_code LIKE %s"
            params.append(f"%{query}%")  # 模糊查询股票代码

            # 执行查询
            self.cursor.execute(query_sql, params)
            results = self.cursor.fetchall()

            if not results:  # 如果没有结果，尝试用股票名称进行查询
                query_sql = "SELECT * FROM stock_rankings WHERE 1=1"
                params = []
                query_sql += " AND stock_name LIKE %s"
                params.append(f"%{query}%")  # 模糊查询股票名称

                self.cursor.execute(query_sql, params)
                results = self.cursor.fetchall()

            # 将查询结果转换为 DataFrame
            columns = [desc[0] for desc in self.cursor.description]
            return pd.DataFrame(results, columns=columns)

        except pymysql.MySQLError as e:
            print(f"模糊查询失败: {e}")
            return pd.DataFrame()  # 返回空 DataFrame

    def update_favorite_status(self, stock_code, is_favorite):
        """
        根据股票代码更新收藏状态
        :param table_name: 表名
        :param stock_code: 股票代码
        :param is_favorite: 收藏状态（0 或 1）
        """
        try:
            # 构建更新 SQL 语句
            update_query = f"""
            UPDATE stock_rankings
            SET is_favorite = %s
            WHERE stock_code = %s
            """
            # 执行更新语句
            self.cursor.execute(update_query, (is_favorite, stock_code))
            self.db.commit()
            print(f"更新股票 {stock_code} 的收藏状态为 {is_favorite}")
        except pymysql.MySQLError as e:
            print(f"更新收藏状态失败: {e}")
            self.db.rollback()
        except Exception as e:
            print(f"发生未知错误: {e}")

    def query_favorite_stocks(self):
        """查询所有被收藏的股票数据 (is_favorite=1)"""
        try:
            # 使用 * 来查询所有列
            query = """
            SELECT * FROM stock_rankings
            WHERE is_favorite = 1
            """
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            # 将查询结果转换为 DataFrame
            df = pd.DataFrame(results, columns=[desc[0] for desc in self.cursor.description])

            # 转换无效时间值为 NaT
            df['data_write_time'] = pd.to_datetime(df['data_write_time'], errors='coerce')

            # 填充 NaT 为默认时间
            default_time = pd.to_datetime('2024-01-01 00:00:00')
            df['data_write_time'] = df['data_write_time'].fillna(default_time)

            # 去除无效的行
            df = df.dropna(subset=['stock_code', 'stock_name'])  # 如果有必要，去除包含NaN的行
            df = df.drop_duplicates(subset=['stock_code', 'stock_name'])  # 基于这些列去重

            return df

        except pymysql.MySQLError as e:
            print(f"查询收藏的股票失败: {e}")
            return pd.DataFrame()  # 返回空 DataFrame

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
