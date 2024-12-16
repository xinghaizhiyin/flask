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

    def search_stocks(self, search_query):
        """
        根据股票名称或代码进行模糊查询
        :param search_query: 用户输入的查询关键字
        :return: 查询到的股票列表
        """
        try:
            # 使用 LIKE 进行模糊查询，查询股票名称或股票代码
            search_query = f"%{search_query}%"  # 在关键字两端加上百分号，表示模糊查询
            query = """
            SELECT * 
            FROM stock_rankings 
            WHERE stock_code LIKE %s OR stock_name LIKE %s
            """
            self.cursor.execute(query, (search_query, search_query))
            results = self.cursor.fetchall()
            return results
        except pymysql.MySQLError as e:
            print(f"查询失败: {e}")
            return []

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

    db = MySQLDatabase(**db_params)

    # 获取用户输入的查询关键字
    search_query = input("请输入股票代码或名称进行查询: ")

    # 执行查询
    results = db.search_stocks(search_query)

    # 打印查询结果
    if results:
        print("\n查询到的股票信息：")
        for stock in results:
            # 打印所有查询到的数据
            print(f"股票代码: {stock[1]}, 股票名称: {stock[2]}, 平均一个月价格: {stock[3]}, "
                  f"平均三个月价格: {stock[4]}, 平均一年价格: {stock[5]}, 最新价格: {stock[6]}, "
                  f"一个月涨跌幅: {stock[7]}, 三个月涨跌幅: {stock[8]}, 一年涨跌幅: {stock[9]}")
    else:
        print("未找到匹配的股票信息。")

    # 关闭数据库连接
    db.close()
