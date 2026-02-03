from django import forms
from .models import UserKeyword
from django.contrib.auth.forms import AuthenticationForm

class UserKeywordForm(forms.ModelForm):
    class Meta:
        model = UserKeyword
        fields = ['word']  # ユーザーに入力させたい項目だけを指定
        labels = {
            'word': '新しいキーワード',
        }
        widgets = {
            'word': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例: Python, ニュース, AI'
            }),
        }
        
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # デフォルトのエラーメッセージを空にする
        self.error_messages['invalid_login'] = ''