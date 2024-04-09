from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config 
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    from app.routes import FabricoPrefix
    app.register_blueprint(FabricoPrefix)
    return app
