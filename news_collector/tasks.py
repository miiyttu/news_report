from apscheduler.schedulers.background import BackgroundScheduler
from .management.commands.fetch_news import Command
import atexit
import logging
import pytz

logger = logging.getLogger(__name__)

def scheduled_fetch():
    """スケジュール実行用のニュース取得"""
    try:
        command = Command()
        command.handle()
        logger.info("スケジュール実行: ニュース取得完了")
    except Exception as e:
        logger.error(f"スケジュール実行エラー: {str(e)}")

def start():
    # 日本時間のタイムゾーンを設定
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    scheduler = BackgroundScheduler(timezone=tokyo_tz)
    
    # 1時間ごとに実行
    scheduler.add_job(scheduled_fetch, 'cron', minute=0, timezone=tokyo_tz)
    
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    logger.info("スケジューラー開始（1時間ごとに実行）")