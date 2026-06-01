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
    
    # Conectamos el módulo saas_admin
    from .saas_admin.routes import saas_admin_bp
    app.register_blueprint(saas_admin_bp)
    
    @app.route('/api/status', methods=['GET'])
    def status():
        return jsonify({"status": "online"})

    return app