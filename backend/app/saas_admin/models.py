from app import db
from datetime import datetime

class Plan(db.Model):
    __tablename__ = 'planes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True) # ej: Básico, Pro, Premium
    precio = db.Column(db.Numeric(10, 2), nullable=False) # ej: 29.99
    limite_usuarios = db.Column(db.Integer, nullable=False) # ej: 3
    limite_pacientes = db.Column(db.Integer, nullable=False) # ej: 500
    activo = db.Column(db.Boolean, default=True)
    
    # Relación inversa (Un plan puede tener muchas clínicas)
    clinicas = db.relationship('Clinica', backref='plan_suscripcion', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio": float(self.precio),
            "limite_usuarios": self.limite_usuarios,
            "limite_pacientes": self.limite_pacientes,
            "activo": self.activo
        }

class Clinica(db.Model):
    __tablename__ = 'clinicas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_negocio = db.Column(db.String(150), nullable=False)
    nit = db.Column(db.String(50), unique=True, nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    # --- NUEVOS CAMPOS PARA INTEGRACIÓN DE WHATSAPP ---
    whatsapp_conectado = db.Column(db.Boolean, default=False)
    whatsapp_instancia = db.Column(db.String(100), unique=True, nullable=True)

    # --- NUEVOS CAMPOS PARA SUSCRIPCIÓN ---
    plan_id = db.Column(db.Integer, db.ForeignKey('planes.id'), nullable=True) 
    fecha_inicio_suscripcion = db.Column(db.DateTime, nullable=True)
    fecha_vencimiento = db.Column(db.DateTime, nullable=True)
    

    usuarios = db.relationship('Usuario', backref='clinica', lazy=True)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=True) 
    nombre_completo = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), default='admin') # 'superadmin', 'admin', 'veterinario', 'cajero', 'peluquero'
    activo = db.Column(db.Boolean, default=True)

class RegistroAuditoria(db.Model):
    __tablename__ = 'registros_auditoria'
    id = db.Column(db.Integer, primary_key=True)
    operador = db.Column(db.String(100), nullable=False) # Ej: "Súper Admin"
    accion = db.Column(db.String(100), nullable=False)   # Ej: "Renovación de Plan"
    detalles = db.Column(db.Text, nullable=False)        # Ej: "Se renovó VetCare Sur por 30 días"
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

class Aviso(db.Model):
    __tablename__ = 'avisos_globales'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), default='info') # Tipos: 'info' (azul), 'warning' (amarillo), 'danger' (rojo)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True) # Para ocultar avisos viejos sin borrarlos