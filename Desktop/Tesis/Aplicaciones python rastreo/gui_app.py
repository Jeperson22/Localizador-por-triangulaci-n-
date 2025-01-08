import requests
import tkinter as tk

# URL del servidor Flask (ajusta según sea necesario)
BASE_URL = "http://localhost:5000"  # Cambia esto si estás usando un servidor remoto

# Escala para el rectángulo (ajusta según el tamaño de la ventana)
REAL_WIDTH = 20  # Ancho real del área (en metros)
REAL_HEIGHT = 7  # Altura real del área (en metros)
CANVAS_WIDTH = 400  # Ancho del canvas (en píxeles)
SCALE_FACTOR = CANVAS_WIDTH / REAL_WIDTH  # Escala para ajustar las dimensiones reales a píxeles
CANVAS_HEIGHT = int(REAL_HEIGHT * SCALE_FACTOR)  # Altura ajustada al canvas

# Coordenadas de los ESP32 (en metros)
ESP32_POSITIONS = {
    "cocina1": (19, 3),
    "patio": (13, 2),
    "cuartocelina": (9, 4),
    "puertacalle": (4, 6),
    "cuartonelson": (1, 0.5),
}

def rssi_to_distance(rssi, tx_power=-59):
    """
    Convierte un valor de RSSI en una distancia aproximada usando el modelo de pérdida de señal.
    """
    try:
        rssi = float(rssi)
        # Aplicando el modelo logarítmico de pérdida de señal
        return 10 ** ((tx_power - rssi) / (10 * 2))  # tx_power es el valor de la potencia de transmisión a 1 metro
    except ValueError:
        print(f"Error: RSSI no es un número válido: {rssi}")
        return None

def fetch_data():
    """
    Llama al endpoint /location para obtener los datos de los dispositivos ESP32 y Bluetooth.
    """
    try:
        response = requests.get(f"{BASE_URL}/location", timeout=5)  # Tiempo de espera de 5 segundos
        response.raise_for_status()  # Verifica si hubo un error en la respuesta
        data = response.json()
        print("Datos recibidos:", data)  # Depuración
        if data.get("status") == "success":
            return data.get("devices", [])
        else:
            print("Error del servidor:", data.get("message", "Desconocido"))
    except requests.exceptions.Timeout:
        print("Error: La solicitud al servidor se agotó.")
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
    return []

def triangulate_position(distances, esp32_positions):
    """
    Calcula la posición estimada de un dispositivo utilizando la triangulación.
    Por simplicidad, este ejemplo devuelve un punto promedio de las posiciones de los ESP32.
    """
    # Solo usamos los ESP32 correspondientes a las distancias
    valid_positions = [esp32_positions[esp32_id] for esp32_id in distances]
    
    if not valid_positions:
        return None, None
    
    # Obtener las coordenadas promedio
    avg_x = sum(x for x, y in valid_positions) / len(valid_positions)
    avg_y = sum(y for x, y in valid_positions) / len(valid_positions)
    
    return avg_x, avg_y

def move_point(marker, x, y):
    """
    Mueve un punto en el canvas a las coordenadas especificadas.
    """
    if marker:
        canvas_x = x * SCALE_FACTOR
        canvas_y = CANVAS_HEIGHT - (y * SCALE_FACTOR)
        canvas.coords(marker, canvas_x - 3, canvas_y - 3, canvas_x + 3, canvas_y + 3)

def remove_point(marker):
    """
    Elimina un punto del canvas si existe.
    """
    if marker:
        canvas.delete(marker)

def update_data():
    """
    Actualiza la información de los dispositivos mostrada en la ventana.
    """
    devices = fetch_data()

    # Si no se recibieron datos, muestra un mensaje de error
    if not devices:
        device_info_label.config(text="Error: No se recibieron datos.")
        return

    # Diccionarios para almacenar las distancias de Celina y Higinio
    celina_distances = {}
    higinio_distances = {}

    # Almacenar los puntos a eliminar en caso de no recibir datos
    celina_marker_to_remove = None
    higinio_marker_to_remove = None

    # Cadena para mostrar los datos recibidos
    data_display = "Datos recibidos:\n"

    for device in devices:
        esp32_id = device.get('esp32_id')
        celina_rssi = device.get('Celina', "No data")
        higinio_rssi = device.get('Higinio', "No data")

        # Agregar información de Celina y Higinio a la cadena de datos
        data_display += f"\nDispositivo {esp32_id}:\n"
        data_display += f"  - Celina RSSI: {celina_rssi}\n"
        data_display += f"  - Higinio RSSI: {higinio_rssi}\n"

        # Solo agregar distancias válidas
        if celina_rssi != "No data":
            distance = rssi_to_distance(celina_rssi)
            if distance is not None:
                celina_distances[esp32_id] = distance

        if higinio_rssi != "No data":
            distance = rssi_to_distance(higinio_rssi)
            if distance is not None:
                higinio_distances[esp32_id] = distance

    # Actualizar la etiqueta con los datos recibidos
    device_info_label.config(text=data_display)
    
    # Calcular la posición de Celina si hay distancias válidas
    if celina_distances:
        celina_x, celina_y = triangulate_position(celina_distances, ESP32_POSITIONS)
        if celina_x is not None and celina_y is not None:
            move_point(celina_marker, celina_x, celina_y)
        else:
            remove_point(celina_marker)
    else:
        remove_point(celina_marker)

    # Calcular la posición de Higinio si hay distancias válidas
    if higinio_distances:
        higinio_x, higinio_y = triangulate_position(higinio_distances, ESP32_POSITIONS)
        if higinio_x is not None and higinio_y is not None:
            move_point(higinio_marker, higinio_x, higinio_y)
        else:
            remove_point(higinio_marker)
    else:
        remove_point(higinio_marker)

    # Actualizar cada 5 segundos
    root.after(5000, update_data)

# Configurar la interfaz gráfica de Tkinter
root = tk.Tk()
root.title("Datos de Dispositivos ESP32")
root.geometry(f"{CANVAS_WIDTH + 20}x{CANVAS_HEIGHT + 200}")  # Ajustar tamaño de la ventana

# Canvas para mostrar el rectángulo que representa el área
canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
canvas.pack(pady=10)

# Dibujar el rectángulo que representa el área
canvas.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, outline="black", width=2)

# Dibujar los puntos de los ESP32
for name, (x, y) in ESP32_POSITIONS.items():
    canvas_x = x * SCALE_FACTOR
    canvas_y = CANVAS_HEIGHT - (y * SCALE_FACTOR)
    canvas.create_oval(
        canvas_x - 3, canvas_y - 3, canvas_x + 3, canvas_y + 3,
        fill="black", outline="black"
    )
    canvas.create_text(canvas_x + 10, canvas_y, text=name, anchor="w", font=("Arial", 8))

# Crear marcadores para Celina y Higinio
celina_marker = canvas.create_oval(0, 0, 0, 0, fill="pink", outline="pink")
higinio_marker = canvas.create_oval(0, 0, 0, 0, fill="blue", outline="blue")

# Etiqueta para mostrar los datos de los dispositivos
device_info_label = tk.Label(
    root, text="Cargando datos...", font=("Arial", 12), justify="left", anchor="nw"
)
device_info_label.pack(fill="both", expand=True, padx=10, pady=10)

# Iniciar la actualización de los datos
update_data()

# Iniciar el loop de la ventana
root.mainloop()
