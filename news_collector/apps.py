from django.apps import AppConfig
import os


class NewsCollectorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "news_collector"

    def ready(self):
        import os

        print(f"環境変数 RUN_MAIN: {os.environ.get('RUN_MAIN')}")

        if os.environ.get("RUN_MAIN") == "true":
            print("条件に一致、スケジューラーを起動します")
            try:
                from . import tasks

                tasks.start()
                print("スケジューラー開始完了")
            except Exception as e:
                print(f"スケジューラーエラー: {e}")
        else:
            print("条件不一致、スケジューラーを起動しません")

    def ready(self):
        if os.environ.get("RUN_MAIN") == "true":
            from . import operator

            operator.start()
