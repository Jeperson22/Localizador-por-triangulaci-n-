from flask import Flask, request, jsonify
import time
from threading import Thread
import math

app = Flask(__name__)

# Estado de conexión de las ESP32 con su último timestamp y datos adicionales
esp32_status = {}

# Tiempo límite en segundos para marcar un dispositivo como "Desconectado"
TIMEOUT = 10

# Coordenadas conocidas de los ESP32 (Ejemplo: X, Y)
esp32_coordinates = {
    "ESP32_1": (0, 0),
    "ESP32_2": (10, 0),
    "ESP32_3": (5, 10),
}

def rssi_to_distance(rssi):
    """
    Convierte RSSI a distancia en metros usando un modelo simplificado.
    Pérdida de trayectoria (path loss) simplificada.
    """
    try:
        tx_power = -59  # Potencia de transmisión (RSSI a 1 metro)
        n = 2  # Factor ambiental típico para interiores
        rssi = int(rssi)
        return 10 ** ((tx_power - rssi) / (10 * n))
    except ValueError:
        return float('inf')  # Devuelve distancia infinita si RSSI no es válido

def triangulate(devices_data):
    """
    Calcula la ubicación estimada con datos de al menos 3 dispositivos.
    devices_data: Diccionario con coordenadas (X, Y) y distancia.
    """
    try:
        if len(devices_data) < 3:
            return None  # Se necesita al menos 3 dispositivos

        x1, y1, d1 = devices_data[0]
        x2, y2, d2 = devices_data[1]
        x3, y3, d3 = devices_data[2]

        # Triangulación utilizando ecuaciones de intersección de círculos
        A = 2 * (x2 - x1)
        B = 2 * (y2 - y1)
        C = d1**2 - d2**2 - x1**2 + x2**2 - y1**2 + y2**2
        D = 2 * (x3 - x2)
        E = 2 * (y3 - y2)
        F = d2**2 - d3**2 - x2**2 + x3**2 - y2**2 + y3**2

        x = (C * E - F * B) / (E * A - B * D)
        y = (C * D - A * F) / (B * D - A * E)

        return round(x, 2), round(y, 2)
    except ZeroDivisionError:
        return None

def monitor_devices():
    """Hilo que actualiza el estado de los dispositivos según el tiempo transcurrido."""
    while True:
        current_time = time.time()
        to_disconnect = []

        # Verificar el estado de cada dispositivo
        for device, info in esp32_status.items():
            last_seen = info.get("last_seen", 0)
            if current_time - last_seen > TIMEOUT:
                to_disconnect.append(device)

        # Actualizar estado de dispositivos desconectados
        for device in to_disconnect:
            esp32_status[device]["status"] = "Disconnected"

        time.sleep(1)  # Verificar cada segundo

@app.route('/data', methods=['POST'])
def handle_data():
    """
    Endpoint para recibir datos desde las ESP32.
    """
    try:
        device_name = request.form.get('esp32_id')
        celina_rssi = request.form.get('Celina', "No data")
        higinio_rssi = request.form.get('Higinio', "No data")

        if not device_name:
            return jsonify({'status': 'error', 'message': 'Identificador de dispositivo no proporcionado'}), 400

        esp32_status[device_name] = {
            "status": "Connected",
            "last_seen": time.time(),
            "bluetooth_data": {
                "Celina": celina_rssi,
                "Higinio": higinio_rssi
            }
        }

        return jsonify({'status': 'success', 'message': f'Datos actualizados para {device_name}'}), 200

    except Exception as e:
        print(f"Error en /data: {e}")
        return jsonify({'status': 'error', 'message': 'Error interno del servidor'}), 500

@app.route('/location', methods=['GET'])
def get_location():
    """
    Endpoint para calcular la ubicación estimada basado en triangulación.
    """
    try:
        # Seleccionar los 3 dispositivos con mejor señal
        active_devices = [
            (device, info)
            for device, info in esp32_status.items()
            if info["status"] == "Connected"
        ]
        active_devices.sort(
            key=lambda x: min(
                int(x[1]["bluetooth_data"].get("Celina", -999)),
                int(x[1]["bluetooth_data"].get("Higinio", -999)),
            ),
            reverse=True,
        )

        if len(active_devices) < 3:
            print("Error: Menos de 3 dispositivos conectados")
            return jsonify({'status': 'error', 'message': 'Se necesitan al menos 3 dispositivos activos'}), 400

        # Extraer coordenadas y distancia
        devices_data = []
        for device, info in active_devices[:3]:
            coord = esp32_coordinates.get(device)
            rssi = info["bluetooth_data"].get("Celina", -999)
            if coord and rssi != -999:
                distance = rssi_to_distance(rssi)
                devices_data.append((*coord, distance))

        print(f"Datos para triangulación: {devices_data}")
        location = triangulate(devices_data)

        if location:
            return jsonify({'status': 'success', 'location': {'x': location[0], 'y': location[1]}}), 200
        else:
            print("Error: Triangulación fallida")
            return jsonify({'status': 'error', 'message': 'No se pudo calcular la ubicación'}), 400

    except Exception as e:
        print(f"Error interno en /location: {e}")
        return jsonify({'status': 'error', 'message': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    monitor_thread = Thread(target=monitor_devices, daemon=True)
    monitor_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
