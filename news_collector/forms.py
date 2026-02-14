from django import forms

from .models import UserKeyword, UserProfile

from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from django.contrib.auth import get_user_model


class UserKeywordForm(forms.ModelForm):

    class Meta:

        model = UserKeyword

        fields = ["word"]  # ユーザーに入力させたい項目だけを指定

        labels = {
            "word": "新しいキーワード",
        }

        widgets = {
            "word": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "例: グルメ, AI, イベント",
                }
            ),
        }


class CustomAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # デフォルトのエラーメッセージを空にする

        self.error_messages["invalid_login"] = ""

        self.fields["username"].label = "ユーザー名"

        self.fields["password"].label = "パスワード"

        self.fields["username"].help_text = (
            "ユーザー名は150文字以下の英数字と @/./+/-/_ のみ使用できます"
        )

        self.fields["password"].help_text = "パスワードは4文字以上で入力してください"

        # エラーメッセージを日本語に

        self.fields["username"].error_messages = {
            "required": "ユーザー名を入力してください。",
            "invalid": "正しいユーザー名を入力してください。",
        }

        self.fields["password"].error_messages = {
            "required": "パスワードを入力してください。",
            "invalid": "正しいパスワードを入力してください。",
        }

        self.error_messages = {
            "invalid_login": "ユーザー名またはパスワードが違います。",
            "inactive": "このアカウントは無効です。",
        }

        # Bootstrapのクラスを追加

        for field in self.fields.values():

            field.widget.attrs["class"] = "form-control"


class CustomUserCreationForm(UserCreationForm):

    class Meta:

        model = get_user_model()

        fields = ("username", "password1", "password2")

        labels = {
            "username": "ユーザー名",
            "password1": "パスワード",
            "password2": "パスワード確認",
        }

        error_messages = {
            "username": {
                "max_length": "ユーザー名は150文字以下で入力してください。",
                "required": "ユーザー名は必須です。",
                "unique": "このユーザー名は既に使用されています。",
                "invalid": "ユーザー名に使用できない文字が含まれています。",
            },
            "password2": {
                "required": "パスワードの確認を入力してください。",
                "password_mismatch": "パスワードが一致しません。",
            },
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["password1"].label = "パスワード"

        self.fields["password2"].label = "パスワード（確認用）"

        self.fields["username"].help_text = (
            "ユーザー名は150文字以下の英数字と @/./+/-/_ のみ使用できます"
        )

        self.fields["password1"].help_text = "パスワードは4文字以上で入力してください"

        self.fields["password2"].help_text = (
            "確認のため、もう一度同じパスワードを入力してください"
        )

        self.fields["password1"].error_messages = {
            "required": "パスワードを入力してください。",
            "password_too_short": "パスワードが短すぎます。4文字以上必要です。",
        }

        for field in self.fields.values():

            field.widget.attrs["class"] = "form-control"

            if field.required:

                field.error_messages = {
                    "required": "この項目は必須です。",
                    **field.error_messages,
                }


class UserProfileForm(forms.ModelForm):
    """ユーザープロフィールフォーム"""

    class Meta:

        model = UserProfile

        fields = ["prefecture"]

        labels = {
            "prefecture": "都道府県",
        }

        widgets = {
            "prefecture": forms.Select(
                attrs={"class": "form-select", "onchange": "this.form.submit()"}
            ),
        }
