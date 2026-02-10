from .models import ArticleModel

def latest_news_time(request):
    latest = ArticleModel.objects.order_by('-updated_at').first()
    return {'latest_news_time': latest.updated_at if latest else None}