from flask import request, jsonify
from werkzeug.security import generate_password_hash
from app import db
from app.saas_admin.models import Usuario 
from . import clinica_bp

# 1. OBTENER LISTA DE EMPLEADOS (ACTIVOS O INACTIVOS)
@clinica_bp.route('/api/clinica/<int:clinica_id>/empleados', methods=['GET'])
def obtener_empleados(clinica_id):
    estado = request.args.get('estado', 'activos')
    
    # Si el estado es "inactivos", traemos los empleados con activo=False, sino traemos los activos
    if estado == 'inactivos':
        empleados = Usuario.query.filter_by(clinica_id=clinica_id, activo=False).order_by(Usuario.id.desc()).all()
    else:
        empleados = Usuario.query.filter_by(clinica_id=clinica_id, activo=True).order_by(Usuario.id.desc()).all()
        
    return jsonify([{
        "id": e.id, 
        "nombre_completo": e.nombre_completo,
        "email": e.email, 
        "rol": e.rol, 
        "activo": e.activo
    } for e in empleados]), 200


# 2. CREAR EMPLEADO
@clinica_bp.route('/api/clinica/<int:clinica_id>/empleados', methods=['POST'])
def crear_empleado(clinica_id):
    datos = request.get_json()
    if Usuario.query.filter_by(email=datos['email']).first():
        return jsonify({"error": "Este correo ya está registrado en el sistema"}), 409
        
    rol_solicitado = datos.get('rol')
    roles_permitidos = ['veterinario', 'recepcionista', 'cajero', 'peluquero']
    
    if rol_solicitado not in roles_permitidos:
        return jsonify({"error": "Acción inválida. Rol no permitido en el sistema."}), 400
        
    nuevo_empleado = Usuario(
        clinica_id=clinica_id,
        nombre_completo=datos['nombre_completo'],
        email=datos['email'],
        password_hash=generate_password_hash(datos['password']),
        rol=rol_solicitado,
        activo=True
    )
    db.session.add(nuevo_empleado)
    db.session.commit()
    return jsonify({"mensaje": "Empleado registrado exitosamente"}), 201

# 3. EDITAR EMPLEADO
@clinica_bp.route('/api/clinica/<int:clinica_id>/empleados/<int:empleado_id>', methods=['PUT'])
def editar_empleado(clinica_id, empleado_id):
    empleado = Usuario.query.filter_by(id=empleado_id, clinica_id=clinica_id).first()
    if not empleado: return jsonify({"error": "Empleado no encontrado"}), 404
    
    datos = request.get_json()
    
    if 'rol' in datos:
        if datos['rol'] not in ['veterinario', 'recepcionista', 'cajero', 'peluquero']:
            return jsonify({"error": "Acción inválida."}), 400
        empleado.rol = datos['rol']
        
    empleado.nombre_completo = datos.get('nombre_completo', empleado.nombre_completo)
    empleado.email = datos.get('email', empleado.email)
    
    if datos.get('password') and datos['password'].strip() != '':
        empleado.password_hash = generate_password_hash(datos['password'])
        
    db.session.commit()
    return jsonify({"mensaje": "Datos actualizados"}), 200

# 4. ELIMINAR EMPLEADO (BORRADO LÓGICO)
@clinica_bp.route('/api/clinica/<int:clinica_id>/empleados/<int:empleado_id>', methods=['DELETE'])
def eliminar_empleado(clinica_id, empleado_id):
    empleado = Usuario.query.filter_by(id=empleado_id, clinica_id=clinica_id).first()
    if not empleado: return jsonify({"error": "Empleado no encontrado"}), 404
    
    empleado.activo = False
    db.session.commit()
    return jsonify({"mensaje": "Empleado suspendido del sistema"}), 200

# 5. RESTAURAR EMPLEADO (VUELVE A ACTIVAR UN EMPLEADO INACTIVO)
@clinica_bp.route('/api/clinica/<int:clinica_id>/empleados/<int:empleado_id>/restaurar', methods=['PATCH'])
def restaurar_empleado(clinica_id, empleado_id):
    empleado = Usuario.query.filter_by(id=empleado_id, clinica_id=clinica_id).first()
    if not empleado: return jsonify({"error": "Empleado no encontrado"}), 404
    
    # Lo volvemos a encender
    empleado.activo = True
    db.session.commit()
    return jsonify({"mensaje": "Empleado restaurado con éxito"}), 200