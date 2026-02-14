from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from .models import ArticleModel, UserKeyword, UserProfile
from .forms import UserKeywordForm, CustomUserCreationForm, UserProfileForm
from .services import (
    fetch_all_categories,
    fetch_user_keywords_news,
    fetch_prefecture_news,
    get_prefecture_articles,
    PREFECTURE_NAMES,
)


def index(request):

    if "reloaded" in request.GET:
        fetch_all_categories()
        if request.user.is_authenticated:
            fetch_user_keywords_news(request.user)
            fetch_prefecture_news(request.user)
        return redirect("/")

    selected_cat = request.GET.get("cat", "")

    # --- 1. 一般カテゴリの記事 ---
    # categoryが 'custom' と 'prefecture' 以外のものを取得
    general_articles = ArticleModel.objects.exclude(
        category__in=["custom", "prefecture"]
    ).order_by("-published_at")

    if selected_cat and selected_cat in dict(ArticleModel.CATEGORY_CHOICES).keys():
        general_articles = general_articles.filter(category=selected_cat)

    # --- マイキーワードを単語ごとに分ける処理 ---
    # --- マイキーワードを単語ごとに分ける処理 ---
    keyword_groups = []
    user_prefecture = None
    prefecture_articles = []

    if request.user.is_authenticated:
        user_keywords = request.user.keywords.all()
        # views.py のマイキーワード部分
        for i, k in enumerate(user_keywords):
            # ターミナルで保存した時に付けたメモ(k.word)と一致するものを全部出す！
            articles = ArticleModel.objects.filter(keyword_tag=k.word).order_by(
                "-published_at"
            )
            keyword_groups.append({"id": i, "word": k.word, "articles": articles})

        # 都道府県情報を取得
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.prefecture:
                user_prefecture = PREFECTURE_NAMES.get(
                    profile.prefecture, profile.prefecture
                )
                prefecture_articles = get_prefecture_articles(request.user)[
                    :10
                ]  # 最大10件
        except UserProfile.DoesNotExist:
            pass

    context = {
        "general_articles": general_articles,
        "keyword_groups": keyword_groups,
        "current_year": timezone.now().year,
        "current_category": selected_cat,
        "category_choices": ArticleModel.CATEGORY_CHOICES,
        "user_prefecture": user_prefecture,
        "prefecture_articles": prefecture_articles,
    }
    return render(request, "news_collector/index.html", context)


class ArticleDetailView(DetailView):
    model = ArticleModel
    template_name = "news_collector/article_detail.html"
    context_object_name = "record"


class UserCreationView(CreateView):
    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = "registration/user_creation.html"
    success_url = reverse_lazy("news_collector:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        from django.contrib.auth import login

        login(self.request, self.object)
        return response


@login_required
def my_page(request):
    # ユーザープロフィールを取得
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # 1. 都道府県フォームの処理
    if request.method == "POST" and "prefecture" in request.POST:
        profile_form = UserProfileForm(request.POST, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect("news_collector:my_page")

    # 2. キーワードフォームの処理
    if request.method == "POST" and "word" in request.POST:
        keyword_form = UserKeywordForm(request.POST)
        if keyword_form.is_valid():
            keyword = keyword_form.save(commit=False)
            keyword.user = request.user
            keyword.save()
            return redirect("news_collector:my_page")

    # 3. 普通にページを開いた時（GET）や、保存が終わった後の処理
    profile_form = UserProfileForm(instance=profile)
    keyword_form = UserKeywordForm()

    # 4. 画面に渡すデータをまとめる
    keyword_list = request.user.keywords.all()

    # 都道府県名を日本語で取得
    current_prefecture_name = None
    if profile.prefecture:
        current_prefecture_name = PREFECTURE_NAMES.get(
            profile.prefecture, profile.prefecture
        )

    context = {
        "keywords": keyword_list,
        "keyword_form": keyword_form,
        "profile_form": profile_form,
        "current_prefecture": current_prefecture_name,
    }
    return render(request, "news_collector/my_page.html", context)


@login_required
def delete_keyword(request, pk):
    # 自分の登録したキーワードの中から、指定されたID(pk)のものを探す
    keyword = UserKeyword.objects.filter(user=request.user, pk=pk).first()
    if keyword:
        keyword.delete()
    return redirect("news_collector:my_page")


@login_required
def custom_logout(request):
    logout(request)
    return render(request, "registration/logout.html")
