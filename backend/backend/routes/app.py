from flask import Flask
from . import chat


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(chat.bp)

    return app
