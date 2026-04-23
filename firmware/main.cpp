#include "esp_camera.h"
#include <Wire.h>
#include "Adafruit_AMG88xx.h"

// --- Configuration ---
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// I2C Pins for Thermal Sensor (Free pins on ESP32-CAM)
#define I2C_SDA 14
#define I2C_SCL 15

Adafruit_AMG88xx amg;

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);

  // 1. Initialize I2C for Thermal Sensor
  Wire.begin(I2C_SDA, I2C_SCL);
  if (!amg.begin()) {
    Serial.println("Could not find a valid AMG8833 sensor, check wiring!");
    // We don't halt, so the camera can still work
  }

  // 2. Camera Configuration
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Frame size and quality
  if(psramFound()){
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_CIF;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Init Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void loop() {
  // --- PART 1: THERMAL ANALYSIS ---
  float pixels[AMG88XX_PIXEL_ARRAY_SIZE];
  amg.readPixels(pixels);

  float maxTemp = 0;
  float minTemp = 100;
  float sumTemp = 0;

  for(int i=0; i<64; i++){
    float t = pixels[i];
    sumTemp += t;
    if(t > maxTemp) maxTemp = t;
    if(t < minTemp) minTemp = t;
  }

  float avgTemp = sumTemp / 64.0;
  float spread = maxTemp - minTemp;
  
  // Thermal Stress Error Calculation
  float theoreticalLimit = 5.0; // °C
  float errorRange = (abs(spread - theoreticalLimit) / theoreticalLimit) * 100.0;

  // --- PART 2: VISUAL CAPTURE ---
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
  } else {
    // --- PART 3: DATA TRANSMISSION ---
    // Format: JSON-like string for Node.js to parse easily
    Serial.print("{");
    Serial.print("\"avg_t\":"); Serial.print(avgTemp);
    Serial.print(", \"spread\":"); Serial.print(spread);
    Serial.print(", \"error\":"); Serial.print(errorRange);
    Serial.print(", \"status\":"); 
    if(spread > theoreticalLimit && errorRange > 10.0) {
      Serial.print("\"DEFECT\"");
    } else {
      Serial.print("\"GOOD\"");
    }
    Serial.println("}");

    // NOTE: Sending raw image data over Serial can be slow. 
    // Usually, you would send the image via HTTP POST to the server.
    
    esp_camera_fb_return(fb);
  }

  delay(2000); // 2-second sampling rate
}