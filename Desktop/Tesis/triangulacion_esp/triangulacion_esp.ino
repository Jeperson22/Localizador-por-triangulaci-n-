#include <BLEDevice.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Definir las credenciales de la red Wi-Fi
const char* ssid = "TeleComNet-OCHOA";           // Reemplaza con tu nombre de red Wi-Fi
const char* password = "1714084496";  // Reemplaza con tu contraseña de Wi-Fi

// Dirección IP y puerto del servidor Flask
const char* serverUrl = "http://192.168.100.5:5000/data";

void setup() {
  Serial.begin(115200);

  // Conectar a Wi-Fi
  Serial.println("Conectando a Wi-Fi...");
  WiFi.begin(ssid, password);

  // Esperar hasta que la conexión Wi-Fi sea exitosa
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando a Wi-Fi...");
  }

  // Imprimir la IP local de la ESP32
  Serial.println("Conexión Wi-Fi exitosa");
  Serial.print("Dirección IP: ");
  Serial.println(WiFi.localIP());

  // Inicializar el dispositivo BLE
  BLEDevice::init("ESP32_Scanner");
  Serial.println("Iniciando escaneo de dispositivos Bluetooth...");
}

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    String nombre = advertisedDevice.getName().c_str();
    int rssi = advertisedDevice.getRSSI();

    if (nombre.length() > 0) {
      Serial.printf("Dispositivo: %s - RSSI: %d\n", nombre.c_str(), rssi);
      enviarDatos(nombre, rssi);
    }
  }
};

void enviarDatos(String nombre, int rssi) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    // Crear el cuerpo del mensaje
    String postData = "nombre=" + nombre + "&rssi=" + String(rssi);

    // Enviar la solicitud POST
    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.printf("Datos enviados: %d, Respuesta: %s\n", httpResponseCode, response.c_str());
    } else {
      Serial.printf("Error al enviar datos: %d\n", httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("Wi-Fi no conectado, no se enviaron datos.");
  }
}

void loop() {
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  pBLEScan->start(10, false);  // Escaneo cada 10 segundos
  delay(1000);  // Pausa antes del siguiente escaneo
}




