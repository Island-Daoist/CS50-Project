"""
Implement docstring here.
"""
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail


# Due to application factory Flask extensions must be initialised prior to app creation.
# Extensions are then attached in the create_app function
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to view this page.'
login.refresh_view = 'auth.validate'
login.needs_refresh_message = 'To protect your account, please re-enter your credentials.'
mail = Mail()


def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Flask extensions used in application are connected to the application here
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)

    # All various blueprints from the application sub-packages are connected to the main application here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blogs import bp as blog_bp
    app.register_blueprint(blog_bp, url_prefix='/blogs')

    from app.errors import bp as error_bp
    app.register_blueprint(error_bp)

    # Setup of the logging functionality of the application
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr=f'no-reply@{app.config["MAIL_SERVER"]}',
                toaddrs=app.config['ADMINS'],
                subject='Blog Application Failure',
                credentials=auth,
                secure=secure
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/blog.log',
                                               maxBytes=10240, backupCount=10)
            file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s '
                                               '[in %(pathname)s:%(lineno)d]')
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Blog Application Startup!')

    # Test route implemented to test that application has been set up properly
    @app.route('/hello')
    def hello():
        return "Hello, World!"

    return app
