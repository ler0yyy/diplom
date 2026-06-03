import os
from datetime import timedelta

from flask import Flask, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from server.config import build_database_uri

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


def create_app() -> Flask:
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
    app = Flask(__name__, static_folder=None)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)
    app.config["SQLALCHEMY_DATABASE_URI"] = build_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }

    cors_origins = os.getenv("CORS_ORIGINS", "*")
    CORS(app, resources={r"/api/*": {"origins": cors_origins}}, supports_credentials=True)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from server.routes.auth import bp as auth_bp
    from server.routes.presentations import bp as presentations_bp
    from server.routes.poll import bp as poll_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(presentations_bp)
    app.register_blueprint(poll_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"ok": True})

    @app.get("/")
    def web_index():
        return send_from_directory(web_dir, "index.html")

    @app.get("/<path:path>")
    def web_files(path: str):
        if path.startswith("api/"):
            return jsonify({"error": "not_found"}), 404
        return send_from_directory(web_dir, path)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
