from flask import Flask, render_template, request, redirect, flash, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # フラッシュメッセージに必要なシークレットキー

# セッションのキーを設定 本番環境では書き換える
app.config['SECRET_KEY'] = os.urandom(24)

# ログインマネージャーの初期化
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'この機能を利用するにはログインが必要です'
login_manager.login_message_category = 'info'

db = SQLAlchemy()
DB_INFO = {
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5432,
    'db': 'postgres'
}

migrate = Migrate(app, db)

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg://{user}:{password}@{host}:{port}/{db}'.format(**DB_INFO)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db.init_app(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.String(1000), nullable=False)
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(tokyo_timezone))
    img_name = db.Column(db.String(100), nullable=True)

# login用DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
# 現在のユーザを識別するためのログインマネージャーの設定
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/admin")
@login_required
def admin():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("admin.html", posts=posts)

# 記事の作成
@app.route('/create', methods=['GET','POST'])
@login_required
def create():
    # リクエストメソッドの判別
    if request.method == 'POST':
    # リクエストできた情報の取得
        title = request.form.get('title')
        body = request.form.get('body')
        # ファイルのアップロード
        file = request.files.get('image')
        img_name = None  # デフォルトでNoneに設定
        
        # タイトルと本文のバリデーション
        if not title or not body:
            flash('タイトルと内容は必須です', 'error')
            return render_template("create.html", method="GET")
        
        if file and file.filename != '':
            # 画像ファイルの拡張子チェック
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            try:
                # ファイル名に「.」がない場合の処理
                if '.' in file.filename:
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    if file_ext in allowed_extensions:
                        # ファイル名の安全な処理
                        img_name = secure_filename(file.filename)
                        # 保存先ディレクトリの確認と作成
                        upload_dir = os.path.join(app.static_folder, 'img')
                        os.makedirs(upload_dir, exist_ok=True)
                        # ファイルの保存
                        file_path = os.path.join(upload_dir, img_name)
                        file.save(file_path)
                    else:
                        # 不正なファイル形式の場合
                        flash('画像ファイル（PNG、JPG、GIF）のみアップロードできます。', 'error')
                        return render_template("create.html", method="GET", title=title, body=body)
                else:
                    # ファイル名に拡張子がない場合
                    flash('有効なファイル名ではありません。', 'error')
                    return render_template("create.html", method="GET", title=title, body=body)
            except Exception as e:
                print(f"ファイル処理エラー: {e}")
                flash('ファイル処理中にエラーが発生しました。', 'error')
                return render_template("create.html", method="GET", title=title, body=body)
        
        # 情報の保存
        post = Post(title=title, body=body, img_name=img_name)
        db.session.add(post)
        db.session.commit()
        flash('記事が正常に投稿されました。', 'success')
        return redirect('/admin')
    elif request.method == 'GET':
        return render_template("create.html", method="GET")

    
# 記事の更新
@app.route('/<int:post_id>/update', methods=['GET','POST'])
@login_required
def update(post_id):
    post = Post.query.get(post_id)
    if not post:
        flash('記事が見つかりません', 'error')
        return redirect('/admin')
        
    # リクエストメソッドの判別
    if request.method == 'POST':
        # リクエストできた情報の取得
        post.title = request.form.get('title')
        post.body = request.form.get('body')
        
        # ファイルのアップロード処理
        file = request.files.get('image')
        if file and file.filename != '':
            # 画像ファイルの拡張子チェック
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            try:
                # ファイル名に「.」がない場合の処理
                if '.' in file.filename:
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    if file_ext in allowed_extensions:
                        # ファイル名の安全な処理
                        img_name = secure_filename(file.filename)
                        # 保存先ディレクトリの確認と作成
                        upload_dir = os.path.join(app.static_folder, 'img')
                        os.makedirs(upload_dir, exist_ok=True)
                        # ファイルの保存
                        file_path = os.path.join(upload_dir, img_name)
                        file.save(file_path)
                        # 画像名を更新
                        post.img_name = img_name
                    else:
                        # 不正なファイル形式の場合
                        flash('画像ファイル（PNG、JPG、GIF）のみアップロードできます。', 'error')
                        return render_template("update.html", post=post)
                else:
                    # ファイル名に拡張子がない場合
                    flash('有効なファイル名ではありません。', 'error')
                    return render_template("update.html", post=post)
            except Exception as e:
                print(f"ファイル処理エラー: {e}")
                flash('ファイル処理中にエラーが発生しました。', 'error')
                return render_template("update.html", post=post)
        
        db.session.commit()
        flash('記事が正常に更新されました。', 'success')
        return redirect('/admin')
    elif request.method == 'GET':
        return render_template("update.html", post=post)
    
# 記事の削除
@app.route('/<int:post_id>/delete')
@login_required
def delete(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/admin')

# ユーザーが記事を閲覧できる画面（index.html）
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts)

# ユーザーが個別記事を閲覧できる画面(readmore.html)
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("readmore.html", post=post)

# サインアップ機能
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User(username=username, password=password)
        # パスワードのハッシュ化
        user.password = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    elif request.method == 'GET':
        return render_template("signup.html")
        

# ログイン機能
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # ユーザー名とパスワードの受け取り
        username = request.form.get('username')
        password = request.form.get('password')
        # ユーザー名を元にデータベースから情報を取得
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('ログインしました', 'success')
            return redirect('/admin')
        else:
            flash('ユーザー名かパスワードが間違っています', 'error')
            return render_template("login.html")
    elif request.method == 'GET':
        return render_template("login.html")
        
            
# ログアウト機能
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

