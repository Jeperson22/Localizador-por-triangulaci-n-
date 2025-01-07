from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Almacenamiento temporal para los datos recibidos de los ESP32
esp32_data = {}

# Coordenadas de los ESP32 en un plano virtual
esp32_locations = {
    "cocina": {"x": 0, "y": 0},
    "patio": {"x": 10, "y": 0},
    "puertacalle": {"x": 5, "y": 5}
}

def calculate_location():
    """
    Realiza la triangulación en base a los datos de RSSI recibidos.
    """
    weights = []
    total_weight = 0
    weighted_x = 0
    weighted_y = 0

    for esp32_id, data in esp32_data.items():
        if esp32_id in esp32_locations:
            location = esp32_locations[esp32_id]
            rssi_celina = data.get("Celina", None)
            
            if rssi_celina and rssi_celina != "No data":
                # Convertir RSSI a un valor positivo para calcular un peso
                signal_strength = abs(int(rssi_celina))
                weight = max(1 / (signal_strength + 1), 0.01)  # Invertir la relación con RSSI
                total_weight += weight
                weighted_x += weight * location["x"]
                weighted_y += weight * location["y"]

    # Calcular la posición estimada basada en los pesos
    if total_weight > 0:
        estimated_x = weighted_x / total_weight
        estimated_y = weighted_y / total_weight
        return {"x": round(estimated_x, 2), "y": round(estimated_y, 2)}
    return None

@app.route('/data', methods=['POST'])
def receive_data():
    """
    Endpoint para recibir datos de los ESP32.
    """
    try:
        # Obtener los datos enviados por el ESP32
        esp32_id = request.form.get("esp32_id")
        celina_rssi = request.form.get("Celina")
        higinio_rssi = request.form.get("Higinio")

        if not esp32_id:
            return jsonify({"status": "error", "message": "esp32_id no proporcionado"}), 400

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
    Endpoint para consultar los datos almacenados de los ESP32 y calcular la ubicación estimada.
    """
    try:
        # Crear una lista con los datos actuales
        data_list = []
        for esp32_id, data in esp32_data.items():
            # Calcular tiempo desde la última actualización
            last_update = time.time() - data["timestamp"]
            data_list.append({
                "esp32_id": esp32_id,
                "last_update_seconds": last_update,
                "Celina": data.get("Celina", "No data"),
                "Higinio": data.get("Higinio", "No data"),
            })

        # Calcular la ubicación estimada mediante triangulación
        estimated_location = calculate_location()

        # Responder con los datos
        return jsonify({
            "status": "success",
            "devices": data_list,
            "location": estimated_location or {"x": "unknown", "y": "unknown"}
        }), 200
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


if __name__ == '__main__':
    # Ejecutar el servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)

