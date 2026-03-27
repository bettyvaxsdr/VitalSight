#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>


const char* ssid = "A1-B122";
const char* password = "83CC22BCA5";

const int oneWireBus = 25;
const int potPin = 34;
int currentBpm = 0; 

OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

WebServer server(80);

void handleDataRequest() {
  sensors.requestTemperatures();
  float tempC = sensors.getTempCByIndex(0);
  
  int rawValue = analogRead(potPin);
  currentBpm = map(rawValue, 0, 4095, 60, 180);
  
  JsonDocument doc; 
  
  if (tempC != DEVICE_DISCONNECTED_C) {
    doc["sensor"] = "DS18B20";
    doc["value"] = tempC;
    doc["unit"] = "Celsius";
    doc["status"] = "OK";
  } else {
    doc["sensor"] = "DS18B20";
    doc["value"] = 0;
    doc["unit"] = "Celsius";
    doc["status"] = "Error: Sensor not found";
  }

  doc["bpm"] = "Error: Sensor not found";

  String response;
  serializeJson(doc, response);
  
  server.send(200, "application/json", response);
  
  Serial.print("Sent temperature: ");
  Serial.println(tempC);
  Serial.print(" | BPM: ");
  Serial.println(currentBpm);
}

void setup() {
  Serial.begin(115200);
  Serial.println("DS18B20 Temperature Sensor Test");

  analogReadResolution(12);
  sensors.begin();


  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP()); //за Flask кода

  // Деф. endpoint
  server.on("/data", HTTP_GET, handleDataRequest);

  server.begin();
  Serial.println("HTTP Server started");
}

void loop() {
  server.handleClient();
}
