from app import db
from datetime import datetime

# MODELO: DUEÑO (Cliente)
class Dueno(db.Model):
    __tablename__ = 'duenos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Candado Multi-Tenant: Obligatorio para saber de qué veterinaria es este cliente
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=False)
    
    # Datos Personales del Cliente
    nombre_completo = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación: Un dueño puede tener muchas mascotas registradas
    # cascade="all, delete-orphan" asegura que si borras al dueño, se borren sus mascotas
    mascotas = db.relationship('Mascota', backref='dueno', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Dueno {self.nombre_completo}>'



# MODELO: MASCOTA (PACIENTE)
class Mascota(db.Model):
    __tablename__ = 'mascotas'
    
    id = db.Column(db.Integer, primary_key=True)
    
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=False)
    dueno_id = db.Column(db.Integer, db.ForeignKey('duenos.id'), nullable=False)
    
    # Datos Médicos / Físicos del Paciente
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)  
    raza = db.Column(db.String(100), nullable=True)
    sexo = db.Column(db.String(20), nullable=True)      
    peso = db.Column(db.Float, nullable=True)           
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Aquí en el futuro agregaremos la relación con el Historial Médico (Consultas, Vacunas, etc.)

    def __repr__(self):
        return f'<Mascota {self.nombre} - {self.especie}>'