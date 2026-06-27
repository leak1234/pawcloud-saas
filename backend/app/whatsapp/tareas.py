from datetime import datetime, timedelta
from app import db
from app.clinica.clinica_models import Consulta, Mascota, Dueno
from app.saas_admin.models import Clinica
from .bot_routes import enviar_texto_api

# 1. Agregamos 'app' entre los paréntesis
def ejecutar_cron_recordatorios(app):
    # 2. Abrimos el contexto de la aplicación para que la base de datos funcione
    with app.app_context():
        ahora_local = datetime.utcnow() - timedelta(hours=4)
        manana_inicio = datetime(ahora_local.year, ahora_local.month, ahora_local.day) + timedelta(days=1)
        manana_fin = manana_inicio + timedelta(hours=23, minutes=59, seconds=59)

        citas_manana = Consulta.query.filter(
            Consulta.estado == 'pendiente',
            Consulta.fecha_programada >= manana_inicio,
            Consulta.fecha_programada <= manana_fin,
            Consulta.recordatorio_enviado == False
        ).all()

        for cita in citas_manana:
            mascota = Mascota.query.get(cita.mascota_id)
            dueno = Dueno.query.get(mascota.dueno_id)
            clinica = Clinica.query.get(dueno.clinica_id)

            if clinica and clinica.whatsapp_conectado:
                hora = cita.fecha_programada.strftime("%H:%M")
                mensaje = f"📅 *RECORDATORIO DE ATENCIÓN*\n\nHola *{dueno.nombre_completo}*, te recordamos que el día de mañana tienes una cita agendada para *{mascota.nombre}* a las *{hora}*.\n🩺 *Motivo:* {cita.motivo}"
                
                enviar_texto_api(clinica.whatsapp_instancia, dueno.telefono, mensaje)
                cita.recordatorio_enviado = True

        db.session.commit()