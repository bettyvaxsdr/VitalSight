#include <OneWire.h>
#include <DallasTemperature.h>

const int oneWireBus = 25;     

OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

void setup() {
  Serial.begin(115200);
  Serial.println("DS18B20 Temperature Sensor Test");
  
  sensors.begin();
}

void loop() {
  Serial.print("Requesting temperatures...");
  sensors.requestTemperatures();
  Serial.println("DONE");
  
  float tempC = sensors.getTempCByIndex(0);
  float tempF = sensors.toFahrenheit(tempC);

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
