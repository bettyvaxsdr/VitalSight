#include <OneWire.h>
#include <DallasTemperature.h>

const int oneWireBus = 25;   
const int potPin = 34;
int currentBpm = 0;  

OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  Serial.println("DS18B20 Temperature Sensor Test");

  analogReadResolution(12);
  Serial.println("Pulse Simulator Ready. Turn the knob!");
  
  sensors.begin();
}

void loop() {
  Serial.print("Requesting temperatures...");
  sensors.requestTemperatures();
  Serial.println("DONE");
  
  float tempC = sensors.getTempCByIndex(0);
  float tempF = sensors.toFahrenheit(tempC);

  int rawValue = analogRead(potPin);

  currentBpm = map(rawValue, 0, 4095, 60, 180);

Serial.print("Raw:");
  Serial.print(rawValue);
  Serial.print(",");
  Serial.print("BPM:");
  Serial.println(currentBpm);

  delay(50);

  if(tempC != DEVICE_DISCONNECTED_C) {
    Serial.print("Temperature: ");
    Serial.print(tempC);
    Serial.print("°C  |  ");
    Serial.print(tempF);
    Serial.println("°F");
  } else {
    Serial.println("Error: Could not read temperature data. Check your wiring!");
  }
  
  delay(2000);
}
