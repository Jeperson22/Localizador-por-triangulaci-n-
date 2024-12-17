from flask import Flask, request, jsonify, Response
import os
import cv2
import numpy as np
import time

app = Flask(__name__)

# URL de la cámara RTSP
RTSP_URL = "rtsp://admin:BVXEDH@192.168.100.2/video"

current_data = {
    'rssi1': None,
    'rssi2': None,
    'x': None,
    'y': None,
    'area': None,
    'detection_message': None,
    'camera_status': 'Disconnected',
    'esp32_status': 'Disconnected'
}

@app.route('/')
def home():
    return "Welcome to the RSSI Triangulation and Face Recognition API"

access_points = {
    'AP1': (100, 100),
    'AP2': (300, 100),
    'AP3': (200, 300)
}

areas = {
    'cocina': (50, 50, 200, 200),
    'cuarto': (200, 50, 350, 200),
    'sala': (50, 200, 350, 350)
}

print("Loading Haar Cascade...")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

recognizer = None
label_dict = {}

training_dir = "training_data"
if not os.path.exists(training_dir):
    os.makedirs(training_dir)

def initialize_recognizer():
    global recognizer, label_dict
    try:
        recognizer, label_dict = train_recognizer()
        print("Recognizer initialized successfully.")
    except ValueError as e:
        print(f"Error initializing recognizer: {e}")

def train_recognizer():
    print("Training recognizer...")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    images = []
    labels = []
    label_dict = {}

    current_label = 0

    for file_name in os.listdir(training_dir):
        if file_name.endswith(".jpg"):
            label = file_name.split("_")[0]
            if label not in label_dict:
                label_dict[label] = current_label
                current_label += 1

            image = cv2.imread(os.path.join(training_dir, file_name), cv2.IMREAD_GRAYSCALE)
            if image is not None:
                images.append(image)
                labels.append(label_dict[label])
            else:
                print(f"Failed to load {file_name}")

    if len(images) < 2:
        raise ValueError("Not enough training data. Ensure there are at least 2 samples for training.")
    
    recognizer.train(images, np.array(labels))
    print("Training completed.")
    return recognizer, label_dict

def recognize_faces(frame):
    print("Recognizing faces...")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    faces_detected = []

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (200, 200))

        try:
            label, confidence = recognizer.predict(face_resized)
            label_text = list(label_dict.keys())[list(label_dict.values()).index(label)]
            faces_detected.append(label_text)
        except:
            faces_detected.append("Unknown")

    if "adulto_mayor" in faces_detected:
        return "La persona adulta mayor ha sido detectada."
    else:
        return "No se ha detectado a la persona adulta mayor."

def generate_video_stream():
    while True:
        cap = cv2.VideoCapture(RTSP_URL)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            current_data['camera_status'] = 'Disconnected'
        else:
            current_data['camera_status'] = 'Connected'

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error al leer el frame de video. Reintentando...")
                cap.release()
                time.sleep(1)
                break

            detection_message = recognize_faces(frame)

            # Dibujar la detección en el frame
            cv2.putText(frame, detection_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

            x, y = trilaterate(
                access_points['AP1'][0], access_points['AP1'][1], dist1,
                access_points['AP2'][0], access_points['AP2'][1], dist2,
                access_points['AP3'][0], access_points['AP3'][1], dist2  # Usar dist2 para ambos si solo hay dos RSSI
            )

            area = determine_position(x, y)

            detection_message = "No se ha realizado reconocimiento facial en esta solicitud."

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
            return "Internal Server Error", 500

    elif request.method == 'GET':
        return jsonify(current_data), 200

@app.route('/get_contact', methods=['GET'])
def get_contact():
    # Aquí defines el nombre del contacto o número de teléfono
    contact_name = "+593xxxxxxxxx"  # Reemplaza con el número de teléfono del contacto

    return jsonify({'contact': contact_name})

def rssi_to_distance(rssi):
    tx_power = -59
    if rssi == 0:
        return -1.0
    ratio = rssi / tx_power
    if ratio < 1.0:
        return ratio ** 10
    else:
        distance = (0.89976) * (ratio ** 7.7095) + 0.111
        return distance

def trilaterate(x1, y1, r1, x2, y2, r2, x3, y3, r3):
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
    print("Initializing recognizer...")
    initialize_recognizer()
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}...")
    app.run(host='0.0.0.0', port=port)
