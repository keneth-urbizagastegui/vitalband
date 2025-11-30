/*
 * ============================================================================
 * I2C SCANNER - Detectar dispositivos I2C
 * ============================================================================
 * 
 * Direcciones esperadas:
 * - 0x48 / 0x4F :  MAX30205 (Temperatura)
 * - 0x57 (87):     MAX30102 (Pulso/SpO2)
 * - 0x68 (104):    MPU6050 (Acelerómetro)
 * 
 * ============================================================================
 */

#include <Wire.h>

#define I2C_SDA 8
#define I2C_SCL 10

// Variable para recordar la dirección del sensor de temperatura (MAX30205)
byte tempSensorAddress = 0xFF;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n╔═══════════════════════════════════╗");
  Serial.println("║      I2C SCANNER - VitalBand      ║");
  Serial.println("╚═══════════════════════════════════╝\n");
  
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000); // 400kHz
  
  Serial.println("Escaneando bus I2C...\n");
  
  byte count = 0;
  
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    byte error = Wire.endTransmission();
    
    if (error == 0) {
      Serial.print("✓ Dispositivo encontrado en 0x");
      if (address < 16) Serial.print("0");
      Serial.print(address, HEX);
      Serial.print(" (");
      Serial.print(address);
      Serial.print(") - ");
      
      // Identificar el dispositivo
      switch(address) {
        case 0x48:
        case 0x4F:  // ← muchos módulos MAX30205 vienen en 0x4F
          Serial.println("MAX30205 (Temperatura)");
          // Guardar la dirección del sensor de temperatura
          tempSensorAddress = address;
          break;
        case 0x57:
          Serial.println("MAX30102 (HR/SpO2)");
          break;
        case 0x68:
          Serial.println("MPU6050 (Acelerómetro)");
          break;
        default:
          Serial.println("Desconocido");
          break;
      }
      count++;
    }
    else if (error == 4) {
      Serial.print("✗ Error desconocido en dirección 0x");
      if (address < 16) Serial.print("0");
      Serial.println(address, HEX);
    }
  }
  
  Serial.println("\n═══════════════════════════════════");
  Serial.print("Total de dispositivos encontrados: ");
  Serial.println(count);
  Serial.println("═══════════════════════════════════\n");

  if (tempSensorAddress != 0xFF) {
    Serial.print("✓ Sensor de temperatura MAX30205 detectado en 0x");
    if (tempSensorAddress < 16) Serial.print("0");
    Serial.println(tempSensorAddress, HEX);
  } else {
    Serial.println("⚠️  No se detectó el sensor de temperatura MAX30205 (0x48/0x4F)");
  }
  
  if (count == 0) {
    Serial.println("⚠️  ADVERTENCIA: No se encontraron dispositivos");
    Serial.println("    Verifica las conexiones:");
    Serial.println("    - SDA → GPIO 8");
    Serial.println("    - SCL → GPIO 10");
    Serial.println("    - VCC → 3.3V");
    Serial.println("    - GND → GND");
  }
  else if (count < 3) {
    Serial.println("⚠️  ADVERTENCIA: Se esperaban 3 dispositivos");
    Serial.println("    Faltan algunos sensores");
  }
  else {
    Serial.println("✅ Todos los sensores detectados correctamente");
  }
}

void loop() {
  // Escanear cada 5 segundos (solo conteo rápido)
  delay(5000);
  
  Serial.println("\n[Re-escaneando...]");
  
  byte count = 0;
  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    if (Wire.endTransmission() == 0) {
      count++;
    }
  }
  
  Serial.print("Dispositivos activos: ");
  Serial.println(count);
}
