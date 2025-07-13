from flask import Flask, jsonify, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.exceptions import Forbidden

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.static_folder = config_class.STATIC_FOLDER
    app.template_folder = config_class.TEMPLATE_FOLDER

    CORS(app)
    db.init_app(app)
    migrate.init_app(app,db)

    # Ensure blueprints are imported after DB is initialized to avoid circular import!
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    # WIP 403 catcher (simply using a different port should circumvent the need for this)
    # @app.errorhandler(Forbidden)
    # def catch_forbidden(e):
    #     app.logger.warning(f"Overriding 403 for path {request.path}")
    #     return jsonify({"status":"ok"}), 200


    return app
