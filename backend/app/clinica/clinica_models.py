from app import db
from datetime import datetime, date

class Dueno(db.Model):
    __tablename__ = 'duenos'
    
    id = db.Column(db.Integer, primary_key=True)
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    direccion = db.Column(db.String(200), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    mascotas = db.relationship('Mascota', backref='propietario', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "clinica_id": self.clinica_id,
            "nombre_completo": self.nombre_completo,
            "telefono": self.telefono,
            "email": self.email,
            "direccion": self.direccion,
            "activo": self.activo,
            "fecha_registro": self.fecha_registro.strftime("%Y-%m-%d"),
            "mascotas": [m.to_dict() for m in self.mascotas if m.activo]
        }

class Mascota(db.Model):
    __tablename__ = 'mascotas'
    
    id = db.Column(db.Integer, primary_key=True)
    dueno_id = db.Column(db.Integer, db.ForeignKey('duenos.id'), nullable=False)
    
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)  
    raza = db.Column(db.String(50), nullable=True)
    color_pelaje = db.Column(db.String(100), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    genero = db.Column(db.String(15), nullable=False)   
    esterilizado = db.Column(db.Boolean, default=False)
    peso = db.Column(db.Numeric(5, 2), nullable=True)   
    temperamento = db.Column(db.String(50), default='Dócil')
    alergias_conocidas = db.Column(db.Text, nullable=True)
    patologias_cronicas = db.Column(db.Text, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    consultas = db.relationship('Consulta', backref='paciente', lazy=True, cascade="all, delete-orphan")

    def calcular_edad(self):
        if not self.fecha_nacimiento:
            return "Edad no registrada"
        hoy = datetime.utcnow().date()
        dias = (hoy - self.fecha_nacimiento).days
        if dias < 0:
            return "Recién nacido"
        elif dias < 30:
            return f"{dias} días"
        elif dias < 365:
            meses = dias // 30
            return f"{meses} mes{'es' if meses > 1 else ''}"
        else:
            anos = dias // 365
            return f"{anos} año{'s' if anos > 1 else ''}"

    def to_dict(self):
        return {
            "id": self.id,
            "dueno_id": self.dueno_id,
            "nombre": self.nombre,
            "especie": self.especie,
            "raza": self.raza,
            "color_pelaje": self.color_pelaje,
            "fecha_nacimiento": self.fecha_nacimiento.strftime("%Y-%m-%d") if self.fecha_nacimiento else None,
            "edad_calculada": self.calcular_edad(),
            "genero": self.genero,
            "esterilizado": self.esterilizado,
            "peso": float(self.peso) if self.peso else None,
            "temperamento": self.temperamento,
            "alergias_conocidas": self.alergias_conocidas,
            "patologias_cronicas": self.patologias_cronicas,
            "activo": self.activo,
            "fecha_registro": self.fecha_registro.strftime("%Y-%m-%d")
        }

class Servicio(db.Model):
    __tablename__ = 'servicios'
    
    id = db.Column(db.Integer, primary_key=True)
    clinica_id = db.Column(db.Integer, db.ForeignKey('clinicas.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    precio_base = db.Column(db.Numeric(10, 2), default=0.0)
    activo = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "precio_base": float(self.precio_base) if self.precio_base else 0.0,
            "activo": self.activo
        }

class Consulta(db.Model):
    __tablename__ = 'consultas'
    
    id = db.Column(db.Integer, primary_key=True)
    mascota_id = db.Column(db.Integer, db.ForeignKey('mascotas.id'), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False) 
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=True)
    fecha_consulta = db.Column(db.DateTime, default=datetime.utcnow)
    peso_actual = db.Column(db.Numeric(5, 2), nullable=True) 
    temperatura = db.Column(db.Numeric(4, 2), nullable=True) 
    motivo = db.Column(db.String(255), nullable=False)
    sintomas = db.Column(db.Text, nullable=True)
    diagnostico = db.Column(db.Text, nullable=True)
    tratamiento_receta = db.Column(db.Text, nullable=True)
    fecha_programada = db.Column(db.DateTime, nullable=True) 
    estado = db.Column(db.String(20), default='completada')
    recordatorio_enviado = db.Column(db.Boolean, default=False)

    servicio = db.relationship('Servicio', backref='consultas', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "mascota_id": self.mascota_id,
            "veterinario_id": self.veterinario_id,
            "servicio_id": self.servicio_id,
            "servicio_nombre": self.servicio.nombre if self.servicio else "Consulta General",
            "fecha_consulta": self.fecha_consulta.strftime("%Y-%m-%d %H:%M"),
            "fecha_programada": self.fecha_programada.strftime("%Y-%m-%d %H:%M") if self.fecha_programada else None,
            "peso_actual": float(self.peso_actual) if self.peso_actual else None,
            "temperatura": float(self.temperatura) if self.temperatura else None,
            "motivo": self.motivo,
            "sintomas": self.sintomas,
            "diagnostico": self.diagnostico,
            "tratamiento_receta": self.tratamiento_receta,
            "estado": self.estado
        }