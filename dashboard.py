import tkinter as tk
import sqlite3
from datetime import datetime

def mostrar_dashboard(cash_cut_id, user_name, on_close_callback):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("parking.db")
    cursor = conn.cursor()

    # Actualizar la hora de cierre
    cursor.execute("""
        UPDATE cash_cuts
        SET closing_time = ?
        WHERE id = ?
    """, (now, cash_cut_id))
    conn.commit()

    # Obtener opening_time y closing_time actualizados
    cursor.execute("""
        SELECT opening_time, closing_time FROM cash_cuts WHERE id = ?
    """, (cash_cut_id,))
    row = cursor.fetchone()
    opening_time, closing_time = row

    # Calcular duración en horas
    fmt = "%Y-%m-%d %H:%M:%S"
    start_dt = datetime.strptime(opening_time, fmt)
    end_dt = datetime.strptime(closing_time, fmt)
    duration_hours = (end_dt - start_dt).total_seconds() / 3600

    # Consultar tickets generados durante el turno
    cursor.execute("""
        SELECT COUNT(*) FROM tickets
        WHERE entry_time BETWEEN ? AND ?
    """, (opening_time, closing_time))
    total_generados = cursor.fetchone()[0]

    # Consultar tickets cerrados durante el turno
    cursor.execute("""
        SELECT COUNT(*) FROM tickets
        WHERE exit_time BETWEEN ? AND ?
    """, (opening_time, closing_time))
    total_cerrados = cursor.fetchone()[0]

    # Consultar total recaudado en efectivo durante el turno
    cursor.execute("""
        SELECT SUM(amount_due) FROM tickets
        WHERE exit_time BETWEEN ? AND ? AND paid = 1
    """, (opening_time, closing_time))
    total_efectivo = cursor.fetchone()[0] or 0.0

    conn.close()

    # Crear ventana del dashboard
    ventana = tk.Toplevel()
    ventana.title("Dashboard del Turno")
    ventana.geometry("1020x650")

    # Mostrar todos los datos
    info_text = (
        f"Responsable: {user_name}\n"
        f"Hora de inicio: {opening_time}\n"
        f"Hora de cierre: {closing_time}\n"
        f"Duración total (horas): {duration_hours:.2f}\n\n"
        f"Total de tickets generados: {total_generados}\n"
        f"Total de tickets cerrados: {total_cerrados}\n"
        f"Total recaudado en efectivo: ${total_efectivo:.2f}"
    )

    label = tk.Label(ventana, text=info_text, font=("Arial", 14), justify="left")
    label.pack(padx=30, pady=50, anchor="w")

    # Función para cerrar el dashboard y volver al login
    def cerrar_dashboard():
        from report_generator import generar_pdf_dashboard
        ventana.destroy()
        on_close_callback()

    btn_cerrar = tk.Button(
        ventana,
        text="Cerrar Dashboard y volver al inicio",
        command=cerrar_dashboard,
        bg="red",
        fg="white",
        font=("Arial", 12)
    )
    btn_cerrar.pack(pady=20)

    ventana.protocol("WM_DELETE_WINDOW", cerrar_dashboard)
