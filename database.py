import sqlite3
from datetime import datetime
import random
import string

# ⚙️ Inicializa la base de datos, crea las tablas necesarias
def init_db():
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # Crear tabla de cortes de caja
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cash_cuts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            opening_time TEXT NOT NULL,
            closing_time TEXT
        )
    ''')

    # Crear tabla de tickets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT UNIQUE,
            entry_time TEXT,
            exit_time TEXT,
            paid INTEGER DEFAULT 0,
            cash_cut_id INTEGER,
            hours_parked REAL,
            amount_due REAL,
            FOREIGN KEY (cash_cut_id) REFERENCES cash_cuts(id)
        )
    ''')

    conn.commit()
    conn.close()

# 🔐 Asegura que las columnas nuevas existan (solo necesario si la tabla ya existía)
def alter_tickets_table():
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE tickets ADD COLUMN hours_parked REAL")
    except sqlite3.OperationalError:
        pass  # Ya existe

    try:
        cursor.execute("ALTER TABLE tickets ADD COLUMN amount_due REAL")
    except sqlite3.OperationalError:
        pass  # Ya existe

    conn.commit()
    conn.close()

# Llama a la inicialización completa
init_db()
alter_tickets_table()

# 🔐 Genera una placa aleatoria (código)
def generate_random_plate(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# 🧾 Crea un nuevo ticket con cash_cut_id (opcional)
def create_ticket(cash_cut_id=None):
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()
    entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    random_plate = generate_random_plate()
    cursor.execute(
        "INSERT INTO tickets (plate, entry_time, cash_cut_id) VALUES (?, ?, ?)",
        (random_plate, entry_time, cash_cut_id)
    )
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id, random_plate, entry_time

# 🔍 Obtiene un ticket por ID
def get_ticket(ticket_id):
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    return ticket

# 🔍 Busca un ticket por placa
def get_ticket_by_plate(plate):
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE plate = ?", (plate,))
    ticket = cursor.fetchone()
    conn.close()
    return ticket

# ✅ Cierra un ticket, calcula horas y monto
def close_ticket(ticket_id, hourly_rate=20.0):
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # Obtener la hora de entrada
    cursor.execute("SELECT entry_time FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None  # No se encontró el ticket

    entry_time = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
    exit_time = datetime.now()
    duration = (exit_time - entry_time).total_seconds() / 3600
    duration_rounded = round(duration, 2)
    total_to_pay = round(duration_rounded * hourly_rate, 2)

    cursor.execute('''
        UPDATE tickets
        SET exit_time = ?, paid = 1, hours_parked = ?, amount_due = ?
        WHERE id = ?
    ''', (
        exit_time.strftime("%Y-%m-%d %H:%M:%S"),
        duration_rounded,
        total_to_pay,
        ticket_id
    ))

    conn.commit()
    conn.close()

    return {
        "exit_time": exit_time.strftime("%Y-%m-%d %H:%M:%S"),
        "hours_parked": duration_rounded,
        "amount_due": total_to_pay
    }
