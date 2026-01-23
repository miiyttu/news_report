from django.contrib import admin
from .models import ArticleModel

# 管理画面にArticleを表示させる魔法の1行
admin.site.register(ArticleModel)