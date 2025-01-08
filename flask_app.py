from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Almacenamiento temporal para los datos recibidos de los ESP32
esp32_data = {}

# Ruta para la raíz, para verificar si el servidor está funcionando
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

        # Imprimir los datos en el servidor para depuración
        print(f"Datos recibidos de {esp32_id}:")
        print(f"  - Celina RSSI: {celina_rssi}")
        print(f"  - Higinio RSSI: {higinio_rssi}")

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
            
            data_list.append({
                "esp32_id": esp32_id,
                "last_update_seconds": last_update,
                "Celina": celina_rssi,
                "Higinio": higinio_rssi,
            })

        # Responder con los datos
        return jsonify({
            "status": "success",
            "devices": data_list
        }), 200
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


if __name__ == '__main__':
    # Ejecutar el servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
