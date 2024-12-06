# 导入 MySQLDatabase 类
from mysql import MySQLDatabase

def main():
    # 设置数据库连接的参数
    db_params = {
        'host': 'localhost',   # 数据库主机
        'user': 'root',        # 用户名
        'password': 'admin',   # 密码
        'database': 'test'     # 数据库名称
    }

    # 实例化 MySQLDatabase 类，建立连接
    db = MySQLDatabase(
        host=db_params['host'],
        user=db_params['user'],
        password=db_params['password'],
        database=db_params['database']
    )

    # 假设你要查询的表名为 "video_data"
    table_name = 'xiaohongshu'

    # 调用查询函数，获取表中所有数据
    try:
        data = db.fetch_all(table_name)
        if data:
            print("查询到的数据:")
            for row in data:
                print(row)
        else:
            print("表中没有数据。")
    except Exception as e:
        print(f"查询失败: {e}")

    # 关闭数据库连接
    db.close()

if __name__ == "__main__":
    main()