from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import db
from .models import Clinica, Usuario

saas_admin_bp = Blueprint('saas_admin', __name__)

# EL GUARDIÁN DE SEGURIDAD
def requerir_usuario_activo(f):
    @wraps(f)
    def decorado(*args, **kwargs):
        if hasattr(g, 'usuario_actual') and g.usuario_actual and not g.usuario_actual.activo:
            return jsonify({"error": "Acceso denegado. Esta clínica se encuentra suspendida."}), 403
        return f(*args, **kwargs)
    return decorado

# 1. OBTENER TODAS LAS CLÍNICAS 
@saas_admin_bp.route('/api/admin/clinicas', methods=['GET'])
def obtener_clinicas():
    clinicas = Clinica.query.order_by(Clinica.id.asc()).all()
    resultado = []
    for c in clinicas:
        admin_local = Usuario.query.filter_by(clinica_id=c.id, rol='admin').first()
        resultado.append({
            "id": c.id,
            "nombre_negocio": c.nombre_negocio,
            "nit": c.nit if c.nit else "S/N",
            "direccion": c.direccion if hasattr(c, 'direccion') and c.direccion else "Sin dirección",
            "email": admin_local.email if admin_local else "Sin asignar",
            "nombre_usuario": admin_local.nombre_completo if admin_local else "Administrador",
            "activo": admin_local.activo if admin_local else False
        })
    return jsonify(resultado), 200



# 2. CAMBIAR ESTADO (Borrado Lógico)
@saas_admin_bp.route('/api/admin/clinicas/<int:id>/cambiar-estado', methods=['POST'])
def cambiar_estado_clinica(id):
    usuarios = Usuario.query.filter_by(clinica_id=id).all()
    if not usuarios:
        return jsonify({"error": "No se encontraron usuarios para esta clínica"}), 404
    
    nuevo_estado = not usuarios[0].activo
    for u in usuarios:
        u.activo = nuevo_estado
        
    db.session.commit()
    return jsonify({"mensaje": "Estado actualizado", "nuevo_estado": nuevo_estado}), 200



# 3. REGISTRAR CLÍNICA
@saas_admin_bp.route('/api/admin/registrar', methods=['POST'])
def registrar_clinica():
    datos = request.get_json()
    
    # 1. Validar correo duplicado
    if Usuario.query.filter_by(email=datos['email']).first():
        return jsonify({"error": "El correo ya está registrado"}), 409
        
    # 2. Validar NIT duplicado
    nit_enviado = datos.get('nit', '').strip()
    if nit_enviado:
        if Clinica.query.filter_by(nit=nit_enviado).first():
            return jsonify({"error": f"El NIT {nit_enviado} ya está registrado en otra clínica"}), 409

    try:
        if datos.get('rol') == 'superadmin':
            nuevo_usuario = Usuario(
                nombre_completo=datos['nombre_usuario'],
                email=datos['email'],
                password_hash=generate_password_hash(datos['password']),
                rol='superadmin'
            )
            db.session.add(nuevo_usuario)
        else:
            nueva_clinica = Clinica(
                nombre_negocio=datos['nombre_negocio'], 
                nit=nit_enviado,
                direccion=datos.get('direccion', '')
            )
            db.session.add(nueva_clinica)
            db.session.flush() 
            
            nuevo_usuario = Usuario(
                clinica_id=nueva_clinica.id,
                nombre_completo=datos['nombre_usuario'],
                email=datos['email'],
                password_hash=generate_password_hash(datos['password']),
                rol='admin'
            )
            db.session.add(nuevo_usuario)
            
        db.session.commit()
        return jsonify({"mensaje": "Registro exitoso"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Falla en servidor: {str(e)}"}), 500


# 4. LOGIN 
@saas_admin_bp.route('/api/admin/login', methods=['POST'])
def login():
    datos = request.get_json()
    usuario = Usuario.query.filter_by(email=datos.get('email')).first()
    
    if usuario and check_password_hash(usuario.password_hash, datos.get('password')):
        if not usuario.activo:
            return jsonify({"error": "Esta cuenta está suspendida."}), 403
        
        # Obtenemos el nombre de la clínica si existe
        nombre_clinica = "PawCloud Vet"
        if usuario.clinica_id:
            clinica = Clinica.query.get(usuario.clinica_id)
            if clinica:
                nombre_clinica = clinica.nombre_negocio
            
        return jsonify({
            "mensaje": "Login exitoso",
            "usuario": usuario.nombre_completo,
            "clinica_id": usuario.clinica_id,
            "rol": usuario.rol,
            "nombre_clinica": nombre_clinica 
        }), 200
        
    return jsonify({"error": "Correo o contraseña incorrectos"}), 401


# 5. ACTUALIZAR CLÍNICA 
@saas_admin_bp.route('/api/admin/clinicas/<int:id>', methods=['PUT'])
def actualizar_clinica(id):
    try:
        datos = request.get_json()
        if not datos: return jsonify({"error": "No hay datos"}), 400
        
        clinica = Clinica.query.get(id)
        if not clinica: return jsonify({"error": "No existe la clínica"}), 404
            
        admin_local = Usuario.query.filter_by(clinica_id=id).first()
        
        # 1. Validar que el nuevo NIT no choque con el de otra clínica
        nuevo_nit = datos.get('nit', '').strip()
        if nuevo_nit and nuevo_nit != clinica.nit:
            if Clinica.query.filter_by(nit=nuevo_nit).first():
                return jsonify({"error": f"El NIT {nuevo_nit} ya pertenece a otra clínica"}), 409
        
        # 2. Actualizar datos de la clínica
        clinica.nombre_negocio = datos.get('nombre_negocio', clinica.nombre_negocio)
        clinica.nit = nuevo_nit
        clinica.direccion = datos.get('direccion', clinica.direccion)
            
        # 3. Actualizar datos del usuario administrador
        if admin_local:
            # Validar que el nuevo correo no esté en uso
            nuevo_email = datos.get('email', '').strip()
            if nuevo_email and nuevo_email != admin_local.email:
                if Usuario.query.filter_by(email=nuevo_email).first():
                    return jsonify({"error": "El correo ya está registrado por otro usuario"}), 409
                admin_local.email = nuevo_email
            
            if datos.get('nombre_usuario'):
                admin_local.nombre_completo = datos.get('nombre_usuario')
                
            if datos.get('password') and datos.get('password').strip():
                admin_local.password_hash = generate_password_hash(datos['password'])

        db.session.commit()
        return jsonify({"mensaje": "Actualizado correctamente"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500