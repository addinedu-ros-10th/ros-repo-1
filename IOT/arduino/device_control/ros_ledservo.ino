/*
 * ESP32 LED + Servo Control HTTP Server
 *
 * - WiFi: SSID/PW 지정
 * - LED:  GPIO 21 (on/off)
 * - Servo: GPIO 5  (0~180도)
 *
 * Endpoint
 *  - GET  /control/{device_id}/led
 *  - POST /control/{device_id}/led        JSON: {"state":"on"|"off"}
 *  - GET  /control/{device_id}/servo
 *  - POST /control/{device_id}/servo      JSON: {"angle":0..180}
 *
 * 필요 라이브러리:
 *  - ArduinoJson (by Benoit Blanchon)
 *  - ESP32Servo  (by Kevin Harrington, John K. Bennett 등)
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// ===== 사용자 설정 =====
const char* WIFI_SSID     = "AIE_509_2.4G";
const char* WIFI_PASSWORD = "addinedu_class1";

const char* DEVICE_ID     = "esp_32";      // ✅ 통일된 device_id
const int   LED_PIN       = 21;            // LED 핀
const int   SERVO_PIN     = 5;             // 서보 핀
// =======================

// HTTP 서버
WebServer server(80);

// LED 상태: "on"/"off"
String ledState = "off";

// 서보 관련
Servo servo;
int   servoAngle = 90;          // 기본 각도
int   servoMinUs = 500;         // 서보 최소 펄스 (us)
int   servoMaxUs = 2500;        // 서보 최대 펄스 (us)

// -------- 공통 유틸 --------
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

// /health
void handleHealth() {
  addCORS();
  DynamicJsonDocument doc(256);
  doc["status"]  = "ok";
  doc["message"] = "ESP32 LED+Servo controller running";
  doc["device"]  = DEVICE_ID;
  doc["ip"]      = WiFi.isConnected() ? WiFi.localIP().toString() : WiFi.softAPIP().toString();
  sendJson(200, doc);
}

// 경로 매칭
bool matchPath(const char* tail) {
  // 기대 경로: /control/{DEVICE_ID}/{tail}
  String expected = String("/control/") + DEVICE_ID + "/" + tail;
  return server.uri().equalsIgnoreCase(expected);
}

// -------- LED --------
// GET: LED 상태
void handleGetLed() {
  if (!matchPath("led")) { notFound(); return; }
  addCORS();
  DynamicJsonDocument doc(256);
  doc["status"]  = "success";
  doc["message"] = "LED state fetched";
  doc["device"]  = DEVICE_ID;
  doc["state"]   = ledState;
  sendJson(200, doc);
}

// POST: LED on/off
void handlePostLed() {
  if (!matchPath("led")) { notFound(); return; }
  addCORS();

  if (!server.hasArg("plain")) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "Missing JSON body";
    sendJson(400, err);
    return;
  }

  DynamicJsonDocument body(256);
  DeserializationError e = deserializeJson(body, server.arg("plain"));
  if (e) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "Invalid JSON";
    sendJson(400, err);
    return;
  }

  String state = body["state"] | "";
  state.toLowerCase();

  if (state != "on" && state != "off") {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "state must be 'on' or 'off'";
    sendJson(400, err);
    return;
  }

  ledState = state;
  digitalWrite(LED_PIN, (ledState == "on") ? HIGH : LOW);

  DynamicJsonDocument doc(256);
  doc["status"]  = "success";
  doc["message"] = String("LED turned ") + ledState;
  doc["device"]  = DEVICE_ID;
  doc["state"]   = ledState;
  sendJson(200, doc);
}

// -------- SERVO --------
// GET: 각도 조회
void handleGetServo() {
  if (!matchPath("servo")) { notFound(); return; }
  addCORS();
  DynamicJsonDocument doc(256);
  doc["status"]  = "success";
  doc["message"] = "Servo angle fetched";
  doc["device"]  = DEVICE_ID;
  doc["angle"]   = servoAngle;
  sendJson(200, doc);
}

// POST: 각도 변경 JSON: {"angle":0..180}
void handlePostServo() {
  if (!matchPath("servo")) { notFound(); return; }
  addCORS();

  if (!server.hasArg("plain")) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "Missing JSON body";
    sendJson(400, err);
    return;
  }

  DynamicJsonDocument body(256);
  DeserializationError e = deserializeJson(body, server.arg("plain"));
  if (e) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "Invalid JSON";
    sendJson(400, err);
    return;
  }

  if (!body.containsKey("angle")) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "angle is required (0..180)";
    sendJson(400, err);
    return;
  }

  int angle = body["angle"];
  if (angle < 0 || angle > 180) {
    DynamicJsonDocument err(256);
    err["status"]  = "error";
    err["message"] = "angle must be 0..180";
    sendJson(400, err);
    return;
  }

  servoAngle = angle;
  servo.write(servoAngle);

  DynamicJsonDocument doc(256);
  doc["status"]  = "success";
  doc["message"] = "Servo angle updated";
  doc["device"]  = DEVICE_ID;
  doc["angle"]   = servoAngle;
  sendJson(200, doc);
}

// -------- SETUP & LOOP --------
void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW); // LED 초기 off

  Serial.begin(115200);
  delay(200);

  Serial.println();
  Serial.println("=== ESP32 LED+Servo HTTP Controller ===");
  Serial.print("SSID: "); Serial.println(WIFI_SSID);

  // 서보 초기화
  servo.attach(SERVO_PIN, servoMinUs, servoMaxUs);
  servo.write(servoAngle); // 초기 90도

  // WiFi 연결
  Serial.println("Connecting WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 60) {
    delay(500);
    Serial.print(".");
    tries++;
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi connected. IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connect timeout. Starting AP as fallback...");
    WiFi.mode(WIFI_AP);
    WiFi.softAP("ESP32-CTRL", "esp32ctrl123");
    Serial.print("AP IP: ");
    Serial.println(WiFi.softAPIP());
  }

  // 라우팅
  server.on("/health", HTTP_GET, handleHealth);

  // LED
  server.on(String("/control/") + DEVICE_ID + "/led", HTTP_GET, handleGetLed);
  server.on(String("/control/") + DEVICE_ID + "/led", HTTP_POST, handlePostLed);
  server.on(String("/control/") + DEVICE_ID + "/led", HTTP_OPTIONS, handleOptions);

  // SERVO
  server.on(String("/control/") + DEVICE_ID + "/servo", HTTP_GET, handleGetServo);
  server.on(String("/control/") + DEVICE_ID + "/servo", HTTP_POST, handlePostServo);
  server.on(String("/control/") + DEVICE_ID + "/servo", HTTP_OPTIONS, handleOptions);

  server.onNotFound(notFound);
  server.begin();

  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}
