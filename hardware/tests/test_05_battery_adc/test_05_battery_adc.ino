/*
 * ============================================================================
 * ADC BATERÍA - TEST Y CALIBRACIÓN (CALIBRADO)
 * ============================================================================
 * 
 * Este sketch lee el voltaje de la batería LiPo a través del ADC.
 * 
 * Circuito divisor de voltaje:
 * 
 *   BAT+ ──[R1=100kΩ]──┬──[R2=100kΩ]── GND
 *                      │
 *                   GPIO 4 (ADC)
 * 
 * Factor de división: 2 (leemos la mitad del voltaje)
 * 
 * Calibración:
 * - Multímetro midió: 4.032 V
 * - Sketch medía: ~6.600 V
 * - Factor nuevo = 1.0 * (4.032 / 6.600) ≈ 0.61
 * 
 * Voltajes LiPo típicos:
 * - 4.2V = 100% (carga completa)
 * - 3.7V = 50% (nominal)
 * - 3.0V = 0% (descargada)
 * 
 * ============================================================================
 */

#define BATTERY_ADC_PIN 4

// Factor de división del divisor de voltaje
// R1 = 100k, R2 = 100k → factor = (R1 + R2) / R2 = 2.0
#define VOLTAGE_DIVIDER_FACTOR 2.0

// Calibración fina (ajustada según tu multímetro: 4.032 V reales)
// Antes: 1.0 → el código mostraba ~6.6 V
// Ahora: 0.61 → 6.6 V medidos * 0.61 ≈ 4.03 V reales
#define CALIBRATION_FACTOR 0.61

// Variables para estadísticas
float voltageSum = 0;
float voltageMin = 10.0;
float voltageMax = 0;
int sampleCount = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n╔═══════════════════════════════════╗");
  Serial.println("║    ADC BATERÍA - TEST & CAL       ║");
  Serial.println("╚═══════════════════════════════════╝\n");
  
  // Configurar ADC
  analogReadResolution(12);      // 12 bits (0-4095)
  analogSetAttenuation(ADC_11db); // Rango aprox 0-3.3V en el pin
  
  Serial.println("Configuración ADC:");
  Serial.println("  Resolución: 12 bits (0-4095)");
  Serial.println("  Atenuación: 11dB (0-3.3V aprox)");
  Serial.print("  Divisor:    ");
  Serial.println(VOLTAGE_DIVIDER_FACTOR, 1);
  Serial.print("  Cal Factor: ");
  Serial.println(CALIBRATION_FACTOR, 2);
  Serial.println();
  
  Serial.println("═══════════════════════════════════");
  Serial.println("INICIANDO LECTURAS CONTINUAS");
  Serial.println("═══════════════════════════════════\n");
  
  Serial.println("ADC | mV (ADC) | mV (BAT) | % | Estado");
  Serial.println("──────────────────────────────────────────");
  
  delay(1000);
}

void loop() {
  // Leer ADC (promedio de 10 lecturas)
  int adcSum = 0;
  for (int i = 0; i < 10; i++) {
    adcSum += analogRead(BATTERY_ADC_PIN);
    delay(5);
  }
  int adcValue = adcSum / 10;
  
  // Convertir ADC a voltaje en el pin (0-3.3V aprox)
  float voltageAtPin = (adcValue / 4095.0) * 3.3;
  
  // Calcular voltaje real de batería (aplicar divisor y factor de calibración)
  float batteryVoltage = voltageAtPin * VOLTAGE_DIVIDER_FACTOR * CALIBRATION_FACTOR;
  
  // Convertir a mV
  int mvAtPin = (int)(voltageAtPin * 1000);
  int mvBattery = (int)(batteryVoltage * 1000);
  
  // Calcular porcentaje (LiPo: 4.2V = 100%, 3.0V = 0%)
  int batteryPercent = constrain(
    map(mvBattery, 3000, 4200, 0, 100),
    0, 100
  );
  
  // Actualizar estadísticas
  voltageSum += batteryVoltage;
  sampleCount++;
  if (batteryVoltage < voltageMin) voltageMin = batteryVoltage;
  if (batteryVoltage > voltageMax) voltageMax = batteryVoltage;
  
  // Mostrar lectura
  Serial.print(adcValue);
  Serial.print("  | ");
  Serial.print(mvAtPin);
  Serial.print(" mV   | ");
  Serial.print(mvBattery);
  Serial.print(" mV  | ");
  Serial.print(batteryPercent);
  Serial.print("% | ");
  
  // Estado de batería
  if (batteryPercent >= 80) {
    Serial.println("✓✓ Excelente");
  } else if (batteryPercent >= 50) {
    Serial.println("✓ Buena");
  } else if (batteryPercent >= 20) {
    Serial.println("⚠ Media");
  } else if (batteryPercent >= 10) {
    Serial.println("⚠⚠ Baja");
  } else {
    Serial.println("❌ Crítica");
  }
  
  // Mostrar estadísticas cada 20 lecturas
  if (sampleCount % 20 == 0) {
    float avgVoltage = voltageSum / sampleCount;
    
    Serial.println("\n╔════════════════════════════════╗");
    Serial.println("║        ESTADÍSTICAS            ║");
    Serial.println("╠════════════════════════════════╣");
    Serial.print("║ Promedio:  ");
    Serial.print(avgVoltage, 3);
    Serial.println(" V           ║");
    Serial.print("║ Mínimo:    ");
    Serial.print(voltageMin, 3);
    Serial.println(" V           ║");
    Serial.print("║ Máximo:    ");
    Serial.print(voltageMax, 3);
    Serial.println(" V           ║");
    Serial.print("║ Muestras:  ");
    Serial.print(sampleCount);
    Serial.println("                ║");
    Serial.println("╚════════════════════════════════╝\n");
    
    // Guía de calibración
    Serial.println("💡 CALIBRACIÓN:");
    Serial.println("   1. Mide el voltaje real con un multímetro");
    Serial.println("   2. Compara con la lectura mostrada arriba");
    Serial.println("   3. Si hay diferencia, ajusta CALIBRATION_FACTOR:");
    Serial.print("      Factor nuevo = ");
    Serial.print(CALIBRATION_FACTOR, 2);
    Serial.println(" × (Voltaje_real / Voltaje_medido)");
    Serial.println();
  }
  
  // Advertencias (sobre batería real, ya calibrada)
  if (batteryPercent < 20) {
    Serial.println("\n⚠️⚠️ ADVERTENCIA: Batería baja, cargar pronto\n");
  }
  
  if (batteryVoltage > 4.25) {
    Serial.println("\n⚠️ ADVERTENCIA: Voltaje muy alto (>4.25V)\n");
  }
  
  if (batteryVoltage < 2.8) {
    Serial.println("\n❌ ADVERTENCIA: Voltaje crítico (<2.8V)\n");
  }
  
  delay(2000);
}
