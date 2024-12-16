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

    def query_stock_data(self):
        """查询所有股票数据并按近一个月均价减去当前价格排序，
           去除最新价格为0的和价格大于5的股票，并剔除重复数据。"""
        try:
            query = """
            SELECT stock_code, stock_name, latest_price, avg_1month, avg_3months, avg_1year
            FROM stock_rankings
            """
            self.cursor.execute(query)
            results = self.cursor.fetchall()

            # 将查询结果转换为 DataFrame
            df = pd.DataFrame(results, columns=['Stock Code', 'Stock Name', 'Latest Price', '1-Month Avg Price',
                                                '3-Month Avg Price', '1-Year Avg Price'])

            # 去除重复数据
            df = df.drop_duplicates()

            # 去除最新价格为零的股票和价格大于5的股票
            df = df[df['Latest Price'] != 0]  # 剔除最新价格为0的股票
            df = df[df['Latest Price'] <= 5]  # 剔除价格大于5的股票

            print(df['Stock Code'].head())  # 打印前几行查看实际内容
            print(df['Stock Code'].unique())  # 查看所有唯一的值

            # 计算近一个月均价与最新价格的差值
            df['Price Difference'] = df['1-Month Avg Price'] - df['Latest Price']

            # 按价格差排序
            df_sorted = df.sort_values(by='Price Difference', ascending=False)

            return df_sorted

        except pymysql.MySQLError as e:
            print(f"查询失败: {e}")
            return pd.DataFrame()  # 返回空的 DataFrame

    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.db:
            self.db.close()
        print("数据库连接已关闭")


# 使用数据库类查询数据并排序
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'test'
}

db = MySQLDatabase(**db_params)

# 查询并按价格差排序
sorted_df = db.query_stock_data()

# 设置 Pandas 显示选项
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# 打印查询结果
if not sorted_df.empty:
    print("按照近一个月均价减去当前价格排序后的股票数据：")
    print(sorted_df)
else:
    print("未查询到数据或发生错误。")

# 关闭数据库连接
db.close()
