from flask import Flask, request, jsonify
import time
import cv2
import mediapipe as mp
import threading

app = Flask(__name__)

# Almacenamiento temporal para los datos recibidos de los ESP32 y detección de personas
esp32_data = {}
person_detected = False

# Inicializa MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)

def process_camera_feed():
    global person_detected

    # Dirección RTSP de la cámara
    rtsp_url = "rtsp://admin:BVXEDH@192.168.100.2/video"
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("Error: No se pudo conectar al stream de la cámara.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al recibir el frame de la cámara, reintentando...")
            time.sleep(0.5)
            continue

        # Convierte la imagen a RGB (MediaPipe requiere este formato)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesa el frame con MediaPipe Pose
        results = pose.process(rgb_frame)

        # Verifica si se detecta una persona
        if results.pose_landmarks:
            visible_landmarks = [lm for lm in results.pose_landmarks.landmark if 0 <= lm.x <= 1 and 0 <= lm.y <= 1]
            person_detected = len(visible_landmarks) >= 10  # Umbral para aceptar detecciones
        else:
            person_detected = False

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
    Endpoint para consultar los datos almacenados de los ESP32 y detección de personas.
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

        # Agregar información de detección de personas
        return jsonify({
            "status": "success",
            "devices": data_list,
            "person_detected": person_detected
        }), 200
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return jsonify({"status": "error", "message": "Error interno del servidor"}), 500

if __name__ == '__main__':
    # Iniciar el procesamiento de la cámara en un hilo separado
    camera_thread = threading.Thread(target=process_camera_feed, daemon=True)
    camera_thread.start()

    # Ejecutar el servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
