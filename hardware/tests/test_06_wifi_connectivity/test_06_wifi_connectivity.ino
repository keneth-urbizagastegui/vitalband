/*
 * ============================================================================
 * WIFI - TEST DE CONECTIVIDAD (modelo GENÉRICO de distancia)
 * ============================================================================
 *
 * Este sketch:
 *  - Se conecta al WiFi
 *  - Muestra RSSI, datos de red
 *  - Estima distancia usando un modelo genérico, útil en "cualquier lugar"
 *
 * NOTA:
 *   La distancia es SIEMPRE una estimación aproximada.
 *   Este modelo es genérico, no calibrado a un entorno específico.
 * ============================================================================
 */

#include <WiFi.h>
#include <math.h>

// ⚠️ CONFIGURA TU RED AQUÍ
const char* WIFI_SSID     = "JANICE - 2.4G";
const char* WIFI_PASSWORD = "Petti2Fottu";

#define WIFI_TIMEOUT_MS 10000

// ============================================================================
// MODELO GENÉRICO DE DISTANCIA
// ============================================================================
// Asumimos (típico interior):
//   - RSSI_REF_dBm ≈ -40 dBm a 1 metro del router
//   - PATH_LOSS_EXPONENT ≈ 3.0 (entre 2 y 4 según entorno)
//
// En la práctica:
//   RSSI = -40 dBm  → ~1 m
//   RSSI = -50 dBm  → ~2 m
//   RSSI = -60 dBm  → ~4 m
//   RSSI = -70 dBm  → ~8 m (muy aproximado)

const float RSSI_REF_dBm       = -40.0f;  // RSSI "esperado" a 1 m (genérico)
const float PATH_LOSS_EXPONENT =  3.0f;   // Exponente de pérdida (genérico)

// ============================================================================
// ESTADÍSTICAS
// ============================================================================
int rssiSum        = 0;
int rssiMin        = 0;
int rssiMax        = -100;
int sampleCount    = 0;
int reconnectCount = 0;

// ============================================================================
// Función: estimar distancia desde RSSI (modelo genérico)
// ============================================================================
float estimateDistanceMeters(int rssi) {
  // Fórmula de pérdida de trayectoria:
  //   d = 10 ^ ( (RSSI_REF - RSSI) / (10 * n) )
  float exponent = (RSSI_REF_dBm - (float)rssi) / (10.0f * PATH_LOSS_EXPONENT);
  float d = pow(10.0f, exponent);

  // Limitar a un rango razonable para no ver cosas raras
  if (d < 0.3f) d = 0.3f;
  if (d > 50.0f) d = 50.0f;

  return d;
}

// ============================================================================
// SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n╔═══════════════════════════════════╗");
  Serial.println("║      WIFI - TEST CONECTIVIDAD     ║");
  Serial.println("╚═══════════════════════════════════╝\n");

  WiFi.mode(WIFI_STA);

  connectWiFi();
}

// ============================================================================
// LOOP
// ============================================================================
void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\n❌ Conexión perdida. Reconectando...");
    reconnectCount++;
    connectWiFi();
  }

  int rssi = WiFi.RSSI();

  // Estadísticas
  rssiSum += rssi;
  if (sampleCount == 0) {
    rssiMin = rssi;
    rssiMax = rssi;
  } else {
    if (rssi < rssiMin) rssiMin = rssi;
    if (rssi > rssiMax) rssiMax = rssi;
  }
  sampleCount++;

  float dist_m = estimateDistanceMeters(rssi);

  Serial.println("\n═══════════════════════════════════");
  Serial.println("ESTADO DE CONEXIÓN");
  Serial.println("═══════════════════════════════════");

  Serial.print("SSID:      ");
  Serial.println(WiFi.SSID());

  Serial.print("IP:        ");
  Serial.println(WiFi.localIP());

  Serial.print("Gateway:   ");
  Serial.println(WiFi.gatewayIP());

  Serial.print("DNS:       ");
  Serial.println(WiFi.dnsIP());

  Serial.print("MAC:       ");
  Serial.println(WiFi.macAddress());

  Serial.print("Channel:   ");
  Serial.println(WiFi.channel());

  Serial.print("\nRSSI:      ");
  Serial.print(rssi);
  Serial.print(" dBm  ");

  if (rssi > -50) {
    Serial.println("(✓✓ Excelente)");
  } else if (rssi > -60) {
    Serial.println("(✓ Muy Buena)");
  } else if (rssi > -70) {
    Serial.println("(~ Buena)");
  } else if (rssi > -80) {
    Serial.println("(⚠ Regular)");
  } else {
    Serial.println("(❌ Débil)");
  }

  Serial.print("Señal:     [");
  int bars = map(rssi, -100, -40, 0, 10);
  bars = constrain(bars, 0, 10);
  for (int i = 0; i < 10; i++) {
    Serial.print(i < bars ? "█" : "░");
  }
  Serial.println("]");

  if (sampleCount > 0) {
    Serial.println("\n─── ESTADÍSTICAS ───");
    Serial.print("Promedio: ");
    Serial.print(rssiSum / sampleCount);
    Serial.println(" dBm");
    Serial.print("Mínimo:   ");
    Serial.print(rssiMin);
    Serial.println(" dBm");
    Serial.print("Máximo:   ");
    Serial.print(rssiMax);
    Serial.println(" dBm");
    Serial.print("Muestras: ");
    Serial.println(sampleCount);
    Serial.print("Reconexiones: ");
    Serial.println(reconnectCount);
    Serial.println("───────────────────");
  }

  Serial.print("\nDistancia estimada (GENÉRICA): ~");
  Serial.print(dist_m, 1);
  Serial.println(" metros");

  if (rssi < -70) {
    Serial.println("\n💡 TIPS PARA MEJORAR SEÑAL:");
    Serial.println("   - Acércate al router");
    Serial.println("   - Evita obstáculos grandes (paredes, metal)");
    Serial.println("   - Cambia el canal WiFi si hay muchas redes");
  }

  delay(5000);
}

// ============================================================================
// Conexión WiFi con timeout y diagnóstico
// ============================================================================
void connectWiFi() {
  Serial.println("\n───────────────────────────────────");
  Serial.println("CONECTANDO A WIFI");
  Serial.println("───────────────────────────────────");
  Serial.print("SSID: ");
  Serial.println(WIFI_SSID);
  Serial.print("Intentando conectar");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startTime = millis();

  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - startTime > WIFI_TIMEOUT_MS) {
      Serial.println("\n\n❌ TIMEOUT: No se pudo conectar");
      Serial.println("\n🔍 DIAGNÓSTICO:");
      Serial.println("   1. Verifica el SSID");
      Serial.println("   2. Verifica la contraseña");
      Serial.println("   3. Asegúrate que sea WiFi 2.4GHz (no 5GHz)");
      Serial.println("   4. Verifica que el router está encendido");
      Serial.println("\nReintentando en 5 segundos...\n");
      delay(5000);
      return;
    }

    delay(500);
    Serial.print(".");
  }

  Serial.println("\n\n✅ CONECTADO EXITOSAMENTE\n");

  Serial.println("╔════════════════════════════════╗");
  Serial.println("║    INFORMACIÓN DE CONEXIÓN     ║");
  Serial.println("╠════════════════════════════════╣");
  Serial.print("║ IP Local:    ");
  Serial.print(WiFi.localIP());
  Serial.println("      ║");
  Serial.print("║ Gateway:     ");
  Serial.print(WiFi.gatewayIP());
  Serial.println("      ║");
  Serial.print("║ Subnet Mask: ");
  Serial.print(WiFi.subnetMask());
  Serial.println("    ║");
  Serial.print("║ DNS Server:  ");
  Serial.print(WiFi.dnsIP());
  Serial.println("      ║");
  Serial.print("║ MAC Address: ");
  Serial.print(WiFi.macAddress());
  Serial.println(" ║");
  Serial.print("║ RSSI:        ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm            ║");
  Serial.println("╚════════════════════════════════╝\n");

  Serial.println("🌐 Probando conectividad a Internet...");
  IPAddress dnsIP;
  if (WiFi.hostByName("8.8.8.8", dnsIP)) {
    Serial.print("✓ DNS OK, IP: ");
    Serial.println(dnsIP);
    Serial.println("✓ Conectividad a Internet (probable) OK\n");
  } else {
    Serial.println("⚠ Sin acceso a Internet (falló resolución DNS)\n");
  }
}

