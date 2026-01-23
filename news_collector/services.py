import feedparser
from datetime import datetime 
from django.utils import timezone
from .models import Article

# カテゴリごとのGoogle News RSS URL
RSS_URLS = {
    'business': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja',
    'technology': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja',
    'science': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja',
    'health': 'https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=ja&gl=JP&ceid=JP%3Aja',
    'sports': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1Y1Y5U0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja',
    'entertainment': 'https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja'
}

def parse_date(entry):
    if hasattr(entry, 'published_parsed'):
        return timezone.make_aware(datetime(*entry.published_parsed[:6]))
    return timezone.now()

def fetch_google_news(category='technology'):
    print(f"\n=== {category.upper()} を取得中... ===")
    try:
        feed = feedparser.parse(RSS_URLS[category])
        for entry in feed.entries[:10]:
            if Article.objects.filter(url=entry.link).exists():
                continue

            Article.objects.create(
                title_jp=entry.title,
                url=entry.link,
                source_name=entry.get('source', {}).get('title', 'Google News'),
                published_at=parse_date(entry),
                category=category,
                summary="詳細な内容は公式サイトにてご確認ください。",
                full_content_flag=False
            )
            print(f"保存成功: {entry.title[:20]}...")
    except Exception as e:
        print(f"エラー: {e}")

def fetch_all_categories():
    for cat in RSS_URLS.keys():
        fetch_google_news(cat)
    print("\n--- 完了しました！ ---")