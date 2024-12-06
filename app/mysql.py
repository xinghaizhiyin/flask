import pymysql

class MySQLDatabase:
    def __init__(self, host, user, password, database):
        """初始化数据库连接"""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.db = None
        self.cursor = None
        self.connect()

    def connect(self):
        """连接数据库"""
        try:
            self.db = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.db.cursor()
            print("数据库连接成功")
        except pymysql.MySQLError as e:
            print(f"数据库连接失败: {e}")
            raise

    def create_table_if_not_exists(self, table_name):
        """
        如果表不存在，则创建表
        """
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(255),
            title VARCHAR(255),
            source VARCHAR(255),
            likes VARCHAR(255)
        )
        """
        self.cursor.execute(create_table_query)
        self.db.commit()
        print(f"表 {table_name} 确认存在或已创建")

    def insert_data(self, table_name, data):
        """
        插入数据到表中，并检查重复数据
        :param table_name: 表名
        :param data: 数据列表，例如 ['分类', '标题', '来源', '点赞']
        """
        if not data:
            print("数据为空，跳过插入")
            return

        try:
            # 定义固定的列名映射
            columns = ['category', 'title', 'source', 'likes']

            # 确保数据和列的长度匹配
            min_length = min(len(columns), len(data))
            data_dict = {columns[i]: data[i] for i in range(min_length)}

            # 检查是否存在重复记录（根据 title 和 source 进行去重）
            check_query = f"SELECT COUNT(*) FROM {table_name} WHERE title = %s AND source = %s"
            self.cursor.execute(check_query, (data_dict.get('title'), data_dict.get('source')))
            result = self.cursor.fetchone()

            if result[0] > 0:
                print(f"数据已存在，跳过插入: {data_dict}")
                return  # 数据已存在，跳过插入

            # 构造插入 SQL 语句
            placeholders = ", ".join(["%s"] * len(data_dict))
            insert_query = f"INSERT INTO {table_name} ({', '.join(data_dict.keys())}) VALUES ({placeholders})"

            # 执行插入操作
            self.cursor.execute(insert_query, tuple(data_dict.values()))
            self.db.commit()
            print(f"已成功插入数据: {data_dict}")

        except pymysql.MySQLError as e:
            print(f"插入数据失败: {e}")
            self.db.rollback()  # 回滚事务

    def fetch_all(self, table_name):
        """
        查询表中的所有数据
        :param table_name: 表名
        :return: 查询到的数据
        """
        try:
            self.cursor.execute(f"SELECT * FROM `{table_name}`")
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            print(f"查询数据失败: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
        print("数据库连接已关闭")



# 使用示例
if __name__ == "__main__":
    db_params = {
        'host': 'localhost',
        'user': 'root',
        'password': 'admin',
        'database': 'test'
    }

    # processor = AppiumDataProcessor(db_params)

    # 假设 driver 是已实例化的 Appium WebDriver 对象
    # processor.process_data(driver, 'video_data', ['category', 'title', 'source', 'likes'])

    # processor.close()
