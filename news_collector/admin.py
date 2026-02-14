from django.contrib import admin
from .models import ArticleModel
from .models import UserProfile, UserKeyword

admin.site.register(ArticleModel)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "prefecture")


@admin.register(UserKeyword)
class UserKeywordAdmin(admin.ModelAdmin):
    list_display = ("user", "word", "registered_at")
    list_filter = ("user",)
