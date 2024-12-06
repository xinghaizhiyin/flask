import pandas as pd
from mysql import MySQLDatabase  # 假设你已经有这个模块
import re

# 自定义函数，用于将带有单位的点赞数转换为整数
def convert_likes(like_str):
    try:
        if '万' in like_str:
            # 提取万后面的数字并转换
            number = float(re.sub(r'[^\d\.]', '', like_str))  # 提取数字部分
            return int(number * 10000)  # 将万转换为实际的点赞数
        elif '千' in like_str:
            # 提取千后面的数字并转换
            number = float(re.sub(r'[^\d\.]', '', like_str))  # 提取数字部分
            return int(number * 1000)  # 将千转换为实际的点赞数
        else:
            # 如果没有单位，直接转换为整数
            number = re.sub(r'[^\d]', '', like_str)  # 提取数字部分
            if number == '':  # 如果没有提取到数字，则返回0或引发错误
                return 0  # 或者选择抛出异常 raise ValueError(f"Invalid like string: {like_str}")
            return int(number)
    except Exception as e:
        print(f"Error processing '{like_str}': {e}")
        return 0  # 如果出现错误返回0，或者根据需求抛出异常
def main():
    # 设置数据库连接的参数
    db_params = {
        'host': 'localhost',  # 数据库主机
        'user': 'root',  # 用户名
        'password': 'admin',  # 密码
        'database': 'test'  # 数据库名称
    }

    # 实例化 MySQLDatabase 类，建立连接
    db = MySQLDatabase(
        host=db_params['host'],
        user=db_params['user'],
        password=db_params['password'],
        database=db_params['database']
    )

    # 假设你要查询的表名为 "xiaohongshu"
    table_name = 'xiaohongshu'

    # 调用查询函数，获取表中所有数据
    try:
        data = db.fetch_all(table_name)
        if data:
            print("查询到的数据:")

            # 将数据转化为 DataFrame
            df = pd.DataFrame(data, columns=['id', 'type', 'title', 'author', 'likes'])

            # 使用自定义函数转换点赞数
            df['likes'] = df['likes'].apply(lambda x: convert_likes(x))

            # 按照作者分组，计算平均点赞数
            avg_likes_by_author = df.groupby('author')['likes'].mean().reset_index()

            # 打印结果
            print(avg_likes_by_author)

            # 2. 获取点赞数最多的视频
            if 'likes' in df.columns:
                top_videos = df.nlargest(5, 'likes')  # 获取点赞数最多的前5个视频
                print("\n点赞数最多的视频:")
                print(top_videos[['title', 'author', 'likes']])

            # 3. 数据的基本统计信息
            print("\n数据的基本统计信息:")
            print(df.describe())

        else:
            print("表中没有数据。")

    except Exception as e:
        print(f"查询失败: {e}")

    # 关闭数据库连接
    db.close()


if __name__ == "__main__":
    main()
