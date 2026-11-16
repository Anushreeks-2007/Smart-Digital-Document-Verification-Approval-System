from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    from app.routes.main_routes import main
    from app.routes.auth_routes import auth
    from app.routes.item_routes import items

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(items)

    return app