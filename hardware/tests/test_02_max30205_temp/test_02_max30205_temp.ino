/*
 * ============================================================================
 * MAX30205 - TEST DE TEMPERATURA CORPORAL
 * ============================================================================
 * 
 * Este sketch lee la temperatura del MAX30205 continuamente.
 * 
 * Temperatura normal del cuerpo: 36.1°C - 37.2°C
 * Temperatura ambiente: ~20°C - 25°C
 * 
 * ============================================================================
 */

#include <Wire.h>

#define I2C_SDA 8
#define I2C_SCL 10

// IMPORTANTE: tu módulo está en 0x4F (lo vimos en los ejemplos con la librería)
#define MAX30205_ADDRESS 0x4F
#define TEMP_REGISTER    0x00

// Variables para estadísticas
float tempSum = 0;
float tempMin = 100;
float tempMax = 0;
int sampleCount = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n╔═══════════════════════════════════╗");
  Serial.println("║   MAX30205 - TEST TEMPERATURA     ║");
  Serial.println("╚═══════════════════════════════════╝\n");
  
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000);
  
  // Verificar que el sensor está presente
  Wire.beginTransmission(MAX30205_ADDRESS);
  byte error = Wire.endTransmission();
  
  if (error == 0) {
    Serial.print("✓ MAX30205 detectado en 0x");
    Serial.println(MAX30205_ADDRESS, HEX);
    Serial.println("\nIniciando lecturas continuas...");
    Serial.println("(Presiona el sensor con tu dedo para ver cambios)\n");
    Serial.println("Temp(°C) | Temp(°F) | Estado");
    Serial.println("─────────────────────────────────");
  } else {
    Serial.println("✗ ERROR: MAX30205 no detectado");
    Serial.print("  Verifica la dirección I2C (0x");
    Serial.print(MAX30205_ADDRESS, HEX);
    Serial.println(")");
    Serial.println("  Verifica las conexiones");
    while(1) delay(1000);
  }
}

void loop() {
  float tempC = readTemperature();
  float tempF = (tempC * 9.0 / 5.0) + 32.0;
  
  // Actualizar estadísticas
  tempSum += tempC;
  sampleCount++;
  if (tempC < tempMin) tempMin = tempC;
  if (tempC > tempMax) tempMax = tempC;
  
  // Mostrar lectura
  Serial.print(tempC, 2);
  Serial.print("°C  | ");
  Serial.print(tempF, 2);
  Serial.print("°F  | ");
  
  // Determinar estado
  if (tempC < 25.0) {
    Serial.println("Ambiente (sin contacto)");
  } else if (tempC >= 25.0 && tempC < 34.0) {
    Serial.println("Calentando... (contacto inicial)");
  } else if (tempC >= 34.0 && tempC < 36.0) {
    Serial.println("Superficie de piel");
  } else if (tempC >= 36.0 && tempC < 37.5) {
    Serial.println("✓ Normal (temperatura corporal)");
  } else if (tempC >= 37.5 && tempC < 38.0) {
    Serial.println("⚠ Ligeramente elevada");
  } else if (tempC >= 38.0) {
    Serial.println("⚠⚠ Fiebre detectada");
  }
  
  // Mostrar estadísticas cada 20 lecturas
  if (sampleCount % 20 == 0) {
    Serial.println("\n─── ESTADÍSTICAS ───");
    Serial.print("Promedio: ");
    Serial.print(tempSum / sampleCount, 2);
    Serial.println("°C");
    Serial.print("Mínima:   ");
    Serial.print(tempMin, 2);
    Serial.println("°C");
    Serial.print("Máxima:   ");
    Serial.print(tempMax, 2);
    Serial.println("°C");
    Serial.print("Muestras: ");
    Serial.println(sampleCount);
    Serial.println("───────────────────\n");
  }
  
  delay(1000); // Leer cada segundo
}

float readTemperature() {
  // Señalar el registro de temperatura
  Wire.beginTransmission(MAX30205_ADDRESS);
  Wire.write(TEMP_REGISTER);
  Wire.endTransmission(false); // repeated START
  
  Wire.requestFrom(MAX30205_ADDRESS, (uint8_t)2);
  
  if (Wire.available() == 2) {
    uint8_t msb = Wire.read();
    uint8_t lsb = Wire.read();
    
    // Combinar bytes (16 bits, complemento a 2)
    int16_t temp_raw = (int16_t)((msb << 8) | lsb);

    // Resolución: 1/256 °C por LSB
    float base = temp_raw * 0.00390625f; // 1 / 256
    float temperature = base;

    // Tu sensor está en FORMATO EXTENDIDO:
    // en ese modo, la temperatura física es: T = raw/256 + 64
    // Detectamos extendido por el signo del valor RAW
    if (temp_raw < 0) {
      temperature += 64.0f;
    }
    
    return temperature;
  }
  
  return -999; // Error de lectura
}
