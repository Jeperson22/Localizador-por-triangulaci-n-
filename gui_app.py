import tkinter as tk
from threading import Thread
import requests
import time

server_url = "https://localizador-por-triangulaci-n.onrender.com/data"

def fetch_data():
    while True:
        try:
            response = requests.get(server_url)
            if response.status_code == 200:
                data = response.json()
                update_label(data['ssid1'], data['rssi1'], data['ssid2'], data['rssi2'], data['ssid3'], data['rssi3'], data['x'], data['y'], data['area'])
            else:
                print("Error al obtener los datos: ", response.status_code)
        except Exception as e:
            print("Error de conexión: ", e)
        time.sleep(5)

def update_label(ssid1, rssi1, ssid2, rssi2, ssid3, rssi3, x, y, area):
    label.config(text=f"SSID1: {ssid1}, RSSI1: {rssi1}\n"
                      f"SSID2: {ssid2}, RSSI2: {rssi2}\n"
                      f"SSID3: {ssid3}, RSSI3: {rssi3}\n"
                      f"Position: ({x}, {y})\n"
                      f"Area: {area}")

root = tk.Tk()
root.title("RSSI Triangulation Data")

label = tk.Label(root, text="Esperando datos...", font=("Helvetica", 16))
label.pack(pady=20, padx=20)

# Iniciar el hilo de actualización de la etiqueta
fetch_thread = Thread(target=fetch_data)
fetch_thread.daemon = True
fetch_thread.start()

root.mainloop()
