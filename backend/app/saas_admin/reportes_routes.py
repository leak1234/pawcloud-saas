from flask import send_file, jsonify
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

from . import saas_admin_bp
from .models import RegistroAuditoria

@saas_admin_bp.route('/api/admin/reportes/pdf/<tipo>', methods=['GET'])
def descargar_pdf(tipo):
    if tipo != 'auditoria':
        return jsonify({"error": "Tipo de reporte no válido"}), 400

    logs = RegistroAuditoria.query.order_by(RegistroAuditoria.fecha.desc()).all()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elementos = []
    
    # Estilos base
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('Titulo', parent=estilos['Heading1'], fontSize=16, textColor=colors.HexColor('#1e293b'), spaceAfter=20)
    
    # --- NUEVO: Estilo específico para celdas con texto largo ---
    estilo_celda = ParagraphStyle(
        'Celda', 
        parent=estilos['Normal'], 
        fontSize=9, 
        textColor=colors.HexColor('#1e293b'),
        leading=12 # Espaciado entre líneas
    )
    
    elementos.append(Paragraph("📋 Historial de Auditoría de PawCloud", estilo_titulo))
    elementos.append(Paragraph(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}", estilos['Normal']))
    elementos.append(Spacer(1, 15))
    
    datos_tabla = [["Fecha", "Operador", "Acción", "Detalles"]]
    
    for log in logs:
        fecha_str = log.fecha.strftime('%Y-%m-%d %H:%M')
        
        # --- NUEVO: Envolvemos 'log.detalles' en un Paragraph para forzar el salto de línea ---
        detalles_multilinea = Paragraph(log.detalles, estilo_celda)
        
        datos_tabla.append([fecha_str, log.operador, log.accion, detalles_multilinea])
    
    if len(datos_tabla) == 1:
        datos_tabla.append(["", "", "Sin registros actuales", ""])
    
    # El ancho 260 de la última columna ahora contendrá el texto perfectamente ordenado
    tabla = Table(datos_tabla, colWidths=[90, 80, 100, 260])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'TOP'), # TOP alinea el texto arriba, ideal para celdas altas
    ]))
    
    elementos.append(tabla)
    doc.build(elementos)
    
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=False, download_name="auditoria_pawcloud.pdf", mimetype='application/pdf')