import datetime
import os
from flask import Flask, render_template, url_for, request, send_from_directory
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from flask_sitemap import Sitemap
from werkzeug.utils import redirect
from werkzeug.utils import secure_filename
import config
from data import db_session
from data.admin import Admin

ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg']
application = Flask(__name__)
ext = Sitemap(app=application)
application.config.from_object(config)

db_session.global_init("db/.sqlite")
login_manager = LoginManager()
login_manager.init_app(application)
set_standard_params = True
standard_params = {}


# Всё, что связано с юзером

# Получение пользователя
@login_manager.user_loader
def load_user(admin_id):
    session = db_session.create_session()
    return session.query(Admin).get(admin_id)


# Специальные функции
def get_render_template(template, **kwargs):
    return render_template(template, standard_params=standard_params, **kwargs)


# Сайт и его страницы
def main(port=8000):
    application.run(port=port)


# Выход с аккаунта
@application.route('/logout/')
@login_required
def logout_page():
    logout_user()
    return redirect("/")


# Страница с базовым шаблоном
@application.route("/base")
def base_page():
    return get_render_template('base.html', title='Главная страница')


# Стартовая страница
@application.route("/")
def main_page():
    return get_render_template('main.html', title='Главная страница')


if __name__ == '__main__':
    main(port=80)