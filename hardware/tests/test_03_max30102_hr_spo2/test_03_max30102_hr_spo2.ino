/*
 * ============================================================================
 * MAX30102 - TEST DE PULSO Y SPO2 (con calibración)
 * ============================================================================
 * 
 * Este sketch prueba el sensor MAX30102 de forma completa.
 * 
 * Incluye:
 * - Detección de dedo
 * - Lectura de señal IR/RED
 * - Cálculo de HR (frecuencia cardíaca)
 * - Cálculo de SpO2 (saturación de oxígeno)
 * - Calibración simple basada en pulsioxímetro médico
 * 
 * Cómo usar:
 * 1. Cargar el sketch
 * 2. Abrir Serial Monitor (115200 baud)
 * 3. Colocar el dedo FIRMEMENTE sobre el sensor
 * 4. NO presionar demasiado fuerte
 * 5. Mantener quieto por 10–15 segundos
 * 
 * ============================================================================
 */

#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

#define I2C_SDA 8
#define I2C_SCL 10

MAX30105 particleSensor;

// Buffers para el algoritmo de Maxim (100 muestras)
uint32_t irBuffer[100];
uint32_t redBuffer[100];

// Variables de resultados crudos del algoritmo
int32_t spo2;
int8_t validSPO2;
int32_t heartRate;
int8_t validHeartRate;

// Historial para promedios (hasta 10 mediciones válidas)
int hrHistory[10];
int spo2History[10];
int historyIndex = 0;

// === Calibración basada en comparación con pulsioxímetro médico ===
// Tras varias mediciones simultáneas:
//   - Pulsioxímetro médico: HR ≈ 75 BPM, SpO2 ≈ 97%
//   - Sensor (tras armónico): HR ≈ 79, SpO2 ≈ 99–100% (crudo)
// Ajuste fino para que el promedio se acerque a la referencia:
const float HR_OFFSET   = -26.0f;  // Ajuste fino de HR (antes -28, ahora más centrado en 75 BPM)
const float HR_SCALE    =  1.0f;   // Por ahora sin escala extra
const float SPO2_OFFSET = -2.0f;   // Sensor suele ir 2% por encima → restamos 2
const float SPO2_SCALE  =  1.0f;   // Sin escala para SpO2

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n╔═══════════════════════════════════╗");
  Serial.println("║   MAX30102 - TEST HR & SPO2       ║");
  Serial.println("╚═══════════════════════════════════╝\n");
  
  Wire.begin(I2C_SDA, I2C_SCL);
  Wire.setClock(400000);
  
  // Inicializar sensor
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("✗ ERROR: MAX30102 no detectado");
    Serial.println("  Verifica las conexiones");
    Serial.println("  Dirección I2C esperada: 0x57");
    while (1);
  }
  
  Serial.println("✓ MAX30102 detectado\n");
  
  // Configuración recomendada
  byte ledBrightness = 60;   // 0=Off to 255=50mA
  byte sampleAverage = 4;    // 1, 2, 4, 8, 16, 32
  byte ledMode = 2;          // 1=Red only, 2=Red+IR, 3=Red+IR+Green
  byte sampleRate = 100;     // 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411;      // 69, 118, 215, 411
  int adcRange = 4096;       // 2048, 4096, 8192, 16384
  
  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
  
  // Apagar LEDs inicialmente
  particleSensor.setPulseAmplitudeRed(0);
  particleSensor.setPulseAmplitudeIR(0);
  
  Serial.println("INSTRUCCIONES:");
  Serial.println("1. Coloca tu dedo FIRMEMENTE sobre el sensor");
  Serial.println("2. NO presiones demasiado fuerte");
  Serial.println("3. Mantén el dedo QUIETO por 10–15 segundos");
  Serial.println("4. Observa los valores de IR/RED y HR/SpO2\n");
  
  delay(2000);

  // Inicializar historial
  for (int i = 0; i < 10; i++) {
    hrHistory[i] = 0;
    spo2History[i] = 0;
  }
}

void loop() {
  Serial.println("\n═══════════════════════════════════");
  Serial.println("NUEVA MEDICIÓN");
  Serial.println("═══════════════════════════════════\n");
  
  // Encender LEDs
  particleSensor.setPulseAmplitudeRed(60);
  particleSensor.setPulseAmplitudeIR(60);
  delay(100);
  
  // Fase 1: Verificar presencia de dedo
  Serial.println("Verificando presencia de dedo...");
  long irCheck = particleSensor.getIR();
  long redCheck = particleSensor.getRed();
  
  Serial.print("IR Signal: ");
  Serial.println(irCheck);
  Serial.print("RED Signal: ");
  Serial.println(redCheck);
  
  if (irCheck < 50000) {
    Serial.println("\n❌ SIN DEDO DETECTADO");
    Serial.println("   Señal IR muy baja (< 50,000)");
    Serial.println("   Coloca tu dedo sobre el sensor\n");
    
    particleSensor.setPulseAmplitudeRed(0);
    particleSensor.setPulseAmplitudeIR(0);
    delay(3000);
    return;
  }
  
  Serial.println("✓ Dedo detectado\n");
  
  // Fase 2: Capturar 100 muestras (≈1 segundo a 100 Hz, pero con check() puede tardar un poco más)
  Serial.println("Capturando datos");
  for (byte i = 0; i < 100; i++) {
    while (!particleSensor.available()) {
      particleSensor.check();
    }
    
    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample();
    
    // Mostrar progreso
    if (i % 10 == 0) {
      Serial.print("█");
    }
  }
  Serial.println(" 100%\n");
  
  // Apagar LEDs para ahorrar energía/calor
  particleSensor.setPulseAmplitudeRed(0);
  particleSensor.setPulseAmplitudeIR(0);
  
  // Fase 3: Procesar datos
  Serial.println("Procesando datos...");
  
  // Calcular HR y SpO2 con el algoritmo de Maxim
  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, 100, 
    redBuffer, 
    &spo2, &validSPO2, 
    &heartRate, &validHeartRate
  );
  
  // Mostrar valores RAW
  Serial.println("\n─── VALORES RAW ───");
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
  
  // Corrección de armónicos (caso típico HR=2x)
  int hrCorrected = heartRate;
  if (validHeartRate && heartRate > 140) {
    hrCorrected = heartRate / 2;
    Serial.println("⚠ Armónico detectado - HR dividido por 2");
  }

  // ===== Aplicar calibración =====
  float hrCalibrated   = hrCorrected * HR_SCALE + HR_OFFSET;
  float spo2Calibrated = spo2        * SPO2_SCALE + SPO2_OFFSET;

  // Limitar a rangos físicos razonables
  if (hrCalibrated   < 0)   hrCalibrated   = 0;
  if (spo2Calibrated < 0)   spo2Calibrated = 0;
  if (spo2Calibrated > 100) spo2Calibrated = 100;

  // Validar rangos usando valores calibrados
  bool hrValid   = (validHeartRate && hrCalibrated   >= 40 && hrCalibrated   <= 200);
  bool spo2Valid = (validSPO2      && spo2Calibrated >= 70 && spo2Calibrated <= 100);

  // Guardar en historial para promedios
  if (hrValid && spo2Valid) {
    hrHistory[historyIndex]   = (int)hrCalibrated;
    spo2History[historyIndex] = (int)spo2Calibrated;
    historyIndex = (historyIndex + 1) % 10;
  }

  // Calcular promedios (sobre el historial calibrado)
  int hrSum = 0, spo2Sum = 0, validCount = 0;
  for (int i = 0; i < 10; i++) {
    if (hrHistory[i] > 0) {
      hrSum += hrHistory[i];
      spo2Sum += spo2History[i];
      validCount++;
    }
  }
  
  // Mostrar resultados finales
  Serial.println("\n╔════════════════════════════════╗");
  Serial.println("║       RESULTADOS FINALES       ║");
  Serial.println("╠════════════════════════════════╣");
  
  if (hrValid) {
    Serial.print("║ 💓 Heart Rate: ");
    Serial.print(hrCalibrated, 0);
    Serial.print(" BPM");
    
    // Clasificación
    if (hrCalibrated < 60) {
      Serial.println("    (Bajo)   ║");
    } else if (hrCalibrated <= 100) {
      Serial.println("  (Normal) ║");
    } else {
      Serial.println("    (Alto)   ║");
    }
  } else {
    Serial.println("║ 💓 Heart Rate: -- BPM (Inválido) ║");
  }
  
  if (spo2Valid) {
    Serial.print("║ 🫁 SpO2:       ");
    Serial.print(spo2Calibrated, 0);
    Serial.print("%");
    
    // Clasificación
    if (spo2Calibrated >= 95) {
      Serial.println("       (Normal) ║");
    } else if (spo2Calibrated >= 90) {
      Serial.println("    (Aceptable) ║");
    } else {
      Serial.println("         (Bajo) ║");
    }
  } else {
    Serial.println("║ 🫁 SpO2:       -- %   (Inválido) ║");
  }
  
  if (validCount > 0) {
    Serial.println("╠════════════════════════════════╣");
    Serial.print("║ Promedio HR:  ");
    Serial.print(hrSum / validCount);
    Serial.println(" BPM           ║");
    Serial.print("║ Promedio SpO2: ");
    Serial.print(spo2Sum / validCount);
    Serial.println("%              ║");
    Serial.print("║ Muestras:      ");
    Serial.print(validCount);
    Serial.println("               ║");
  }
  
  Serial.println("╚════════════════════════════════╝\n");
  
  // Calcular calidad de señal
  long avgIR = 0;
  for (byte i = 0; i < 100; i++) {
    avgIR += irBuffer[i];
  }
  avgIR /= 100;
  
  Serial.println("─── CALIDAD DE SEÑAL ───");
  Serial.print("IR Promedio: ");
  Serial.println(avgIR);
  
  if (avgIR < 50000) {
    Serial.println("❌ MUY BAJA - Sin dedo");
  } else if (avgIR < 80000) {
    Serial.println("⚠️  DÉBIL - Ajusta posición del dedo");
  } else if (avgIR < 150000) {
    Serial.println("✓ BUENA");
  } else {
    Serial.println("✓✓ EXCELENTE");
  }
  
  Serial.println("───────────────────────\n");
  
  // Tips de calibración
  if (!hrValid || !spo2Valid) {
    Serial.println("💡 TIPS PARA MEJORAR:");
    Serial.println("   1. Mantén el dedo completamente quieto");
    Serial.println("   2. Presiona firmemente pero sin aplastar");
    Serial.println("   3. Usa el dedo índice o medio");
    Serial.println("   4. Asegúrate de tener las manos calientes");
    Serial.println("   5. Espera 10–15 segundos completos\n");
  }
  
  delay(5000);
}

