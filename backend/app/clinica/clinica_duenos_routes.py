from flask import request, jsonify
from app import db
from .clinica_models import Dueno
from . import clinica_bp

@clinica_bp.route('/api/clinica/<int:clinica_id>/duenos', methods=['GET'])
def obtener_duenos(clinica_id):
    estado = request.args.get('estado', 'activos')
    if estado == 'inactivos':
        duenos = Dueno.query.filter_by(clinica_id=clinica_id, activo=False).order_by(Dueno.id.desc()).all()
    else:
        duenos = Dueno.query.filter_by(clinica_id=clinica_id, activo=True).order_by(Dueno.id.desc()).all()
    return jsonify([d.to_dict() for d in duenos]), 200

@clinica_bp.route('/api/clinica/<int:clinica_id>/duenos', methods=['POST'])
def crear_dueno(clinica_id):
    datos = request.get_json()
    try:
        if datos.get('email') and Dueno.query.filter_by(clinica_id=clinica_id, email=datos['email']).first():
            return jsonify({"error": "Este correo ya está registrado"}), 409

        nuevo_dueno = Dueno(
            clinica_id=clinica_id, nombre_completo=datos['nombre_completo'],
            telefono=datos['telefono'], email=datos.get('email', ''),
            direccion=datos.get('direccion', ''), activo=True
        )
        db.session.add(nuevo_dueno)
        db.session.commit()
        return jsonify({"mensaje": "Cliente registrado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@clinica_bp.route('/api/clinica/<int:clinica_id>/duenos/<int:dueno_id>', methods=['PUT'])
def editar_dueno(clinica_id, dueno_id):
    dueno = Dueno.query.filter_by(id=dueno_id, clinica_id=clinica_id).first()
    if not dueno: return jsonify({"error": "Cliente no encontrado"}), 404
    datos = request.get_json()
    dueno.nombre_completo = datos.get('nombre_completo', dueno.nombre_completo)
    dueno.telefono = datos.get('telefono', dueno.telefono)
    dueno.email = datos.get('email', dueno.email)
    dueno.direccion = datos.get('direccion', dueno.direccion)
    db.session.commit()
    return jsonify({"mensaje": "Datos actualizados"}), 200

@clinica_bp.route('/api/clinica/<int:clinica_id>/duenos/<int:dueno_id>', methods=['DELETE'])
def eliminar_dueno(clinica_id, dueno_id):
    dueno = Dueno.query.filter_by(id=dueno_id, clinica_id=clinica_id).first()
    if not dueno: return jsonify({"error": "Cliente no encontrado"}), 404
    dueno.activo = False
    db.session.commit()
    return jsonify({"mensaje": "Cliente suspendido"}), 200

@clinica_bp.route('/api/clinica/<int:clinica_id>/duenos/<int:dueno_id>/restaurar', methods=['PATCH'])
def restaurar_dueno(clinica_id, dueno_id):
    dueno = Dueno.query.filter_by(id=dueno_id, clinica_id=clinica_id).first()
    if not dueno: return jsonify({"error": "Cliente no encontrado"}), 404
    dueno.activo = True
    db.session.commit()
    return jsonify({"mensaje": "Cliente restaurado"}), 200