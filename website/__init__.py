from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager



# extensions from database
db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dfghgfhfgjhfg'
    #update database
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    #initialize extensions
    db.init_app(app)

    #import blueprints for auth and views
    from .views import views
    from .auth import auth

    #register blueprints
    app.register_blueprint(views, url_prefix = '/')
    app.register_blueprint(auth, url_prefix = '/')


    from .models import User, Project, Workhours
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    create_database(app)

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all
        print('Created Database!')