from flask import jsonify
from datetime import datetime
from . import saas_admin_bp
from .models import Clinica, Usuario, Plan

@saas_admin_bp.route('/api/admin/estadisticas', methods=['GET'])
def obtener_estadisticas_saas():
    try:
        todas_clinicas = Clinica.query.all()
        planes = Plan.query.all()
        # Diccionario rápido para saber cuánto cuesta cada plan {id_plan: precio}
        planes_dict = {p.id: p.precio for p in planes} 

        total_clinicas = len(todas_clinicas)
        total_usuarios = Usuario.query.count() 

        activas = 0
        vencidas = 0
        suspendidas = 0
        ingresos_mensuales = 0
        fecha_actual = datetime.utcnow()

        # Array para contar registros de Enero a Diciembre
        crecimiento_mensual = {i: 0 for i in range(1, 13)}
        actividad_reciente = []

        for c in todas_clinicas:
            admin_local = Usuario.query.filter_by(clinica_id=c.id, rol='admin').first()
            
            # 1. ESTADOS
            if admin_local and not admin_local.activo:
                suspendidas += 1
            elif c.fecha_vencimiento and c.fecha_vencimiento < fecha_actual:
                vencidas += 1
                # Agregamos evento de vencimiento al log
                actividad_reciente.append({
                    "icono": "⚠️", "color": "text-warning",
                    "mensaje": f"La clínica '{c.nombre_negocio}' ha vencido.",
                    "fecha": c.fecha_vencimiento.strftime('%Y-%m-%d')
                })
            else:
                activas += 1
                # 2. CÁLCULO DE MRR (Ingresos)
                if c.plan_id and c.plan_id in planes_dict:
                    ingresos_mensuales += planes_dict[c.plan_id]
            
            # 3. GRÁFICO DE CRECIMIENTO
            if c.fecha_inicio_suscripcion:
                mes = c.fecha_inicio_suscripcion.month
                crecimiento_mensual[mes] += 1
                
                # Agregamos evento de creación al log
                actividad_reciente.append({
                    "icono": "✨", "color": "text-success",
                    "mensaje": f"Nueva clínica registrada: '{c.nombre_negocio}'.",
                    "fecha": c.fecha_inicio_suscripcion.strftime('%Y-%m-%d')
                })

        # Ordenar log desde lo más reciente
        actividad_reciente.sort(key=lambda x: x['fecha'], reverse=True)
        datos_crecimiento = [crecimiento_mensual[i] for i in range(1, 13)]

        ultimas = Clinica.query.order_by(Clinica.id.desc()).limit(5).all()
        ultimas_clinicas = [{"id": c.id, "nombre_negocio": c.nombre_negocio, "nit": c.nit if c.nit else "S/N"} for c in ultimas]
        
        return jsonify({
            "total_clinicas": total_clinicas,
            "clinicas_activas": activas,
            "clinicas_vencidas": vencidas,
            "clinicas_suspendidas": suspendidas,
            "total_usuarios": total_usuarios,
            "ingresos_mensuales": float(ingresos_mensuales), # MRR
            "crecimiento_mensual": datos_crecimiento,        # Línea de tiempo
            "actividad_reciente": actividad_reciente[:5],    # Log de auditoría
            "ultimas_clinicas": ultimas_clinicas
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500