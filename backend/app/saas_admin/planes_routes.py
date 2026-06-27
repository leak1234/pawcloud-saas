from flask import request, jsonify
from app import db
from . import saas_admin_bp
from .models import Plan

@saas_admin_bp.route('/api/admin/planes', methods=['GET'])
def obtener_planes():
    try:
        planes = Plan.query.order_by(Plan.id.asc()).all()
        return jsonify([plan.to_dict() for plan in planes]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@saas_admin_bp.route('/api/admin/planes', methods=['POST'])
def crear_plan():
    data = request.get_json()
    if not all(campo in data for campo in ['nombre', 'precio', 'limite_usuarios', 'limite_pacientes']):
        return jsonify({"error": "Faltan datos obligatorios"}), 400
        
    try:
        nuevo_plan = Plan(
            nombre=data['nombre'], precio=data['precio'],
            limite_usuarios=data['limite_usuarios'], limite_pacientes=data['limite_pacientes'],
            activo=data.get('activo', True)
        )
        db.session.add(nuevo_plan)
        db.session.commit()
        return jsonify({"mensaje": "Plan creado", "plan": nuevo_plan.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@saas_admin_bp.route('/api/admin/planes/<int:id>', methods=['PUT'])
def actualizar_plan(id):
    try:
        plan = Plan.query.get(id)
        if not plan: return jsonify({"error": "Plan no encontrado"}), 404
        
        data = request.get_json()
        plan.nombre = data.get('nombre', plan.nombre)
        plan.precio = data.get('precio', plan.precio)
        plan.limite_usuarios = data.get('limite_usuarios', plan.limite_usuarios)
        plan.limite_pacientes = data.get('limite_pacientes', plan.limite_pacientes)
        
        db.session.commit()
        return jsonify({"mensaje": "Plan actualizado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@saas_admin_bp.route('/api/admin/planes/<int:id>/cambiar-estado', methods=['POST'])
def cambiar_estado_plan(id):
    try:
        plan = Plan.query.get(id)
        if not plan: return jsonify({"error": "Plan no encontrado"}), 404
        
        plan.activo = not plan.activo 
        db.session.commit()
        return jsonify({"mensaje": "Estado actualizado", "nuevo_estado": plan.activo}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500