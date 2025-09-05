from flask import Flask
from flask_migrate import Migrate
from models import db
from config import Config

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init db + migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # import and register routes
    with app.app_context():
        import routes  # keep all your routes in routes.py
    return app
