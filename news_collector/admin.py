from django.contrib import admin
from .models import ArticleModel
from .models import UserProfile, UserKeyword


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "prefecture", "is_line_subscribed", "line_user_id")
    list_filter = ("user", "prefecture", "is_line_subscribed")


@admin.register(UserKeyword)
class UserKeywordAdmin(admin.ModelAdmin):
    list_display = ("user", "word", "registered_at")
    list_filter = ("user",)


@admin.register(ArticleModel)
class ArticleModelAdmin(admin.ModelAdmin):
    list_display = ("title_jp", "category", "keyword_tag", "published_at", "is_sent")
    list_filter = ("category", "keyword_tag", "is_sent", "published_at")
    search_fields = ("title_jp", "keyword_tag")
