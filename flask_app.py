from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Lista de IDs autorizados de ESP32
AUTHORIZED_DEVICES = ["puertacalle", "otrodispositivo"]

# Almacenamiento temporal de datos recibidos
data_storage = {}

@app.route('/data', methods=['POST'])
def receive_data():
    esp32_id = request.form.get("esp32_id")
    celina_rssi = request.form.get("Celina")
    higinio_rssi = request.form.get("Higinio")

    if not esp32_id:
        return "Falta el ID del dispositivo ESP32", 400

    if esp32_id not in AUTHORIZED_DEVICES:
        return "Dispositivo no autorizado", 403

    # Guardar los datos en el almacenamiento
    data_storage[esp32_id] = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Celina": celina_rssi,
        "Higinio": higinio_rssi
    }

    return "Datos recibidos correctamente", 200

@app.route('/data/<esp32_id>', methods=['GET'])
def get_data(esp32_id):
    if esp32_id not in data_storage:
        return "No hay datos para este dispositivo", 404

    return jsonify(data_storage[esp32_id])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
