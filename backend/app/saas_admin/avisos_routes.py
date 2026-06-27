from flask import request, jsonify
from datetime import datetime
from app import db
from . import saas_admin_bp
from .models import Aviso, RegistroAuditoria

# 1. OBTENER TODOS LOS AVISOS
@saas_admin_bp.route('/api/admin/avisos', methods=['GET'])
def obtener_avisos():
    avisos = Aviso.query.order_by(Aviso.fecha_creacion.desc()).all()
    resultado = [{
        "id": a.id,
        "titulo": a.titulo,
        "mensaje": a.mensaje,
        "tipo": a.tipo,
        "fecha_creacion": a.fecha_creacion.strftime('%Y-%m-%d %H:%M'),
        "activo": a.activo
    } for a in avisos]
    return jsonify(resultado), 200

# 2. CREAR UN NUEVO AVISO
@saas_admin_bp.route('/api/admin/avisos', methods=['POST'])
def crear_aviso():
    datos = request.get_json()
    try:
        nuevo_aviso = Aviso(
            titulo=datos['titulo'],
            mensaje=datos['mensaje'],
            tipo=datos.get('tipo', 'info')
        )
        db.session.add(nuevo_aviso)
        
        # --- REGISTRO DE AUDITORÍA ---
        auditoria = RegistroAuditoria(
            operador="Súper Admin",
            accion="Nuevo Aviso Global",
            detalles=f"Se publicó el aviso: '{nuevo_aviso.titulo}'."
        )
        db.session.add(auditoria)
        
        db.session.commit()
        return jsonify({"mensaje": "Aviso publicado correctamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# 3. CAMBIAR ESTADO (ACTIVAR/DESACTIVAR) AVISO
@saas_admin_bp.route('/api/admin/avisos/<int:id>/estado', methods=['PUT'])
def cambiar_estado_aviso(id):
    try:
        aviso = Aviso.query.get(id)
        if not aviso: return jsonify({"error": "Aviso no encontrado"}), 404
        
        aviso.activo = not aviso.activo
        
        if aviso.activo:
            aviso.fecha_creacion = datetime.utcnow()

        db.session.commit()
        return jsonify({"mensaje": "Estado actualizado", "activo": aviso.activo}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# 4. EDITAR AVISO
@saas_admin_bp.route('/api/admin/avisos/<int:id>', methods=['PUT'])
def editar_aviso(id):
    datos = request.get_json()
    try:
        aviso = Aviso.query.get(id)
        if not aviso: return jsonify({"error": "Aviso no encontrado"}), 404
        
        titulo_anterior = aviso.titulo
        aviso.titulo = datos.get('titulo', aviso.titulo)
        aviso.mensaje = datos.get('mensaje', aviso.mensaje)
        aviso.tipo = datos.get('tipo', aviso.tipo)
        
        # --- AUDITORÍA ---
        auditoria = RegistroAuditoria(
            operador="Súper Admin",
            accion="Edición de Aviso",
            detalles=f"Se modificó el aviso: '{titulo_anterior}'."
        )
        db.session.add(auditoria)
        
        db.session.commit()
        return jsonify({"mensaje": "Aviso actualizado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# 5. ELIMINAR AVISO DEFINITIVAMENTE
@saas_admin_bp.route('/api/admin/avisos/<int:id>', methods=['DELETE'])
def eliminar_aviso(id):
    try:
        aviso = Aviso.query.get(id)
        if not aviso: return jsonify({"error": "Aviso no encontrado"}), 404
        
        titulo_eliminado = aviso.titulo
        db.session.delete(aviso)
        
        # --- AUDITORÍA ---
        auditoria = RegistroAuditoria(
            operador="Súper Admin",
            accion="Eliminación de Aviso",
            detalles=f"Se eliminó definitivamente el aviso: '{titulo_eliminado}'."
        )
        db.session.add(auditoria)
        
        db.session.commit()
        return jsonify({"mensaje": "Aviso eliminado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# 6. ENPOINT PÚBLICO/PARA CLÍNICAS: OBTENER SOLO AVISOS ACTIVOS
@saas_admin_bp.route('/api/clinicas/avisos-activos', methods=['GET'])
def obtener_avisos_activos():
    # Filtramos estrictamente por activo=True
    avisos = Aviso.query.filter_by(activo=True).order_by(Aviso.fecha_creacion.desc()).all()
    resultado = [{
        "id": a.id,
        "titulo": a.titulo,
        "mensaje": a.mensaje,
        "tipo": a.tipo,
        "fecha_creacion": a.fecha_creacion.strftime('%Y-%m-%d %H:%M')
    } for a in avisos]
    return jsonify(resultado), 200