from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Ruta de prueba para verificar que el backend levantó
    @app.route('/api/status', methods=['GET'])
    def status():
        return jsonify({
            "status": "online",
            "message": "¡El motor de PawCloud está funcionando al 100%!"
        })

    return app