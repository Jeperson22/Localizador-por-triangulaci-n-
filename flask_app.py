from flask import Flask, request, jsonify
import time
from threading import Thread

app = Flask(__name__)

# Estado de conexión de las ESP32 con su último timestamp
esp32_status = {}

# Tiempo límite en segundos para marcar un dispositivo como "Desconectado"
TIMEOUT = 10

def monitor_devices():
    """Hilo que actualiza el estado de los dispositivos según el tiempo transcurrido."""
    while True:
        current_time = time.time()
        to_disconnect = []
        for device, info in esp32_status.items():
            last_seen = info["last_seen"]
            if current_time - last_seen > TIMEOUT:
                to_disconnect.append(device)
        
        # Marcar dispositivos como "Disconnected"
        for device in to_disconnect:
            esp32_status[device]["status"] = "Disconnected"

        time.sleep(1)  # Verificar cada segundo

@app.route('/')
def home():
    return "Bienvenido a la API de Monitoreo de ESP32"

@app.route('/data', methods=['POST'])
def handle_data():
    try:
        # Obtener el nombre del dispositivo desde el cuerpo de la solicitud
        device_name = request.form.get('esp32_id')

        if device_name:  # Si se recibe un nombre de dispositivo
            # Actualizamos el estado del dispositivo o lo agregamos si es nuevo
            esp32_status[device_name] = {
                "status": "Connected",
                "last_seen": time.time()
            }
            print(f"Datos recibidos de {device_name}")
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Nombre de dispositivo no proporcionado'}), 400

    except Exception as e:
        print(f"Error al manejar los datos POST: {e}")
        return "Error Interno del Servidor", 500

@app.route('/status', methods=['GET'])
def get_status():
    # Retornar solo los estados actuales de los dispositivos
    return jsonify({device: info["status"] for device, info in esp32_status.items()}), 200

if __name__ == '__main__':
    # Iniciar el monitor de dispositivos en un hilo separado
    monitor_thread = Thread(target=monitor_devices, daemon=True)
    monitor_thread.start()
    app.run(host="0.0.0.0", port=5000, debug=True)
