from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime
from app import db
from app.saas_admin.models import Usuario
from .models import Dueno, Mascota

clinica_bp = Blueprint('clinica', __name__)

# ==============================================================================
# GESTIÓN DE DUEÑOS (CLIENTES)
# ==============================================================================

@clinica_bp.route('/api/clinica/duenos', methods=['GET'])
def obtener_duenos():
    clinica_id = request.headers.get('X-Clinica-Id')
    if not clinica_id:
        return jsonify({"error": "Falta identificar la clínica"}), 400

    duenos = Dueno.query.filter_by(clinica_id=clinica_id).order_by(Dueno.id.desc()).all()
    
    resultado = []
    for d in duenos:
        resultado.append({
            "id": d.id,
            "nombre_completo": d.nombre_completo,
            "telefono": d.telefono or "Sin teléfono",
            "email": d.email or "Sin correo",
            "direccion": d.direccion or "Sin dirección",
            "cantidad_mascotas": len(d.mascotas) 
        })
    return jsonify(resultado), 200

@clinica_bp.route('/api/clinica/duenos/registrar', methods=['POST'])
def registrar_dueno():
    clinica_id = request.headers.get('X-Clinica-Id')
    if not clinica_id:
        return jsonify({"error": "Acceso denegado"}), 403

    datos = request.get_json()
    
    # Validar campos obligatorios
    if not datos.get('nombre_completo'):
        return jsonify({"error": "El nombre del cliente es obligatorio"}), 400
    
    try:
        nuevo_dueno = Dueno(
            clinica_id=clinica_id,
            nombre_completo=datos['nombre_completo'],
            telefono=datos.get('telefono', ''),
            email=datos.get('email', ''),
            direccion=datos.get('direccion', '')
        )
        db.session.add(nuevo_dueno)
        db.session.commit()
        return jsonify({"mensaje": "Cliente registrado exitosamente", "id": nuevo_dueno.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al registrar: {str(e)}"}), 500

# ==============================================================================
# GESTIÓN DE MASCOTAS (PACIENTES)
# ==============================================================================

@clinica_bp.route('/api/clinica/mascotas/<int:dueno_id>', methods=['GET'])
def obtener_mascotas_por_dueno(dueno_id):
    clinica_id = request.headers.get('X-Clinica-Id')
    if not clinica_id:
        return jsonify({"error": "Falta identificar la clínica"}), 400

    mascotas = Mascota.query.filter_by(dueno_id=dueno_id, clinica_id=clinica_id).all()
    
    resultado = []
    for m in mascotas:
        resultado.append({
            "id": m.id,
            "nombre": m.nombre,
            "especie": m.especie,
            "raza": m.raza or "Mestizo",
            "sexo": m.sexo or "No especificado",
            "peso": m.peso,
            "fecha_nacimiento": m.fecha_nacimiento.strftime('%Y-%m-%d') if m.fecha_nacimiento else None
        })
    return jsonify(resultado), 200

@clinica_bp.route('/api/clinica/mascotas/registrar', methods=['POST'])
def registrar_mascota():
    clinica_id = request.headers.get('X-Clinica-Id')
    if not clinica_id:
        return jsonify({"error": "Acceso denegado"}), 403

    datos = request.get_json()
    dueno_id = datos.get('dueno_id')
    
    # Validaciones básicas
    if not datos.get('nombre') or not datos.get('especie'):
        return jsonify({"error": "El nombre y la especie son obligatorios"}), 400
    
    dueno = Dueno.query.filter_by(id=dueno_id, clinica_id=clinica_id).first()
    if not dueno:
        return jsonify({"error": "El dueño no existe o no pertenece a esta clínica"}), 404

    try:
        # Convertir fecha si viene en el JSON
        fecha_nac = None
        if datos.get('fecha_nacimiento'):
            fecha_nac = datetime.strptime(datos['fecha_nacimiento'], '%Y-%m-%d').date()

        nueva_mascota = Mascota(
            clinica_id=clinica_id,
            dueno_id=dueno_id,
            nombre=datos['nombre'],
            especie=datos['especie'],
            raza=datos.get('raza', ''),
            sexo=datos.get('sexo', ''),
            peso=float(datos['peso']) if datos.get('peso') else None,
            fecha_nacimiento=fecha_nac
        )
        db.session.add(nueva_mascota)
        db.session.commit()
        return jsonify({"mensaje": "Paciente registrado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error al registrar paciente: {str(e)}"}), 500