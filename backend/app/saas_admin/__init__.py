from flask import Blueprint

# 1. Creamos el Blueprint principal aquí mismo
saas_admin_bp = Blueprint('saas_admin', __name__)

# 2. Importamos las rutas de los submódulos al final para que Flask las reconozca
# (Esto evita problemas de dependencias circulares)
from . import auth_routes
from . import clinicas_routes
from . import planes_routes
from . import stats_routes
from . import reportes_routes
from . import avisos_routes