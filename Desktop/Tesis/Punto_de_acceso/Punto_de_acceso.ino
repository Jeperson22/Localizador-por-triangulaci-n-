#include <ESP8266WiFi.h>

// Nombre del punto de acceso y contraseña
const char* ssid = "Cocina";
const char* password = "12345678";

void setup() {
  // Iniciar el monitor serie
  Serial.begin(115200);
  delay(10);

  // Configurar el ESP8266 como punto de acceso
  Serial.println("Configuring access point...");
  WiFi.softAP(ssid, password);

  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
}

void loop() {
  // El ESP8266 permanecerá en modo AP, permitiendo que los dispositivos se conecten
}
