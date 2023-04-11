from flask import Flask, flash, request, redirect, url_for
from flaskr import pages
from flask_login import LoginManager
from wtforms.validators import InputRequired, Length, ValidationError
from flaskr.user import User
from flaskr.backend import Backend
from werkzeug.utils import secure_filename
from flaskr.pages import Upload

import logging

logging.basicConfig(level=logging.DEBUG)


# The flask terminal command inside "run-flask.sh" searches for
# this method inside of __init__.py (containing flaskr module
# properties) as we set "FLASK_APP=flaskr" before running "flask".
def create_app(test_config=None, backend=Backend()):
    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)

    # By default the dev environment uses the key 'dev'
    # Generated random key with secrets.token_hex()
    app.config.from_mapping(
        SECRET_KEY=
        '5cfdb0b2f0177067d707306d43820b1bd479a558ad5ce7eac645cb77f8aacaa1')

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        # This file is not committed. Place it in production deployments.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        app.config.from_mapping(test_config)

    # backend = Backend()
    # TODO(Project 1): Make additional modifications here for logging in, backends
    # and additional endpoints.
    login_manager = LoginManager()
    login_manager.init_app(app)

    app.config['UPLOAD_FOLDER'] = Upload().UPLOAD_FOLDER

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    pages.make_endpoints(app, backend)

    return app
