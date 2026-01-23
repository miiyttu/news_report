from django.shortcuts import render
from django.utils import timezone
from django.views.generic import DetailView
from .models import ArticleModel

def index(request):
    selected_cat = request.GET.get('cat', '')
    # 要求されたカテゴリの記事を公開日時の新しい順に取得
    articles = ArticleModel.objects.all()
    if selected_cat and selected_cat in dict(ArticleModel.CATEGORY_CHOICES).keys():
        articles = articles.filter(category=selected_cat)
        
    context = {
        'articles': articles.order_by('-published_at'),
        'current_year': timezone.now().year,
        'current_category': selected_cat,
        'category_choices': ArticleModel.CATEGORY_CHOICES,
    }
    return render(request, 'news_collector/index.html', context)

class ArticleDetailView(DetailView):
    model = ArticleModel
    template_name = 'news_collector/article_detail.html'
    context_object_name = 'article'