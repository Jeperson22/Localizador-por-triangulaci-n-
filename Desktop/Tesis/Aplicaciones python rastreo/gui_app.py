import tkinter as tk
from threading import Thread
import requests
import time

# URL del servidor Flask
server_url = "http://127.0.0.1:5000"

# Diccionario global para mantener el estado de las ESP32
esp32_status = {}

def fetch_status():
    """Función que obtiene el estado de las ESP32 desde el servidor Flask."""
    while True:
        try:
            # Realizar la solicitud GET para obtener el estado de todos los dispositivos
            response = requests.get(f"{server_url}/status")
            if response.status_code == 200:
                new_status = response.json()
                # Solo actualizamos si el estado ha cambiado
                if new_status != esp32_status:
                    esp32_status.update(new_status)
                    # Actualizamos la interfaz gráfica en el hilo principal
                    root.after(0, update_display)
            else:
                print(f"Error al obtener el estado: {response.status_code}")
        except Exception as e:
            print(f"Error de conexión: {e}")
        time.sleep(5)  # Pausa de 5 segundos entre cada intento

def update_display():
    """Función para actualizar la interfaz gráfica con el estado de las ESP32."""
    # Convertimos el diccionario en texto para mostrarlo
    status_text = "\n".join([f"{device}: {status}" for device, status in esp32_status.items()])
    label.config(text=status_text)

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Estado de Conexión de ESP32")

label = tk.Label(root, text="Obteniendo estado...", font=("Helvetica", 16), justify="left")
label.pack(pady=20, padx=20)

# Iniciar el hilo para obtener el estado de las ESP32
fetch_thread = Thread(target=fetch_status)
fetch_thread.daemon = True
fetch_thread.start()

root.mainloop()
