import os
import base64
import requests
import re
from flask import Blueprint, request, jsonify, current_app
from app.clinica.clinica_models import Dueno, Mascota, Consulta
from app.saas_admin.models import Clinica
from app.clinica.pdf_generator import generar_historial_pdf

whatsapp_webhook_bp = Blueprint('whatsapp_webhook', __name__)

EVOLUTION_API_URL = os.environ.get('EVOLUTION_URL', 'http://evolution_api:8080')
EVOLUTION_API_KEY = os.environ.get('EVOLUTION_API_KEY')

@whatsapp_webhook_bp.route('/api/whatsapp/webhook/<int:clinica_id>', methods=['POST'])
def recibir_mensaje(clinica_id):
    datos = request.get_json()
    
    if datos.get('event') != 'messages.upsert':
        return jsonify({"status": "ignorado"}), 200
        
    instancia_wa = datos.get('instance') 
    mensaje_data = datos.get('data', {}).get('message', {})
    
    # --- CAMBIO CLAVE: Priorizamos el campo 'sender' que trae el número real ---
    remitente_info = datos.get('sender', '') 
    if not remitente_info:
        # Fallback si no llega sender en la raíz, usamos el JID
        remitente_info = datos.get('data', {}).get('key', {}).get('remoteJid', '')
    
    # Extraemos solo los dígitos del número (quitamos el @s.whatsapp.net, @lid, etc)
    import re
    telefono_numerico = re.sub(r'\D', '', remitente_info)
    
    # Si empieza con 591, lo quitamos para buscar en BD (ajusta esto a tu formato de BD)
    if len(telefono_numerico) >= 11 and telefono_numerico.startswith('591'):
        telefono_limpio = telefono_numerico[3:]
    else:
        telefono_limpio = telefono_numerico
    
    texto_mensaje = mensaje_data.get('conversation') or \
                    mensaje_data.get('extendedTextMessage', {}).get('text') or \
                    mensaje_data.get('imageMessage', {}).get('caption') or ''
    texto_limpio = texto_mensaje.strip().lower()

    print(f"DEBUG: Mensaje de {remitente_info}. Buscando en BD número: {telefono_limpio}")

    if texto_limpio.startswith('historial'):
        procesar_peticion_historial(clinica_id, instancia_wa, telefono_limpio, texto_limpio, remitente_info)
        
    return jsonify({"status": "recibido"}), 200

def procesar_peticion_historial(clinica_id, instancia_wa, telefono, texto_cliente, remitente_jid):
    # Buscamos al dueño por teléfono en la clínica correspondiente
    dueno = Dueno.query.filter_by(telefono=telefono, clinica_id=clinica_id).first()
    
    if not dueno:
        print(f"DEBUG: Dueño NO encontrado para teléfono {telefono}. Revisa si el número en DB coincide.")
        enviar_texto_api(instancia_wa, remitente_jid, "No estás registrado en nuestra clínica. Contacta al administrador.")
        return

    print(f"DEBUG: Dueño encontrado: {dueno.nombre_completo}")
    mascotas = Mascota.query.filter_by(dueno_id=dueno.id, activo=True).all()
    
    if not mascotas:
        enviar_texto_api(instancia_wa, remitente_jid, "No tienes mascotas registradas.")
        return

    # Lógica de respuesta
    if texto_cliente == 'historial':
        if len(mascotas) == 1:
            enviar_pdf_whatsapp(instancia_wa, remitente_jid, mascotas[0])
        else:
            nombres = [m.nombre.capitalize() for m in mascotas]
            enviar_texto_api(instancia_wa, remitente_jid, f"Hola {dueno.nombre_completo}, tienes a: {', '.join(nombres)}. Escribe: *historial nombre*")
            
    elif texto_cliente.startswith('historial '):
        nombre_pedido = texto_cliente.replace('historial', '').strip()
        mascota_elegida = next((m for m in mascotas if m.nombre.lower() == nombre_pedido), None)
        
        if mascota_elegida:
            enviar_pdf_whatsapp(instancia_wa, remitente_jid, mascota_elegida)
        else:
            enviar_texto_api(instancia_wa, remitente_jid, f"No encontré a '{nombre_pedido.capitalize()}'.")

def enviar_texto_api(instancia_wa, numero, texto):
    url = f"{EVOLUTION_API_URL}/message/sendText/{instancia_wa}"
    headers = {"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"}
    
    payload = {
        "number": numero,
        "textMessage": { "text": texto }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"DEBUG: Envío texto status {response.status_code}")
    except Exception as e:
        print(f"DEBUG: ERROR enviando texto: {e}")
        
def enviar_pdf_whatsapp(instancia_wa, remitente_jid, mascota):
    dueno = mascota.dueno
    clinica = Clinica.query.get(dueno.clinica_id)
    consultas = Consulta.query.filter_by(mascota_id=mascota.id, estado='completada').order_by(Consulta.fecha_consulta.desc()).all()
    
    nombre_pdf = generar_historial_pdf(clinica, dueno, mascota, consultas)
    ruta_pdf = os.path.join(current_app.root_path, 'static', 'reportes', nombre_pdf)
    
    with open(ruta_pdf, "rb") as archivo:
        pdf_base64 = base64.b64encode(archivo.read()).decode('utf-8')

    url = f"{EVOLUTION_API_URL}/message/sendMedia/{instancia_wa}"
    headers = {"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"}
    payload = {
        "number": remitente_jid,
        "mediatype": "document",
        "mimetype": "application/pdf",
        "fileName": f"Historial_{mascota.nombre}.pdf",
        "media": pdf_base64
    }
    requests.post(url, json=payload, headers=headers)