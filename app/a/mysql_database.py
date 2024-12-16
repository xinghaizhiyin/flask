import pymysql
import pandas as pd

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

    def query_stock_data(self, latest_price):
        """根据最新价格查询股票数据并按近一个月均价减去当前价格排序"""
        try:
            query = """
            SELECT stock_code, stock_name, latest_price, avg_1month, avg_3months, avg_1year
            FROM stock_rankings
            WHERE latest_price = %s
            """
            self.cursor.execute(query, (latest_price,))
            results = self.cursor.fetchall()

            # 将查询结果转换为 DataFrame
            df = pd.DataFrame(results, columns=['股票代码', '股票名称', '最新价格', '近一个月均价', '近三个月均价', '近一年均价'])

            # 去除最新价格为零的股票和最新价格大于5的股票
            df = df[df['最新价格'] != 0]  # 剔除最新价格为0的股票
            df = df[df['最新价格'] <= 5]  # 剔除最新价格大于5的股票

            # 计算近一个月均价与最新价格的差值
            df['价格差'] = df['近一个月均价'] - df['最新价格']

            # 按价格差排序
            df_sorted = df.sort_values(by='价格差', ascending=False)

            return df_sorted

        except pymysql.MySQLError as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()  # 返回空 DataFrame

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
        print("数据库连接已关闭")
