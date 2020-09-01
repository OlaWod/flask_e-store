from flask import Flask, render_template, flash, request, session, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import base64
from exts import db
from forms import *
from models import *
from myYOLO import *

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

from myadmin import *
admin = Admin(app, name='朴实无华后台', index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session, name='用户'))
admin.add_view(MyModelView(Book, db.session, name='书籍'))
admin.add_view(MyModelView(Order, db.session, name='订单'))
admin.add_view(MyModelView(Message, db.session, name='留言'))
admin.add_view(MyModelView(Comment, db.session, name='评论'))
admin.add_view(MyModelView(Report, db.session, name='举报'))


@app.route('/detect', methods=['GET', 'POST'])
def detect():
    form = UploadImgForm()
    if form.validate_on_submit():
        image = request.files['image'].read()
        image = np.asarray(bytearray(image), dtype=np.uint8)
        image = cv2.imdecode(image, 1)

        yolo_net = Yolo()
        detected_image = yolo_net.detect(image, "./weights/YOLO_small.ckpt")
        detected_image = cv2.imencode('.jpg', detected_image)[1]
        detected_image = np.array(detected_image).tostring()

        return render_template('detect_result.html', img=detected_image, base64=base64, str=str)

    return render_template('detect.html', form=form)


@app.route('/airport')
def takeoff():
    return render_template('airport.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = BuyBookForm()
    searchform = SearchForm()
    books = Book.query.filter(Book.state == "正在卖").order_by(db.desc(Book.id)).all()
    return render_template('index.html', books=books, base64=base64, str=str, form=form, searchform=searchform)


@app.route('/index/comment', methods=['GET', 'POST'])
@login_required
def index_comment():
    form = BuyBookForm()
    if form.validate_on_submit():
        session['comment_book_id'] = form.book_id.data
        return redirect(url_for('leave_comment'))

    return render_template('index.html', form=form)


@app.route('/index/report', methods=['GET', 'POST'])
@login_required
def index_report():
    form = BuyBookForm()
    if form.validate_on_submit():
        session['report_book_id'] = form.book_id.data
        return redirect(url_for('leave_report'))

    return render_template('index.html', form=form)


@app.route('/index/like', methods=['GET', 'POST'])
@login_required
def index_like():
    form = BuyBookForm()
    if form.validate_on_submit():
        order = Order.query.filter(Order.book_id == form.book_id.data, Order.seller_id == form.seller_id.data,
                                   Order.buyer_id == current_user.id, Order.state == "收藏").first()
        if order:
            flash('您已经收藏过这本书了呢')
        else:
            book = Book.query.filter(Book.id == form.book_id.data).first()
            order = Order(book_id=form.book_id.data, seller_id=form.seller_id.data, buyer_id=current_user.id,
                          state="收藏", file=book.file)
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
        orders = Order.query.filter(Order.book_id == form.book_id.data, Order.seller_id == form.seller_id.data,
                                    Order.buyer_id == current_user.id, Order.state == "收藏").all()
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
        order = Order.query.filter(Order.book_id == form.book_id.data, Order.seller_id == form.seller_id.data,
                                   Order.buyer_id == current_user.id, Order.state == "已购买").first()
        if order:
            flash('您已经买过这本书了呢')
        else:
            book = Book.query.filter(Book.id == form.book_id.data, Book.seller_id == form.seller_id.data).first()
            return render_template('pay.html', book=book, base64=base64, str=str, form=form)
    return redirect(url_for('cart'))

@app.route('/paysuccess', methods=['GET', 'POST'])
@login_required
def paysuccess():
    form = BuyBookForm()
    if form.validate_on_submit():
        order = Order.query.filter(Order.book_id == form.book_id.data, Order.seller_id == form.seller_id.data,
                                   Order.buyer_id == current_user.id, Order.state == "收藏").first()
        if order:
             order.state = "已购买"
        else:
            book = Book.query.filter(Book.id == form.book_id.data).first()
            book.sales += 1
            order = Order(book_id=form.book_id.data, seller_id=form.seller_id.data, buyer_id=current_user.id, file=book.file, state="已购买")
            db.session.add(order)

        db.session.commit()
        flash('购买成功！')
        return redirect(url_for('cart'))


@app.route('/mysell/delete', methods=['GET', 'POST'])
@login_required
def mysell_delete():
    form = BuyBookForm()
    if form.validate_on_submit():
        orders = Order.query.filter(Order.book_id == form.book_id.data, Order.seller_id == current_user.id,
                                    Order.state == "收藏").all()
        for order in orders:
            db.session.delete(order)

        book = Book.query.filter(Book.id == form.book_id.data, Book.seller_id == current_user.id).first()
        book.state = "已下架"

        db.session.commit()
        flash('下架成功')
        return redirect(url_for('mysell'))

    return render_template('mysell.html')


@app.route('/mysell/edit', methods=['GET', 'POST'])
@login_required
def mysell_edit():
    form = BuyBookForm()
    if form.validate_on_submit():
        session['edit_book_id'] = form.book_id.data
        return redirect(url_for('edit'))

    return render_template('mysell.html', form=form)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditBookForm()
    book = Book.query.filter(Book.id == session['edit_book_id']).first()
    if form.validate_on_submit():

        book.bookname = form.bookname.data
        book.tag = form.tag.data
        book.detail = form.detail.data
        book.file = form.file.data
        book.price = form.price.data
        if form.image.data:
            image = request.files['image'].read()
            book.image = image
        if form.qrcode.data:
            qrcode = request.files['qrcode'].read()
            book.qrcode = qrcode

        db.session.commit()
        flash('书本信息已更改')
        session.pop('edit_book_id', None)
        return redirect(url_for('mysell'))

    return render_template('edit.html', form=form, book=book, int=int)


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
            flash('登录成功!')
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
    books = Book.query.filter(Book.seller_id == current_user.id, Book.state == "正在卖").all()

    return render_template('mysell.html', books=books, base64=base64, str=str, form=form)


@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    form = UploadBookForm()
    if form.validate_on_submit():
        image = request.files['image'].read()
        qrcode = request.files['qrcode'].read()
        book = Book(bookname=form.bookname.data, tag=form.tag.data, detail=form.detail.data, price=form.price.data, state=form.state.data,
                    image=image, qrcode=qrcode, file=form.file.data, seller_id=current_user.id, sales=0)
        db.session.add(book)
        db.session.commit()
        flash('这本书成功上架啦！')
        return redirect(url_for('sell'))

    return render_template('sell.html', form=form)


@app.route('/userinfo', methods=['GET', 'POST'])
@login_required
def userinfo():
    form = EditUserForm()
    user = User(current_user.id, current_user.username, current_user.password, current_user.moreinfo)
    if form.validate_on_submit():
        return redirect(url_for('userinfo_edit'))

    return render_template('userinfo.html', user=user, form=form)


@app.route('/userinfo/edit', methods=['GET', 'POST'])
@login_required
def userinfo_edit():
    form = RegisterForm()
    user = User.query.filter(User.id == current_user.id).first()
    if form.validate_on_submit():
        checkuser = None
        if current_user.username != form.username.data:
            checkuser = User.query.filter(User.username == form.username.data).first()
        if checkuser:
            flash('此用户名已被使用!')
        else:
            user.username = form.username.data
            user.password = form.password.data
            user.moreinfo = form.moreinfo.data
            db.session.commit()
            flash('用户信息已更改')
            return redirect(url_for('userinfo'))

    return render_template('userinfo_edit.html', form=form, user=user)


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = BuyBookForm()
    searchform = SearchForm()
    books = Book.query.filter(Book.state == "正在卖").all()
    if searchform.validate_on_submit():
        content = searchform.content.data
        print(content)
        books = Book.query.filter(or_(Book.id.like('%'+content+'%'), Book.bookname.like('%'+content+'%'), Book.detail.like('%'+content+'%')), Book.state == "正在卖").all()

    return render_template('index.html', books=books, base64=base64, str=str, form=form, searchform=searchform)


@app.route('/hotsort', methods=['GET', 'POST'])
def hotsort():
    form = BuyBookForm()
    searchform = SearchForm
    hotsortform = HotSortForm()
    books = Book.query.filter(Book.state == "正在卖").all()
    if hotsortform.validate_on_submit():
        books = Book.query.order_by(db.desc(Book.sales)).all()

    return render_template('index.html', books=books, base64=base64, str=str, form=form, searchform=searchform, hotsortform=hotsortform)



@app.route('/searchtag', methods=['GET', 'POST'])
def searchtag():
    form = BuyBookForm()
    searchform = SearchForm()
    books = Book.query.filter(Book.state == "正在卖").all()
    if searchform.validate_on_submit():
        content = searchform.content.data
        print(content)
        books = Book.query.filter(Book.tag == content, Book.state == "正在卖").all()

    return render_template('index.html', books=books, base64=base64, str=str, form=form, searchform=searchform)


@app.route('/admin')
def admin():
    return 'hello world'


@app.route('/leave_message', methods=['GET', 'POST'])
def leave_message():
    form = MessageForm()
    messages = Message.query.order_by(db.desc(Message.id)).all()
    if form.validate_on_submit():
        user_id = 0
        username = "匿名用户"
        if current_user.is_authenticated:
            user_id = current_user.id
            username = current_user.username
        message = Message(user_id=user_id, username=username, text=form.text.data)
        db.session.add(message)
        db.session.commit()
        flash('留言成功！')
        return redirect(url_for('leave_message'))

    return render_template('leave_message.html', form=form, messages=messages)


@app.route('/comment', methods=['GET', 'POST'])
@login_required
def leave_comment():
    form = MessageForm()
    book = Book.query.filter(Book.id == session['comment_book_id']).first()
    comments = Comment.query.filter(Comment.book_id == session['comment_book_id']).order_by(db.desc(Comment.id)).all()
    if form.validate_on_submit():
        comment = Comment(user_id=current_user.id, username=current_user.username, book_id=book.id, bookname=book.bookname, text=form.text.data)
        db.session.add(comment)
        db.session.commit()
        flash('评论成功！')
        session.pop('comment_book_id', None)
        return redirect(url_for('index'))

    return render_template('leave_comment.html', form=form, book=book, comments=comments)


@app.route('/report', methods=['GET', 'POST'])
@login_required
def leave_report():
    form = MessageForm()
    book = Book.query.filter(Book.id == session['report_book_id']).first()
    if form.validate_on_submit():
        report = Report(user_id=current_user.id, username=current_user.username, book_id=book.id, bookname=book.bookname, text=form.text.data)
        db.session.add(report)
        db.session.commit()
        flash('举报成功！')
        session.pop('report_book_id', None)
        return redirect(url_for('index'))

    return render_template('leave_report.html', form=form, book=book)


if __name__ == '__main__':
    app.run()
