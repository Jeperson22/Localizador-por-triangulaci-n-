from flask import Flask, request, jsonify, Response
import os
import cv2
import numpy as np

app = Flask(__name__)

# URL de la cámara RTSP
RTSP_URL = "rtsp://admin:BVXEDH@192.168.3.4/video"

current_data = {}

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
    cap = cv2.VideoCapture(RTSP_URL)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detection_message = recognize_faces(frame)

        # Dibujar la detección en el frame
        cv2.putText(frame, detection_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data', methods=['POST', 'GET'])
def handle_data():
    if request.method == 'POST':
        try:
            ssid1 = request.form['ssid1']
            rssi1 = int(request.form['rssi1'])
            ssid2 = request.form['ssid2']
            rssi2 = int(request.form['rssi2'])
            ssid3 = request.form['ssid3']
            rssi3 = int(request.form['rssi3'])

            print(f"SSID1: {ssid1}, RSSI1: {rssi1}")
            print(f"SSID2: {ssid2}, RSSI2: {rssi2}")
            print(f"SSID3: {ssid3}, RSSI3: {rssi3}")

            dist1 = rssi_to_distance(rssi1)
            dist2 = rssi_to_distance(rssi2)
            dist3 = rssi_to_distance(rssi3)

            x, y = trilaterate(
                access_points['AP1'][0], access_points['AP1'][1], dist1,
                access_points['AP2'][0], access_points['AP2'][1], dist2,
                access_points['AP3'][0], access_points['AP3'][1], dist3
            )

            area = determine_position(x, y)

            # Aquí no se está pasando el frame a recognize_faces. Necesitamos arreglarlo.
            # Dado que recognize_faces requiere un frame, podrías necesitar ajustar cómo obtienes el frame para reconocimiento facial.
            detection_message = "No se ha realizado reconocimiento facial en esta solicitud."

            current_data.update({
                'ssid1': ssid1, 'rssi1': rssi1,
                'ssid2': ssid2, 'rssi2': rssi2,
                'ssid3': ssid3, 'rssi3': rssi3,
                'x': x, 'y': y, 'area': area,
                'detection_message': detection_message
            })

            return detection_message, 200

        except Exception as e:
            print(f"Error handling POST data: {e}")
            return "Internal Server Error", 500

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
