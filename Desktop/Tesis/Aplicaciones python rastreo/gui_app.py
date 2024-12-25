import requests
import time

# URL del servidor Flask (ajusta según sea necesario)
BASE_URL = "https://localizador-por-triangulaci-n.onrender.com"

def get_status():
    try:
        # Hacer una solicitud GET al endpoint /status
        response = requests.get(f"{BASE_URL}/status")
        response.raise_for_status()  # Lanza un error si la respuesta tiene un código de estado no exitoso
        
        # Imprimir los datos recibidos
        data = response.json()
        print("Estado de las ESP32:")
        for device, info in data.items():
            status = info["status"]
            bluetooth_data = info.get("bluetooth_data", {})
            celina_rssi = bluetooth_data.get("Celina", "No disponible")
            higinio_rssi = bluetooth_data.get("Higinio", "No disponible")
            print(f"Dispositivo: {device}")
            print(f"  Estado: {status}")
            print(f"  Celina RSSI: {celina_rssi}")
            print(f"  Higinio RSSI: {higinio_rssi}")
        print("-" * 30)  # Separador para la salida
    
    except requests.exceptions.RequestException as e:
        print(f"Error al conectarse al servidor: {e}")
    except ValueError:
        print("Error al procesar la respuesta del servidor")

if __name__ == "__main__":
    print("Iniciando monitoreo constante del servidor...")
    while True:
        get_status()
        time.sleep(5)  # Espera 5 segundos antes de hacer otra solicitud

