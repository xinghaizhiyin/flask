import pymysql
from flask import Flask, jsonify, request

app = Flask(__name__)

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'test',
    'charset': 'utf8mb4'
}

def query_stock_by_code_or_name(stock_code=None, stock_name=None):
    """
    通过股票代码或股票名称模糊查询
    :param stock_code: 股票代码，支持模糊查询
    :param stock_name: 股票名称，支持模糊查询
    :return: 查询结果
    """
    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # 构建查询 SQL
        sql = "SELECT * FROM stock_rankings WHERE 1=1"
        params = []

        if stock_code:
            sql += " AND stock_code LIKE %s"
            params.append(f"%{stock_code}%")

        if stock_name:
            sql += " AND stock_name LIKE %s"
            params.append(f"%{stock_name}%")

        # 执行查询
        cursor.execute(sql, params)
        result = cursor.fetchall()

        # 关闭连接
        cursor.close()
        connection.close()

        return result
    except Exception as e:
        print(f"查询失败: {e}")
        return None


@app.route('/search_stocks', methods=['GET'])
def search_stocks():
    """
    Flask API 接口：通过股票代码或名称模糊查询
    """
    try:
        stock_code = request.args.get('stock_code', default=None, type=str)
        stock_name = request.args.get('stock_name', default=None, type=str)

        if not stock_code and not stock_name:
            return jsonify({"error": "请至少提供股票代码或股票名称中的一个参数"}), 400

        # 调用查询函数
        result = query_stock_by_code_or_name(stock_code, stock_name)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"message": "未找到匹配的股票数据"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, threaded=True)
