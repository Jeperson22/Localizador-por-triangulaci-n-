from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Datos actuales
current_data = {
    'rssi1': None,
    'rssi2': None,
    'x': None,
    'y': None,
    'area': None,
    'detection_message': None,
    'esp32_status': 'Disconnected'
}

@app.route('/')
def home():
    return "Bienvenido a la API de Triangulación RSSI"

# Puntos de acceso (AP) en las coordenadas
access_points = {
    'AP1': (100, 100),
    'AP2': (300, 100),
    'AP3': (200, 300)
}

# Definición de áreas
areas = {
    'cocina': (50, 50, 200, 200),
    'cuarto': (200, 50, 350, 200),
    'sala': (50, 200, 350, 350)
}

@app.route('/data', methods=['POST', 'GET'])
def handle_data():
    if request.method == 'POST':
        try:
            rssi1 = int(request.form['Higinio'])
            rssi2 = int(request.form['Celina'])

            print(f"RSSI Higinio: {rssi1}")
            print(f"RSSI Celina: {rssi2}")

            current_data['esp32_status'] = 'Connected'

            dist1 = rssi_to_distance(rssi1)
            dist2 = rssi_to_distance(rssi2)

            # Trilateración para obtener las coordenadas (x, y)
            x, y = trilaterate(
                access_points['AP1'][0], access_points['AP1'][1], dist1,
                access_points['AP2'][0], access_points['AP2'][1], dist2,
                access_points['AP3'][0], access_points['AP3'][1], dist2  # Usar dist2 para ambos si solo hay dos RSSI
            )

            # Determinación del área donde se encuentra la persona
            area = determine_position(x, y)

            detection_message = "No se ha realizado reconocimiento facial en esta solicitud."

            # Actualizar los datos actuales
            current_data.update({
                'rssi1': rssi1,
                'rssi2': rssi2,
                'x': x,
                'y': y,
                'area': area,
                'detection_message': detection_message
            })

            return jsonify(current_data), 200

        except Exception as e:
            print(f"Error handling POST data: {e}")
            current_data['esp32_status'] = 'Disconnected'
            return "Error Interno del Servidor", 500

    elif request.method == 'GET':
        return jsonify(current_data), 200

def rssi_to_distance(rssi):
    tx_power = -59
    if rssi == 0:
        return -1.0
    ratio = rssi / tx_power
    if ratio < 1.0:
        return ratio ** 10
    else:
        return 0.89976 * (ratio ** 7.7095) + 0.111

def trilaterate(x1, y1, d1, x2, y2, d2, x3, y3, d3):
    # Resolución de sistema de ecuaciones para obtener las coordenadas (x, y)
    A = 2 * (x2 - x1)
    B = 2 * (y2 - y1)
    C = 2 * (x3 - x1)
    D = 2 * (y3 - y1)

    E = d1 ** 2 - d2 ** 2 - x1 ** 2 + x2 ** 2 - y1 ** 2 + y2 ** 2
    F = d1 ** 2 - d3 ** 2 - x1 ** 2 + x3 ** 2 - y1 ** 2 + y3 ** 2

    # Resolución del sistema de ecuaciones lineales
    x = (E - F * B / D) / (A - C * B / D)
    y = (E - A * x) / B

    return x, y

def determine_position(x, y):
    # Determinar el área en la que se encuentra la persona basándose en las coordenadas
    for area, coords in areas.items():
        if coords[0] <= x <= coords[2] and coords[1] <= y <= coords[3]:
            return area
    return "Fuera de área conocida"

if __name__ == '__main__':
    if __name__ == "__main__":
     app.run(host="0.0.0.0", port=5000, debug=True)

