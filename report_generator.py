import os
from fpdf import FPDF
from datetime import datetime

def generar_pdf_dashboard(user_name, opening_time, closing_time, duration_hours, total_efectivo):
    # Crear la carpeta reports si no existe
    os.makedirs("reports", exist_ok=True)

    # Nombre del archivo PDF con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dashboard_{timestamp}.pdf"
    ruta_pdf = os.path.join("reports", filename)

    # Crear el PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Resumen del Turno", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Responsable: {user_name}", ln=True)
    pdf.cell(200, 10, txt=f"Apertura: {opening_time}", ln=True)
    pdf.cell(200, 10, txt=f"Cierre: {closing_time}", ln=True)
    pdf.cell(200, 10, txt=f"Duración (hrs): {duration_hours:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total recaudado: ${total_efectivo:.2f}", ln=True)

    pdf.output(ruta_pdf)
    return ruta_pdf
