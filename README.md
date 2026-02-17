# News Report

## 概要

「あなた専用ニュースを、もっと簡単に。」
ログイン機能を備えたパーソナライズ型ニュース集約Webアプリケーションです。 膨大なニュースの中から、ユーザーがあらかじめ登録した「特定のキーワード」や「選択した都道府県」に関連する記事だけを自動収集・一覧表示します。

**デプロイ先**: https://news-report-app-ec1c57c2f618.herokuapp.com/

## 開発理由

警察官として勤務する中で、SNS上の不確かな情報や誤報を鵜呑みにしてしまう若者が多い現状を目の当たりにしてきました。また、私自身の世代を含め、新聞を購読しない世帯が増えたことで、信頼できる一次情報に触れる機会が減り、情報の取捨選択がますます困難になっています。 「フェイクニュースに惑わされず、公的機関や信頼できるメディアなどの正確なソースから、自分に必要な情報だけを効率的に受け取れる環境を作りたい」と考えたことが、このアプリの制作動機です。

## 主な機能

### ニュース収集・表示機能

- **カテゴリ別ニュース**：ビジネス、テクノロジー、科学、健康、スポーツ、エンターテイメントの6カテゴリ
- **都道府県ニュース**：47NEWSから47都道府県別のローカルニュースを収集
- **マイキーワード機能**：ユーザーが登録したキーワードに基づくパーソナライズニュース
- **リアルタイム更新**：RSSフィードによる自動ニュース収集

### ユーザー機能

- **ユーザー登録・認証**：新規登録、ログイン、ログアウト機能
- **プロフィール設定**：居住地（都道府県）の登録
- **マイページ**：登録キーワードの管理、削除機能
- **パーソナライズ表示**：ユーザーごとのカスタマイズされたニュース表示

### 自動通知機能

- **LINE通知**：登録した地域の新着ニュースをLINEで自動送信
- **スケジュール実行**：毎日8:00に自動ニュース収集と通知送信
- **送信管理**：送信済み記事の管理（重複送信防止）

### 管理機能

- **Django Admin**：記事、ユーザープロフィール、キーワードの管理
- **管理コマンド**：手動でのニュース収集・通知送信

## 技術構成

### バックエンド

- **Python 3.10+**
- **Django 5.2.8**
- **PostgreSQL** (psycopg2-binary)
- **APScheduler**：スケジュールタスク管理
- **django-apscheduler**：Django連携スケジューラ

### ニュース収集

- **feedparser**：RSSフィード解析
- **BeautifulSoup4**：Webスクレイピング
- **requests**：HTTPクライアント
- **47NEWS API**：地域ニュース取得

### LINE通知

- **line-bot-sdk**：LINE Messaging API

### フロントエンド

- **HTML5 / CSS3**
- **Bootstrap 5.3.0**
- **Google Fonts**：Noto Sans JP, Material Symbols
- **レスポンシブデザイン**：モバイル対応

### デプロイ

- **Heroku**：Procfile対応
- **Gunicorn**：WSGIサーバー
- **Whitenoise**：静的ファイル配信

## 環境変数設定

```
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_USER_ID=your_line_user_id
```

## インストール手順

1. リポジトリをクローン

```bash
git clone https://github.com/username/news-report-app.git
cd news_report_app
```

2. 仮想環境作成と有効化

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

3. 依存パッケージインストール

```bash
pip install -r requirements.txt
```

4. 環境変数設定

```bash
cp .env.example .env
LINE_CHANNEL_ACCESS_TOKEN=あなたのアクセストークン
LINE_CHANNEL_SECRET=あなたのチャネルシークレット
# LINE_USER_ID は通知送信時のフォールバックや管理者用として使用
LINE_USER_ID=あなたのユーザーID
```

5. データベースマイグレーション

```bash
python manage.py makemigrations
python manage.py migrate
```

6. スーパーユーザー作成

```bash
python manage.py createsuperuser
```

7. 開発サーバー起動

```bash
python manage.py runserver
```

## 使い方

1. **ユーザー登録**：トップページから新規登録
2. **プロフィール設定**：居住地（都道府県）を設定
3. **キーワード登録**：興味のあるキーワードをマイページで登録
4. **ニュース閲覧**：カテゴリ別、地域別、キーワード別でニュースを閲覧
5. **LINE通知**：設定した地域の新着ニュースを毎日自動受信

## 管理コマンド

### ニュース収集と通知送信

```bash
python manage.py fetch_news
```

- 全ユーザーの地域ニュースを収集
- 未送信の記事をLINEで通知
- 送信済みフラグを更新

## スケジューラー設定

アプリケーション起動時に自動でスケジューラーが起動し、毎日8:00に以下を実行します：

- 一般ニュースの収集（6カテゴリ）
- 全ユーザーのキーワードニュース収集
- 全ユーザーの地域ニュース収集
- LINE通知送信

## 手動更新

開発中やテスト時に手動でニュースを更新する場合：

```
http://localhost:8000/?reloaded
```

## ライセンス

© 2026 News Report App.
