from celery import shared_task
from django.utils import timezone
from .models import Article
from .article_utils import extract_article_content

@shared_task(bind=True, max_retries=3)
def update_article_content(self, article_id):
    """
    記事の本文を非同期で取得して更新するタスク
    
    Args:
        article_id (int): 更新する記事のID
        
    Returns:
        str: 処理結果のメッセージ
    """
    try:
        article = Article.objects.get(id=article_id)
        
        # 既にフルコンテンツを取得済みの場合はスキップ
        if article.full_content_flag:
            return f"記事 {article_id} は既に更新済みです"
            
        # 記事本文を抽出
        new_summary, success = extract_article_content(
            article.url,
            existing_summary=article.summary
        )
        
        # 記事を更新
        article.summary = new_summary
        article.full_content_flag = success
        article.content_updated_at = timezone.now()
        article.save(update_fields=['summary', 'full_content_flag', 'content_updated_at'])
        
        return f"記事 {article_id} の本文を更新しました"
        
    except Article.DoesNotExist:
        # 記事がまだ存在しない場合は5分後に再試行
        self.retry(countdown=60 * 5)
    except Exception as e:
        # その他のエラーが発生した場合も5分後に再試行
        self.retry(countdown=60 * 5, exc=e)