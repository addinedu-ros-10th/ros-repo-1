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

// LED 핀
const int LED_RED_PIN    = 26;  // RED
const int LED_YELLOW_PIN = 25;  // YELLOW red
const int LED_BLUE_PIN   = 32;  // BLUE
const int LED_GREEN_PIN  = 27;  // GREEN

// HTTP 서버
WebServer server(80);

// 서보
Servo servo1;
Servo servo2;

int servo1Angle = 90;
int servo2Angle = 90;

int servoMinUs = 500;
int servoMaxUs = 2500;

// LED 상태 (0=OFF, 1=ON)
int ledRedState    = 0;
int ledYellowState = 0;
int ledBlueState   = 0;
int ledGreenState  = 0;

// ★ 서보 속도 조절용 (값이 클수록 느려짐)
const int SERVO_STEP_DELAY_MS = 30;   // 지금 체감 속도 10 → 5 정도 느낌
const int SERVO_STEP_DEG      = 1;    // 1도씩 이동

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

// ===== 서보를 부드럽게 이동시키는 함수 =====
void moveServoSmooth(Servo &servo, int &currentAngle, int targetAngle) {
  if (targetAngle == currentAngle) return;

  int step = (targetAngle > currentAngle) ? SERVO_STEP_DEG : -SERVO_STEP_DEG;

  for (int a = currentAngle; a != targetAngle; a += step) {
    servo.write(a);
    delay(SERVO_STEP_DELAY_MS);
  }
  // 마지막 목표 각도 보정
  servo.write(targetAngle);
  currentAngle = targetAngle;
}

// ===== LED 상태를 실제 핀에 반영 =====
void applyLedStates() {
  digitalWrite(LED_RED_PIN,    ledRedState    ? HIGH : LOW);
  digitalWrite(LED_YELLOW_PIN, ledYellowState ? HIGH : LOW);
  digitalWrite(LED_BLUE_PIN,   ledBlueState   ? HIGH : LOW);
  digitalWrite(LED_GREEN_PIN,  ledGreenState  ? HIGH : LOW);
}

// ========== Health ==========
void handleHealth() {
  addCORS();
  DynamicJsonDocument doc(512);
  doc["status"] = "ok";
  doc["device"] = DEVICE_ID;
  doc["servo1"] = servo1Angle;
  doc["servo2"] = servo2Angle;
  doc["ip"] = WiFi.localIP().toString();

  JsonObject leds = doc.createNestedObject("leds");
  leds["red"]    = ledRedState;
  leds["yellow"] = ledYellowState;
  leds["blue"]   = ledBlueState;
  leds["green"]  = ledGreenState;

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

  // ★ 부드럽고 느리게 이동
  moveServoSmooth(servo1, servo1Angle, angle);

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

  // ★ 부드럽고 느리게 이동
  moveServoSmooth(servo2, servo2Angle, angle);

  DynamicJsonDocument doc(256);
  doc["status"]  = "success";
  doc["device"]  = DEVICE_ID;
  doc["servo"]   = 2;
  doc["angle"]   = servo2Angle;
  sendJson(200, doc);
}

// ========== LEDs ==========
// GET: 현재 LED 상태 조회
void handleGetLeds() {
  addCORS();
  DynamicJsonDocument doc(256);
  doc["status"] = "success";
  doc["device"] = DEVICE_ID;

  JsonObject leds = doc.createNestedObject("leds");
  leds["red"]    = ledRedState;
  leds["yellow"] = ledYellowState;
  leds["blue"]   = ledBlueState;
  leds["green"]  = ledGreenState;

  sendJson(200, doc);
}

// POST: LED 상태 변경
// Body 예시:
// {
//   "red": 1,
//   "yellow": 0,
//   "blue": 1,
//   "green": 0
// }
void handlePostLeds() {
  addCORS();
  DynamicJsonDocument body(256);

  if (!server.hasArg("plain") || deserializeJson(body, server.arg("plain"))) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "Invalid JSON";
    sendJson(400, err);
    return;
  }

  // 각 색상은 선택적으로 보낼 수 있음 (보낸 것만 변경)
  if (body.containsKey("red")) {
    ledRedState = body["red"] ? 1 : 0;
  }
  if (body.containsKey("yellow")) {
    ledYellowState = body["yellow"] ? 1 : 0;
  }
  if (body.containsKey("blue")) {
    ledBlueState = body["blue"] ? 1 : 0;
  }
  if (body.containsKey("green")) {
    ledGreenState = body["green"] ? 1 : 0;
  }

  // 실제 핀에 반영
  applyLedStates();

  DynamicJsonDocument doc(256);
  doc["status"] = "success";
  doc["device"] = DEVICE_ID;
  JsonObject leds = doc.createNestedObject("leds");
  leds["red"]    = ledRedState;
  leds["yellow"] = ledYellowState;
  leds["blue"]   = ledBlueState;
  leds["green"]  = ledGreenState;

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

  // LED 핀 초기화
  pinMode(LED_RED_PIN,    OUTPUT);
  pinMode(LED_YELLOW_PIN, OUTPUT);
  pinMode(LED_BLUE_PIN,   OUTPUT);
  pinMode(LED_GREEN_PIN,  OUTPUT);
  applyLedStates();  // 모두 OFF

  // Health
  server.on("/health", HTTP_GET, handleHealth);

  // Servo1
  server.on(String("/control/") + DEVICE_ID + "/servo1", HTTP_GET,  handleGetServo1);
  server.on(String("/control/") + DEVICE_ID + "/servo1", HTTP_POST, handlePostServo1);
  server.on(String("/control/") + DEVICE_ID + "/servo1", HTTP_OPTIONS, handleOptions);

  // Servo2
  server.on(String("/control/") + DEVICE_ID + "/servo2", HTTP_GET,  handleGetServo2);
  server.on(String("/control/") + DEVICE_ID + "/servo2", HTTP_POST, handlePostServo2);
  server.on(String("/control/") + DEVICE_ID + "/servo2", HTTP_OPTIONS, handleOptions);

  // LEDs
  server.on(String("/control/") + DEVICE_ID + "/leds", HTTP_GET,  handleGetLeds);
  server.on(String("/control/") + DEVICE_ID + "/leds", HTTP_POST, handlePostLeds);
  server.on(String("/control/") + DEVICE_ID + "/leds", HTTP_OPTIONS, handleOptions);

  server.onNotFound(notFound);
  server.begin();
}

void loop() {
  server.handleClient();
}
