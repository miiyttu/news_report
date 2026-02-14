from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """ユーザープロフィールモデル"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="ユーザー"
    )

    # 都道府県の選択肢
    PREFECTURE_CHOICES = [
        ("hokkaido", "北海道"),
        ("aomori", "青森県"),
        ("iwate", "岩手県"),
        ("miyagi", "宮城県"),
        ("akita", "秋田県"),
        ("yamagata", "山形県"),
        ("fukushima", "福島県"),
        ("ibaraki", "茨城県"),
        ("tochigi", "栃木県"),
        ("gunma", "群馬県"),
        ("saitama", "埼玉県"),
        ("chiba", "千葉県"),
        ("tokyo", "東京都"),
        ("kanagawa", "神奈川県"),
        ("niigata", "新潟県"),
        ("toyama", "富山県"),
        ("ishikawa", "石川県"),
        ("fukui", "福井県"),
        ("yamanashi", "山梨県"),
        ("nagano", "長野県"),
        ("gifu", "岐阜県"),
        ("shizuoka", "静岡県"),
        ("aichi", "愛知県"),
        ("mie", "三重県"),
        ("shiga", "滋賀県"),
        ("kyoto", "京都府"),
        ("osaka", "大阪府"),
        ("hyogo", "兵庫県"),
        ("nara", "奈良県"),
        ("wakayama", "和歌山県"),
        ("tottori", "鳥取県"),
        ("shimane", "島根県"),
        ("okayama", "岡山県"),
        ("hiroshima", "広島県"),
        ("yamaguchi", "山口県"),
        ("tokushima", "徳島県"),
        ("kagawa", "香川県"),
        ("ehime", "愛媛県"),
        ("kochi", "高知県"),
        ("fukuoka", "福岡県"),
        ("saga", "佐賀県"),
        ("nagasaki", "長崎県"),
        ("kumamoto", "熊本県"),
        ("oita", "大分県"),
        ("miyazaki", "宮崎県"),
        ("kagoshima", "鹿児島県"),
        ("okinawa", "沖縄県"),
    ]

    prefecture = models.CharField(
        "都道府県",
        max_length=20,
        choices=PREFECTURE_CHOICES,
        blank=True,
        null=True,
        help_text="お住まいの都道府県を選択してください",
    )
    created_at = models.DateTimeField("作成日時", default=timezone.now)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "ユーザープロフィール"
        verbose_name_plural = "ユーザープロフィール"

    def __str__(self):
        return f"{self.user.username}のプロフィール"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """ユーザー作成時にプロフィールも作成"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """ユーザー保存時にプロフィールも保存"""
    if hasattr(instance, "profile"):
        instance.profile.save()


class ArticleModel(models.Model):
    # カテゴリの選択肢
    CATEGORY_CHOICES = [
        ("business", "ビジネス"),
        ("technology", "テクノロジー"),
        ("science", "科学"),
        ("health", "健康"),
        ("sports", "スポーツ"),
        ("entertainment", "エンターテイメント"),
        ("prefecture", "地域ニュース"),
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
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    keyword_tag = models.CharField("検索キーワード", max_length=100, blank=True)
    is_sent = models.BooleanField("送信済みフラグ", default=False)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "記事"
        verbose_name_plural = "記事一覧"

    def __str__(self):
        return self.title_jp


class UserKeyword(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="keywords", verbose_name="ユーザー"
    )
    word = models.CharField("マイキーワード", max_length=100)
    registered_at = models.DateTimeField("マイキーワード登録日時", default=timezone.now)

    class Meta:
        ordering = ["-registered_at"]

    def __str__(self):
        return f"{self.user.username}: {self.word}"
