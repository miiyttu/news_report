from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from news_collector.models import ArticleModel
from news_collector.services import fetch_prefecture_news, fetch_user_keywords_news
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "ユーザーの都道府県に合わせた新着ニュースをLINEで送信し、既読にします"

    def handle(self, *args, **options):
        self.stdout.write("--- ニュース送信処理を開始します ---")

        User = get_user_model()
        users = User.objects.all()

        for user in users:

            self.stdout.write(f"--- {user.username}の最新ニュースを取得中 ---")
            fetch_user_keywords_news(user)
            fetch_prefecture_news(user)

            profile = getattr(user, "profile", None)

            if profile and profile.prefecture:
                target_pref_name = profile.get_prefecture_display()

                all_unread = ArticleModel.objects.filter(
                    keyword_tag=target_pref_name, is_sent=False
                ).order_by("-published_at")

                if all_unread.exists():
                    to_send = all_unread[:5]

                    from news_collector.services import send_line_news_notification

                    title_msg = f"【{target_pref_name}の新着ニュース】"
                    send_line_news_notification(user, to_send, title_msg)

                    all_unread.update(is_sent=True)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"{user.username}様({target_pref_name}): 最新{len(to_send)}件を送信し、残りの未読分もすべて既読にしました"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{target_pref_name}: 新しい記事はありません"
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"{user.username}: 都道府県が設定されていないためスキップしました"
                    )
                )

        self.stdout.write("--- すべての送信処理が完了しました ---")
