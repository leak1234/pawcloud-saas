from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
scheduler = BackgroundScheduler()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Conectamos Módulos SaaS y Clínica
    from .saas_admin import saas_admin_bp
    app.register_blueprint(saas_admin_bp)
    
    from .clinica import clinica_bp
    app.register_blueprint(clinica_bp)
    
    # Conectamos Módulo de Automatización WhatsApp
    from .whatsapp import whatsapp_bp
    app.register_blueprint(whatsapp_bp)
    
    # 🔥 NUEVO: Conectamos el Webhook para el Bot Interactivo
    from .whatsapp.webhook_routes import whatsapp_webhook_bp
    app.register_blueprint(whatsapp_webhook_bp)
    
    # Inicialización del Scheduler en segundo plano
    from .whatsapp.tareas import ejecutar_cron_recordatorios
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        ctx = app.app_context()
        # Se ejecuta cada hora buscando citas que cumplan el tiempo exacto de aviso
        scheduler.add_job(func=ejecutar_cron_recordatorios, args=[ctx], trigger="interval", hours=1)
        scheduler.start()
    
    @app.route('/api/status', methods=['GET'])
    def status():
        return jsonify({"status": "online"})

    return app