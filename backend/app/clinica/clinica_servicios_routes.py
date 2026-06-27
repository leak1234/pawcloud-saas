from flask import request, jsonify
from app import db
from .clinica_models import Servicio
from . import clinica_bp

@clinica_bp.route('/api/clinica/<int:clinica_id>/servicios', methods=['GET'])
def obtener_servicios(clinica_id):
    estado = request.args.get('estado', 'activos')
    if estado == 'inactivos':
        servicios = Servicio.query.filter_by(clinica_id=clinica_id, activo=False).order_by(Servicio.nombre.asc()).all()
    else:
        servicios = Servicio.query.filter_by(clinica_id=clinica_id, activo=True).order_by(Servicio.nombre.asc()).all()
    return jsonify([s.to_dict() for s in servicios]), 200

@clinica_bp.route('/api/clinica/<int:clinica_id>/servicios', methods=['POST'])
def crear_servicio(clinica_id):
    try:
        datos = request.get_json()
        nuevo_servicio = Servicio(
            clinica_id=clinica_id, nombre=datos['nombre'], 
            precio_base=datos.get('precio_base', 0.0), activo=True
        )
        db.session.add(nuevo_servicio)
        db.session.commit()
        return jsonify({"mensaje": "Servicio creado", "id": nuevo_servicio.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@clinica_bp.route('/api/clinica/<int:clinica_id>/servicios/<int:servicio_id>', methods=['PUT'])
def editar_servicio(clinica_id, servicio_id):
    servicio = Servicio.query.filter_by(id=servicio_id, clinica_id=clinica_id).first()
    if not servicio: return jsonify({"error": "Servicio no encontrado"}), 404
    datos = request.get_json()
    servicio.nombre = datos.get('nombre', servicio.nombre)
    if 'precio_base' in datos:
        servicio.precio_base = datos['precio_base']
    db.session.commit()
    return jsonify({"mensaje": "Servicio actualizado"}), 200

@clinica_bp.route('/api/clinica/<int:clinica_id>/servicios/<int:servicio_id>', methods=['DELETE'])
def eliminar_servicio(clinica_id, servicio_id):
    servicio = Servicio.query.filter_by(id=servicio_id, clinica_id=clinica_id).first()
    if not servicio: return jsonify({"error": "Servicio no encontrado"}), 404
    servicio.activo = False
    db.session.commit()
    return jsonify({"mensaje": "Servicio enviado a la papelera"}), 200

@clinica_bp.route('/api/clinica/<int:clinica_id>/servicios/<int:servicio_id>/restaurar', methods=['PATCH'])
def restaurar_servicio(clinica_id, servicio_id):
    servicio = Servicio.query.filter_by(id=servicio_id, clinica_id=clinica_id).first()
    if not servicio: return jsonify({"error": "Servicio no encontrado"}), 404
    servicio.activo = True
    db.session.commit()
    return jsonify({"mensaje": "Servicio restaurado"}), 200