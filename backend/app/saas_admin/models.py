from app import db
from datetime import datetime

class Clinica(db.Model):
    __tablename__ = 'clinicas'
    id = db.Column(db.Integer, primary_key=True)
    nombre_negocio = db.Column(db.String(150), nullable=False)
    nit = db.Column(db.String(50), unique=True, nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    usuarios = db.relationship('Usuario', backref='clinica', lazy=True)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=True) 
    nombre_completo = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), default='admin') # 'superadmin', 'admin', 'veterinario', 'cajero'
    activo = db.Column(db.Boolean, default=True)