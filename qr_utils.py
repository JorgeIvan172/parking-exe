import os
import sys
import qrcode

def generate_ticket_qr(ticket_id):
    data = str(ticket_id)
    qr_img = qrcode.make(data)

    # Obtener la ruta base dependiendo de si se ejecuta como .py o como .exe
    if getattr(sys, 'frozen', False):
        # Ejecutable (.exe)
        base_path = os.path.dirname(sys.executable)
    else:
        # Script (.py)
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Carpeta donde se guardarán los QR
    folder = os.path.join(base_path, "qrcodes")
    os.makedirs(folder, exist_ok=True)

    file_name = os.path.join(folder, f"ticket_{ticket_id}.png")
    qr_img.save(file_name)

    return file_name
