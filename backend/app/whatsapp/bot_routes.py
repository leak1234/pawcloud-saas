import os
import requests
from flask import request, jsonify
from app import db 
from app.clinica.clinica_models import Dueno, Mascota, Consulta
from app.saas_admin.models import Clinica
from app.clinica.pdf_generator import generar_historial_pdf
from . import whatsapp_bp

EVOLUTION_API_URL = os.environ.get("EVOLUTION_URL", "http://evolution_api:8080")
EVOLUTION_API_KEY = os.environ.get("EVOLUTION_API_KEY", "PawCloudGlobalKey123")
HEADERS = {"apikey": EVOLUTION_API_KEY, "Content-Type": "application/json"}

@whatsapp_bp.route('/api/whatsapp/instancia/<int:clinica_id>/conectar', methods=['POST'])
def conectar_instancia(clinica_id):
    clinica = Clinica.query.get_or_404(clinica_id)
    instance_name = f"clinica_{clinica_id}"
    
    try:
        # 1. Borramos cualquier sesión anterior para asegurar que salga el QR
        requests.delete(f"{EVOLUTION_API_URL}/instance/delete/{instance_name}", headers=HEADERS)
        
        # 2. Creamos una nueva
        requests.post(f"{EVOLUTION_API_URL}/instance/create", json={
            "instanceName": instance_name, "token": f"tkn_{instance_name}", "qrcode": True
        }, headers=HEADERS, timeout=15)

        # 3. Configuramos el Webhook de pasada
        requests.post(f"{EVOLUTION_API_URL}/webhook/set/{instance_name}", json={
            "url": "http://pawcloud_backend:5000/api/whatsapp/webhook",
            "webhook_by_events": False,
            "events": ["MESSAGES_UPSERT"]
        }, headers=HEADERS)

        # 4. Solicitamos la conexión (esto devuelve el QR)
        res = requests.get(f"{EVOLUTION_API_URL}/instance/connect/{instance_name}", headers=HEADERS)
        data = res.json()

        if data.get("status") == "CONNECTED":
            clinica.whatsapp_conectado = True
            clinica.whatsapp_instancia = instance_name
            db.session.commit()
            return jsonify({"status": "CONNECTED"}), 200

        # ARREGLO IMAGEN ROTA: Asegurarnos de que el Base64 tenga el formato correcto para Vue
        qr_code = data.get("base64", "")
        if qr_code and not qr_code.startswith("data:image"):
            qr_code = f"data:image/png;base64,{qr_code}"

        return jsonify({"status": "SCAN_QR", "qr": qr_code}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@whatsapp_bp.route('/api/whatsapp/instancia/<int:clinica_id>/enviar-manual', methods=['POST'])
def enviar_manual(clinica_id):
    clinica = Clinica.query.get_or_404(clinica_id)
    if not clinica.whatsapp_conectado:
        return jsonify({"error": "WhatsApp desvinculado de este consultorio."}), 400
    
    datos = request.get_json()
    
    # Ahora capturamos la respuesta real de Evolution API
    exito, detalle = enviar_texto_api(clinica.whatsapp_instancia, datos['telefono'], datos['mensaje'])
    
    if exito:
        return jsonify({"mensaje": "Mensaje enviado exitosamente"}), 200
    else:
        # Si Evolution falla, le devolvemos el error al Frontend
        print(f"Error al enviar WA: {detalle}")
        return jsonify({"error": "Evolution API rechazó el mensaje", "detalle": detalle}), 400

@whatsapp_bp.route('/api/whatsapp/webhook', methods=['POST'])
def webhook_receptor():
    datos = request.get_json()
    instance_name = datos.get("instance")
    if datos.get("event") != "messages.upsert":
        return jsonify({"status": "ignorado"}), 200
    try:
        clinica_id = int(instance_name.split("_")[1])
        payload = datos.get("data", {})
        if payload.get("key", {}).get("fromMe"): return jsonify({"status": "propio"}), 200
        
        chat_id = payload.get("key", {}).get("remoteJid")
        texto = payload.get("message", {}).get("conversation", "").strip().lower()
        if not texto and "extendedTextMessage" in payload.get("message", {}):
            texto = payload["message"]["extendedTextMessage"].get("text", "").strip().lower()

        if chat_id and texto:
            procesar_peticion(clinica_id, chat_id, texto)
        return jsonify({"status": "ok"}), 200
    except Exception:
        return jsonify({"status": "error"}), 200

def procesar_peticion(clinica_id, chat_id, texto):
    numero = chat_id.split("@")[0][-8:]
    dueno = Dueno.query.filter_by(clinica_id=clinica_id).filter(Dueno.telefono.like(f"%{numero}%")).first()
    instancia = f"clinica_{clinica_id}"
    clinica = Clinica.query.get(clinica_id)

    if not dueno:
        enviar_texto_api(instancia, chat_id, "Hola. Tu número no se encuentra registrado en nuestra base de datos.")
        return

    if "historial" not in texto:
        masc = ", ".join([m.nombre for m in dueno.mascotas if m.activo])
        enviar_texto_api(instancia, chat_id, f"¡Hola {dueno.nombre_completo}! 👋\nPara obtener el expediente médico digital escribe:\n👉 *Historial [Nombre de tu mascota]*\n\nTus pacientes vinculados: *{masc}*")
        return

    nombre_masc = texto.split("historial")[1].strip()
    mascota = next((m for m in dueno.mascotas if m.nombre.lower() == nombre_masc.lower() and m.activo), None)

    if not mascota:
        enviar_texto_api(instancia, chat_id, f"No encontramos ninguna mascota activa llamada *{nombre_masc}*.")
        return

    consultas = Consulta.query.filter_by(mascota_id=mascota.id, estado='completada').order_by(Consulta.fecha_consulta.desc()).all()
    if not consultas:
        enviar_texto_api(instancia, chat_id, f"El paciente *{mascota.nombre}* no registra consultas médicas completadas.")
        return

    enviar_texto_api(instancia, chat_id, f"⏳ Construyendo el expediente formal de *{mascota.nombre}*... un momento por favor.")
    
    nombre_pdf = generar_historial_pdf(clinica, dueno, mascota, consultas)
    url_publica_pdf = f"http://localhost:5000/public/reportes/{nombre_pdf}"
    
    enviar_pdf_api(instancia, chat_id, url_publica_pdf, f"Historial_{mascota.nombre}.pdf", f"Aquí tienes el Historial Clínico de *{mascota.nombre}*.")

def enviar_texto_api(instancia, chat_id, texto):
    # 1. Limpiar el número (quitar espacios o signos raros)
    numero_limpio = str(chat_id).strip().replace(" ", "").replace("+", "")
    
    # 2. Si el número tiene 8 dígitos, le agregamos el 591
    if len(numero_limpio) == 8:
        numero_limpio = f"591{numero_limpio}"
        
    # 3. EL ARREGLO CLAVE: Estructura exacta que pide Evolution API v1.8.2
    payload = {
        "number": numero_limpio, 
        "textMessage": {
            "text": texto
        }
    }
    
    try:
        url = f"{EVOLUTION_API_URL}/message/sendText/{instancia}"
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        
        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def enviar_pdf_api(instancia, chat_id, url, filename, caption):
    if "@" not in str(chat_id): chat_id = f"591{chat_id}@s.whatsapp.net"
    requests.post(f"{EVOLUTION_API_URL}/message/sendMedia/{instancia}", json={
        "number": chat_id, "mediaMessage": {"mediatype": "document", "fileName": filename, "caption": caption, "media": url}
    }, headers=HEADERS)

@whatsapp_bp.route('/api/whatsapp/instancia/<int:clinica_id>/logout', methods=['POST'])
def logout_whatsapp(clinica_id):
    clinica = Clinica.query.get_or_404(clinica_id)
    
    # Si perdimos el nombre, reconstruimos el nombre por defecto para intentar borrarlo
    instance_name = clinica.whatsapp_instancia or f"clinica_{clinica_id}"

    try:
        # Intentamos cerrar sesión y borrar la instancia en Evolution API
        requests.delete(f"{EVOLUTION_API_URL}/instance/logout/{instance_name}", headers=HEADERS)
        requests.delete(f"{EVOLUTION_API_URL}/instance/delete/{instance_name}", headers=HEADERS)
    except Exception as e:
        print(f"Aviso interno: {e}")

    # FORZAR LIMPIEZA EN LA BASE DE DATOS
    clinica.whatsapp_conectado = False
    clinica.whatsapp_instancia = None 
    db.session.commit()

    return jsonify({"mensaje": "Sesión cerrada correctamente"}), 200
@whatsapp_bp.route('/api/whatsapp/instancia/<int:clinica_id>/estado', methods=['GET'])
def estado_instancia(clinica_id):
    clinica = Clinica.query.get_or_404(clinica_id)
    instance_name = clinica.whatsapp_instancia or f"clinica_{clinica_id}"
    
    try:
        # Preguntamos directamente a Evolution API cuál es el estado real
        res = requests.get(f"{EVOLUTION_API_URL}/instance/connectionState/{instance_name}", headers=HEADERS, timeout=5)
        
        if res.status_code == 200:
            estado_real = res.json().get("instance", {}).get("state")
            
            if estado_real == "open":
                # Si Evolution dice que está abierto, aseguramos que la DB también lo sepa
                if not clinica.whatsapp_conectado:
                    clinica.whatsapp_conectado = True
                    clinica.whatsapp_instancia = instance_name
                    db.session.commit()
                return jsonify({"status": "CONNECTED"}), 200
                
    except Exception as e:
        pass # Si hay error de red con Evolution, caemos al return de abajo
        
    # Si no está 'open', devolvemos desconectado
    return jsonify({"status": "DISCONNECTED"}), 200