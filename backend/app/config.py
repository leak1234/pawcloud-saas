import os

class Config:
    # Lee la variable DATABASE_URL del archivo .env
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://admin:password123@localhost:5432/pawcloud')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'clave_por_defecto')