from django.core.management.base import BaseCommand
from news_collector.services import fetch_all_categories, fetch_user_keywords_news
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '手動でニュースを取得する'

    def handle(self, *args, **options):
        try:
            self.stdout.write('ニュース取得開始...')
            
            # 全カテゴリのニュースを取得
            fetch_all_categories()
            self.stdout.write(self.style.SUCCESS('一般ニュース取得完了'))
            
            # 全ユーザーのキーワードニュースを取得
            User = get_user_model()
            users = User.objects.all()
            
            for user in users:
                fetch_user_keywords_news(user)
                self.stdout.write(self.style.SUCCESS(f'ユーザー {user.username} のキーワードニュース取得完了'))
            
            self.stdout.write(self.style.SUCCESS('全ニュース取得完了'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'エラー: {str(e)}'))