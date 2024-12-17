from flask import Flask, request, jsonify

app = Flask(__name__)

# Estado de conexión de las ESP32
esp32_status = {}

@app.route('/')
def home():
    return "Bienvenido a la API de Monitoreo de ESP32"

@app.route('/data', methods=['POST'])
def handle_data():
    try:
        # Obtener el nombre del dispositivo desde el cuerpo de la solicitud
        device_name = request.form.get('esp32_id')  # Cambié 'device_name' a 'esp32_id' para alinearlo con el código de la ESP32

        if device_name:  # Si se recibe un nombre de dispositivo
            # Actualizamos el estado del dispositivo o lo agregamos si es nuevo
            esp32_status[device_name] = 'Connected'
            print(f"Datos recibidos de {device_name}")
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Nombre de dispositivo no proporcionado'}), 400

    except Exception as e:
        print(f"Error al manejar los datos POST: {e}")
        return "Error Interno del Servidor", 500

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(esp32_status), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)



