from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_session import Session
from flask_migrate import Migrate  # Import Flask-Migrate
from config import Config

db = SQLAlchemy()
mail = Mail()
sess = Session()
migrate = Migrate()  # Initialize Flask-Migrate


def create_app():
    from app.auth import auth

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)
    sess.init_app(app)

    migrate.init_app(app, db)  # Initialize Flask-Migrate with the app and db

    app.register_blueprint(auth, url_prefix="/auth")

    return app
