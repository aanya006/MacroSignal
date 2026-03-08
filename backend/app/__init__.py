from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app, origins=["http://localhost:5173", "http://localhost:5174"])

    from app.routes.status import status_bp
    from app.routes.ingestion import ingestion_bp
    from app.routes.themes import themes_bp
    from app.routes.memory import memory_bp
    app.register_blueprint(status_bp)
    app.register_blueprint(ingestion_bp)
    app.register_blueprint(themes_bp)
    app.register_blueprint(memory_bp)

    return app
