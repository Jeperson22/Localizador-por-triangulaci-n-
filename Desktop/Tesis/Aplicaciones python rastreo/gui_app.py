import requests
import time
import tkinter as tk

# URL del servidor Flask (ajusta según sea necesario)
BASE_URL = "https://localizador-por-triangulaci-n.onrender.com"

# Tamaño del canvas (representa el área de monitoreo)
CANVAS_SIZE = 400
SCALE_FACTOR = 10  # Escala para ajustar las coordenadas al tamaño del canvas

def fetch_location():
    """
    Llama al endpoint /location para obtener las coordenadas.
    """
    try:
        response = requests.get(f"{BASE_URL}/location")
        response.raise_for_status()
        data = response.json()
        
        if data["status"] == "success":
            location = data["location"]
            return location["x"], location["y"]
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al conectarse al servidor: {e}")
        return None

def update_canvas():
    """
    Actualiza las posiciones de los puntos en el Canvas basándose en las coordenadas obtenidas.
    """
    # Obtener coordenadas desde el servidor
    location = fetch_location()
    
    if location:
        x, y = location
        
        # Escalar las coordenadas al tamaño del Canvas
        canvas_x = x * SCALE_FACTOR
        canvas_y = CANVAS_SIZE - (y * SCALE_FACTOR)  # Invertir Y para que el origen esté abajo
        
        # Mover el punto de Celina
        canvas.coords(celina_point, canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5)

        # Simular otro punto (por ejemplo, Higinio) con un pequeño desplazamiento
        canvas.coords(higinio_point, canvas_x + 20 - 5, canvas_y + 20 - 5, canvas_x + 20 + 5, canvas_y + 20 + 5)

        # Actualizar la etiqueta con las coordenadas
        coordinates_label.config(text=f"Coordenadas: Celina ({x}, {y})")

    else:
        coordinates_label.config(text="Error al obtener coordenadas")

    # Llamar a esta función nuevamente después de 5 segundos
    root.after(5000, update_canvas)

# Configurar la interfaz gráfica de Tkinter
root = tk.Tk()
root.title("Visualización de ESP32")
root.geometry(f"{CANVAS_SIZE + 50}x{CANVAS_SIZE + 100}")  # Tamaño de la ventana

# Canvas para mostrar los puntos y el área de monitoreo
canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
canvas.pack(pady=20)

# Dibujar un cuadrado que representa el área de monitoreo
canvas.create_rectangle(0, 0, CANVAS_SIZE, CANVAS_SIZE, outline="black")

# Crear puntos para "Celina" y "Higinio"
celina_point = canvas.create_oval(0, 0, 10, 10, fill="blue", outline="blue", tags="Celina")
higinio_point = canvas.create_oval(0, 0, 10, 10, fill="red", outline="red", tags="Higinio")

# Etiqueta para mostrar las coordenadas actuales
coordinates_label = tk.Label(root, text="Coordenadas: Celina (0, 0)")
coordinates_label.pack()

# Iniciar la actualización del Canvas
update_canvas()

# Iniciar el loop de la ventana
root.mainloop()
