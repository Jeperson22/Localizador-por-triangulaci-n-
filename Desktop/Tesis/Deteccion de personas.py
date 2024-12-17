import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import simpledialog

# Directorio donde se almacenarán las imágenes de entrenamiento
training_dir = "training_data"

# Crear el directorio de entrenamiento si no existe
if not os.path.exists(training_dir):
    os.makedirs(training_dir)

# Función para capturar imágenes de entrenamiento
def capture_training_images(label):
    cap = cv2.VideoCapture(0)
    count = 0

    while count < 20:  # Capturar 20 imágenes
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face_resized = cv2.resize(face, (200, 200))

            file_name = f"{training_dir}/{label}_{count}.jpg"
            cv2.imwrite(file_name, face_resized)
            print(f"Saved {file_name}")
            count += 1

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, f"Capturing {count}/20", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        cv2.imshow('Capture Training Images', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Función para entrenar el reconocedor con las imágenes capturadas
def train_recognizer():
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
    return recognizer, label_dict

# Cargar el clasificador de Haar
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Función para capturar nuevas imágenes de personas seleccionadas
def capture_new_person():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal

    # Pedir al usuario que ingrese el nombre de la persona
    person_name = simpledialog.askstring("Input", "Nombre de la persona:")
    if person_name:
        capture_training_images(person_name)
        print(f"Imágenes de {person_name} capturadas.")

    root.destroy()

# Capturar imágenes de al menos dos personas antes del entrenamiento
print("Captura de imágenes de la primera persona:")
capture_new_person()
print("Captura de imágenes de la segunda persona:")
capture_new_person()

# Entrenar el modelo con los datos disponibles
recognizer, label_dict = train_recognizer()

# Inicializar la cámara
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        face = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face, (200, 200))

        try:
            label, confidence = recognizer.predict(face_resized)
            label_text = list(label_dict.keys())[list(label_dict.values()).index(label)]
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, label_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
            cv2.putText(frame, f"Conf: {confidence:.2f}", (x, y+h+30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        except:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

