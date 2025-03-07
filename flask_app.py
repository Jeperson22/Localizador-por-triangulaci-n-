from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

# Almacenamiento temporal para los datos recibidos de los ESP32 y la detección de personas
esp32_data = {}
person_detected = False  # Variable que guarda si se detectó o no una persona

@app.route('/')
def home():
    return "Servidor Flask en funcionamiento", 200

@app.route('/data', methods=['POST'])
def receive_data():
    """
    Endpoint para recibir datos de los ESP32.
    """
    try:
        # Obtener los datos enviados por el ESP32 como datos de formulario (x-www-form-urlencoded)
        esp32_id = request.form.get('esp32_id')
        celina_rssi = request.form.get('Celina')
        higinio_rssi = request.form.get('Higinio')

        # Validación de datos
        if not esp32_id or not celina_rssi or not higinio_rssi:
            return jsonify({"status": "error", "message": "Datos incompletos"}), 400

        # Almacenar los datos en el diccionario esp32_data
        esp32_data[esp32_id] = {
            "timestamp": time.time(),
            "Celina": celina_rssi,
            "Higinio": higinio_rssi
        }

        # Responder al ESP32 con éxito
        return jsonify({"status": "success", "message": "Datos recibidos correctamente"}), 200
    except Exception as e:
        print(f"Error al procesar los datos: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


@app.route('/location', methods=['GET'])
def get_location():
    """
    Endpoint para consultar los datos almacenados de los ESP32.
    """
    try:
        # Crear una lista con los datos actuales
        data_list = []
        for esp32_id, data in esp32_data.items():
            # Calcular tiempo desde la última actualización
            last_update = time.time() - data["timestamp"]

            # Reemplazar 'No data' con 0
            celina_rssi = int(data.get("Celina", 0)) if data.get("Celina") != "No data" else 0
            higinio_rssi = int(data.get("Higinio", 0)) if data.get("Higinio") != "No data" else 0

            # Crear la respuesta con los datos actuales
            data_list.append({
                "esp32_id": esp32_id,
                "last_update_seconds": last_update,
                "Celina": celina_rssi,
                "Higinio": higinio_rssi,
            })

        return jsonify({
            "status": "success",
            "devices": data_list,
            "person_detected": person_detected  # Incluye el estado de detección de persona
        }), 200
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


@app.route('/person_detection', methods=['POST'])
def update_person_detection():
    """
    Endpoint para recibir la información de la detección de persona desde el cliente.
    """
    global person_detected
    try:
        data = request.get_json()
        if "person_detected" not in data:
            return jsonify({"status": "error", "message": "Falta el dato 'person_detected'"}), 400

        person_detected = data["person_detected"]  # Actualiza el estado de detección
        return jsonify({"status": "success", "message": "Estado de detección de persona actualizado"}), 200
    except Exception as e:
        print(f"Error al procesar la detección de persona: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


if __name__ == '__main__':
    # Ejecutar el servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
