# Flask ブログアプリケーション

シンプルで使いやすいFlask製ブログアプリケーションです。管理者はログインして記事の投稿、編集、削除ができ、一般ユーザーは記事を閲覧できます。

## 機能

- **ユーザー認証**: ログイン/ログアウト機能
- **記事管理**: 記事の作成、編集、削除
- **画像アップロード**: 記事に画像を添付可能
- **レスポンシブデザイン**: モバイルデバイスにも対応

## 技術スタック

- **バックエンド**: Python/Flask
- **データベース**: PostgreSQL
- **ORM**: SQLAlchemy
- **認証**: Flask-Login
- **マイグレーション**: Flask-Migrate
- **フロントエンド**: HTML/CSS/Bootstrap

## インストール方法

### 前提条件

- Python 3.8以上
- PostgreSQL

### セットアップ

1. リポジトリをクローン
   ```
   git clone https://github.com/あなたのユーザー名/flask-blog-app.git
   cd flask-blog-app
   ```

2. 仮想環境を作成して有効化
   ```
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. 依存パッケージをインストール
   ```
   pip install -r requirements.txt
   ```

4. PostgreSQLデータベースの設定
   - PostgreSQLをインストールして起動
   - `myapp.py`内のデータベース設定を自分の環境に合わせて変更

   ```python
   DB_INFO = {
       'user': 'postgres',
       'password': 'postgres',
       'host': 'localhost',
       'port': 5432,
       'db': 'postgres'
   }
   ```

5. データベースのマイグレーション
   ```
   flask db upgrade
   ```

6. アプリケーションの起動
   ```
   flask run
   ```

## 使い方

1. ブラウザで`http://localhost:5000`にアクセスすると、ブログのトップページが表示されます
2. 管理者機能を利用するには`http://localhost:5000/login`からログインします
3. ログイン後、記事の作成・編集・削除が可能になります

## 管理者アカウントの作成

初回起動時に管理者アカウントを作成するには:

1. `/signup`にアクセスして管理者アカウントを作成
2. 作成したアカウント情報でログイン

## ライセンス

MIT

## 開発者

autotunecode
