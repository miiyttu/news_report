from django.db import models
from django.utils import timezone

class ArticleModel(models.Model):
    # カテゴリの選択肢
    CATEGORY_CHOICES = [
        ('business', 'ビジネス'),
        ('technology', 'テクノロジー'),
        ('science', '科学'),
        ('health', '健康'),
        ('sports', 'スポーツ'),
        ('entertainment', 'エンターテイメント'),
    ]
    
    # 基本情報
    title_jp = models.CharField('日本語タイトル', max_length=200)
    url = models.URLField('URL', unique=True)
    source_name = models.CharField('情報源', max_length=100, blank=True)
    summary = models.TextField('要約', blank=True)
    category = models.CharField('カテゴリ', max_length=20, choices=CATEGORY_CHOICES, default='technology')
    
    # 日付関連
    published_at = models.DateTimeField('公開日時', default=timezone.now)
    created_at = models.DateTimeField('作成日時', default=timezone.now)
    

    class Meta:
        ordering = ['-published_at']
        verbose_name = '記事'
        verbose_name_plural = '記事一覧'

    def __str__(self):
        return self.title_jp