import smtplib
from email.message import EmailMessage
import os

def enviar_pdf_por_correo(destinatario, asunto, cuerpo, ruta_pdf):
    remitente = 'parking.system172@gmail.com'  # Cambia esto por tu correo
    contraseña_app = 'vtyvhsakeyphxziz'  # Pega aquí la contraseña de aplicación

    # Crear el mensaje
    mensaje = EmailMessage()
    mensaje['Subject'] = asunto
    mensaje['From'] = remitente
    mensaje['To'] = destinatario
    mensaje.set_content(cuerpo)

    # Leer el PDF y adjuntarlo
    with open(ruta_pdf, 'rb') as f:
        contenido_pdf = f.read()
        nombre_pdf = os.path.basename(ruta_pdf)
        mensaje.add_attachment(contenido_pdf, maintype='application', subtype='pdf', filename=nombre_pdf)

    # Enviar el correo
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remitente, contraseña_app)
            smtp.send_message(mensaje)
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
