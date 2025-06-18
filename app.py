import tkinter as tk
from tkinter import messagebox
from database import create_ticket, close_ticket, get_ticket_by_plate
import sqlite3
from datetime import datetime
from qr_utils import generate_ticket_qr
from PIL import ImageTk, Image
import sys
import os
import qrcode
from turno import mostrar_cierre_turno
from dashboard import mostrar_dashboard
import report_generator


def generate_ticket_qr(plate):
    qr_folder = "qrcodes"
    # Crea la carpeta si no existe
    os.makedirs(qr_folder, exist_ok=True)
    # Genera el código QR con la placa
    qr = qrcode.make(plate)
    # Ruta para guardar el QR
    qr_path = os.path.join(qr_folder, f"{plate}.png")
    # Guarda el QR
    qr.save(qr_path)
    return qr_path


if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------
# Base de datos: abrir corte
# ---------------------------
def open_cash_cut(name):
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()
    opening_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO cash_cuts (name, opening_time) VALUES (?, ?)",
        (name, opening_time)
    )
    conn.commit()
    cash_cut_id = cursor.lastrowid
    conn.close()
    return cash_cut_id

# ---------------------------
# Clase principal
# ---------------------------

class ParkingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Estacionamiento")
        self.cash_cut_id = None
        self.user_name = ""
        self.setup_login_screen()  # <- Aquí debe iniciar la pantalla de login
        

    def cerrar_turno(self):
        from turno import mostrar_cierre_turno

        def on_confirm():
            # Aquí va la lógica para terminar el turno y mostrar dashboard
            print("Turno terminado. Mostrando dashboard...")
            from dashboard import mostrar_dashboard
            mostrar_dashboard(self.cash_cut_id, self.user_name, self.setup_login_screen)

        def on_cancel():
            print("Cierre de turno cancelado.")

        mostrar_cierre_turno(on_confirm, on_cancel)



            # ------------------------
    # Pantalla de login
    # ------------------------
    def setup_login_screen(self):
        self.clear_screen()

        # Título general arriba
        tk.Label(self.root, text="Estacionamiento AutoZone 24/7", font=("Arial", 20, "bold")).pack(pady=(20, 10))

        # Marco para login
        login_frame = tk.LabelFrame(self.root, text="Iniciar sesión", font=("Arial", 12, "bold"), padx=80, pady=20)
        login_frame.pack(padx=40, pady=20)

        # Etiqueta y entrada del nombre dentro del marco
        tk.Label(login_frame, text="Nombre del responsable:", font=("Arial", 13)).pack(pady=(0, 5))
        self.name_entry = tk.Entry(login_frame, font=("Arial", 12), bg="#A0A0A0", fg="black")
        self.name_entry.pack(pady=(0, 10))

        # Botón para iniciar turno dentro del marco
        tk.Button(login_frame,
            text="Iniciar Turno",
            font=("Arial", 12),
            bg="green",
            fg="white",
            activebackground="darkgreen",
            activeforeground="white", command=self.start_shift).pack()


    # ------------------------
    # Al iniciar turno
    # ------------------------
    def start_shift(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Atención", "Debes ingresar un nombre.")
            return

        self.cash_cut_id = open_cash_cut(name)
        self.user_name = name
        self.setup_main_screen()

        

    # ------------------------
    # Interfaz principal
    # ------------------------
    def setup_main_screen(self):
        self.clear_screen()

        # Contenedor principal
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True)

        # Menú lateral (todo el contenido irá aquí)
        left_frame = tk.Frame(container, width=350, bg="#f4f4f4")
        left_frame.pack(side="left", fill="y")

        # Espacio vacío a la derecha
        right_frame = tk.Frame(container, bg="#ffffff")
        self.show_tickets(right_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        # ------------------------
        # Contenido en left_frame
        # ------------------------

        tk.Label(left_frame, text="Estacionamiento AutoZone 24/7", font=("Arial", 18, "bold"), bg="#f4f4f4").pack(pady=(20, 10))

        # Administración
        title_frame = tk.LabelFrame(left_frame, text="Administración", padx=10, pady=10)
        title_frame.pack(padx=10, pady=10, fill="x")

        tk.Label(title_frame, text=f"Responsable: {self.user_name}", font=("Arial", 12, "bold")).pack()


        # Entrada
        self.entry_frame = tk.LabelFrame(left_frame, text="Entrada", padx=10, pady=10)
        self.entry_frame.pack(padx=10, pady=10, fill="x")

        self.create_ticket_btn = tk.Button(
            self.entry_frame,
            text="New Ticket",
            command=self.create_ticket_ui,
            bg="#d3d3d3",          # Gris claro
            font=("Arial", 12, "bold"),  # Fuente más grande y en negrita
            width=20,              # Ancho del botón (en caracteres aprox.)
            height=2               # Altura del botón (en líneas de texto)
        )
        self.create_ticket_btn.pack(pady=5)


        self.entry_info_label = tk.Label(self.entry_frame, text="", justify="left", font=("Arial", 10))
        self.entry_info_label.pack(pady=10)

        self.qr_label = tk.Label(self.entry_frame)
        self.qr_label.pack()

        # Salida
        self.exit_frame = tk.LabelFrame(left_frame, text="Salida", padx=50, pady=10)
        self.exit_frame.pack(padx=10, pady=10, fill="x")

        self.plate_entry = tk.Entry(self.exit_frame, width=20, font=("Arial", 12))
        self.plate_entry.pack(pady=5)

        self.search_ticket_btn = tk.Button(
            self.exit_frame,
            text="Cerrar Ticket",
            command=self.close_ticket_ui,
            bg="#d3d3d3",          # Gris claro
            font=("Arial", 12, "bold"),  # Fuente más grande y en negrita
            width=20,              # Ancho del botón (en caracteres aprox.)
            height=2            # Altura del botón (en líneas de texto)
            )
        self.search_ticket_btn.pack(pady=5)

        self.result_label = tk.Label(self.exit_frame, text="", justify="left", font=("Arial", 10))
        self.result_label.pack(pady=10)
        btn_cerrar_turno = tk.Button(
            left_frame,  # <- Aquí defines en qué parte del layout se mostrará
            text="Cierre de turno",
            command=self.cerrar_turno,
            bg="#ff4d4d",  # Un rojo claro para destacar
            fg="white",
            font=("Arial", 12, "bold"),
            width=20,
            height=2
        )
        btn_cerrar_turno.pack(pady=20)

        # Dentro de tu función que crea la pantalla principal o menú lateral

       



    # ------------------------
    # Crear Ticket (Entrada)
    # ------------------------
    def create_ticket_ui(self):
    # Paso 1: Crear ticket y obtener placa
        ticket_id, plate, entry_time = create_ticket(self.cash_cut_id)

        # Paso 2: Mostrar info en la interfaz
        self.entry_info_label.config(
            text=(
                f"Ticket ID: {ticket_id}\n"
                f"Placa: {plate}\n"
                f"Entrada: {entry_time}"
            )
        )

        # Paso 3: Generar QR a partir de la placa
        qr_path = generate_ticket_qr(plate)  # función para generar el QR
        qr_img = Image.open(qr_path)
        qr_img = qr_img.resize((100, 100))
        qr_img_tk = ImageTk.PhotoImage(qr_img)

        # Paso 4: Mostrar QR
        self.qr_label.config(image=qr_img_tk)
        self.qr_label.image = qr_img_tk

        if self.tickets_frame:
            self.show_tickets(self.tickets_frame)

        


    # ------------------------
    # Cerrar Ticket (Salida)
    # ------------------------
    def close_ticket_ui(self):
        plate = self.plate_entry.get().strip().upper()
        if not plate:
            self.result_label.config(text="Ingresa una placa.")
            return

        ticket = get_ticket_by_plate(plate)
        if not ticket:
            self.result_label.config(text="Ticket no encontrado.")
            return

        ticket_id, _, entry_time, exit_time, already_paid, _, hours, amount = ticket

        if already_paid == 1:
            time_format = self.format_hours(hours) if hours else "N/A"
            self.result_label.config(
                text=(
                    f"Ticket ya cerrado\n"
                    f"Entrada: {entry_time}\n"
                    f"Salida: {exit_time}\n"
                    f"Tiempo: {time_format}\n"
                    f"Total: ${amount:.2f}"
                )
            )
        else:
            result = close_ticket(ticket_id)
            if result:
                time_format = self.format_hours(result['hours_parked'])
                self.result_label.config(
                    text=(
                        f"Ticket cerrado\n"
                        f"Entrada: {entry_time}\n"
                        f"Salida: {result['exit_time']}\n"
                        f"Tiempo: {time_format}\n"
                        f"Total: ${result['amount_due']:.2f}"
                    )
                )
            else:
                self.result_label.config(text="Error al cerrar ticket.")
        if self.tickets_frame:
            self.show_tickets(self.tickets_frame)


    # ------------------------
    # Formato de horas
    # ------------------------
    def format_hours(self, hours):
        total_minutes = int(hours * 60)
        hh = total_minutes // 60
        mm = total_minutes % 60
        return f"{hh:02}:{mm:02}"

    # ------------------------
    # Limpiar ventana
    # ------------------------
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_tickets(self, parent_frame):
        self.tickets_frame = parent_frame  # <- Guarda el frame para poder actualizarlo luego

        import sqlite3
        from tkinter import ttk

        # Conectar a la base de datos
        conn = sqlite3.connect("parking.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, plate, entry_time, exit_time, paid
            FROM tickets
            WHERE cash_cut_id = ?
            ORDER BY id ASC
        """, (self.cash_cut_id,))
        tickets = cursor.fetchall()
        conn.close()

        # Limpiar contenido previo si existe
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Crear tabla (Treeview)
        columns = ("ID", "Placa", "Entrada", "Salida", "Pagado")
        tree = ttk.Treeview(parent_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        # Agregar datos a la tabla
        for row in tickets:
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True, padx=10, pady=10)


# ---------------------------
# Ejecutar aplicación
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1020x650")
    app = ParkingApp(root)
    root.mainloop()
