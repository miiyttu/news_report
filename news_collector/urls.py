from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import ArticleDetailView, custom_logout, UserCreationView
from .forms import CustomAuthenticationForm

app_name = "news_collector"

urlpatterns = [
    path("", views.index, name="index"),
    path("article/<int:pk>/", ArticleDetailView.as_view(), name="article_detail"),
    path("mypage/", views.my_page, name="my_page"),
    path("delete_keyword/<int:pk>/", views.delete_keyword, name="delete_keyword"),
    path("register/", UserCreationView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=CustomAuthenticationForm,
            next_page="news_collector:index",
        ),
        name="login",
    ),
    path("callback/", views.callback, name="callback"),
    path("logout/", custom_logout, name="logout"),
]
