import tkinter as tk
import requests
from tkinter import messagebox

# Dirección del servidor Flask en Render
server_url = "https://localizador-por-triangulaci-n.onrender.com/location"

# Variable global para rastrear el último dispositivo detectado
ultimo_dispositivo = {"Celina": None, "Higinio": None}
ultimo_tiempo = {"Celina": 0, "Higinio": 0}

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

    # Variables para mantener el RSSI más alto en cada categoría
    celina_cerca = -float('inf')
    celina_lejos = -float('inf')
    higinio_cerca = -float('inf')
    higinio_lejos = -float('inf')

    celina_cerca_id = None
    celina_lejos_id = None
    higinio_cerca_id = None
    higinio_lejos_id = None

    for device in devices:
        esp32_id = device["esp32_id"]
        celina_rssi = device["Celina"]
        higinio_rssi = device["Higinio"]

        # Evaluar proximidad para Celina
        if determinar_proximidad(celina_rssi) == "Cerca":
            if celina_rssi > celina_cerca:
                celina_cerca = celina_rssi
                celina_cerca_id = esp32_id
        elif determinar_proximidad(celina_rssi) == "Lejos":
            if celina_rssi > celina_lejos:
                celina_lejos = celina_rssi
                celina_lejos_id = esp32_id

        # Evaluar proximidad para Higinio
        if determinar_proximidad(higinio_rssi) == "Cerca":
            if higinio_rssi > higinio_cerca:
                higinio_cerca = higinio_rssi
                higinio_cerca_id = esp32_id
        elif determinar_proximidad(higinio_rssi) == "Lejos":
            if higinio_rssi > higinio_lejos:
                higinio_lejos = higinio_rssi
                higinio_lejos_id = esp32_id

    # Decidir ubicación basándose en la lógica establecida
    ubicaciones["Celina"] = celina_cerca_id if celina_cerca_id else celina_lejos_id
    ubicaciones["Higinio"] = higinio_cerca_id if higinio_cerca_id else higinio_lejos_id

    return ubicaciones

# Función para obtener los datos del servidor
def obtener_datos():
    global ultimo_dispositivo, ultimo_tiempo
    try:
        response = requests.get(server_url)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                ubicaciones = determinar_ubicacion(data["devices"])
                mostrar_datos(data["devices"], data["person_detected"], ubicaciones)

                # Actualizar el último dispositivo detectado y su tiempo
                for persona in ["Celina", "Higinio"]:
                    if ubicaciones[persona] != "Desconocida":
                        ultimo_dispositivo[persona] = ubicaciones[persona]
                        ultimo_tiempo[persona] = 0  # Reiniciar el tiempo si se detecta
                    else:
                        ultimo_tiempo[persona] += 10  # Incrementar el tiempo si no se detecta

                    # Verificar si han salido de casa
                    if ultimo_tiempo[persona] >= 10 and ultimo_dispositivo[persona] == "cuartonelson":
                        ubicaciones[persona] = "Salió de casa"

                    # Verificar si están en el patio trasero
                    elif ultimo_tiempo[persona] >= 10 and ultimo_dispositivo[persona] == "cocina1":
                        ubicaciones[persona] = "Patio trasero"

            else:
                messagebox.showerror("Error", "No se pudieron obtener los datos.")
        else:
            messagebox.showerror("Error", f"Error al conectar al servidor: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

# Función para mostrar los datos en la interfaz
def mostrar_datos(devices, person_detected, ubicaciones):
    # Limpiar las tres secciones
    for widget in frame_esp32.winfo_children():
        widget.destroy()
    for widget in frame_camera.winfo_children():
        widget.destroy()
    for widget in frame_location.winfo_children():
        widget.destroy()

    # Mostrar datos de los ESP32
    for device in devices:
        esp32_id = device["esp32_id"]
        celina_rssi = device["Celina"]
        higinio_rssi = device["Higinio"]
        last_update = round(device["last_update_seconds"], 2)

        celina_proximidad = determinar_proximidad(celina_rssi)
        higinio_proximidad = determinar_proximidad(higinio_rssi)

        label = tk.Label(frame_esp32, text=f"Dispositivo: {esp32_id} | "
                                           f"Celina RSSI: {celina_rssi} ({celina_proximidad}) | "
                                           f"Higinio RSSI: {higinio_rssi} ({higinio_proximidad}) | "
                                           f"Última actualización: {last_update}s")
        label.pack(padx=5, pady=2)

    # Mostrar estado de detección de personas
    if person_detected:
        mensaje_personas = "Persona detectada"
        if (ubicaciones["Celina"] in ["cuartocelina", "puertacalle"] and
            ubicaciones["Higinio"] in ["cuartocelina", "puertacalle"]):
            mensaje_personas = "La persona detectada es Celina y Higinio"
        elif ubicaciones["Celina"] in ["cuartocelina", "puertacalle"]:
            mensaje_personas = "La persona detectada es Celina"
        elif ubicaciones["Higinio"] in ["cuartocelina", "puertacalle"]:
            mensaje_personas = "La persona detectada es Higinio"

        person_label = tk.Label(frame_camera, text=mensaje_personas, fg="green", font=("Arial", 14, "bold"))
    else:
        person_label = tk.Label(frame_camera, text="No se detecta persona", fg="red", font=("Arial", 14, "bold"))
    person_label.pack(padx=5, pady=10)

    # Mostrar ubicación de Celina y Higinio
    label_celina = tk.Label(frame_location, text=f"Celina se encuentra en: {ubicaciones['Celina']}")
    label_celina.pack(padx=5, pady=5)

    label_higinio = tk.Label(frame_location, text=f"Higinio se encuentra en: {ubicaciones['Higinio']}")
    label_higinio.pack(padx=5, pady=5)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Datos de Dispositivos y Detección")

# Crear frames para las tres secciones
frame_esp32 = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_esp32.pack(fill="x", padx=10, pady=5)
frame_esp32_title = tk.Label(frame_esp32, text="Datos de ESP32", font=("Arial", 12, "bold"))
frame_esp32_title.pack()

frame_camera = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_camera.pack(fill="x", padx=10, pady=5)
frame_camera_title = tk.Label(frame_camera, text="Detección de Personas", font=("Arial", 12, "bold"))
frame_camera_title.pack()

frame_location = tk.Frame(ventana, bd=2, relief="groove", padx=10, pady=10)
frame_location.pack(fill="x", padx=10, pady=5)
frame_location_title = tk.Label(frame_location, text="Ubicación de Celina y Higinio", font=("Arial", 12, "bold"))
frame_location_title.pack()

# Actualizar datos automáticamente
def actualizar_datos_periodicamente():
    obtener_datos()
    ventana.after(10000, actualizar_datos_periodicamente)

actualizar_datos_periodicamente()
ventana.mainloop()
