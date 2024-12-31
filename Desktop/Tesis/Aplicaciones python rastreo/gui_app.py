import requests
import time
import tkinter as tk
from tkinter import scrolledtext

# URL del servidor Flask (ajusta según sea necesario)
BASE_URL = "https://localizador-por-triangulaci-n.onrender.com"

def get_status():
    try:
        # Hacer una solicitud GET al endpoint /status
        response = requests.get(f"{BASE_URL}/status")
        response.raise_for_status()  # Lanza un error si la respuesta tiene un código de estado no exitoso
        
        # Imprimir los datos recibidos
        data = response.json()
        
        # Separar dispositivos conectados y desconectados
        connected_devices = {k: v for k, v in data.items() if v["status"] == "Connected"}
        disconnected_devices = {k: v for k, v in data.items() if v["status"] == "Disconnected"}

        # Limpiar la caja de texto
        text_box.delete(1.0, tk.END)

        text_box.insert(tk.END, "==== Estado de las ESP32 ====\n")
        
        # Mostrar dispositivos conectados
        if connected_devices:
            text_box.insert(tk.END, "Dispositivos Conectados:\n")
            for device, info in connected_devices.items():
                bluetooth_data = info.get("bluetooth_data", {})
                celina_rssi = bluetooth_data.get("Celina", "No disponible")
                higinio_rssi = bluetooth_data.get("Higinio", "No disponible")
                text_box.insert(tk.END, f"  Dispositivo: {device}\n")
                text_box.insert(tk.END, f"    Estado: {info['status']}\n")
                text_box.insert(tk.END, f"    Celina RSSI: {celina_rssi}\n")
                text_box.insert(tk.END, f"    Higinio RSSI: {higinio_rssi}\n")
        else:
            text_box.insert(tk.END, "  No hay dispositivos conectados.\n")

        # Mostrar dispositivos desconectados
        if disconnected_devices:
            text_box.insert(tk.END, "\nDispositivos Desconectados:\n")
            for device, info in disconnected_devices.items():
                text_box.insert(tk.END, f"  Dispositivo: {device}\n")
                text_box.insert(tk.END, f"    Estado: {info['status']}\n")
        else:
            text_box.insert(tk.END, "\n  No hay dispositivos desconectados.\n")

        text_box.insert(tk.END, "=" * 30 + "\n")  # Separador para la salida
    
    except requests.exceptions.RequestException as e:
        text_box.insert(tk.END, f"Error al conectarse al servidor: {e}\n")
    except ValueError:
        text_box.insert(tk.END, "Error al procesar la respuesta del servidor\n")

    # Llamar a la función cada 5 segundos
    root.after(5000, get_status)

# Configurar la interfaz gráfica de Tkinter
root = tk.Tk()
root.title("Monitoreo de ESP32")
root.geometry("500x400")  # Tamaño de la ventana

# Caja de texto para mostrar los resultados
text_box = scrolledtext.ScrolledText(root, width=60, height=20)
text_box.pack(padx=10, pady=10)

# Llamar la función inicial para cargar los datos
get_status()

# Iniciar el loop de la ventana
root.mainloop()
