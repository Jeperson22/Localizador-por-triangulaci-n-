import tkinter as tk
import requests
from tkinter import messagebox
import json

# Dirección del servidor Flask en Render
server_url = "https://localizador-por-triangulaci-n.onrender.com/location"

# Función para determinar la proximidad según el RSSI
def determinar_proximidad(rssi):
    if rssi == 0:
        return "No data"
    elif rssi >= -77:
        return "Cerca"
    else:
        return "Lejos"

# Función para determinar la ubicación más probable
def determinar_ubicacion(devices):
    ubicaciones = {"Celina": "Desconocida", "Higinio": "Desconocida"}
    proximidad_celina = -float('inf')  # El valor más bajo posible
    proximidad_higinio = -float('inf')

    for device in devices:
        esp32_id = device["esp32_id"]
        celina_rssi = device["Celina"]
        higinio_rssi = device["Higinio"]

        # Evaluar proximidad para Celina
        if determinar_proximidad(celina_rssi) == "Cerca" and celina_rssi > proximidad_celina:
            ubicaciones["Celina"] = esp32_id
            proximidad_celina = celina_rssi

        # Evaluar proximidad para Higinio
        if determinar_proximidad(higinio_rssi) == "Cerca" and higinio_rssi > proximidad_higinio:
            ubicaciones["Higinio"] = esp32_id
            proximidad_higinio = higinio_rssi

    return ubicaciones

# Función para obtener los datos del servidor
def obtener_datos():
    try:
        # Hacer una solicitud GET al servidor Flask
        response = requests.get(server_url)
        # Verificar si la respuesta es exitosa
        if response.status_code == 200:
            # Parsear la respuesta JSON
            data = response.json()
            if data["status"] == "success":
                ubicaciones = determinar_ubicacion(data["devices"])
                mostrar_datos(data["devices"], ubicaciones)
            else:
                messagebox.showerror("Error", "No se pudieron obtener los datos.")
        else:
            messagebox.showerror("Error", f"Error al conectar al servidor: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# Función para mostrar los datos en la interfaz
def mostrar_datos(devices, ubicaciones):
    # Limpiar la ventana de datos anteriores
    for widget in frame_datos.winfo_children():
        widget.destroy()

    # Mostrar los datos en la interfaz
    for device in devices:
        esp32_id = device["esp32_id"]
        celina_rssi = device["Celina"]
        higinio_rssi = device["Higinio"]
        last_update = round(device["last_update_seconds"], 2)

        # Determinar la proximidad de Celina y Higinio
        celina_proximidad = determinar_proximidad(celina_rssi)
        higinio_proximidad = determinar_proximidad(higinio_rssi)

        # Crear etiquetas para mostrar los datos
        label = tk.Label(frame_datos, text=f"Dispositivo: {esp32_id} | "
                                          f"Celina RSSI: {celina_rssi} ({celina_proximidad}) | "
                                          f"Higinio RSSI: {higinio_rssi} ({higinio_proximidad}) | "
                                          f"Última actualización: {last_update}s")
        label.pack(padx=5, pady=5)

    # Mostrar las ubicaciones determinadas
    label_celina = tk.Label(frame_datos, text=f"Celina se encuentra en: {ubicaciones['Celina']}")
    label_celina.pack(padx=5, pady=5)

    label_higinio = tk.Label(frame_datos, text=f"Higinio se encuentra en: {ubicaciones['Higinio']}")
    label_higinio.pack(padx=5, pady=5)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Datos de los Dispositivos ESP32")

# Crear un frame para contener los datos
frame_datos = tk.Frame(ventana)
frame_datos.pack(padx=10, pady=10)

# Función para actualizar los datos automáticamente
def actualizar_datos_periodicamente():
    obtener_datos()
    # Configuramos el intervalo de actualización (por ejemplo, cada 10 segundos)
    ventana.after(10000, actualizar_datos_periodicamente)

# Iniciar la actualización automática de datos
actualizar_datos_periodicamente()

# Iniciar la ventana
ventana.mainloop()
