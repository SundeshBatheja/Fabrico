from flask import Flask
from app.routes import init_routes
from config import Config 

def create_app():
    app = Flask(__name__)
    init_routes(app)
    app.config.from_object(Config)
    return app
