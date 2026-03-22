# 定时任务调度器
# 用于定期执行自动评价等任务

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from routes.review.service import ReviewService
from models import SessionLocal
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建调度器
scheduler = BackgroundScheduler()


def auto_review_job():
    """
    自动评价任务：7天未评价的已收货订单默认好评
    """
    logger.info("开始执行自动评价任务")
    db = SessionLocal()
    try:
        ReviewService.auto_review(db)
        logger.info("自动评价任务执行完成")
    except Exception as e:
        logger.error(f"自动评价任务执行失败: {e}")
    finally:
        db.close()


def start_scheduler():
    """
    启动调度器
    """
    # 添加自动评价任务，每天凌晨1点执行
    scheduler.add_job(
        auto_review_job,
        CronTrigger(hour=1, minute=0),
        id='auto_review',
        name='自动评价任务',
        replace_existing=True
    )
    scheduler.start()
    logger.info("调度器启动成功")


def stop_scheduler():
    """
    停止调度器
    """
    scheduler.shutdown()
    logger.info("调度器已停止")
