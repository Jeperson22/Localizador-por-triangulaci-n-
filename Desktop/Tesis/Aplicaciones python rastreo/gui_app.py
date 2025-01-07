import requests
import tkinter as tk

# URL del servidor Flask (ajusta según sea necesario)
BASE_URL = "https://localizador-por-triangulaci-n.onrender.com"

def fetch_data():
    """
    Llama al endpoint /location para obtener los datos de los dispositivos ESP32 y las ubicaciones estimadas.
    """
    try:
        response = requests.get(f"{BASE_URL}/location")
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            devices = data.get("devices", [])
            locations = data.get("locations", {})  # Nueva clave que contiene posiciones de Celina y Higinio
            return devices, locations
        else:
            print("Error del servidor: ", data.get("message", "Desconocido"))
            return [], {}
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error de conexión: {req_err}")
    except ValueError as val_err:
        print(f"Error al analizar la respuesta JSON: {val_err}")
    return [], {}

def update_data():
    """
    Actualiza la información de los dispositivos mostrada en la ventana.
    """
    devices, locations = fetch_data()
    if devices:
        # Crear texto con la información de los dispositivos
        device_info_text = "\n".join(
            [
                f"ESP32: {device['esp32_id']}\n"
                f"  - Celina RSSI: {device.get('Celina', 'No data')}\n"
                f"  - Higinio RSSI: {device.get('Higinio', 'No data')}"
                for device in devices
            ]
        )

        # Agregar la ubicación estimada de Celina y Higinio
        celina_location = locations.get("Celina", {"x": "unknown", "y": "unknown"})
        higinio_location = locations.get("Higinio", {"x": "unknown", "y": "unknown"})

        location_text = (
            f"\nUbicación estimada:\n"
            f"  - Celina: X={celina_location['x']}, Y={celina_location['y']}\n"
            f"  - Higinio: X={higinio_location['x']}, Y={higinio_location['y']}"
        )

        device_info_label.config(text=device_info_text + location_text)
    else:
        device_info_label.config(text="Error al obtener datos de los dispositivos.")
    
    # Llamar nuevamente a esta función después de 5 segundos
    root.after(5000, update_data)

# Configurar la interfaz gráfica de Tkinter
root = tk.Tk()
root.title("Datos de Dispositivos Bluetooth y ESP32")
root.geometry("500x500")  # Ajustar el tamaño de la ventana

# Etiqueta para mostrar los datos de los dispositivos
device_info_label = tk.Label(
    root, text="Cargando datos...", font=("Arial", 12), justify="left", anchor="nw"
)
device_info_label.pack(fill="both", expand=True, padx=10, pady=10)

# Iniciar la actualización de los datos
update_data()

# Iniciar el loop de la ventana
root.mainloop()
