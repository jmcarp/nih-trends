import flask
from flask_sqlalchemy import SQLAlchemy

from nih_trends import config

class Config:
    SQLALCHEMY_DATABASE_URI = config.DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def make_app(config=Config):
    app = flask.Flask(__name__)
    app.config.from_object(config)
    SQLAlchemy(app)
    return app
