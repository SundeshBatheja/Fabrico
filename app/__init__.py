from flask import Flask
from app.routes import FabricoPrefix
from config import Config 

def create_app():
    app = Flask(__name__)
    app.register_blueprint(FabricoPrefix)
    app.config.from_object(Config)
    return app
