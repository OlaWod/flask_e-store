from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField, IntegerField
from wtforms.validators import DataRequired, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired


class RegisterForm(FlaskForm):
    username = StringField(label='用户名', validators=[DataRequired('用户名不能为空')])
    password = PasswordField(label='密码', validators=[DataRequired('密码不能为空')])
    password2 = PasswordField(label='确认密码', validators=[DataRequired('确认密码不能为空'),
                                                         EqualTo("password", '两次密码不一致')])
    moreinfo = TextAreaField(label='更多信息')
    submit = SubmitField(label='提交')


class LoginForm(FlaskForm):
    username = StringField(label='用户名', validators=[DataRequired('用户名不能为空')])
    password = PasswordField(label='密码', validators=[DataRequired('密码不能为空')])
    submit = SubmitField(label='登入')


class UploadBookForm(FlaskForm):
    bookname = StringField(label='书名', validators=[DataRequired('书名不能为空')])
    detail = TextAreaField(label='更多信息')
    price = FloatField(label='单价', validators=[DataRequired('单价不能为空')])
    image = FileField(label='照片', validators=[
        FileAllowed(['jpg', 'png'], '照片只能上传图片!')
    ])
    qrcode = FileField(label='付款码', validators=[
        FileRequired("付款码图片不能为空!"),
        FileAllowed(['jpg', 'png'], '付款码只能上传图片!')
    ])
    submit = SubmitField(label='发布')


class BuyBookForm(FlaskForm):
    book_id = IntegerField(validators=[DataRequired('book_id is null!')])
    seller_id = IntegerField(validators=[DataRequired('seller_id is null!')])
    dislike = SubmitField(label='取消收藏')
    like = SubmitField(label='收藏')
    buy = SubmitField(label='购买')