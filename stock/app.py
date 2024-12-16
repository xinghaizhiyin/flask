from flask import Flask, jsonify, request
import logging
from scheduler_module.scheduler import start_scheduler, run_fetch_task  # 从 scheduler 模块导入任务调度器
from flask_cors import CORS  # 导入 CORS
from Page.home import Home
from Page.search import Search


app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库配置
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'stock',
    'charset': 'utf8mb4'

}

# 手动触发接口：获取股票数据并保存到数据库
@app.route('/start_data', methods=['POST'])
def fetch_stock_data():
    try:
        # 直接启动定时任务调度器
        logger.info("手动触发定时任务开始...")
        run_fetch_task()  # 手动执行定时任务函数
        logger.info("手动触发定时任务成功完成。")
        return jsonify({"message": "手动触发任务成功！"}), 200
    except Exception as e:
        logger.error(f"获取数据失败: {str(e)}")
        return jsonify({"error": "启动定时任务调度器失败", "details": str(e)}), 500


# 新增的路由：合并三个表的数据
@app.route('/home_data', methods=['GET'])
def fetch_merged_three_data():
    try:
        # 从请求中获取参数，如果没有提供则使用默认值
        threshold = float(request.args.get('threshold', 10))  # 默认阈值为 10

        # 创建 Home 实例
        home = Home(db_params)

        # 获取合并后的数据，并将参数传递给 merge_three_data
        merged_data = home.merge_three_data(threshold=threshold)

        if merged_data:
            return jsonify({"merged_data": merged_data}), 200
        else:
            return jsonify({"error": "没有找到数据"}), 404

    except Exception as e:
        logger.error(f"查询数据失败: {str(e)}")
        return jsonify({"error": "查询数据失败", "details": str(e)}), 500
    finally:
        # 关闭数据库连接
        if 'home' in locals():
            home.close()


@app.route('/search', methods=['GET'])
def search_data():
    try:
        search_param = request.args.get('search_param')  # 获取查询参数
        if not search_param:
            return jsonify({'error': 'Search parameter is required'}), 400

        search = Search(db_params)
        # 查询数据
        df = search.get_data_by_search(search_param)

        if not df.empty:
            return jsonify({"merged_data": df.to_dict(orient='records')}), 200
        else:
            return jsonify({"error": "No matching data found"}), 404

    except Exception as e:
        return jsonify({'error': 'An error occurred, please try again later'}), 500


@app.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    """
    更新股票收藏状态
    """
    try:
        # 从前端接收 JSON 数据
        data = request.get_json()
        stock_code = data.get('stock_code')
        is_favorite = data.get('is_favorite')

        # 检查参数有效性
        if not stock_code or not isinstance(is_favorite, int) or is_favorite not in [0, 1]:
            return jsonify({"error": "参数无效，请提供有效的 'stock_code' 和 'is_favorite' (0 或 1)"}), 400

        # 创建数据库实例
        df = Search(db_params)

        # 更新收藏状态
        df.add_favorite_status(stock_code, is_favorite)

        # 返回成功响应
        return jsonify({"message": f"股票 {stock_code} 收藏状态更新为 {is_favorite}"}), 200

    except Exception as e:
        logger.error(f"更新收藏状态失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/favorites', methods=['GET'])
def get_favorites():
    try:
        # 创建 Search 实例
        search = Search(db_params)

        # 查询所有 is_favorite = 1 的记录
        df = search.get_favorites()

        # 检查是否找到了数据
        if not df.empty:
            return jsonify({"merged_data": df.to_dict(orient='records')}), 200
        else:
            return jsonify({"message": "没有收藏的股票"}), 404

    except Exception as e:
        logger.error(f"查询收藏失败: {str(e)}")
        return jsonify({"error": "查询收藏失败", "details": str(e)}), 500


# 启动 Flask 应用和调度器
if __name__ == "__main__":
    logger.info("Flask 启动，启动定时任务调度器...")
    scheduler = start_scheduler()  # 启动定时任务调度器

    # 启动 Flask 服务，禁用自动重载
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
