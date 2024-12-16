from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
import logging
from stock_processor import process_all_stocks  # 你之前的代码文件
from database import MySQLDatabase  # 你之前的数据库处理代码
from flask_cors import CORS  # 导入 CORS
from datetime import datetime
import pandas as pd

app = Flask(__name__)
CORS(app)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接参数
db_params = {
    'host': 'localhost',
    'user': 'root',
    'password': 'admin',
    'database': 'test'
}

# 定时任务函数
def job():
    try:
        logger.info("定时任务开始执行...")

        # 获取排名数据
        ranked_df = process_all_stocks()  # 获取所有股票处理结果的DataFrame

        # 将 NaN 值替换为 None (即 NULL 在数据库中的表示)
        ranked_df = ranked_df.where(pd.notnull(ranked_df), None)

        # 创建数据库连接
        db = MySQLDatabase(**db_params)
        db.create_table_if_not_exists("stock_rankings")

        # 插入数据到数据库
        for index, row in ranked_df.iterrows():
            data = {
                'stock_code': row['股票代码'],
                'stock_name': row['股票名称'],
                'latest_price': row['最新价格'],
                'avg_1month': row['近一个月均价'],
                'avg_3months': row['近三个月均价'],
                'avg_1year': row['近一年均价'],
                'month_change_pct': row['一个月涨跌幅(%)'],
                'three_month_change_pct': row['三个月涨跌幅(%)'],
                'year_change_pct': row['一年涨跌幅(%)'],
                'change_pct': row['涨跌幅(%)'],  # 新增的涨跌幅字段
                'amplitude_pct': row['振幅(%)'],  # 新增的振幅字段
                'avg_5days': row['近五天均价'],  # 新增字段：最近五天的平均价
                'down_count': row['五天下跌次数'],  # 新增字段：下跌的次数
                'data_write_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 去除 T 和微秒部分
            }

            db.insert_data("stock_rankings", data)

        db.close()
        logger.info("定时任务成功完成！数据已写入数据库。")
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}")


# 创建调度器并添加定时任务
def start_scheduler():
    if not hasattr(start_scheduler, "scheduler"):
        start_scheduler.scheduler = BackgroundScheduler(timezone=timezone('Asia/Shanghai'))

        # 设置定时任务，Cron 表达式为每天 1:00 执行
        trigger = CronTrigger(hour=13, minute=55, second=0)  # 每天 13:55 执行任务
        start_scheduler.scheduler.add_job(job, trigger)

        # 启动调度器
        start_scheduler.scheduler.start()
        logger.info("调度器启动成功，任务会每天 13:55 执行。")
    else:
        logger.info("调度器已经启动，无需重复启动。")

# 新增手动触发接口
@app.route('/run_scheduler_job', methods=['POST'])
def run_scheduler_job():
    try:
        logger.info("手动触发定时任务开始...")
        job()  # 手动执行定时任务函数
        logger.info("手动触发定时任务成功完成。")
        return jsonify({"message": "手动触发任务成功！"}), 200
    except Exception as e:
        logger.error(f"手动触发定时任务失败: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_sorted_stock_data', methods=['GET'])
def get_sorted_stock_data():
    try:
        # 从前端获取最新价格参数，若没有提供则默认值为 10
        latest_price = request.args.get('latest_price', default=10, type=float)

        # 确保传入的 latest_price 是合理的
        if latest_price <= 0:
            return jsonify({"error": "最新价格必须是大于 0 的数字"}), 400

        # 创建数据库连接并查询数据
        db = MySQLDatabase(**db_params)
        sorted_df = db.query_stock_data(latest_price)

        # 关闭数据库连接
        db.close()

        if not sorted_df.empty:
            # 将查询结果转换为字典列表返回
            result = sorted_df.to_dict(orient='records')
            return jsonify(result)
        else:
            return jsonify({"message": "未查询到数据或发生错误"}), 404
    except Exception as e:
        logger.error(f"查询失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/search_stock', methods=['GET'])
def search_stock_api():
    query = request.args.get('query', default=None, type=str)

    # 至少提供一个查询条件
    if not query:
        return jsonify({"error": "请输入股票代码或股票名称"}), 400

    try:
        # 创建数据库实例并调用查询函数
        db = MySQLDatabase(**db_params)
        result = db.search_stock_data(query)
        db.close()

        if not result.empty:
            return jsonify(result.to_dict(orient='records')), 200
        else:
            return jsonify({"message": "未找到匹配的股票数据"}), 404
    except Exception as e:
        return jsonify({"error": f"查询失败: {str(e)}"}), 500


@app.route('/update_favorite_status', methods=['POST'])
def update_favorite_status():
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
        db = MySQLDatabase(**db_params)

        # 更新收藏状态
        db.update_favorite_status(stock_code, is_favorite)
        db.close()

        # 返回成功响应
        return jsonify({"message": f"股票 {stock_code} 收藏状态更新为 {is_favorite}"}), 200

    except Exception as e:
        logger.error(f"更新收藏状态失败: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/get_favorite_stocks', methods=['GET'])
def get_favorite_stocks():
    """查询所有被收藏的股票数据 (is_favorite=1)"""
    try:
        # 创建数据库连接
        db = MySQLDatabase(**db_params)

        # 查询收藏的股票数据
        favorite_df = db.query_favorite_stocks()

        # 关闭数据库连接
        db.close()

        if not favorite_df.empty:
            # 将查询结果转换为字典列表返回
            result = favorite_df.to_dict(orient='records')
            return jsonify(result)
        else:
            return jsonify({"message": "未查询到收藏的股票数据"}), 404
    except Exception as e:
        logger.error(f"查询收藏股票失败: {e}")
        return jsonify({"error": str(e)}), 500


# Flask 启动时，直接启动定时任务调度器
if __name__ == '__main__':
    logger.info("Flask 启动，启动定时任务调度器...")
    start_scheduler()  # 启动定时任务调度器

    # 启动 Flask 服务，允许多线程运行
    # 启动 Flask 服务，监听所有可用的 IP 地址
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True, use_reloader=False)
