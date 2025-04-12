from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import User, Article
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'login'

@app.route('/')
def home():
    articles = Article.query.filter_by(is_published=True).order_by(Article.timestamp.desc()).all()
    return render_template('index.html', articles=articles)

@app.route('/article/<int:id>')
def article(id):
    article = Article.query.get_or_404(id)
    return render_template('article.html', article=article)

@app.route('/category/<category>')
def category(category):
    articles = Article.query.filter_by(category=category, is_published=True).order_by(Article.timestamp.desc()).all()
    return render_template('category.html', articles=articles, category=category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/create_article', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'POST':
        article = Article(
            title=request.form['title'],
            content=request.form['content'],
            category=request.form['category'],
            image_url=request.form['image_url'],
            author=current_user
        )
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('article', id=article.id))
    return render_template('create_article.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 