from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.core.management import call_command
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


def fetch_all_news_job():
    """全ニュースを取得する関数（一般ニュース＋キーワードニュース＋地域ニュース）"""
    logger.info("全ニュース取得ジョブを開始します...")

    try:
        # 1. 一般ニュースを取得
        from news_collector.services import fetch_all_categories

        fetch_all_categories()
        logger.info("一般ニュース取得完了")

        # 2. 全ユーザーのキーワードニュースを取得
        User = get_user_model()
        users = User.objects.all()

        for user in users:
            from news_collector.services import (
                fetch_user_keywords_news,
                fetch_prefecture_news,
            )

            fetch_user_keywords_news(user)
            fetch_prefecture_news(user)
            logger.info(f"ユーザー {user.username} のキーワード・地域ニュース取得完了")

        # 3. LINE通知送信
        call_command("fetch_news")
        logger.info("LINE通知送信完了")

    except Exception as e:
        logger.error(f"ニュース取得ジョブでエラーが発生しました: {e}")


def start():
    """スケジューラーを起動する設定"""
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        fetch_all_news_job,
        trigger="cron",
        hour=8,
        minute=0,
        id="fetch_all_news_regular",
        max_instances=1,
        replace_existing=True,
    )

    register_events(scheduler)
    scheduler.start()
    logger.info("スケジューラーが起動しました（毎日08:00実行）")
