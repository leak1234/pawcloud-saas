import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generar_historial_pdf(clinica, dueno, mascota, consultas):
    carpeta_reportes = os.path.join('app', 'static', 'reportes')
    os.makedirs(carpeta_reportes, exist_ok=True)
    
    nombre_archivo = f"historial_{mascota.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    ruta_completa = os.path.join(carpeta_reportes, nombre_archivo)

    c = canvas.Canvas(ruta_completa, pagesize=letter)
    ancho, alto = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, alto - 50, clinica.nombre_negocio.upper())
    c.setFont("Helvetica", 10)
    c.drawString(50, alto - 68, f"Dirección: {clinica.direccion or 'No especificada'}")
    c.drawString(50, alto - 82, f"Fecha Reporte: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    c.line(50, alto - 95, ancho - 50, alto - 95)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, alto - 120, "EXPEDIENTE CLÍNICO DIGITAL")
    c.setFont("Helvetica", 10)
    c.drawString(50, alto - 142, f"Mascota: {mascota.nombre} ({mascota.especie})")
    c.drawString(50, alto - 157, f"Propietario: {dueno.nombre_completo} | Telf: {dueno.telefono}")
    c.line(50, alto - 170, ancho - 50, alto - 170)

    y = alto - 195
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y, "HISTORIAL DE ATENCIONES MÉDICAS:")
    y -= 25

    for consulta in consultas:
        if y < 100: 
            c.showPage()
            y = alto - 50

        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, f"📅 Fecha: {consulta.fecha_consulta.strftime('%d/%m/%Y')}")
        y -= 15
        c.setFont("Helvetica", 10)
        c.drawString(60, y, f"Motivo: {consulta.motivo}")
        y -= 14
        c.drawString(60, y, f"🩺 Diagnóstico: {consulta.diagnostico or 'Revisión General'}")
        y -= 14
        c.drawString(60, y, f"💊 Tratamiento / Receta: {consulta.tratamiento_receta or 'Sin observaciones.'}")
        y -= 20
        c.setDash(1, 2)
        c.line(50, y, ancho - 50, y)
        c.setDash()
        y -= 15

    c.save()
    return nombre_archivo