from flask import Flask
from flask_cors import CORS
from . import auth, chat, inventory, payments


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    app.register_blueprint(auth.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(payments.bp)

    return app
