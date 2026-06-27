from flask import Blueprint

whatsapp_bp = Blueprint('whatsapp', __name__)

from . import bot_routes
from . import tareas
from . import webhook_routes