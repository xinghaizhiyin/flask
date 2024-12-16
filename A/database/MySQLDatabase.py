import pymysql
import pandas as pd
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'stock',
    'charset': 'utf8mb4'

}
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

    def create_table_if_not_exists(self, table_name, columns):
        """ 创建表，如果表不存在的话 """
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
        """ 插入数据，并处理重复插入情况 """
        if not data:
            print("数据为空，跳过插入")
            return
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            update_part = ', '.join([f"{key} = VALUES({key})" for key in data.keys()])
            data = {key: (None if value != value else value) for key, value in data.items()}
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
            self.db.rollback()

    def get_all_data(self, table_name):
        """ 查询表中所有数据 """
        try:
            query = f"SELECT * FROM {table_name}"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            columns = [desc[0] for desc in self.cursor.description]
            df = pd.DataFrame(results, columns=columns)
            return df
        except pymysql.MySQLError as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()

    def get_data_by_search(self, table_name, search_param):
        """ 根据 search_param 查询数据 """
        try:
            query = f"SELECT * FROM {table_name} WHERE stock_code LIKE %s"
            self.cursor.execute(query, (f"%{search_param}%",))
            results = self.cursor.fetchall()

            if results:
                columns = [desc[0] for desc in self.cursor.description]
                df = pd.DataFrame(results, columns=columns)
                return df

            query = f"SELECT * FROM {table_name} WHERE stock_name LIKE %s"
            self.cursor.execute(query, (f"%{search_param}%",))
            results = self.cursor.fetchall()

            if results:
                columns = [desc[0] for desc in self.cursor.description]
                df = pd.DataFrame(results, columns=columns)
                return df

            return pd.DataFrame()

        except pymysql.MySQLError as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()

    def update_favorite_status(self, stock_code, is_favorite):
        """ 更新股票的收藏状态 """
        try:
            # 确保更新的数据是 0 或 1
            is_favorite = 1 if is_favorite else 0
            query = """
                UPDATE merged_stock_data 
                SET is_favorite = %s 
                WHERE stock_code = %s
            """
            self.cursor.execute(query, (is_favorite, stock_code))
            self.db.commit()  # 提交事务
            print(f"股票 {stock_code} 收藏状态更新为 {is_favorite}")
        except pymysql.MySQLError as e:
            print(f"更新收藏状态失败: {e}")
            self.db.rollback()  # 回滚事务
        except Exception as e:
            print(f"发生未知错误: {e}")
            self.db.rollback()  # 回滚事务
        finally:
            # 确保每次操作后都关闭连接
            # 请确保关闭连接在所有操作完成后再进行
            if self.cursor:
                self.cursor.close()
            if self.db:
                self.db.close()

    def get_favorites(self, table_name):
        """ 查询所有收藏的股票（is_favorite = 1） """
        try:
            query = f"SELECT * FROM {table_name} WHERE is_favorite = 1"
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            if results:
                columns = [desc[0] for desc in self.cursor.description]
                df = pd.DataFrame(results, columns=columns)
                return df
            else:
                return pd.DataFrame()  # 返回空 DataFrame 如果没有收藏

        except pymysql.MySQLError as e:
            print(f"查询收藏数据失败: {e}")
            return pd.DataFrame()  # 返回空 DataFrame

    def close(self):
        """ 关闭数据库连接 """
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
