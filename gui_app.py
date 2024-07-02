import tkinter as tk
from threading import Thread
import requests
import time
from PIL import Image, ImageTk
import cv2

server_url = "https://localizador-por-triangulaci-n.onrender.com"
video_feed_url = f"{server_url}/video_feed"

# Dimensiones del canvas
canvas_width = 400
canvas_height = 400

# Límites del área de monitoreo
monitoring_area = {
    'x_min': 0,
    'x_max': 400,
    'y_min': 0,
    'y_max': 400
}

def fetch_data():
    while True:
        try:
            response = requests.get(f"{server_url}/data")
            if response.status_code == 200:
                data = response.json()
                update_display(data['ssid1'], data['rssi1'], data['ssid2'], data['rssi2'], data['ssid3'], data['rssi3'], data['x'], data['y'], data['area'], data['detection_message'])
            else:
                print("Error al obtener los datos: ", response.status_code)
        except Exception as e:
            print("Error de conexión: ", e)
        time.sleep(5)

def update_display(ssid1, rssi1, ssid2, rssi2, ssid3, rssi3, x, y, area, detection_message):
    # Actualizar la etiqueta con los datos
    label.config(text=f"SSID1: {ssid1}, RSSI1: {rssi1}\n"
                      f"SSID2: {ssid2}, RSSI2: {rssi2}\n"
                      f"SSID3: {ssid3}, RSSI3: {rssi3}\n"
                      f"Position: ({x:.2f}, {y:.2f})\n"
                      f"Area: {area}\n"
                      f"Message: {detection_message}")

    # Mapear las coordenadas del área de monitoreo al canvas
    mapped_x = (x - monitoring_area['x_min']) / (monitoring_area['x_max'] - monitoring_area['x_min']) * canvas_width
    mapped_y = (y - monitoring_area['y_min']) / (monitoring_area['y_max'] - monitoring_area['y_min']) * canvas_height

    # Actualizar la posición del punto en el canvas
    canvas.coords(point, mapped_x-5, mapped_y-5, mapped_x+5, mapped_y+5)

def update_video():
    cap = cv2.VideoCapture(video_feed_url)
    while True:
        ret, frame = cap.read()
        if ret:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            video_label.imgtk = imgtk
            video_label.config(image=imgtk)
        time.sleep(0.03)

root = tk.Tk()
root.title("RSSI Triangulation Data")

# Canvas para dibujar el cuadrado y el punto
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack(pady=20)

# Dibujar el cuadrado dividido en dos partes
canvas.create_rectangle(50, 50, 350, 200, outline="black")  # Cocina
canvas.create_rectangle(50, 200, 350, 350, outline="black")  # Cuarto
canvas.create_text(200, 125, text="Cocina", font=("Helvetica", 16))
canvas.create_text(200, 275, text="Cuarto", font=("Helvetica", 16))

# Crear un punto inicial en el canvas
point = canvas.create_oval(195, 195, 205, 205, fill="red")

# Etiqueta para mostrar los datos
label = tk.Label(root, text="Esperando datos...", font=("Helvetica", 16), justify="left")
label.pack(pady=20, padx=20)

# Etiqueta para mostrar el video
video_label = tk.Label(root)
video_label.pack()

# Iniciar el hilo de actualización de la etiqueta y el canvas
fetch_thread = Thread(target=fetch_data)
fetch_thread.daemon = True
fetch_thread.start()

# Iniciar el hilo de actualización del video
video_thread = Thread(target=update_video)
video_thread.daemon = True
video_thread.start()

root.mainloop()
