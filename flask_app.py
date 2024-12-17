from flask import Flask, request, jsonify

app = Flask(__name__)

# Estado de conexión de las ESP32
esp32_status = {
    'Higinio': 'Disconnected',
    'Celina': 'Disconnected'
}

@app.route('/')
def home():
    return "Bienvenido a la API de Monitoreo de ESP32"

@app.route('/data', methods=['POST'])
def handle_data():
    try:
        # Suponiendo que las ESP32 envían su nombre en el campo 'device_name'
        device_name = request.form.get('device_name')
        if device_name in esp32_status:
            esp32_status[device_name] = 'Connected'
            print(f"Datos recibidos de {device_name}")
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Dispositivo no reconocido'}), 400
    except Exception as e:
        print(f"Error al manejar los datos POST: {e}")
        return "Error Interno del Servidor", 500

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(esp32_status), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)


