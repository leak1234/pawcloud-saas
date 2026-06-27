from flask import request, jsonify, g
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime 
from . import saas_admin_bp
from .models import Usuario, Clinica

# Decorador de seguridad
def requerir_usuario_activo(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        if hasattr(g, 'usuario_actual') and g.usuario_actual and not g.usuario_actual.activo:
            return jsonify({"error": "Acceso denegado. Esta clínica se encuentra suspendida."}), 403
        return f(*args, **kwargs)
    return decorado

# LOGIN
@saas_admin_bp.route('/api/admin/login', methods=['POST'])
def login():
    datos = request.get_json()
    usuario = Usuario.query.filter_by(email=datos.get('email')).first()
    
    if usuario and check_password_hash(usuario.password_hash, datos.get('password')):
        
        # 1. VALIDACIÓN DE USUARIO ACTIVO
        if not usuario.activo:
            return jsonify({"error": "Esta cuenta está suspendida por el administrador."}), 403
        
        nombre_clinica = "PawCloud Vet"
        if usuario.clinica_id:
            clinica = Clinica.query.get(usuario.clinica_id)
            if clinica:
                # 2. VALIDACIÓN DE SUSCRIPCIÓN VENCIDA
                if clinica.fecha_vencimiento and datetime.utcnow() > clinica.fecha_vencimiento:
                    return jsonify({"error": "Tu suscripción ha vencido. Por favor, contacta a soporte para renovar."}), 402
                
                nombre_clinica = clinica.nombre_negocio
            
        return jsonify({
            "mensaje": "Login exitoso",
            "usuario": usuario.nombre_completo,
            "clinica_id": usuario.clinica_id,
            "rol": usuario.rol,
            "nombre_clinica": nombre_clinica 
        }), 200
        
    return jsonify({"error": "Correo o contraseña incorrectos"}), 401