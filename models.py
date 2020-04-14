from app import db
from flask_login import UserMixin


# 书
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bookname = db.Column(db.String(100), nullable=False)  # 书名
    detail = db.Column(db.Text)  # 详细介绍
    price = db.Column(db.Float, nullable=False)  # 单价
    sales = db.Column(db.Integer, nullable=False)  # 销量
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # 卖家id,外键
    state = db.Column(db.String(100), nullable=False)  # 书本状态
    # 书本状态：正在卖; 已下架
    tag = db.Column(db.String(100))  # 标签
    image = db.Column(db.LargeBinary(length=65536))  # 照片
    qrcode = db.Column(db.LargeBinary(length=65536), nullable=False)  # 付款码
    file = db.Column(db.Text, nullable=False)  # 文件的磁力链接


# 用户
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)  # 用户名
    password = db.Column(db.Text, nullable=False)  # 密码
    moreinfo = db.Column(db.Text)  # 更多信息

    def __init__(self, id=None, username=None, password=None, moreinfo=None):
        self.id = id
        self.username = username
        self.password = password
        self.moreinfo = moreinfo

    def get_id(self):
        return str(self.id)


# 管理员
class MyAdministrator(db.Model, UserMixin):
    __tablename__ = 'administrators'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)  # 用户名
    password = db.Column(db.Text, nullable=False)  # 密码

    def __init__(self, id=None, username=None, password=None):
        self.id = id
        self.username = username
        self.password = password

    def get_id(self):
        return str(self.id)


# 订单
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    seller_id = db.Column(db.Integer, nullable=False)  # 卖家id
    buyer_id = db.Column(db.Integer, nullable=False)  # 买家id
    book_id = db.Column(db.Integer, nullable=False)  # 书籍id
    state = db.Column(db.String(100), nullable=False)  # 订单状态
    # 订单状态：收藏; 已购买
    file = db.Column(db.Text, nullable=False)  # 文件的磁力链接


# 留言
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  # 用户id
    username = db.Column(db.String(100), nullable=False)  # 用户名
    text = db.Column(db.Text, nullable=False)


# 评论
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  # 用户id
    username = db.Column(db.String(100), nullable=False)  # 用户名
    book_id = db.Column(db.Integer, nullable=False)  # 书籍id
    bookname = db.Column(db.String(100), nullable=False)  # 书籍名
    text = db.Column(db.Text, nullable=False)


# 举报
class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)  # 用户id
    username = db.Column(db.String(100), nullable=False)  # 用户名
    book_id = db.Column(db.Integer, nullable=False)  # 书籍id
    bookname = db.Column(db.String(100), nullable=False)  # 书籍名
    text = db.Column(db.Text, nullable=False)