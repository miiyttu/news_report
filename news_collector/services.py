import feedparser
import urllib.parse
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
from .models import ArticleModel

# カテゴリごとのGoogle News RSS URL
RSS_URLS = {
    "business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja",
    "technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja",
    "science": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja",
    "health": "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ?hl=ja&gl=JP&ceid=JP%3Aja",
    "sports": "https://news.google.com/rss/search?q=when:1d+スポーツ&hl=ja&gl=JP&ceid=JP:ja",
    "entertainment": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB?hl=ja&gl=JP&ceid=JP:ja",
}


def parse_date(entry):
    if hasattr(entry, "published_parsed"):
        return timezone.make_aware(datetime(*entry.published_parsed[:6]))
    return timezone.now()


def fetch_google_news(category="technology"):
    print(f"\n=== {category.upper()} を取得中... ===")
    try:
        feed = feedparser.parse(RSS_URLS[category])
        for entry in feed.entries[:10]:
            if ArticleModel.objects.filter(url=entry.link).exists():
                continue

            ArticleModel.objects.create(
                title_jp=entry.title,
                description=entry.get("summary", ""),
                url=entry.link,
                source_name=entry.get("source", {}).get("title", "Google News"),
                published_at=parse_date(entry),
                category=category,
            )
            print(f"保存成功: {entry.title[:20]}...")
    except Exception as e:
        print(f"エラー: {e}")


def fetch_all_categories():
    three_days_ago = timezone.now() - timedelta(days=3)
    deleted_count, _ = ArticleModel.objects.filter(
        published_at__lt=three_days_ago
    ).delete()

    if deleted_count > 0:
        print(f"DEBUG: 古い記事を {deleted_count} 件削除しました。")

    for cat in RSS_URLS.keys():
        fetch_google_news(cat)
    print("\n--- 完了しました！ ---")

def fetch_user_keywords_news(user):
    print(f"\n=== {user.username} のキーワードニュースを取得中... ===")
    keywords = user.keywords.all()

    for k in keywords:
        word_text = k.word.strip()
        print(f"キーワード「{word_text}」で検索中...")
        try:
            encoded_keyword = urllib.parse.quote(word_text)
            search_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ja&gl=JP&ceid=JP:ja"
            print(f"検索URL: {search_url}")

            feed = feedparser.parse(search_url)
            print(f"  検索結果: {len(feed.entries)}件")
            
            for entry in feed.entries[:15]:  # 最大15件まで処理
                try:
                    ArticleModel.objects.update_or_create(
                        url=entry.link,
                        defaults={
                            "title_jp": entry.get('title', ''),
                            "description": entry.get('summary', ''),
                            "source_name": entry.get('source', {}).get('title', 'Google News'),
                            "category": "custom",
                            "keyword_tag": word_text,
                            "published_at": parse_date(entry),
                        }
                    )
                    print(f"  保存完了: {entry.get('title', '')[:30]}...")
                except Exception as e:
                    print(f"  記事の保存中にエラーが発生しました: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"キーワード「{word_text}」の処理中にエラーが発生しました: {str(e)}")
            continue

    print("\n=== キーワードニュースの取得が完了しました ===")