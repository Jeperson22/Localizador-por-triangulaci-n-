import cv2
import mediapipe as mp

# Inicializa MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

def main():
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
            cv2.waitKey(500)
            continue

        # Convierte la imagen a RGB (MediaPipe requiere este formato)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesa el frame con MediaPipe Pose
        results = pose.process(rgb_frame)

        # Verifica si se detecta una persona
        if results.pose_landmarks:
            visible_landmarks = [lm for lm in results.pose_landmarks.landmark if 0 <= lm.x <= 1 and 0 <= lm.y <= 1]
            if len(visible_landmarks) >= 10:  # Umbral para aceptar detecciones
                # Dibuja los puntos clave y las conexiones de la pose
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
                cv2.putText(frame, "Persona Detectada", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Falso positivo", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "No se detecta persona", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Muestra el frame en una ventana
        cv2.imshow("Cámara Ezviz", frame)

        # Presiona 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera recursos
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
