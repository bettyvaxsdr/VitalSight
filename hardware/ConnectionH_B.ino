#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const char* ssid = "A1-B122";
const char* password = "83CC22BCA5";

const char* serverUrl = "http://192.168.8.24:5000/sensor-data"; 

const int oneWireBus = 25;
const int potPin = 34;
int currentBpm = 0; 

unsigned long previousMillis = 0;
const long interval = 15000;

OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
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
  Serial.println(WiFi.localIP());
}

void loop() {
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis; 
    
    Serial.println("\n--- Timer Triggered: Preparing to send data ---");
    sendData(); 
  }
}

void sendData() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    sensors.requestTemperatures();
    float tempC = sensors.getTempCByIndex(0);
    int rawValue = analogRead(potPin);
    currentBpm = map(rawValue, 0, 4095, 60, 180);

    JsonDocument doc;
    doc["sensor"] = "DS18B20";
    doc["value"] = (tempC != DEVICE_DISCONNECTED_C) ? tempC : 0;
    doc["bpm"] = currentBpm;

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    Serial.print("Sending JSON: ");
    Serial.println(jsonPayload);

    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("SUCCESS! Backend responded with code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("FAILED! Error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
    Serial.println("--- Done ---");
  } else {
    Serial.println("Error: WiFi Disconnected. Cannot send data.");
  }
}