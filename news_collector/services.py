import os
import feedparser
import urllib.parse
import requests
from bs4 import BeautifulSoup
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
from .models import ArticleModel, UserProfile
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
from linebot.exceptions import LineBotApiError

# 都道府県名のマッピング
PREFECTURE_NAMES = {
    "hokkaido": "北海道",
    "aomori": "青森県",
    "iwate": "岩手県",
    "miyagi": "宮城県",
    "akita": "秋田県",
    "yamagata": "山形県",
    "fukushima": "福島県",
    "ibaraki": "茨城県",
    "tochigi": "栃木県",
    "gunma": "群馬県",
    "saitama": "埼玉県",
    "chiba": "千葉県",
    "tokyo": "東京都",
    "kanagawa": "神奈川県",
    "niigata": "新潟県",
    "toyama": "富山県",
    "ishikawa": "石川県",
    "fukui": "福井県",
    "yamanashi": "山梨県",
    "nagano": "長野県",
    "gifu": "岐阜県",
    "shizuoka": "静岡県",
    "aichi": "愛知県",
    "mie": "三重県",
    "shiga": "滋賀県",
    "kyoto": "京都府",
    "osaka": "大阪府",
    "hyogo": "兵庫県",
    "nara": "奈良県",
    "wakayama": "和歌山県",
    "tottori": "鳥取県",
    "shimane": "島根県",
    "okayama": "岡山県",
    "hiroshima": "広島県",
    "yamaguchi": "山口県",
    "tokushima": "徳島県",
    "kagawa": "香川県",
    "ehime": "愛媛県",
    "kochi": "高知県",
    "fukuoka": "福岡県",
    "saga": "佐賀県",
    "nagasaki": "長崎県",
    "kumamoto": "熊本県",
    "oita": "大分県",
    "miyazaki": "宮崎県",
    "kagoshima": "鹿児島県",
    "okinawa": "沖縄県",
}

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
                            "title_jp": entry.get("title", ""),
                            "description": entry.get("summary", ""),
                            "source_name": entry.get("source", {}).get(
                                "title", "Google News"
                            ),
                            "category": "custom",
                            "keyword_tag": word_text,
                            "published_at": parse_date(entry),
                        },
                    )
                    print(f"  保存完了: {entry.get('title', '')[:30]}...")
                except Exception as e:
                    print(f"  記事の保存中にエラーが発生しました: {str(e)}")
                    continue

        except Exception as e:
            print(f"キーワード「{word_text}」の処理中にエラーが発生しました: {str(e)}")
            continue

    print("\n=== キーワードニュースの取得が完了しました ===")


def get_47news_latest(area):
    """47NEWSから指定された地域の最新ニュースを取得"""
    url = f"https://www.47news.jp/localnews/area-{area}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")

        articles = soup.select("a.post_item")

        prefecture_name = PREFECTURE_NAMES.get(area, area)
        print(f"\n--- {prefecture_name} の47NEWS 最新ニュース ---")

        count = 0
        for article in articles:
            if count >= 10:  # 最大10件まで取得
                break

            title_el = article.select_one(".item_ttl")
            time_el = article.select_one(".item_time")

            if title_el:
                title = title_el.get_text(strip=True)
                link = "https://www.47news.jp" + article.get("href", "")
                time_str = time_el.get_text(strip=True) if time_el else ""

                # 日付を解析
                published_at = timezone.now()
                if time_str:
                    try:
                        # 簡単な日付解析（例: "2024/2/11 15:30"）
                        if "/" in time_str and ":" in time_str:
                            date_part, time_part = time_str.split(" ")
                            month_day = date_part.split("/")
                            if len(month_day) == 2:
                                month, day = month_day
                                hour_min = time_part.split(":")
                                if len(hour_min) == 2:
                                    hour, minute = hour_min
                                    published_at = timezone.make_aware(
                                        datetime(
                                            timezone.now().year,
                                            int(month),
                                            int(day),
                                            int(hour),
                                            int(minute),
                                        )
                                    )
                    except:
                        pass

                # 記事を保存
                ArticleModel.objects.update_or_create(
                    url=link,
                    defaults={
                        "title_jp": title,
                        "description": "",
                        "source_name": "47NEWS",
                        "category": "prefecture",
                        "keyword_tag": prefecture_name,
                        "published_at": published_at,
                    },
                )
                print(f"  保存完了: {title[:40]}...")
                count += 1

        if count == 0:
            print(f"警告: {prefecture_name} の記事が見つかりませんでした。")

    except Exception as e:
        print(f"47NEWS取得エラー: {e}")


def fetch_prefecture_news(user):
    """ユーザーの都道府県に特化したニュースを取得（47NEWS使用）"""
    try:
        profile = UserProfile.objects.get(user=user)
        if not profile.prefecture:
            print(f"ユーザー {user.username} の都道府県が設定されていません")
            return

        prefecture_name = PREFECTURE_NAMES.get(profile.prefecture, profile.prefecture)
        print(f"\n=== {prefecture_name} のニュースを取得中（47NEWS）... ===")

        # 47NEWSから取得
        get_47news_latest(profile.prefecture)

        print(f"\n=== {prefecture_name} のニュース取得が完了しました ===")

    except UserProfile.DoesNotExist:
        print(f"ユーザー {user.username} のプロフィールが存在しません")
    except Exception as e:
        print(f"都道府県ニュースの取得中にエラーが発生しました: {str(e)}")


def get_prefecture_articles(user):
    """ユーザーの都道府県に関連する記事を取得"""
    try:
        profile = UserProfile.objects.get(user=user)
        if not profile.prefecture:
            return ArticleModel.objects.none()

        prefecture_name = PREFECTURE_NAMES.get(profile.prefecture, profile.prefecture)
        return ArticleModel.objects.filter(
            category="prefecture", keyword_tag=prefecture_name
        ).order_by("-published_at")

    except UserProfile.DoesNotExist:
        return ArticleModel.objects.none()


LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


def send_line_news_notification(user, articles, title_text):
    """取得した記事を、そのユーザーのLINE IDに送信する"""
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("LINE_CHANNEL_ACCESS_TOKEN が設定されていません")
        return

    # 環境変数からではなく、引数で渡された user のプロフィールから ID を取得する
    profile = getattr(user, "profile", None)
    line_user_id = profile.line_user_id if profile else None

    if not line_user_id:
        print(
            f"ユーザー {user.username} の LINE ID が登録されていないためスキップします"
        )
        return

    message = f"{title_text}\n\n"
    for article in articles:
        message += f"■{article.title_jp}\n{article.url}\n\n"

    try:
        # 取得した line_user_id 宛に送信
        line_bot_api.push_message(line_user_id, TextSendMessage(text=message.strip()))
        print(f"LINE送信成功: {user.username} ({line_user_id})")
    except LineBotApiError as e:
        print(f"LINE送信エラー ({user.username}): {e}")


LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


def send_line_news_notification(user, articles, title_text):
    """取得した記事をLINEに送信する"""
    if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_USER_ID:
        print("LINE設定が足りないため送信をスキップします")
        return

    message = f"{title_text}\n\n"
    for article in articles:
        # 'title' ではなく 'title_jp' に修正
        message += f"■{article.title_jp}\n{article.url}\n\n"

    try:
        line_bot_api.push_message(LINE_USER_ID, TextSendMessage(text=message.strip()))
    except LineBotApiError as e:
        print(f"LINE送信エラー: {e}")
