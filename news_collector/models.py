from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class ArticleModel(models.Model):
    # カテゴリの選択肢
    CATEGORY_CHOICES = [
        ("business", "ビジネス"),
        ("technology", "テクノロジー"),
        ("science", "科学"),
        ("health", "健康"),
        ("sports", "スポーツ"),
        ("entertainment", "エンターテイメント"),
    ]

    # 基本情報
    title_jp = models.CharField("日本語タイトル", max_length=500)
    url = models.TextField("URL", unique=True)
    source_name = models.CharField("情報源", max_length=100, blank=True)
    category = models.CharField(
        "カテゴリ", max_length=20, choices=CATEGORY_CHOICES, default="technology"
    )
    description = models.TextField("概要", blank=True)
    published_at = models.DateTimeField("公開日時", default=timezone.now)
    created_at = models.DateTimeField("作成日時", default=timezone.now)
    keyword_tag = models.CharField("検索キーワード", max_length=100, blank=True)
    
    class Meta:
        ordering = ["-published_at"]
        verbose_name = "記事"
        verbose_name_plural = "記事一覧"

    def __str__(self):
        return self.title_jp


class UserKeyword(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="keywords", verbose_name="ユーザー")
    word = models.CharField("マイキーワード", max_length=100)
    registered_at = models.DateTimeField("マイキーワード登録日時", default=timezone.now)
    
    class Meta:
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.user.username}: {self.word}"
