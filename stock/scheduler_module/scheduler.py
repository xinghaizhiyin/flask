# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler  # 导入后台调度器
from apscheduler.triggers.cron import CronTrigger  # 导入Cron触发器，用于定时任务
from stock.data_fetcher.SevenDays import main  # 导入封装好的模块，用于获取数据
from stock.data_fetcher.RealTime import write_realtime_data_to_db  # 导入封装好的模块，用于获取数据
from stock.Analysis.ATable import process_and_insert_stock_data  # 导入封装好的模块，用于获取数据


import logging  # 导入日志模块
from pytz import timezone  # 导入时区模块（如果需要时区处理）

# 配置日志
logger = logging.getLogger(__name__)  # 获取日志记录器

def run_fetch_task():
    """执行数据获取任务"""
    try:
        logger.info("定时任务开始...")  # 记录定时任务开始的信息
        write_realtime_data_to_db()  #获取实时数据并写入数据库

        # 默认获取 7 天，30 天，90 天的数据
        main(days=7)   # 获取并写入 7 天的数据
        main(days=30)  # 获取并写入 30 天的数据
        main(days=90)  # 获取并写入 90 天的数据
        process_and_insert_stock_data()

        logger.info("定时任务完成。")  # 记录任务完成的信息
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}")  # 如果任务执行失败，记录错误信息

def start_scheduler():
    """启动调度器"""
    # 创建调度器对象，设置时区为"Asia/Shanghai"
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    # 设置定时任务，Cron 表达式为每天 1:00 执行任务
    # CronTrigger 表示任务的调度规则，例如 hour=1 表示每天 1 点执行，minute=0 表示第 0 分钟执行，second=0 表示第 0 秒执行
    trigger = CronTrigger(hour=1, minute=0, second=0)  # 每天 1:00 执行任务
    scheduler.add_job(run_fetch_task, trigger)  # 将定时任务添加到调度器

    # 启动调度器
    scheduler.start()  # 启动调度器，开始按照设定的规则执行任务
    logger.info("调度器启动成功，任务会每天 1:00 执行。")  # 记录调度器启动成功的信息

    return scheduler  # 返回调度器对象，以便在其他地方需要时可以进行操作
