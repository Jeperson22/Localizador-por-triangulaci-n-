import tkinter as tk
from tkinter import ttk
import requests

# URL del servidor en la nube
server_url = "https://localizador-por-triangulaci-n.onrender.com/data"

def fetch_data():
    try:
        response = requests.post(server_url, data={})
        response.raise_for_status()
        data = response.json()
        
        ssid1 = data.get('ssid1', 'N/A')
        rssi1 = data.get('rssi1', 'N/A')
        ssid2 = data.get('ssid2', 'N/A')
        rssi2 = data.get('rssi2', 'N/A')
        ssid3 = data.get('ssid3', 'N/A')
        rssi3 = data.get('rssi3', 'N/A')

        ssid1_var.set(f"SSID1: {ssid1} RSSI1: {rssi1}")
        ssid2_var.set(f"SSID2: {ssid2} RSSI2: {rssi2}")
        ssid3_var.set(f"SSID3: {ssid3} RSSI3: {rssi3}")
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        ssid1_var.set("Error fetching data")
        ssid2_var.set("")
        ssid3_var.set("")

# Crear la ventana principal
root = tk.Tk()
root.title("Datos de Triangulación RSSI")
root.geometry("400x300")

# Variables para mostrar los datos
ssid1_var = tk.StringVar()
ssid2_var = tk.StringVar()
ssid3_var = tk.StringVar()

# Crear etiquetas para mostrar los datos
ssid1_label = ttk.Label(root, textvariable=ssid1_var)
ssid1_label.pack(pady=10)

ssid2_label = ttk.Label(root, textvariable=ssid2_var)
ssid2_label.pack(pady=10)

ssid3_label = ttk.Label(root, textvariable=ssid3_var)
ssid3_label.pack(pady=10)

# Botón para actualizar los datos
update_button = ttk.Button(root, text="Actualizar Datos", command=fetch_data)
update_button.pack(pady=20)

# Llamar a fetch_data al inicio para cargar los datos iniciales
fetch_data()

# Ejecutar la aplicación tkinter
root.mainloop()
