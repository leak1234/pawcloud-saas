from flask import request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from app import db
from . import saas_admin_bp
from .models import Clinica, Usuario, Plan, RegistroAuditoria


# 1. OBTENER TODAS LAS CLÍNICAS (CON LÓGICA DE 3 ESTADOS)
@saas_admin_bp.route('/api/admin/clinicas', methods=['GET'])
def obtener_clinicas():
    clinicas = Clinica.query.order_by(Clinica.id.asc()).all()
    resultado = []
    fecha_actual = datetime.utcnow()

    for c in clinicas:
        admin_local = Usuario.query.filter_by(clinica_id=c.id, rol='admin').first()
        
        plan_db = Plan.query.get(c.plan_id) if c.plan_id else None
        nombre_texto = plan_db.nombre if plan_db else "Sin Plan"
        fecha_vence = c.fecha_vencimiento.strftime('%Y-%m-%d') if c.fecha_vencimiento else "Sin registro"

        # Cálculo dinámico del estado real de la clínica
        estado_real = "activa"
        if admin_local and not admin_local.activo:
            estado_real = "suspendida"
        elif c.fecha_vencimiento and c.fecha_vencimiento < fecha_actual:
            estado_real = "vencida"

        resultado.append({
            "id": c.id,
            "nombre_negocio": c.nombre_negocio,
            "nit": c.nit if c.nit else "S/N",
            "direccion": c.direccion if hasattr(c, 'direccion') and c.direccion else "Sin dirección",
            "email": admin_local.email if admin_local else "Sin asignar",
            "nombre_usuario": admin_local.nombre_completo if admin_local else "Administrador",
            "activo": admin_local.activo if admin_local else False,
            "estado_real": estado_real,
            "plan_id": c.plan_id,
            "nombre_plan": nombre_texto,
            "fecha_vencimiento": fecha_vence
        })
    return jsonify(resultado), 200


# 2. REGISTRAR NUEVA CLÍNICA
@saas_admin_bp.route('/api/admin/registrar', methods=['POST'])
def registrar_clinica():
    datos = request.get_json()
    # NUEVA SEGURIDAD: Solo permitir si es registro de clínica O si no hay superadmins aún
    if datos.get('rol') == 'superadmin':
        # (Opcional) Verificar un token secreto o si ya existe admin
        admin_existente = Usuario.query.filter_by(rol='superadmin').first()
        if admin_existente:
             return jsonify({"error": "Ya existe un superadmin"}), 403
        
    if Usuario.query.filter_by(email=datos['email']).first():
        return jsonify({"error": "El correo ya está registrado"}), 409
        
    nit_enviado = datos.get('nit', '').strip()
    if nit_enviado and Clinica.query.filter_by(nit=nit_enviado).first():
        return jsonify({"error": f"El NIT {nit_enviado} ya está registrado"}), 409

    try:
        if datos.get('rol') == 'superadmin':
            nuevo_usuario = Usuario(
                nombre_completo=datos['nombre_usuario'], email=datos['email'],
                password_hash=generate_password_hash(datos['password']), rol='superadmin'
            )
            db.session.add(nuevo_usuario)
            
            # --- AUDITORÍA: CREACIÓN SÚPER ADMIN ---
            auditoria = RegistroAuditoria(
                operador="Súper Admin",
                accion="Creación Súper Admin",
                detalles=f"Se registró un nuevo usuario con rol Súper Administrador: {nuevo_usuario.nombre_completo} ({nuevo_usuario.email})."
            )
            db.session.add(auditoria)
        else:
            plan_id = datos.get('plan_id')
            fecha_actual = datetime.utcnow()
            fecha_vence = fecha_actual + timedelta(days=30) if plan_id else None

            nueva_clinica = Clinica(
                nombre_negocio=datos['nombre_negocio'], nit=nit_enviado, direccion=datos.get('direccion', ''),
                plan_id=plan_id, fecha_inicio_suscripcion=fecha_actual if plan_id else None, fecha_vencimiento=fecha_vence 
            )
            db.session.add(nueva_clinica)
            db.session.flush()

            nuevo_usuario = Usuario(
                clinica_id=nueva_clinica.id, nombre_completo=datos['nombre_usuario'], email=datos['email'],
                password_hash=generate_password_hash(datos['password']), rol='admin'
            )
            db.session.add(nuevo_usuario)
            
            # --- AUDITORÍA: CREACIÓN DE CLÍNICA ---
            auditoria = RegistroAuditoria(
                operador="Súper Admin",
                accion="Creación de Clínica",
                detalles=f"Se registró la clínica '{nueva_clinica.nombre_negocio}' con el administrador '{nuevo_usuario.nombre_completo}'."
            )
            db.session.add(auditoria)
            
        db.session.commit()
        return jsonify({"mensaje": "Registro exitoso"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# 3. ACTUALIZAR CLÍNICA
@saas_admin_bp.route('/api/admin/clinicas/<int:id>', methods=['PUT'])
def actualizar_clinica(id):
    try:
        datos = request.get_json()
        clinica = Clinica.query.get(id)
        if not clinica: return jsonify({"error": "No existe la clínica"}), 404
            
        admin_local = Usuario.query.filter_by(clinica_id=id).first()
        nuevo_nit = datos.get('nit', '').strip()
        
        if nuevo_nit and nuevo_nit != clinica.nit and Clinica.query.filter_by(nit=nuevo_nit).first():
            return jsonify({"error": "El NIT ya pertenece a otra clínica"}), 409
        
        # Guardamos los nombres anteriores para dejar un registro detallado en los logs
        nombre_anterior = clinica.nombre_negocio
        
        clinica.nombre_negocio = datos.get('nombre_negocio', clinica.nombre_negocio)
        clinica.nit = nuevo_nit
        clinica.direccion = datos.get('direccion', clinica.direccion)
            
        if 'plan_id' in datos:
            clinica.plan_id = int(datos.get('plan_id')) if datos.get('plan_id') else None
            
        if admin_local:
            nuevo_email = datos.get('email', '').strip()
            if nuevo_email and nuevo_email != admin_local.email and Usuario.query.filter_by(email=nuevo_email).first():
                return jsonify({"error": "El correo ya está registrado"}), 409
            
            admin_local.email = nuevo_email if nuevo_email else admin_local.email
            if datos.get('nombre_usuario'): admin_local.nombre_completo = datos.get('nombre_usuario')
            if datos.get('password') and datos.get('password').strip(): admin_local.password_hash = generate_password_hash(datos['password'])

        # --- AUDITORÍA: ACTUALIZACIÓN ---
        auditoria = RegistroAuditoria(
            operador="Súper Admin",
            accion="Modificación",
            detalles=f"Se actualizaron los datos generales de la clínica '{nombre_anterior}' (ID: {id})."
        )
        db.session.add(auditoria)

        db.session.commit()
        return jsonify({"mensaje": "Actualizado correctamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# 4. CAMBIAR ESTADO MANUAL (SUSPENDER / REACTIVAR)
@saas_admin_bp.route('/api/admin/clinicas/<int:id>/cambiar-estado', methods=['POST'])
def cambiar_estado_clinica(id):
    clinica = Clinica.query.get(id)
    usuarios = Usuario.query.filter_by(clinica_id=id).all()
    if not usuarios or not clinica: return jsonify({"error": "No se encontraron registros asociados"}), 404
    
    nuevo_estado = not usuarios[0].activo
    for u in usuarios: u.activo = nuevo_estado
    
    # --- AUDITORÍA: CAMBIO DE ESTADO ---
    texto_estado = "Reactivada" if nuevo_estado else "Suspendida"
    auditoria = RegistroAuditoria(
        operador="Súper Admin",
        accion="Cambio de Estado",
        detalles=f"La clínica '{clinica.nombre_negocio}' fue {texto_estado} y el acceso a sus usuarios fue modificado."
    )
    db.session.add(auditoria)
        
    db.session.commit()
    return jsonify({"mensaje": "Estado actualizado", "nuevo_estado": nuevo_estado}), 200


# 5. RENOVAR SUSCRIPCIÓN MANUAL (+30 DÍAS)
@saas_admin_bp.route('/api/admin/clinicas/<int:id>/renovar', methods=['POST'])
def renovar_suscripcion(id):
    try:
        clinica = Clinica.query.get(id)
        if not clinica: return jsonify({"error": "Clínica no encontrada"}), 404
        if not clinica.plan_id: return jsonify({"error": "La clínica no tiene un plan asignado."}), 400

        fecha_actual = datetime.utcnow()
        # Si ya venció, se cuentan 30 días a partir de hoy. Si no, se acumulan a su fecha de corte.
        if not clinica.fecha_vencimiento or clinica.fecha_vencimiento < fecha_actual:
            clinica.fecha_vencimiento = fecha_actual + timedelta(days=30)
        else:
            clinica.fecha_vencimiento = clinica.fecha_vencimiento + timedelta(days=30)
            
        # --- AUDITORÍA: RENOVAR SUSCRIPCIÓN ---
        fecha_texto = clinica.fecha_vencimiento.strftime('%Y-%m-%d')
        auditoria = RegistroAuditoria(
            operador="Súper Admin",
            accion="Renovación Manual",
            detalles=f"Se extendió la suscripción de '{clinica.nombre_negocio}' por 30 días. Próximo vencimiento: {fecha_texto}."
        )
        db.session.add(auditoria)
            
        db.session.commit()
        return jsonify({"mensaje": "Suscripción renovada con éxito", "nueva_fecha": clinica.fecha_vencimiento.strftime('%Y-%m-%d')}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500