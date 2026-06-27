from flask import Blueprint


clinica_bp = Blueprint('clinica', __name__)



from . import empleados_routes  
from . import clinica_duenos_routes     
from . import clinica_dashboard_routes
from . import clinica_mascotas_routes
from . import clinica_consultas_routes
from . import clinica_servicios_routes
from . import pdf_generator
  