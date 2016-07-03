import flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from nih_trends import config
from nih_trends import cli
from nih_trends import api

class Config:
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = config.CORS_ORIGINS

def make_app(config=Config):
    app = flask.Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(api.blueprint)
    cli.add_commands(app)
    CORS(app)
    SQLAlchemy(app)
    return app
