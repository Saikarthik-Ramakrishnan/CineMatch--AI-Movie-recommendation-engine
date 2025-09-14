from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Enable CORS for frontend communication
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])
    
    # Register routes
    from app.routes import main
    app.register_blueprint(main)
    
    return app