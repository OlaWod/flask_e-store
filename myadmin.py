from flask import redirect, url_for, request, flash, session
from flask_admin import expose, AdminIndexView, helpers
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, logout_user
from forms import LoginForm
from models import Administrator


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and ('admin' in session)


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or ('admin' not in session):
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        logout_user()
        session.pop('login', None)
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            print(form.username.data)
            print(form.password.data)
            admin = Administrator.query.filter(Administrator.username == form.username.data,
                                               Administrator.password == form.password.data).first()
            if admin:
                login_user(admin)
                session['admin'] = True
                flash('登入成功!')
            else:
                flash('用户名或密码错误')

        if current_user.is_authenticated:
            return redirect(url_for('.index'))

        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        session.pop('admin', None)
        return redirect(url_for('.index'))
