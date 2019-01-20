/******************************************************************************
 * Copyright 2018 Google
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *****************************************************************************/
#include "esp32-mqtt.h"

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  setupCloudIoT();
}

uint32_t lastMillis = 0;

void loop() {
  mqttClient->loop();
  delay(1500);  // Delay the loop so we arn't calling so often
  
  if (!mqttClient->connected()) {
    // Keep the mqtt connection
    connect();
  }

  // publish a message roughly every second.
  if (millis() - lastMillis > 1000) {
    lastMillis = millis();
    while (Serial2.available())
    { 
      // Recieving the data from the BLE bluetooth board
      String code = "";
      char r = Serial2.read();
      if (r == 64)
      {
        r = Serial2.read();
        while (!(r == 35))
        {
          code += String(r);
          r = Serial2.read();
        }
      }
      // Send the code to the cloud server
      publishTelemetry(code);
    }
  }
}
