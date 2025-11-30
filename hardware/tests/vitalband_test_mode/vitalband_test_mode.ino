/*
 * ============================================================================
 * VITALBAND FIRMWARE v1.0 - TESTING MODE
 * Solo lectura de sensores (sin transmisión MQTT)
 * ============================================================================
 * 
 * Esta versión es para testing de hardware sin necesidad de AWS IoT Core.
 * Imprime los datos por Serial cada 2 minutos.
 * 
 * ============================================================================
 */

#include <Wire.h>
#include <ArduinoJson.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"
#include "Adafruit_MPU6050.h"
#include "Adafruit_Sensor.h"
#include <math.h>
#include "esp_sleep.h"

// ============================================================================
// CONFIGURACIÓN DE HARDWARE
// ============================================================================

#define I2C_SDA 8
#define I2C_SCL 10
#define BATTERY_ADC_PIN 4

// MAX30205
#define MAX30205_ADDR_1   0x48
#define MAX30205_ADDR_2   0x4F
#define MAX30205_TEMP_REG 0x00

// Dirección efectiva detectada en initSensors()
uint8_t g_max30205Address = MAX30205_ADDR_2;  // por defecto el que te funcionó

// ============================================================================
// CONFIGURACIÓN
// ============================================================================

#define SLEEP_TIME_SECONDS 120
#define DEVICE_SERIAL "VB-0001"

// ---------------------- Calibración HR / SpO2 ----------------------
// Valores que estuviste usando en el test MAX30102
const float HR_OFFSET   = -26.0f;  // Ajuste fino HR (centrado ~75 BPM)
const float HR_SCALE    =  1.0f;

const float SPO2_OFFSET = -2.0f;   // Sensor suele dar ~2% de más
const float SPO2_SCALE  =  1.0f;

// ---------------------- Calibración batería ------------------------
#define VOLTAGE_DIVIDER_FACTOR  2.0f     // R1=100k, R2=100k
#define BAT_CALIBRATION_FACTOR  0.61f    // Ajustado con multímetro (4.032V)

// ============================================================================
// SENSORES
// ============================================================================

MAX30105 heartSensor;
Adafruit_MPU6050 mpu;

uint32_t irBuffer[100];
uint32_t redBuffer[100];
int32_t spo2, heartRate;
int8_t validSPO2, validHeartRate;

// ============================================================================
// ESTRUCTURA DE DATOS
// ============================================================================

struct SensorData {
  String serial;
  int heart_rate_bpm;
  int spo2_pct;
  float temp_c;
  int motion_level;
  int battery_mv;
  int battery_pct;
};

SensorData currentData;

RTC_DATA_ATTR int bootCount = 0;

// ============================================================================
// PROTOTIPOS
// ============================================================================

bool  initSensors();
void  sampleAllSensors();
void  sampleHeartAndSpO2();
float readTemperature();
int   calculateMotionLevel();
void  readBattery();
void  printJSON();
void  goToSleep();

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  bootCount++;
  
  Serial.begin(115200);
  delay(500);
  
  Serial.println("\n╔═══════════════════════════════════╗");
  Serial.println("║   VITALBAND TEST MODE v1.0        ║");
  Serial.println("╚═══════════════════════════════════╝");
  Serial.printf("Boot #%d | Serial: %s\n\n", bootCount, DEVICE_SERIAL);
  
  currentData.serial = DEVICE_SERIAL;
  
  // Inicializar sensores
  if (initSensors()) {
    Serial.println("✓ Todos los sensores OK\n");
    
    // Muestrear
    sampleAllSensors();
    
    // Mostrar JSON
    printJSON();
    
  } else {
    Serial.println("✗ Error en sensores");
  }
  
  // Dormir
  goToSleep();
}

void loop() {
  // Vacío: todo se hace en setup() y luego deep-sleep
}

// ============================================================================
// INICIALIZACIÓN
// ============================================================================

bool initSensors() {
  Serial.println("Inicializando sensores...");
  
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000);
  
  bool allOK = true;
  
  // --------------------------- MAX30102 ---------------------------
  if (!heartSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("✗ MAX30102");
    allOK = false;
  } else {
    // mismos parámetros de tu test, solo amplitud un poco moderada
    byte ledBrightness = 60;   // 0-255
    byte sampleAverage = 4;
    byte ledMode       = 2;    // Red + IR
    byte sampleRate    = 100;  // 100 Hz
    int  pulseWidth    = 411;
    int  adcRange      = 4096;
    
    heartSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
    heartSensor.setPulseAmplitudeRed(0);
    heartSensor.setPulseAmplitudeIR(0);
    Serial.println("✓ MAX30102");
  }
  
  // --------------------------- MPU6050 ----------------------------
  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("✗ MPU6050");
    allOK = false;
  } else {
    mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
    Serial.println("✓ MPU6050");
  }
  
  // --------------------------- MAX30205 ---------------------------
  // Detectar automáticamente 0x48 o 0x4F (tu módulo usa 0x4F)
  Serial.print("Detectando MAX30205: ");
  bool found = false;
  
  // Probar 0x48
  Wire.beginTransmission(MAX30205_ADDR_1);
  if (Wire.endTransmission() == 0) {
    g_max30205Address = MAX30205_ADDR_1;
    found = true;
  } else {
    // Probar 0x4F
    Wire.beginTransmission(MAX30205_ADDR_2);
    if (Wire.endTransmission() == 0) {
      g_max30205Address = MAX30205_ADDR_2;
      found = true;
    }
  }
  
  if (found) {
    Serial.print("✓ Encontrado en 0x");
    if (g_max30205Address < 16) Serial.print("0");
    Serial.println(g_max30205Address, HEX);
  } else {
    Serial.println("✗ NO detectado (0x48/0x4F)");
    allOK = false;
  }
  
  return allOK;
}

// ============================================================================
// MUESTREO
// ============================================================================

void sampleAllSensors() {
  Serial.println("═══════════════════════════════════");
  Serial.println("MUESTREO DE SENSORES");
  Serial.println("═══════════════════════════════════\n");
  
  // Heart Rate y SpO2
  sampleHeartAndSpO2();
  
  // Temperatura
  currentData.temp_c = readTemperature();
  Serial.printf("🌡️  Temp: %.1f°C\n", currentData.temp_c);
  
  // Movimiento
  currentData.motion_level = calculateMotionLevel();
  Serial.printf("🏃 Motion: %d/10\n", currentData.motion_level);
  
  // Batería
  readBattery();
  Serial.printf("🔋 Bat: %dmV (%d%%)\n\n", currentData.battery_mv, currentData.battery_pct);
  
  Serial.println("═══════════════════════════════════\n");
}

// ------------------------ HR & SpO2 (MAX30102) ------------------------

void sampleHeartAndSpO2() {
  Serial.println("💓 Leyendo MAX30102...");
  
  heartSensor.setPulseAmplitudeRed(60); // mismo que en test
  heartSensor.setPulseAmplitudeIR(60);
  delay(100);
  
  for (byte i = 0; i < 100; i++) {
    while (!heartSensor.available()) heartSensor.check();
    redBuffer[i] = heartSensor.getRed();
    irBuffer[i]  = heartSensor.getIR();
    heartSensor.nextSample();
    if (i % 20 == 0) Serial.print(".");
  }
  Serial.println(" OK");
  
  heartSensor.setPulseAmplitudeRed(0);
  heartSensor.setPulseAmplitudeIR(0);
  
  // Verificar presencia de dedo
  long avgIR = 0;
  for (byte i = 0; i < 100; i++) avgIR += irBuffer[i];
  avgIR /= 100;
  
  Serial.print("IR Promedio: ");
  Serial.println(avgIR);
  
  if (avgIR < 50000) {
    Serial.println("⚠️  Sin dedo, HR/SpO2 = 0\n");
    currentData.heart_rate_bpm = 0;
    currentData.spo2_pct       = 0;
    return;
  }
  
  // Algoritmo original de Maxim
  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, 100,
    redBuffer,
    &spo2, &validSPO2,
    &heartRate, &validHeartRate
  );
  
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
  
  // Manejar armónicos HR > 140 → dividir por 2 (mismo criterio que en test)
  int hrCorrected = heartRate;
  if (validHeartRate && heartRate > 140) {
    hrCorrected = heartRate / 2;
    Serial.println("⚠ Armónico detectado - HR dividido por 2");
  }
  
  // Aplicar calibración (igual que en tu test)
  float hrCalibrated   = hrCorrected * HR_SCALE + HR_OFFSET;
  float spo2Calibrated = spo2         * SPO2_SCALE + SPO2_OFFSET;
  
  // Redondear
  int hrFinal   = (int)round(hrCalibrated);
  int spo2Final = (int)round(spo2Calibrated);
  
  // Validar rangos
  bool hrValid   = (validHeartRate && hrFinal   >= 40 && hrFinal   <= 200);
  bool spo2Valid = (validSPO2      && spo2Final >= 70 && spo2Final <= 100);
  
  currentData.heart_rate_bpm = hrValid   ? hrFinal   : 0;
  currentData.spo2_pct       = spo2Valid ? spo2Final : 0;
  
  Serial.printf("💓 HR (calibrado): %d BPM\n", currentData.heart_rate_bpm);
  Serial.printf("🫁 SpO2 (calibrado): %d%%\n\n", currentData.spo2_pct);
}

// ------------------------ Temperatura (MAX30205) ------------------------

float readTemperature() {
  // Lectura RAW como en tu test, soportando formato extendido
  Wire.beginTransmission(g_max30205Address);
  Wire.write(MAX30205_TEMP_REG);
  if (Wire.endTransmission(false) != 0) {
    Serial.println("⚠️  Error I2C MAX30205");
    return 36.5f; // valor por defecto "humano"
  }
  
  Wire.requestFrom((int)g_max30205Address, 2);
  if (Wire.available() == 2) {
    uint8_t msb = Wire.read();
    uint8_t lsb = Wire.read();
    
    int16_t temp_raw = (int16_t)((msb << 8) | lsb);
    
    // Mismo cálculo robusto que en test_02_max30205_temp:
    // base = raw * 0.00390625; si raw < 0 asumimos formato extendido → +64
    float base        = temp_raw * 0.00390625f;
    float temperature = base;
    
    if (temp_raw < 0) {
      // Formato extendido (two's complement)
      temperature += 64.0f;
    }
    
    return temperature;
  }
  
  Serial.println("⚠️  MAX30205 sin datos, usando 36.5°C por defecto");
  return 36.5f;
}

// ------------------------ Movimiento (MPU6050) ------------------------

int calculateMotionLevel() {
  sensors_event_t a, g, temp;
  float totalMagnitude = 0;
  
  for (int i = 0; i < 10; i++) {
    mpu.getEvent(&a, &g, &temp);
    float magnitude = sqrt(
      a.acceleration.x * a.acceleration.x +
      a.acceleration.y * a.acceleration.y +
      a.acceleration.z * a.acceleration.z
    );
    totalMagnitude += magnitude;
    delay(50);
  }
  
  float avgMagnitude = totalMagnitude / 10.0f;
  
  // Misma lógica que ya tenías (map a 0-10)
  int level = map((int)(avgMagnitude * 10.0f), 98, 150, 0, 10);
  level = constrain(level, 0, 10);
  
  return level;
}

// ------------------------ Batería (ADC) ------------------------

void readBattery() {
  // Promedio de 10 lecturas (como en el test)
  int adcSum = 0;
  for (int i = 0; i < 10; i++) {
    adcSum += analogRead(BATTERY_ADC_PIN);
    delay(10);
  }
  int adcValue = adcSum / 10;
  
  // Voltaje en el pin (0-3.3V)
  float voltageAtPin = (adcValue / 4095.0f) * 3.3f;
  
  // Voltaje real de batería (divisor + calibración)
  float batteryVoltage = voltageAtPin * VOLTAGE_DIVIDER_FACTOR * BAT_CALIBRATION_FACTOR;
  
  currentData.battery_mv = (int)(batteryVoltage * 1000.0f);
  currentData.battery_pct = constrain(
    map(currentData.battery_mv, 3000, 4200, 0, 100),
    0, 100
  );
}

// ============================================================================
// MOSTRAR JSON
// ============================================================================

void printJSON() {
  StaticJsonDocument<256> doc;
  
  doc["serial"]         = currentData.serial;
  doc["heart_rate_bpm"] = currentData.heart_rate_bpm;
  doc["spo2_pct"]       = currentData.spo2_pct;
  doc["temp_c"]         = currentData.temp_c;
  doc["motion_level"]   = currentData.motion_level;
  doc["battery_mv"]     = currentData.battery_mv;
  doc["battery_pct"]    = currentData.battery_pct;
  doc["rssi_dbm"]       = 0;  // No aplica en modo test (sin WiFi)
  
  Serial.println("JSON OUTPUT:");
  Serial.println("───────────────────────────────────");
  serializeJsonPretty(doc, Serial);
  Serial.println("\n───────────────────────────────────\n");
}

// ============================================================================
// SLEEP
// ============================================================================

void goToSleep() {
  Serial.printf("💤 Sleep %ds\n", SLEEP_TIME_SECONDS);
  Serial.println("═══════════════════════════════════\n");
  Serial.flush();
  
  heartSensor.shutDown();
  
  esp_sleep_enable_timer_wakeup((uint64_t)SLEEP_TIME_SECONDS * 1000000ULL);
  esp_deep_sleep_start();
}
