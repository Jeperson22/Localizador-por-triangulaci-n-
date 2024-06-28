import os
from flask import Flask, request, jsonify
import math

app = Flask(__name__)

current_data = {}

# Ruta para la URL raíz
@app.route('/')
def home():
    return "Welcome to the RSSI Triangulation API"

# Posiciones fijas de los puntos de acceso
access_points = {
    'AP1': (100, 100),
    'AP2': (300, 100),
    'AP3': (200, 300)
}

# Definir las áreas para "cocina", "cuarto" y "sala"
areas = {
    'cocina': (50, 50, 200, 200),
    'cuarto': (200, 50, 350, 200),
    'sala': (50, 200, 350, 350)
}

@app.route('/data', methods=['POST', 'GET'])
def handle_data():
    if request.method == 'POST':
        ssid1 = request.form['ssid1']
        rssi1 = int(request.form['rssi1'])
        ssid2 = request.form['ssid2']
        rssi2 = int(request.form['rssi2'])
        ssid3 = request.form['ssid3']
        rssi3 = int(request.form['rssi3'])

        print(f"SSID1: {ssid1}, RSSI1: {rssi1}")
        print(f"SSID2: {ssid2}, RSSI2: {rssi2}")
        print(f"SSID3: {ssid3}, RSSI3: {rssi3}")

        # Convertir RSSI a distancia (aquí se usa un modelo simple)
        dist1 = rssi_to_distance(rssi1)
        dist2 = rssi_to_distance(rssi2)
        dist3 = rssi_to_distance(rssi3)

        # Calcular la posición del punto basado en la trilateración
        x, y = trilaterate(
            access_points['AP1'][0], access_points['AP1'][1], dist1,
            access_points['AP2'][0], access_points['AP2'][1], dist2,
            access_points['AP3'][0], access_points['AP3'][1], dist3
        )

        area = determine_position(x, y)

        current_data.update({
            'ssid1': ssid1, 'rssi1': rssi1,
            'ssid2': ssid2, 'rssi2': rssi2,
            'ssid3': ssid3, 'rssi3': rssi3,
            'x': x, 'y': y, 'area': area
        })

        return area, 200

    elif request.method == 'GET':
        return jsonify(current_data), 200

def rssi_to_distance(rssi):
    # Convertir RSSI a distancia usando un modelo simple
    tx_power = -59  # Potencia de transmisión a 1 metro
    if rssi == 0:
        return -1.0
    ratio = rssi / tx_power
    if ratio < 1.0:
        return ratio ** 10
    else:
        distance = (0.89976) * (ratio ** 7.7095) + 0.111
        return distance

def trilaterate(x1, y1, r1, x2, y2, r2, x3, y3, r3):
    # Usar la trilateración para calcular la posición
    A = 2 * x2 - 2 * x1
    B = 2 * y2 - 2 * y1
    C = r1 ** 2 - r2 ** 2 - x1 ** 2 + x2 ** 2 - y1 ** 2 + y2 ** 2
    D = 2 * x3 - 2 * x2
    E = 2 * y3 - 2 * y2
    F = r2 ** 2 - r3 ** 2 - x2 ** 2 + x3 ** 2 - y2 ** 2 + y3 ** 2
    x = (C * E - F * B) / (E * A - B * D)
    y = (C * D - A * F) / (B * D - A * E)
    return x, y

def determine_position(x, y):
    for area, (x1, y1, x2, y2) in areas.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return area
    return "Desconocido"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
