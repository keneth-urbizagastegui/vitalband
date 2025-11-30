/*
 * ============================================================================
 * VITALBAND FIRMWARE v1.0 - PRODUCCIÓN
 * ============================================================================
 * 
 * - Lee HR/SpO2 (MAX30102), temperatura (MAX30205), movimiento (MPU6050),
 *   batería (ADC) y RSSI WiFi.
 * - Publica JSON a AWS IoT Core vía MQTT/TLS.
 * - Deep Sleep entre ciclos para ahorrar batería.
 * 
 * Este archivo ya incorpora todas las correcciones y calibraciones
 * que probaste en los sketches de testing.
 * ============================================================================
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>

#include <Wire.h>
#include <ArduinoJson.h>

#include "MAX30105.h"
#include "spo2_algorithm.h"

#include "Adafruit_MPU6050.h"
#include "Adafruit_Sensor.h"

#include "credentials.h"
#include "esp_sleep.h"
#include <math.h>

// ============================================================================
// CONFIGURACIÓN DE HARDWARE
// ============================================================================

#define I2C_SDA        8
#define I2C_SCL        10
#define BATTERY_ADC_PIN 4

// ============================================================================
// CONFIGURACIÓN GENERAL
// ============================================================================

// Cambia a 0 si quieres probar sólo sensores sin WiFi/MQTT
#define ENABLE_AWS_IOT 1

#define SLEEP_TIME_SECONDS 120
#define DEVICE_SERIAL      "VB-0001"

// Umbrales de alerta (sólo para mensajes de debug)
#define HR_ALERT_HIGH    120       // BPM
#define HR_ALERT_LOW     40        // BPM
#define SPO2_ALERT_LOW   90        // %
#define TEMP_ALERT_HIGH  37.5f     // °C
#define BATTERY_ALERT_LOW 20       // %

/* --------------------------------------------------------------------------
 * Calibración HR / SpO2 (MAX30102)
 * Estos valores vienen de tu calibración con el pulsioxímetro médico.
 * ------------------------------------------------------------------------*/
const float HR_OFFSET   = -26.0f;  // Ajuste fino de HR
const float HR_SCALE    =  1.0f;

const float SPO2_OFFSET = -2.0f;   // El sensor tiende a ir ~2% alto
const float SPO2_SCALE  =  1.0f;

/* --------------------------------------------------------------------------
 * Calibración temperatura (MAX30205)
 * Usa TEMP_OFFSET_C si quieres ajustar contra un termómetro clínico.
 * ------------------------------------------------------------------------*/
const float TEMP_OFFSET_C = 0.0f;
const float TEMP_SCALE    = 1.0f;

/* --------------------------------------------------------------------------
 * Calibración batería (ADC + divisor de tensión)
 * Divisor: R1=100k, R2=100k  => factor ≈ 2.0
 * BAT_CALIBRATION_FACTOR viene del sketch de test_05.
 * ------------------------------------------------------------------------*/
const float VOLTAGE_DIVIDER_FACTOR = 2.0f;
const float BAT_CALIBRATION_FACTOR = 1.0015f;  // ajustado con tu multímetro

// Dirección real del MAX30205 en tu placa (según tests): 0x4F
const uint8_t MAX30205_ADDR   = 0x4F;
const uint8_t MAX30205_TEMP_REG = 0x00;

// ============================================================================
// ESTADO DEL FIRMWARE
// ============================================================================

enum FirmwareState {
  STATE_INIT = 0,
  STATE_SAMPLE_SENSORS,
  STATE_CONNECT_WIFI,
  STATE_CONNECT_MQTT,
  STATE_PUBLISH,
  STATE_SLEEP
};

FirmwareState currentState = STATE_INIT;

// ============================================================================
// OBJETOS GLOBALES
// ============================================================================

MAX30105 heartSensor;
Adafruit_MPU6050 mpu;

WiFiClientSecure net;
PubSubClient mqttClient(net);

uint32_t irBuffer[100];
uint32_t redBuffer[100];

int32_t spo2;
int8_t  validSPO2;
int32_t heartRate;
int8_t  validHeartRate;

// Estructura de datos a enviar
struct SensorData {
  String serial;
  int    heart_rate_bpm;
  int    spo2_pct;
  float  temp_c;
  int    motion_level;
  int    battery_mv;
  int    battery_pct;
  int    rssi_dbm;
};

SensorData currentData;

RTC_DATA_ATTR int bootCount = 0;

// ============================================================================
// PROTOTIPOS
// ============================================================================

bool initSensors();
void runStateMachine();
void sampleAllSensors();
void sampleHeartAndSpO2();
float readTemperature();
int   calculateMotionLevel();
void  readBattery();
void  printJSON();
void  checkAlerts();
bool  connectWiFi();
bool  connectMQTT();
void  publishData();
void  goToSleep();

// ============================================================================
// SETUP / LOOP
// ============================================================================

void setup() {
  bootCount++;

  Serial.begin(115200);
  delay(500);

  Serial.println();
  Serial.println("╔═══════════════════════════════════╗");
  Serial.println("║      VITALBAND FIRMWARE v1.0      ║");
  Serial.println("╚═══════════════════════════════════╝");
  Serial.printf("Boot #%d | Serial: %s\n\n", bootCount, DEVICE_SERIAL);

  currentData.serial = DEVICE_SERIAL;

  // I2C
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000);

  // ADC batería
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);

  // WiFi / MQTT (configuración básica, aún sin conectar)
  WiFi.mode(WIFI_STA);

  mqttClient.setServer(AWS_IOT_ENDPOINT, AWS_IOT_PORT);
  mqttClient.setBufferSize(512);

  // Certificados TLS
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);

  currentState = STATE_INIT;

  // Ejecuta la máquina de estados una vez por ciclo de arranque
  while (true) {
    runStateMachine();
    // goToSleep() no vuelve
  }
}

void loop() {
  // No se usa: todo se ejecuta en setup() + deep sleep
}

// ============================================================================
// MÁQUINA DE ESTADOS
// ============================================================================

void runStateMachine() {
  switch (currentState) {
    case STATE_INIT:
      Serial.println("[STATE] INIT");
      Serial.println("Inicializando I2C y sensores...");

      if (!initSensors()) {
        Serial.println("✗ Uno o más sensores no respondieron");
      } else {
        Serial.println("✓ Todos los sensores OK");
      }

      currentState = STATE_SAMPLE_SENSORS;
      break;

    case STATE_SAMPLE_SENSORS:
      Serial.println();
      Serial.println("[STATE] SAMPLE_SENSORS");
      sampleAllSensors();
      checkAlerts();

#if ENABLE_AWS_IOT
      currentState = STATE_CONNECT_WIFI;
#else
      currentState = STATE_SLEEP;
#endif
      break;

    case STATE_CONNECT_WIFI:
      Serial.println();
      Serial.println("[STATE] CONNECT_WIFI");
      if (connectWiFi()) {
        currentData.rssi_dbm = WiFi.RSSI();
        currentState = STATE_CONNECT_MQTT;
      } else {
        currentData.rssi_dbm = 0;
        currentState = STATE_SLEEP;
      }
      break;

    case STATE_CONNECT_MQTT:
      Serial.println();
      Serial.println("[STATE] CONNECT_MQTT");
      if (connectMQTT()) {
        currentState = STATE_PUBLISH;
      } else {
        currentState = STATE_SLEEP;
      }
      break;

    case STATE_PUBLISH:
      Serial.println();
      Serial.println("[STATE] PUBLISH");
      publishData();
      currentState = STATE_SLEEP;
      break;

    case STATE_SLEEP:
    default:
      Serial.println();
      Serial.println("[STATE] SLEEP");
      goToSleep();
      break;
  }
}

// ============================================================================
// INICIALIZACIÓN DE SENSORES
// ============================================================================

bool initSensors() {
  bool allOK = true;

  // MAX30102
  if (!heartSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("✗ MAX30102 no detectado");
    allOK = false;
  } else {
    byte ledBrightness = 50;   // 0-255
    byte sampleAverage = 4;    // 1,2,4,8,16,32
    byte ledMode       = 2;    // 2 = Red + IR
    byte sampleRate    = 100;  // Hz
    int  pulseWidth    = 411;  // µs
    int  adcRange      = 4096; // nA

    heartSensor.setup(ledBrightness, sampleAverage, ledMode,
                      sampleRate, pulseWidth, adcRange);
    heartSensor.setPulseAmplitudeRed(0);
    heartSensor.setPulseAmplitudeIR(0);

    Serial.println("✓ MAX30102");
  }

  // MPU6050
  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("✗ MPU6050 no detectado");
    allOK = false;
  } else {
    mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
    mpu.setGyroRange(MPU6050_RANGE_250_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("✓ MPU6050");
  }

  // MAX30205
  Wire.beginTransmission(MAX30205_ADDR);
  uint8_t err = Wire.endTransmission();
  if (err == 0) {
    Serial.print("✓ Detectando MAX30205: ");
    Serial.print("✓ Encontrado en 0x");
    Serial.println(MAX30205_ADDR, HEX);
  } else {
    Serial.println("✗ MAX30205 no detectado");
    allOK = false;
  }

  return allOK;
}

// ============================================================================
// MUESTREO DE SENSORES
// ============================================================================

void sampleAllSensors() {
  Serial.println();
  Serial.println("═══════════════════════════════════");
  Serial.println("MUESTREO DE SENSORES");
  Serial.println("═══════════════════════════════════");

  // HR / SpO2
  sampleHeartAndSpO2();

  // Temperatura
  currentData.temp_c = readTemperature();
  Serial.printf("🌡️  Temp: %.2f°C\n", currentData.temp_c);

  // Movimiento
  currentData.motion_level = calculateMotionLevel();
  Serial.printf("🏃 Motion: %d/10\n", currentData.motion_level);

  // Batería
  readBattery();
  Serial.printf("🔋 Bat: %dmV (%d%%)\n",
                currentData.battery_mv,
                currentData.battery_pct);

  Serial.println("═══════════════════════════════════");
}

void sampleHeartAndSpO2() {
  Serial.println("💓 Muestreando MAX30102...");

  heartSensor.setPulseAmplitudeRed(50);
  heartSensor.setPulseAmplitudeIR(50);
  delay(100);

  for (byte i = 0; i < 100; i++) {
    while (!heartSensor.available()) {
      heartSensor.check();
    }

    redBuffer[i] = heartSensor.getRed();
    irBuffer[i]  = heartSensor.getIR();
    heartSensor.nextSample();

    if (i % 10 == 0) Serial.print("█");
  }
  Serial.println(" 100%");

  heartSensor.setPulseAmplitudeRed(0);
  heartSensor.setPulseAmplitudeIR(0);

  long avgIR = 0;
  for (byte i = 0; i < 100; i++) {
    avgIR += irBuffer[i];
  }
  avgIR /= 100;

  Serial.print("IR Promedio: ");
  Serial.println(avgIR);

  // Detección de dedo
  if (avgIR < 50000) {
    Serial.println("⚠️  Sin dedo, HR/SpO2 = 0");
    currentData.heart_rate_bpm = 0;
    currentData.spo2_pct       = 0;
    return;
  }

  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, 100,
    redBuffer,
    &spo2, &validSPO2,
    &heartRate, &validHeartRate
  );

  Serial.println("─── VALORES RAW ───");
  Serial.print("HR Raw: ");
  Serial.print(heartRate);
  Serial.print(" BPM (Valid: ");
  Serial.print(validHeartRate ? "Yes" : "No");
  Serial.println(")");

  Serial.print("SpO2 Raw: ");
  Serial.print(spo2);
  Serial.print("% (Valid: ");
  Serial.print(validSPO2 ? "Yes" : "No");
  Serial.println(")");

  // Corrección de armónicos
  int hrProcessed = heartRate;
  if (validHeartRate && heartRate > 140) {
    hrProcessed = heartRate / 2;
    Serial.println("⚠ Armónico detectado - HR dividido por 2");
  }

  // Aplicar calibración lineal
  int hrFinal   = 0;
  int spo2Final = 0;

  if (validHeartRate) {
    float hrCal = hrProcessed * HR_SCALE + HR_OFFSET;
    if (hrCal < 0) hrCal = 0;
    hrFinal = (int)(hrCal + 0.5f);
  }

  if (validSPO2) {
    float spo2Cal = spo2 * SPO2_SCALE + SPO2_OFFSET;
    if (spo2Cal < 0) spo2Cal = 0;
    spo2Final = (int)(spo2Cal + 0.5f);
  }

  bool hrValid   = validHeartRate && hrFinal   >= 40 && hrFinal   <= 200;
  bool spo2Valid = validSPO2     && spo2Final >= 70 && spo2Final <= 100;

  if (!hrValid)   hrFinal   = 0;
  if (!spo2Valid) spo2Final = 0;

  currentData.heart_rate_bpm = hrFinal;
  currentData.spo2_pct       = spo2Final;

  Serial.println("─── VALORES FINALES ───");
  Serial.print("HR Final:   ");
  Serial.print(currentData.heart_rate_bpm);
  Serial.println(" BPM");

  Serial.print("SpO2 Final: ");
  Serial.print(currentData.spo2_pct);
  Serial.println(" %");
  Serial.println();
}

float readTemperature() {
  Wire.beginTransmission(MAX30205_ADDR);
  Wire.write(MAX30205_TEMP_REG);
  if (Wire.endTransmission(false) != 0) {
    Serial.println("⚠️  Error I2C MAX30205");
    return NAN;
  }

  Wire.requestFrom((int)MAX30205_ADDR, 2);
  if (Wire.available() != 2) {
    Serial.println("⚠️  Lectura incompleta MAX30205");
    return NAN;
  }

  uint8_t msb = Wire.read();
  uint8_t lsb = Wire.read();

  int16_t raw = (msb << 8) | lsb;
  float tempC = raw * 0.00390625f;  // 1/256 °C

  tempC = tempC * TEMP_SCALE + TEMP_OFFSET_C;
  return tempC;
}

int calculateMotionLevel() {
  sensors_event_t a, g, temp;
  float totalMagnitude = 0.0f;

  for (int i = 0; i < 10; i++) {
    mpu.getEvent(&a, &g, &temp);
    float mag = sqrtf(a.acceleration.x * a.acceleration.x +
                      a.acceleration.y * a.acceleration.y +
                      a.acceleration.z * a.acceleration.z);
    totalMagnitude += mag;
    delay(50);
  }

  float avgMagnitude = totalMagnitude / 10.0f;

  // 1g ≈ 9.8 m/s^2 → en reposo ~1g
  int level = map((int)(avgMagnitude * 10.0f), 98, 150, 0, 10);
  level = constrain(level, 0, 10);
  return level;
}

void readBattery() {
  int adcSum = 0;
  for (int i = 0; i < 10; i++) {
    adcSum += analogRead(BATTERY_ADC_PIN);
    delay(5);
  }
  int adcValue = adcSum / 10;

  float voltageAtPin   = (adcValue / 4095.0f) * 3.3f;
  float batteryVoltage = voltageAtPin * VOLTAGE_DIVIDER_FACTOR * BAT_CALIBRATION_FACTOR;

  currentData.battery_mv   = (int)(batteryVoltage * 1000.0f + 0.5f);
  currentData.battery_pct  = constrain(
    map(currentData.battery_mv, 3000, 4200, 0, 100),
    0, 100
  );
}

// ============================================================================
// ALERTAS (solo mensajes por Serial)
// ============================================================================

void checkAlerts() {
  Serial.println();
  Serial.println("--- Verificando alertas ---");

  bool anyAlert = false;

  if (currentData.heart_rate_bpm == 0 && currentData.spo2_pct == 0) {
    Serial.println("⚠️  HR/SpO2 no disponibles (sin dedo o lectura inválida)");
  } else {
    if (currentData.heart_rate_bpm > HR_ALERT_HIGH) {
      Serial.printf("⚠️  HR alto: %d BPM\n", currentData.heart_rate_bpm);
      anyAlert = true;
    }
    if (currentData.heart_rate_bpm > 0 && currentData.heart_rate_bpm < HR_ALERT_LOW) {
      Serial.printf("⚠️  HR bajo: %d BPM\n", currentData.heart_rate_bpm);
      anyAlert = true;
    }
    if (currentData.spo2_pct > 0 && currentData.spo2_pct < SPO2_ALERT_LOW) {
      Serial.printf("⚠️  SpO2 baja: %d%%\n", currentData.spo2_pct);
      anyAlert = true;
    }
  }

  if (!isnan(currentData.temp_c) && currentData.temp_c > TEMP_ALERT_HIGH) {
    Serial.printf("⚠️  Temperatura alta: %.2f°C\n", currentData.temp_c);
    anyAlert = true;
  }

  if (currentData.battery_pct < BATTERY_ALERT_LOW) {
    Serial.printf("⚠️  Batería baja: %d%%\n", currentData.battery_pct);
    anyAlert = true;
  }

  if (!anyAlert) {
    Serial.println("✓ Todos los valores normales");
  }

  Serial.println("--- Fin verificación ---");
}

// ============================================================================
// WIFI / MQTT
// ============================================================================

bool connectWiFi() {
  if (WIFI_SSID == nullptr || strlen(WIFI_SSID) == 0) {
    Serial.println("⚠️  WIFI_SSID vacío en credentials.h → Omitiendo WiFi/MQTT");
    return false;
  }

  Serial.print("Conectando a WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start   = millis();
  const unsigned long timeout = 15000; // 15s

  while (WiFi.status() != WL_CONNECTED && (millis() - start) < timeout) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ Timeout WiFi");
    return false;
  }

  Serial.println("✓ WiFi conectado");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
  Serial.print("RSSI: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");

  return true;
}

bool connectMQTT() {
  Serial.print("Conectando a MQTT: ");
  Serial.println(AWS_IOT_ENDPOINT);

  String clientId = String("VB-") + DEVICE_SERIAL + "-" + String(bootCount);

  if (!mqttClient.connect(clientId.c_str())) {
    Serial.print("✗ Error MQTT: ");
    Serial.println(mqttClient.state());
    Serial.println("   (Revisa endpoint, certificados y política en AWS)");
    return false;
  }

  Serial.println("✓ MQTT conectado");
  return true;
}

void publishData() {
  StaticJsonDocument<256> doc;

  doc["serial"]          = currentData.serial;
  doc["heart_rate_bpm"]  = currentData.heart_rate_bpm;
  doc["spo2_pct"]        = currentData.spo2_pct;
  doc["temp_c"]          = currentData.temp_c;
  doc["motion_level"]    = currentData.motion_level;
  doc["battery_mv"]      = currentData.battery_mv;
  doc["battery_pct"]     = currentData.battery_pct;
  doc["rssi_dbm"]        = currentData.rssi_dbm;

  char payload[256];
  size_t len = serializeJson(doc, payload);

  Serial.println("--- Publicando datos ---");
  Serial.write(payload, len);
  Serial.println();

  if (mqttClient.publish(AWS_IOT_TOPIC, payload, len)) {
    Serial.println("✓ Datos publicados exitosamente");
  } else {
    Serial.println("✗ Error al publicar datos");
  }

  Serial.println("--- Fin transmisión ---");
}

// ============================================================================
// JSON POR SERIAL (para debugging local)
// ============================================================================

void printJSON() {
  StaticJsonDocument<256> doc;

  doc["serial"]          = currentData.serial;
  doc["heart_rate_bpm"]  = currentData.heart_rate_bpm;
  doc["spo2_pct"]        = currentData.spo2_pct;
  doc["temp_c"]          = currentData.temp_c;
  doc["motion_level"]    = currentData.motion_level;
  doc["battery_mv"]      = currentData.battery_mv;
  doc["battery_pct"]     = currentData.battery_pct;
  doc["rssi_dbm"]        = currentData.rssi_dbm;

  Serial.println("JSON OUTPUT:");
  Serial.println("───────────────────────────────────");
  serializeJsonPretty(doc, Serial);
  Serial.println("\n───────────────────────────────────");
}

// ============================================================================
// DEEP SLEEP
// ============================================================================

void goToSleep() {
  // Imprimir último resumen
  printJSON();

  Serial.println();
  Serial.printf("🩺 HR=%d BPM | SpO2=%d%% | Temp=%.2f°C | Bat=%d%%\n",
                currentData.heart_rate_bpm,
                currentData.spo2_pct,
                currentData.temp_c,
                currentData.battery_pct);

  Serial.printf("💤 Entrando en Deep Sleep por %d segundos\n",
                SLEEP_TIME_SECONDS);
  Serial.println("═══════════════════════════════════");
  Serial.flush();

  heartSensor.shutDown();
  mpu.setSleepEnabled(true);
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);

  esp_sleep_enable_timer_wakeup((uint64_t)SLEEP_TIME_SECONDS * 1000000ULL);
  esp_deep_sleep_start();
}
