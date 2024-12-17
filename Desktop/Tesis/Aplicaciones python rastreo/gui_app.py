import tkinter as tk
from threading import Thread
import requests
import time
from PIL import Image, ImageTk
import cv2

# Configuraciones
server_url = "https://localizador-por-triangulaci-n.onrender.com"
video_feed_url = f"{server_url}/video_feed"
canvas_width = 400
canvas_height = 400
video_width = 320
video_height = 240

monitoring_area = {
    'x_min': 0,
    'x_max': 400,
    'y_min': 0,
    'y_max': 400
}

# Variables globales para mantener los datos
data = {
    'rssi1': None,
    'rssi2': None,
    'x': None,
    'y': None,
    'area': None,
    'detection_message': None,
    'camera_status': None,
    'esp32_status': None
}

def fetch_data():
    """Función que obtiene los datos del servidor Flask de forma controlada"""
    retry_count = 0
    while True:
        try:
            response = requests.get(f"{server_url}/data")
            if response.status_code == 200:
                new_data = response.json()
                if new_data != data:  # Solo actualizamos si los datos han cambiado
                    print("Datos recibidos: ", new_data)
                    # Actualizamos los datos globales
                    data.update(new_data)
                    # Llamamos a update_display para actualizar la UI
                    update_display()
                retry_count = 0  # Reiniciamos el contador de reintentos en caso de éxito
            else:
                print("Error al obtener los datos: ", response.status_code)
        except Exception as e:
            print("Error de conexión: ", e)
            retry_count += 1
            time.sleep(min(2 ** retry_count, 60))  # Retardo exponencial hasta 60 segundos
        time.sleep(5)  # Hacemos una pausa de 5 segundos entre cada intento

def update_display():
    """Función para actualizar la interfaz gráfica con los nuevos datos"""
    # Obtener los datos actuales de la variable global 'data'
    rssi1 = data['rssi1']
    rssi2 = data['rssi2']
    x = data['x']
    y = data['y']
    area = data['area']
    detection_message = data['detection_message']
    camera_status = data['camera_status']
    esp32_status = data['esp32_status']
    
    # Actualizar el texto de la etiqueta
    label.config(text=f"RSSI1 (Higinio): {rssi1}\n"
                      f"RSSI2 (Celina): {rssi2}\n"
                      f"Position: ({x:.2f}, {y:.2f})\n"
                      f"Area: {area}\n"
                      f"Message: {detection_message}\n"
                      f"Camera Status: {camera_status}\n"
                      f"ESP32 Status: {esp32_status}")

    # Actualizar la posición del punto en el canvas solo si se reciben coordenadas válidas
    if x is not None and y is not None:
        mapped_x = (x - monitoring_area['x_min']) / (monitoring_area['x_max'] - monitoring_area['x_min']) * canvas_width
        mapped_y = (y - monitoring_area['y_min']) / (monitoring_area['y_max'] - monitoring_area['y_min']) * canvas_height
        canvas.coords(point, mapped_x-5, mapped_y-5, mapped_x+5, mapped_y+5)
    else:
        canvas.coords(point, -10, -10, -10, -10)  # Mover el punto fuera del área visible si no hay datos

def update_video():
    """Función para mostrar el video desde el servidor"""
    while True:
        try:
            cap = cv2.VideoCapture(video_feed_url)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, video_width)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, video_height)
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error al abrir el flujo de video. Reintentando...")
                    cap.release()
                    time.sleep(2)
                    break

                frame = cv2.resize(frame, (video_width, video_height))
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                video_label.imgtk = imgtk
                video_label.config(image=imgtk)
                time.sleep(0.03)
        except Exception as e:
            print("Error en la captura de video: ", e)
            time.sleep(5)

root = tk.Tk()
root.title("RSSI Triangulation Data")

root.geometry(f"{video_width + canvas_width + 50}x{max(video_height, canvas_height) + 100}")

frame_left = tk.Frame(root, width=video_width, height=video_height)
frame_left.grid(row=0, column=0, padx=10, pady=10)
frame_right = tk.Frame(root, width=canvas_width, height=canvas_height)
frame_right.grid(row=0, column=1, padx=10, pady=10)

canvas = tk.Canvas(frame_right, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()
canvas.create_rectangle(50, 50, 350, 200, outline="black")  
canvas.create_rectangle(50, 200, 350, 350, outline="black")  
canvas.create_text(200, 125, text="Cocina", font=("Helvetica", 16))
canvas.create_text(200, 275, text="Cuarto", font=("Helvetica", 16))
point = canvas.create_oval(195, 195, 205, 205, fill="red")

label = tk.Label(frame_right, text="Esperando datos...", font=("Helvetica", 16), justify="left")
label.pack(pady=20, padx=20)

video_label = tk.Label(frame_left)
video_label.pack()

fetch_thread = Thread(target=fetch_data)
fetch_thread.daemon = True
fetch_thread.start()

video_thread = Thread(target=update_video)
video_thread.daemon = True
video_thread.start()

root.mainloop()
