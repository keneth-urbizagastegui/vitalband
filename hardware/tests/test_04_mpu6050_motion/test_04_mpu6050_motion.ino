/*
 * ============================================================================
 * MPU6050 - TEST DE ACELERÓMETRO Y MOVIMIENTO
 * ============================================================================
 * 
 * Este sketch prueba el MPU6050 y calcula el nivel de movimiento.
 * 
 * Funciones:
 * - Leer aceleración X, Y, Z
 * - Leer giroscopio X, Y, Z
 * - Calcular magnitud de movimiento
 * - Detectar pasos (básico)
 * - Calibración de offset
 * 
 * Cómo usar:
 * 1. Dejar quieto sobre mesa → Calibración automática
 * 2. Mover la pulsera → Ver cambios en aceleración
 * 3. Simular pasos → Contador de pasos
 * 
 * ============================================================================
 */

#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

#define I2C_SDA 8
#define I2C_SCL 10

Adafruit_MPU6050 mpu;

// Variables para detección de pasos
float lastMagnitude = 0;
int stepCount = 0;
unsigned long lastStepTime = 0;
#define STEP_THRESHOLD 12.0  // m/s²
#define STEP_MIN_INTERVAL 300  // ms entre pasos

// Variables para calibración
float accelOffsetX = 0;
float accelOffsetY = 0;
float accelOffsetZ = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n╔═══════════════════════════════════╗");
  Serial.println("║     MPU6050 - TEST MOVIMIENTO     ║");
  Serial.println("╚═══════════════════════════════════╝\n");
  
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000);
  
  // Inicializar MPU6050
  if (!mpu.begin(0x68, &Wire)) {
    Serial.println("✗ ERROR: MPU6050 no detectado");
    Serial.println("  Verifica la dirección I2C (0x68)");
    Serial.println("  Verifica las conexiones");
    while (1) delay(1000);
  }
  
  Serial.println("✓ MPU6050 detectado\n");
  
  // Configuración
  mpu.setAccelerometerRange(MPU6050_RANGE_2_G);
  mpu.setGyroRange(MPU6050_RANGE_250_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
  
  Serial.println("Configuración:");
  Serial.print("  Accel Range: ±2G\n");
  Serial.print("  Gyro Range:  ±250°/s\n");
  Serial.print("  Filter:      21 Hz\n\n");
  
  // Calibración
  Serial.println("🔧 CALIBRANDO...");
  Serial.println("   Mantén el sensor COMPLETAMENTE QUIETO");
  Serial.println("   sobre una superficie plana\n");
  
  calibrate();
  
  Serial.println("\n✅ Calibración completada\n");
  Serial.println("═══════════════════════════════════");
  Serial.println("INICIANDO MONITOREO");
  Serial.println("═══════════════════════════════════\n");
  Serial.println("Mueve el sensor para ver cambios");
  Serial.println("Simula caminar para detectar pasos\n");
  
  delay(2000);
}

void loop() {
  // Leer datos del sensor
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);
  
  // Aplicar offset de calibración
  float ax = a.acceleration.x - accelOffsetX;
  float ay = a.acceleration.y - accelOffsetY;
  float az = a.acceleration.z - accelOffsetZ;
  
  // Calcular magnitud total
  float magnitude = sqrt(ax * ax + ay * ay + az * az);
  
  // Detección de pasos (algoritmo simple)
  if (magnitude > STEP_THRESHOLD && 
      (millis() - lastStepTime) > STEP_MIN_INTERVAL) {
    
    // Verificar que sea un pico (magnitud aumenta y luego disminuye)
    if (magnitude > lastMagnitude) {
      stepCount++;
      lastStepTime = millis();
      
      Serial.print("\n👣 PASO DETECTADO! Total: ");
      Serial.println(stepCount);
    }
  }
  
  lastMagnitude = magnitude;
  
  // Calcular nivel de movimiento (0-10)
  int motionLevel = constrain(map(magnitude * 10, 98, 150, 0, 10), 0, 10);
  
  // Mostrar datos cada 500ms
  static unsigned long lastDisplay = 0;
  if (millis() - lastDisplay > 500) {
    lastDisplay = millis();
    
    Serial.println("───────────────────────────────────");
    
    // Aceleración
    Serial.println("ACELERACIÓN (m/s²):");
    Serial.print("  X: ");
    Serial.print(ax, 2);
    Serial.print("  Y: ");
    Serial.print(ay, 2);
    Serial.print("  Z: ");
    Serial.println(az, 2);
    
    // Giroscopio
    Serial.println("GIROSCOPIO (rad/s):");
    Serial.print("  X: ");
    Serial.print(g.gyro.x, 2);
    Serial.print("  Y: ");
    Serial.print(g.gyro.y, 2);
    Serial.print("  Z: ");
    Serial.println(g.gyro.z, 2);
    
    // Magnitud y movimiento
    Serial.print("MAGNITUD: ");
    Serial.print(magnitude, 2);
    Serial.println(" m/s²");
    
    Serial.print("MOTION LEVEL: ");
    Serial.print(motionLevel);
    Serial.print("/10  ");
    
    // Barra de progreso visual
    Serial.print("[");
    for (int i = 0; i < 10; i++) {
      if (i < motionLevel) {
        Serial.print("█");
      } else {
        Serial.print("░");
      }
    }
    Serial.println("]");
    
    // Estado
    Serial.print("ESTADO: ");
    if (motionLevel == 0) {
      Serial.println("Quieto");
    } else if (motionLevel < 3) {
      Serial.println("Movimiento leve");
    } else if (motionLevel < 6) {
      Serial.println("Movimiento moderado");
    } else {
      Serial.println("Movimiento intenso");
    }
    
    // Temperatura interna
    Serial.print("TEMP SENSOR: ");
    Serial.print(temp.temperature);
    Serial.println("°C");
    
    Serial.print("PASOS: ");
    Serial.println(stepCount);
    
    Serial.println();
  }
  
  delay(50);
}

void calibrate() {
  const int samples = 100;
  float sumX = 0, sumY = 0, sumZ = 0;
  
  for (int i = 0; i < samples; i++) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    
    sumX += a.acceleration.x;
    sumY += a.acceleration.y;
    sumZ += a.acceleration.z;
    
    if (i % 10 == 0) {
      Serial.print(".");
    }
    
    delay(10);
  }
  
  // Calcular offsets (esperamos ~0, ~0, ~9.8 en reposo)
  accelOffsetX = sumX / samples;
  accelOffsetY = sumY / samples;
  accelOffsetZ = (sumZ / samples) - 9.8;  // Restar gravedad
  
  Serial.println(" OK");
  Serial.println("\nOffsets calculados:");
  Serial.print("  X: ");
  Serial.println(accelOffsetX, 3);
  Serial.print("  Y: ");
  Serial.println(accelOffsetY, 3);
  Serial.print("  Z: ");
  Serial.println(accelOffsetZ, 3);
}
