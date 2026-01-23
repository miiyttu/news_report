import requests
from newspaper import Article as NewspaperArticle
from newspaper import Config

def extract_article_content(url):
    """
    URLから本文を抽出する。Googleニュースのリダイレクト対応。
    待ち時間を厳格に制限してフリーズを防ぐ。
    """
    # newspaperの設定作成
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    config.request_timeout = 5  # 本文取得を5秒でタイムアウトさせる

    try:
        # 1. Googleニュースのリダイレクト解決（ここも短く5秒）
        response = requests.get(url, headers={'User-Agent': config.browser_user_agent}, timeout=5, allow_redirects=True)
        final_url = response.url

        # 2. newspaper3kで解析
        article = NewspaperArticle(final_url, config=config)
        article.download()  # ここでconfigのタイムアウトが適用される
        article.parse()
        
        if article.text and len(article.text) > 100:
            return article.text
        return None

    except Exception as e:
        # タイムアウト等のエラー時は即座にNoneを返して次に進む
        print(f"  (抽出スキップ: {str(e)[:50]})")
        return None