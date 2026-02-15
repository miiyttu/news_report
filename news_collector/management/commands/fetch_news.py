from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from news_collector.models import ArticleModel
from news_collector.services import fetch_prefecture_news, fetch_user_keywords_news
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "ユーザーの都道府県に合わせた新着ニュースをLINEで送信し、既読にします"

    def handle(self, *args, **options):
        # 1. ニュース取得のメイン処理（スクレイピング等は別途実行されている前提）
        self.stdout.write("--- ニュース送信処理を開始します ---")

        User = get_user_model()
        users = User.objects.all()

        for user in users:

            self.stdout.write(f"--- {user.username}の最新ニュースを取得中 ---")
            fetch_user_keywords_news(user)
            fetch_prefecture_news(user)

            # ユーザーのプロフィール（都道府県）を取得
            # models.py の related_name="profile" に合わせる
            profile = getattr(user, "profile", None)

            if profile and profile.prefecture:
                # 'saitama' などのコードから '埼玉県' などの表示名を取得
                target_pref_name = profile.get_prefecture_display()

                # 未送信（is_sent=False）の該当都道府県ニュースをすべて取得
                all_unread = ArticleModel.objects.filter(
                    keyword_tag=target_pref_name, is_sent=False
                ).order_by("-published_at")

                if all_unread.exists():
                    # 送信用に最新の5件だけを切り出す
                    to_send = all_unread[:5]

                    # LINE送信用の関数をインポート
                    from news_collector.services import send_line_news_notification

                    # LINE送信実行
                    title_msg = f"【{target_pref_name}の新着ニュース】"
                    send_line_news_notification(user, to_send, title_msg)

                    # 【重要】今回ヒットした未読記事を「すべて」送信済みに更新
                    # これにより、送らなかった古い記事も次回以降は対象外になります
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
