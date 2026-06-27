from flask import jsonify
from app import db
from .clinica_models import Dueno, Mascota, Consulta
from . import clinica_bp
from datetime import datetime, timedelta

@clinica_bp.route('/api/clinica/<int:clinica_id>/dashboard', methods=['GET'])
def obtener_datos_dashboard(clinica_id):
    try:
        # Sincronización a zona horaria local (Bolivia UTC-4)
        ahora_bolivia = datetime.utcnow() - timedelta(hours=4)
        hoy_fecha = ahora_bolivia.date()
        hora_actual = ahora_bolivia.time()
        primer_dia_mes = datetime(ahora_bolivia.year, ahora_bolivia.month, 1)

        total_duenos = Dueno.query.filter_by(clinica_id=clinica_id, activo=True).count()
        total_mascotas = Mascota.query.join(Dueno).filter(Dueno.clinica_id == clinica_id, Mascota.activo == True).count()
        
        consultas_mes = Consulta.query.join(Mascota).join(Dueno).filter(
            Dueno.clinica_id == clinica_id,
            Consulta.estado == 'completada',
            Consulta.fecha_consulta >= primer_dia_mes
        ).count()

        citas_hoy_query = Consulta.query.join(Mascota).join(Dueno).filter(
            Dueno.clinica_id == clinica_id,
            Consulta.estado == 'pendiente',
            db.func.date(Consulta.fecha_programada) == hoy_fecha
        ).order_by(Consulta.fecha_programada.asc()).all()

        ultimos_pacientes = Mascota.query.join(Dueno).filter(
            Dueno.clinica_id == clinica_id, Mascota.activo == True
        ).order_by(Mascota.id.desc()).limit(5).all()

        # Lógica para detectar citas retrasadas
        citas_formateadas = []
        for c in citas_hoy_query:
            esta_retrasada = False
            if c.fecha_programada:
                # Compara si la hora programada ya pasó respecto a la hora actual
                esta_retrasada = c.fecha_programada.time() < hora_actual

            citas_formateadas.append({
                "id": c.id,
                "hora": c.fecha_programada.strftime("%H:%M") if c.fecha_programada else "--:--",
                "mascota_nombre": c.paciente.nombre,
                "especie": c.paciente.especie,
                "dueno_nombre": c.paciente.propietario.nombre_completo,
                "telefono": c.paciente.propietario.telefono,
                "motivo": c.motivo,
                "servicio": c.servicio.nombre if c.servicio else "Consulta General",
                "retrasada": esta_retrasada # 👈 Propiedad clave para Vue
            })

        return jsonify({
            "kpis": {
                "total_duenos": total_duenos,
                "total_mascotas": total_mascotas,
                "consultas_mes": consultas_mes,
                "citas_hoy_count": len(citas_hoy_query)
            },
            "citas_hoy": citas_formateadas,
            "ultimos_pacientes": [{
                "id": m.id,
                "nombre": m.nombre,
                "especie": m.especie,
                "raza": m.raza or "N/A",
                "dueno": m.propietario.nombre_completo,
                "fecha": m.fecha_registro.strftime("%d/%m/%Y")
            } for m in ultimos_pacientes]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500