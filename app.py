from flask import Flask, render_template, flash, request, session, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
import base64
from forms import *

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from models import *


@app.route('/', methods=['GET', 'POST'])
def index():
    form = BuyBookForm()
    books = Book.query.all()
    return render_template('index.html', books=books, base64=base64, str=str, form=form)


@app.route('/index/like', methods=['GET', 'POST'])
@login_required
def index_like():
    form = BuyBookForm()
    if form.validate_on_submit():
        order = Order.query.filter(Order.book_id == form.book_id.data, Order.seller_id == form.seller_id.data, Order.buyer_id == current_user.id, Order.state == "收藏").first()
        if order:
            flash('您已经收藏过这本书了呢')
        else:
            order = Order(book_id=form.book_id.data, seller_id=form.seller_id.data, buyer_id=current_user.id, state="收藏")
            db.session.add(order)
            db.session.commit()
            flash('收藏成功！')
            return redirect(url_for('index'))

    form = BuyBookForm()
    books = Book.query.all()
    return render_template('index.html', books=books, base64=base64, str=str, form=form)


@app.route('/cart/dislike', methods=['GET', 'POST'])
@login_required
def cart_dislike():
    form = BuyBookForm()
    if form.validate_on_submit():
        orders = Order.query.filter(Order.book_id == form.book_id.data, Order.seller_id == form.seller_id.data, Order.buyer_id == current_user.id, Order.state == "收藏").all()
        print(orders)
        for order in orders:
            db.session.delete(order)
        db.session.commit()
        flash('已取消收藏')
        return redirect(url_for('cart'))

    return render_template('cart.html')


@app.route('/index/buy', methods=['GET', 'POST'])
@login_required
def index_buy():
    form = BuyBookForm()
    if form.validate_on_submit():
        order = Order(book_id=form.book_id.data, seller_id=form.seller_id.data, buyer_id=current_user.id, state="已购买")
        db.session.add(order)
        db.session.commit()
        flash('购买成功！')
        return redirect(url_for('index'))

    form = BuyBookForm()
    books = Book.query.all()
    return render_template('index.html', books=books, base64=base64, str=str, form=form)


@app.route('/cart/buy', methods=['GET', 'POST'])
@login_required
def cart_buy():
    form = BuyBookForm()
    if form.validate_on_submit():
        order = Order.query.filter(Order.book_id == form.book_id.data, Order.seller_id == form.seller_id.data, Order.buyer_id == current_user.id, Order.state == "收藏").first()
        order.state = "已购买"
        db.session.commit()
        flash('购买成功！')
        return redirect(url_for('cart'))

    return render_template('cart.html')


@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('login.html', form=form)

        user = User.query.filter(User.username == form.username.data,
                                 User.password == form.password.data).first()
        if user:
            login_user(user)
            session['login'] = True
            flash('登入成功!')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('login', None)
    flash('已退出登录')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('register.html', form=form)

        user = User.query.filter(User.username == form.username.data).first()
        if user:
            flash('此用户名已被使用!')
        else:
            user = User(username=form.username.data, password=form.password.data, moreinfo=form.moreinfo.data)
            db.session.add(user)
            db.session.commit()
            flash('注册成功')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    form = BuyBookForm()
    likeorders = Order.query.filter(Order.buyer_id == current_user.id, Order.state == "收藏").all()
    likeid = []
    for x in likeorders:
        likeid.append(x.book_id)
    likebooks = Book.query.filter(Book.id.in_(likeid)).all()

    boughtorders = Order.query.filter(Order.buyer_id == current_user.id, Order.state == "已购买").all()
    boughtid = []
    for x in boughtorders:
        boughtid.append(x.book_id)
    boughtbooks = Book.query.filter(Book.id.in_(boughtid)).all()

    return render_template('cart.html', likebooks=likebooks, boughtbooks=boughtbooks, base64=base64, str=str, form=form)


@app.route('/mysell', methods=['GET', 'POST'])
@login_required
def mysell():
    form = BuyBookForm()
    books = Book.query.filter(Book.seller_id == current_user.id).all()

    return render_template('mysell.html', books=books, base64=base64, str=str, form=form)


@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    form = UploadBookForm()
    if form.validate_on_submit():
        image = request.files['image'].read()
        qrcode = request.files['qrcode'].read()
        book = Book(bookname=form.bookname.data, detail=form.detail.data ,price=form.price.data ,image=image ,qrcode=qrcode ,seller_id=current_user.id)
        db.session.add(book)
        db.session.commit()
        flash('这本书已经放在货架上啦！')
        return redirect(url_for('sell'))

    return render_template('sell.html', form=form)


@app.route('/userinfo')
@login_required
def userinfo():
    user = User(current_user.id, current_user.username, current_user.password, current_user.moreinfo)
    return render_template('userinfo.html', user=user)


@app.route('/admin')
def admin():
    return "hello-world"


if __name__ == '__main__':
    app.run()
