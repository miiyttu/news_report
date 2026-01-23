from django.urls import path
from . import views
from .views import ArticleDetailView  

app_name = 'news_collector'

urlpatterns = [
    path('', views.index, name='index'),
    path('article/<int:pk>/', ArticleDetailView.as_view(), name='article_detail'),
]