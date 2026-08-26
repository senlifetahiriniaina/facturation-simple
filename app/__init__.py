import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(os.path.join(app.instance_path, "uploads"), exist_ok=True)

    app.config["SECRET_KEY"] = "dev-local-only"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        app.instance_path, "app.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(app.instance_path, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

    db.init_app(app)

    from app.routes.clients import clients_bp
    from app.routes.invoices import invoices_bp
    from app.routes.products import products_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(clients_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(settings_bp)

    with app.app_context():
        from app import models

        db.create_all()
        models.get_settings()

    @app.context_processor
    def inject_settings():
        from app.models import get_settings

        return {"settings": get_settings()}

    @app.route("/")
    def index():
        from flask import redirect, url_for

        return redirect(url_for("invoices.list_invoices"))

    return app
