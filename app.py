import cv2

# Incluye las credenciales en la URL RTSP
video_feed_url = "rtsp://admin:BVXEDH@192.168.3.6/video"  # Asegúrate de que estas credenciales son correctas

cap = cv2.VideoCapture(video_feed_url)

if not cap.isOpened():
    print("Error al abrir el flujo de video.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al leer el frame.")
            break
        
        cv2.imshow('Video Feed', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
