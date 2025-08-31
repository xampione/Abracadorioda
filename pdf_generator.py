from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_moliture_report(moliture):
    """Genera un report PDF per le moliture selezionate"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, 
                          topMargin=20*mm, bottomMargin=20*mm)
    
    # Stili
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Contenuto del documento
    story = []
    
    # Titolo
    title = Paragraph("REPORT MOLITURE - FRANTOIO OLEARIO", title_style)
    story.append(title)
    
    # Data generazione
    data_gen = Paragraph(f"Generato il: {datetime.now().strftime('%d/%m/%Y alle %H:%M')}", styles['Normal'])
    story.append(data_gen)
    story.append(Spacer(1, 20))
    
    # Riepilogo
    story.append(Paragraph("RIEPILOGO", heading_style))
    
    riepilogo_data = [
        ['Numero Moliture:', str(len(moliture))],
        ['Totale Cassoni:', str(sum(len(m.cassoni) for m in moliture))],
        ['Quantità Totale (kg):', str(sum(m.quantita_totale for m in moliture))],
    ]
    
    riepilogo_table = Table(riepilogo_data, colWidths=[80*mm, 40*mm])
    riepilogo_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(riepilogo_table)
    story.append(Spacer(1, 20))
    
    # Dettaglio moliture
    story.append(Paragraph("DETTAGLIO MOLITURE", heading_style))
    
    for molitura in moliture:
        # Intestazione molitura
        molitura_title = f"Molitura #{molitura.id} - {molitura.cliente.nome_completo}"
        story.append(Paragraph(molitura_title, styles['Heading3']))
        
        # Dati molitura
        molitura_data = [
            ['Cliente:', molitura.cliente.nome_completo],
            ['Data/Ora:', molitura.data_ora.strftime('%d/%m/%Y %H:%M')],
            ['Sezione:', str(molitura.sezione)],
            ['Stato:', molitura.stato.upper()],
        ]
        
        if molitura.note:
            molitura_data.append(['Note:', molitura.note])
        
        molitura_table = Table(molitura_data, colWidths=[30*mm, 140*mm])
        molitura_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(molitura_table)
        story.append(Spacer(1, 10))
        
        # Cassoni
        if molitura.cassoni:
            story.append(Paragraph("Cassoni:", styles['Heading4']))
            
            cassoni_data = [['Numero Cassone', 'Quantità (kg)']]
            for cassone in sorted(molitura.cassoni, key=lambda x: x.numero_cassone):
                cassoni_data.append([str(cassone.numero_cassone), str(cassone.quantita)])
            
            # Totale
            cassoni_data.append(['TOTALE', str(molitura.quantita_totale)])
            
            cassoni_table = Table(cassoni_data, colWidths=[50*mm, 40*mm])
            cassoni_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(cassoni_table)
        
        story.append(Spacer(1, 20))
    
    # Costruisci PDF
    doc.build(story)
    buffer.seek(0)
    
    return buffer
