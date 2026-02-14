import os
import re
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import DetailView, CreateView
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot import LineBotApi, WebhookHandler
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
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # 都道府県フォーム または LINE通知フォーム の保存処理
        if form_type in ["prefecture", "line"]:
            profile_form = UserProfileForm(request.POST, instance=profile)
            if profile_form.is_valid():  # ここを is_valid() に修正
                profile_form.save()
                return redirect("news_collector:my_page")

        # キーワードフォームの保存処理
        if "word" in request.POST:
            keyword_form = UserKeywordForm(request.POST)
            if keyword_form.is_valid():
                keyword = keyword_form.save(commit=False)
                keyword.user = request.user
                keyword.save()
                return redirect("news_collector:my_page")

    # 画面表示用のデータ準備
    profile_form = UserProfileForm(instance=profile)
    keyword_form = UserKeywordForm()
    keyword_list = request.user.keywords.all()

    current_prefecture_name = (
        PREFECTURE_NAMES.get(profile.prefecture, profile.prefecture)
        if profile.prefecture
        else None
    )

    context = {
        "keywords": keyword_list,
        "keyword_form": keyword_form,
        "profile_form": profile_form,
        "current_prefecture": current_prefecture_name,
        "is_line_subscribed": profile.is_line_subscribed,  # これでDBの最新値が渡る
        "is_line_linked": bool(profile.line_user_id),
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


# LINE Botの設定（.env から読み込み）
line_bot_api = LineBotApi(os.environ.get("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("LINE_CHANNEL_SECRET"))


@csrf_exempt
def callback(request):
    """LINEからのメッセージを受け取る窓口"""
    signature = request.META.get("HTTP_X_LINE_SIGNATURE", "")
    body = request.body.decode("utf-8")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden()

    return HttpResponse("OK")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """LINEメッセージの内容を解析して連携する"""
    text = event.message.text
    line_user_id = event.source.user_id  # LINEのユーザー固有ID

    # ユーザーが送ってきた文章に【ユーザー名】が含まれているかチェック
    match = re.search(r"ユーザー名【(.+)】でLINEと連携します", text)

    if match:
        username = match.group(1)
        User = get_user_model()

        try:
            # 1. ユーザーを探す
            user = User.objects.get(username=username)
            # 2. プロフィールにLINE IDを保存する
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.line_user_id = line_user_id
            profile.save()

            reply_text = f"【連携成功】\n{user.username}さん、こんにちは！LINE連携が完了しました。これからニュースをお届けします。"
        except User.DoesNotExist:
            reply_text = f"エラー：ユーザー「{username}」が見つかりませんでした。サイトのユーザー名を正しく入力してください。"
    else:
        # 指定の文章以外が送られてきた場合
        reply_text = "連携するには、マイページに表示されている文章をそのままコピーして送ってくださいね！"

    # LINEに応答を返す
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
