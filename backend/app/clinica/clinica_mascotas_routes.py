from flask import request, jsonify
from app import db
from .clinica_models import Dueno, Mascota
from . import clinica_bp
from datetime import datetime

@clinica_bp.route('/api/clinica/<int:clinica_id>/duenos/<int:dueno_id>/mascotas', methods=['POST'])
def agregar_mascota_extra(clinica_id, dueno_id):
    try:
        dueno = Dueno.query.filter_by(id=dueno_id, clinica_id=clinica_id).first()
        if not dueno: return jsonify({"error": "Cliente no localizado"}), 404
        
        datos = request.get_json()
        f_nac = None
        if datos.get('fecha_nacimiento'):
            f_nac = datetime.strptime(datos['fecha_nacimiento'], "%Y-%m-%d").date()

        nueva_mascota = Mascota(
            dueno_id=dueno.id, nombre=datos['nombre'], especie=datos['especie'],
            raza=datos.get('raza', ''), color_pelaje=datos.get('color_pelaje', ''),
            fecha_nacimiento=f_nac, genero=datos.get('genero', 'Macho'),
            esterilizado=bool(datos.get('esterilizado', False)),
            peso=datos.get('peso') if datos.get('peso') else None,
            temperamento=datos.get('temperamento', 'Dócil'),
            alergias_conocidas=datos.get('alergias_conocidas', ''),
            patologias_cronicas=datos.get('patologias_cronicas', ''), activo=True
        )
        db.session.add(nueva_mascota)
        db.session.commit()
        return jsonify({"mensaje": "Paciente vinculado exitosamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@clinica_bp.route('/api/clinica/<int:clinica_id>/mascotas/<int:mascota_id>', methods=['PUT'])
def editar_mascota_perfil(clinica_id, mascota_id):
    try:
        mascota = Mascota.query.join(Dueno).filter(Mascota.id == mascota_id, Dueno.clinica_id == clinica_id).first()
        if not mascota: return jsonify({"error": "Paciente inexistente"}), 404
        
        datos = request.get_json()
        if datos.get('fecha_nacimiento'):
            mascota.fecha_nacimiento = datetime.strptime(datos['fecha_nacimiento'], "%Y-%m-%d").date()

        mascota.nombre = datos.get('nombre', mascota.nombre)
        mascota.especie = datos.get('especie', mascota.especie)
        mascota.raza = datos.get('raza', mascota.raza)
        mascota.color_pelaje = datos.get('color_pelaje', mascota.color_pelaje)
        mascota.genero = datos.get('genero', mascota.genero)
        mascota.esterilizado = bool(datos.get('esterilizado', mascota.esterilizado))
        mascota.temperamento = datos.get('temperamento', mascota.temperamento)
        mascota.alergias_conocidas = datos.get('alergias_conocidas', mascota.alergias_conocidas)
        mascota.patologias_cronicas = datos.get('patologias_cronicas', mascota.patologias_cronicas)
        
        if datos.get('peso'):
            mascota.peso = datos.get('peso')

        db.session.commit()
        return jsonify({"mensaje": "Ficha médica del paciente actualizada"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500