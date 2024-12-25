from flask import Flask, request, jsonify
import time
from threading import Thread

app = Flask(__name__)

# Estado de conexión de las ESP32 con su último timestamp y datos adicionales
esp32_status = {}

# Tiempo límite en segundos para marcar un dispositivo como "Desconectado"
TIMEOUT = 10


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


@app.route('/')
def home():
    return "Bienvenido a la API de Monitoreo de ESP32"


@app.route('/data', methods=['POST'])
def handle_data():
    """
    Endpoint para recibir datos desde las ESP32.
    Datos esperados:
    - esp32_id: Identificador único del dispositivo.
    - Celina: RSSI del dispositivo Celina.
    - Higinio: RSSI del dispositivo Higinio.
    """
    try:
        # Obtener datos enviados por la ESP32
        device_name = request.form.get('esp32_id')
        celina_rssi = request.form.get('Celina', "No data")
        higinio_rssi = request.form.get('Higinio', "No data")

        if not device_name:
            return jsonify({'status': 'error', 'message': 'Identificador de dispositivo no proporcionado'}), 400

        # Actualizar o agregar el estado del dispositivo
        esp32_status[device_name] = {
            "status": "Connected",
            "last_seen": time.time(),
            "bluetooth_data": {
                "Celina": celina_rssi,
                "Higinio": higinio_rssi
            }
        }

        print(f"Datos actualizados para {device_name}:")
        print(f"  Celina RSSI: {celina_rssi}")
        print(f"  Higinio RSSI: {higinio_rssi}")
        return jsonify({'status': 'success', 'message': f'Datos actualizados para {device_name}'}), 200

    except Exception as e:
        print(f"Error al manejar los datos POST: {e}")
        return jsonify({'status': 'error', 'message': 'Error interno del servidor'}), 500


@app.route('/status', methods=['GET'])
def get_status():
    """
    Endpoint para consultar el estado actual de todas las ESP32.
    Devuelve un JSON con el estado y los datos de cada dispositivo.
    """
    try:
        return jsonify({
            device: {
                "status": info["status"],
                "bluetooth_data": info.get("bluetooth_data", {})
            }
            for device, info in esp32_status.items()
        }), 200
    except Exception as e:
        print(f"Error al manejar la solicitud GET: {e}")
        return jsonify({'status': 'error', 'message': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    # Iniciar el monitor de dispositivos en un hilo separado
    monitor_thread = Thread(target=monitor_devices, daemon=True)
    monitor_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
