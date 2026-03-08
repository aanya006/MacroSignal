from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173", "http://localhost:5174"])

    from app.routes.status import status_bp
    app.register_blueprint(status_bp)

    return app
