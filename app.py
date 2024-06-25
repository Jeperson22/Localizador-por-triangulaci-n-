from flask import Flask, request
import tkinter as tk
from threading import Thread
import math

app = Flask(__name__)

# Crear ventana con tkinter
root = tk.Tk()
root.title("Triangulación RSSI")
root.geometry("500x500")

# Crear un canvas para dibujar el cuadrado y el punto
canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack(pady=20)

# Dibujar un cuadrado
square = canvas.create_rectangle(50, 50, 350, 350, outline="black")

# Dibujar un punto que se moverá
point = canvas.create_oval(195, 195, 205, 205, fill="red")

# Etiqueta para mostrar la posición
position_label = tk.Label(root, text="Posición: Desconocido", font=("Helvetica", 14))
position_label.pack(pady=20)

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

def move_point(x, y):
    canvas.coords(point, x-5, y-5, x+5, y+5)
    # Determinar el área (posición) del dispositivo
    position = determine_position(x, y)
    # Actualizar la etiqueta con la posición
    position_label.config(text=f"Posición: {position}")

@app.route('/data', methods=['POST'])
def receive_data():
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
    
    # Mover el punto en el canvas
    move_point(x, y)

    return determine_position(x, y), 200

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

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Iniciar el servidor Flask en un hilo separado
flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Ejecutar la aplicación tkinter
root.mainloop()
