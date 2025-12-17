#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// ===== 사용자 설정 =====
const char* WIFI_SSID     = "AIE_509_2.4G";
const char* WIFI_PASSWORD = "addinedu_class1";

const char* DEVICE_ID     = "esp_32";      

// 서보 핀
const int SERVO1_PIN = 5;   
const int SERVO2_PIN = 18;  

// HTTP 서버
WebServer server(80);

// 서보
Servo servo1;
Servo servo2;

int servo1Angle = 90;
int servo2Angle = 90;

int servoMinUs = 500;
int servoMaxUs = 2500;

void addCORS() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
}

void handleOptions() {
  addCORS();
  server.send(204);
}

void sendJson(int code, const JsonDocument& doc) {
  String out;
  serializeJson(doc, out);
  server.send(code, "application/json", out);
}

void notFound() {
  addCORS();
  DynamicJsonDocument doc(256);
  doc["status"] = "error";
  doc["message"] = "Not Found";
  sendJson(404, doc);
}

// ========== Health ==========
void handleHealth() {
  addCORS();
  DynamicJsonDocument doc(256);
  doc["status"] = "ok";
  doc["device"] = DEVICE_ID;
  doc["servo1"] = servo1Angle;
  doc["servo2"] = servo2Angle;
  doc["ip"] = WiFi.localIP().toString();
  sendJson(200, doc);
}

// ========== Servo1 ==========
void handleGetServo1() {
  addCORS();
  DynamicJsonDocument doc(256);
  doc["status"] = "success";
  doc["device"] = DEVICE_ID;
  doc["servo"] = 1;
  doc["angle"] = servo1Angle;
  sendJson(200, doc);
}

void handlePostServo1() {
  addCORS();
  DynamicJsonDocument body(256);

  if (!server.hasArg("plain") || deserializeJson(body, server.arg("plain"))) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "Invalid JSON";
    sendJson(400, err);
    return;
  }

  if (!body.containsKey("angle")) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "angle is required";
    sendJson(400, err);
    return;
  }

  int angle = body["angle"];
  if (angle < 0 || angle > 180) {
    DynamicJsonDocument err(256);
    err["status"] = "error";
    err["message"] = "angle must be 0..180";
    sendJson(400, err);
    return;
  }

  servo1Angle = angle;
  servo1.write(angle);

  DynamicJsonDocument doc(256);
  doc["status"]  = "success";
  doc["device"]  = DEVICE_ID;
  doc["servo"]   = 1;
  doc["angle"]   = servo1Angle;
  sendJson(200, doc);
}

// ========== Servo2 ==========
void handleGetServo2() {
  addCORS();
  DynamicJsonDocument doc(256);
  doc["status"] = "success";
  doc["device"] = DEVICE_ID;
  doc["servo"] = 2;
  doc["angle"] = servo2Angle;
  sendJson(200, doc);
}

void handlePostServo2() {
  addCORS();
  DynamicJsonDocument body(256);

  if (!server.hasArg("plain") || deserializeJson(body, server.arg("plain"))) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "Invalid JSON";
    sendJson(400, err);
    return;
  }

  if (!body.containsKey("angle")) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "angle is required";
    sendJson(400, err);
    return;
  }

  int angle = body["angle"];
  if (angle < 0 || angle > 180) {
    DynamicJsonDocument err(256);
    err["status"] = "error";
    err["message"] = "angle must be 0..180";
    sendJson(400, err);
    return;
  }

  servo2Angle = angle;
  servo2.write(angle);

  DynamicJsonDocument doc(256);
  doc["status"]  = "success";
  doc["device"]  = DEVICE_ID;
  doc["servo"]   = 2;
  doc["angle"]   = servo2Angle;
  sendJson(200, doc);
}

void setup() {
  Serial.begin(115200);
  delay(200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int tries = 0;
  Serial.print("WiFi connecting");
  while (WiFi.status() != WL_CONNECTED && tries < 60) {
    Serial.print(".");
    delay(500);
    tries++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi connected! IP: ");
    Serial.println(WiFi.localIP());
  }

  // 서보 초기화
  servo1.attach(SERVO1_PIN, servoMinUs, servoMaxUs);
  servo2.attach(SERVO2_PIN, servoMinUs, servoMaxUs);

  servo1.write(servo1Angle);
  servo2.write(servo2Angle);

  // Health
  server.on("/health", HTTP_GET, handleHealth);

  // Servo1
  server.on(String("/control/") + DEVICE_ID + "/servo1", HTTP_GET, handleGetServo1);
  server.on(String("/control/") + DEVICE_ID + "/servo1", HTTP_POST, handlePostServo1);
  server.on(String("/control/") + DEVICE_ID + "/servo1", HTTP_OPTIONS, handleOptions);

  // Servo2
  server.on(String("/control/") + DEVICE_ID + "/servo2", HTTP_GET, handleGetServo2);
  server.on(String("/control/") + DEVICE_ID + "/servo2", HTTP_POST, handlePostServo2);
  server.on(String("/control/") + DEVICE_ID + "/servo2", HTTP_OPTIONS, handleOptions);

  server.onNotFound(notFound);
  server.begin();
}

void loop() {
  server.handleClient();
}
