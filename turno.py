# turno.py
import tkinter as tk
from tkinter import messagebox

def mostrar_cierre_turno(on_confirm, on_cancel):
    ventana = tk.Toplevel()
    ventana.title("Cierre de turno")
    ventana.geometry("400x150")
    ventana.resizable(False, False)

    label = tk.Label(ventana, text="¿Estás seguro que quieres terminar el turno?", font=("Arial", 13, "bold"))
    label.pack(pady=20)

    button_frame = tk.Frame(ventana)
    button_frame.pack(pady=10)

    def confirmar():
        on_confirm()
        ventana.destroy()

    def cancelar():
        on_cancel()
        ventana.destroy()

    btn_confirmar = tk.Button(button_frame, text="Sí, terminar", bg="#d3d3d3", font=("Arial", 12, "bold"), width=12, command=confirmar)
    btn_confirmar.pack(side="left", padx=10)

    btn_cancelar = tk.Button(button_frame, text="Cancelar", bg="#d3d3d3", font=("Arial", 12, "bold"), width=12, command=cancelar)
    btn_cancelar.pack(side="left", padx=10)
