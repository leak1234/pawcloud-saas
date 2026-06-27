from flask import request, jsonify, send_from_directory, current_app
from app import db
from .clinica_models import Dueno, Mascota, Consulta
from . import clinica_bp
from datetime import datetime, timedelta
import os

@clinica_bp.route('/api/clinica/<int:clinica_id>/mascotas/<int:mascota_id>/consultas', methods=['POST'])
def registrar_consulta(clinica_id, mascota_id):
    try:
        mascota = Mascota.query.join(Dueno).filter(Mascota.id == mascota_id, Dueno.clinica_id == clinica_id).first()
        if not mascota: return jsonify({"error": "Paciente no verificado"}), 404
        
        datos = request.get_json()
        ahora_bolivia = datetime.utcnow() - timedelta(hours=4)
        
        # BÚSQUEDA INTELIGENTE: ¿Esta mascota tiene una cita pendiente para hoy o de días anteriores?
        hoy_fecha = ahora_bolivia.date()
        consulta_existente = Consulta.query.filter(
            Consulta.mascota_id == mascota_id,
            Consulta.estado == 'pendiente',
            db.func.date(Consulta.fecha_programada) <= hoy_fecha
        ).order_by(Consulta.fecha_programada.asc()).first()

        estado_final = datos.get('estado', 'completada')
        
        # BLINDAJE DE DATOS: Convertimos estrictamente a float o None para que Numeric(4,2) no explote
        try:
            peso_limpio = float(datos.get('peso_actual')) if datos.get('peso_actual') not in [None, '', '0.0', 0] else None
        except:
            peso_limpio = None

        try:
            temp_limpia = float(datos.get('temperatura')) if datos.get('temperatura') not in [None, '', '0.0', 0] else None
        except:
            temp_limpia = None

        servicio_limpio = datos.get('servicio_id') if datos.get('servicio_id') not in [None, ''] else None

        if consulta_existente:
            consulta_existente.veterinario_id = datos['veterinario_id']
            if servicio_limpio:
                consulta_existente.servicio_id = servicio_limpio
            consulta_existente.peso_actual = peso_limpio
            consulta_existente.temperatura = temp_limpia
            consulta_existente.sintomas = datos.get('sintomas', '')
            consulta_existente.diagnostico = datos.get('diagnostico', '')
            consulta_existente.tratamiento_receta = datos.get('tratamiento_receta', '')
            consulta_existente.estado = estado_final
            consulta_existente.fecha_consulta = ahora_bolivia 
        else:
            f_prog = None
            if datos.get('fecha_programada'):
                f_prog = datetime.strptime(datos['fecha_programada'], "%Y-%m-%dT%H:%M")

            nueva_consulta = Consulta(
                mascota_id=mascota_id, veterinario_id=datos['veterinario_id'],
                servicio_id=servicio_limpio,
                fecha_consulta=ahora_bolivia,
                peso_actual=peso_limpio,
                temperatura=temp_limpia,
                motivo=datos['motivo'], sintomas=datos.get('sintomas', ''),
                diagnostico=datos.get('diagnostico', ''), tratamiento_receta=datos.get('tratamiento_receta', ''),
                fecha_programada=f_prog, estado=estado_final
            )
            db.session.add(nueva_consulta)
        
        if peso_limpio and estado_final == 'completada':
            mascota.peso = peso_limpio
            
        db.session.commit()
        return jsonify({"mensaje": "Consulta cerrada e historial actualizado"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@clinica_bp.route('/api/clinica/<int:clinica_id>/mascotas/<int:mascota_id>/consultas', methods=['GET'])
def obtener_historial_consultas(clinica_id, mascota_id):
    consultas = Consulta.query.filter_by(mascota_id=mascota_id).order_by(Consulta.fecha_consulta.desc()).all()
    return jsonify([c.to_dict() for c in consultas]), 200
