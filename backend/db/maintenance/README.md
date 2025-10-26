# Mantenimiento de base de datos (MySQL/MariaDB)

Este folder contiene guías y snippets para tareas de **mantenimiento** de la BD `vitalband`.

---

## 1) Importar esquema y datos de ejemplo

**phpMyAdmin**
1. Crear BD `vitalband` (colación `utf8mb4_unicode_ci`).
2. Importar `../schema.sql`.
3. (Opcional) Importar `../seed.sql`.

**Consola (XAMPP Shell / PowerShell)**
```bat
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS vitalband CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p vitalband < "..\schema.sql"
mysql -u root -p vitalband < "..\seed.sql"
```

---

## 2) Políticas recomendadas

### Integridad
- **FK con `ON DELETE CASCADE`** para `readings` y `device_telemetry` (si se elimina un `device`, cae su histórico).
- **`devices.patient_id` con `ON DELETE SET NULL`** (si se borra un `patient`, el `device` queda disponible).

### Índices
- `readings (device_id, ts)` y `device_telemetry (device_id, ts)` para consultas por rango.
- `alerts (patient_id, ts)` y `thresholds (patient_id, metric)` con **UNIQUE**.

### Retención
- Mantener `readings` y `device_telemetry` por defecto **90 días** (ajustable).

### Backups
- Producción: **full diario** o **incrementales**.  
- Desarrollo: dumps **semanales** suelen ser suficientes.

---

## 3) Purgado automático de histórico (EVENT)

> Requiere `event_scheduler = ON`.

### Activar el scheduler (XAMPP)
1. **Stop** MySQL.
2. Abrir `C:\xampp\mysql\bin\my.ini` y en `[mysqld]` agregar:
   ```
   event_scheduler=ON
   ```
3. **Start** MySQL.  
   Verificación: `SHOW VARIABLES LIKE 'event_scheduler';` → `ON`.

### Crear eventos (cada noche)
```sql
USE vitalband;

-- Lecturas > 90 días
CREATE EVENT IF NOT EXISTS ev_purge_readings
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE, '02:00:00')
DO
  DELETE FROM readings
  WHERE ts < NOW() - INTERVAL 90 DAY;

-- Telemetría > 90 días
CREATE EVENT IF NOT EXISTS ev_purge_tel
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE, '02:05:00')
DO
  DELETE FROM device_telemetry
  WHERE ts < NOW() - INTERVAL 90 DAY;

-- Alertas > 180 días
CREATE EVENT IF NOT EXISTS ev_purge_alerts
ON SCHEDULE EVERY 1 DAY
STARTS TIMESTAMP(CURRENT_DATE, '02:10:00')
DO
  DELETE FROM alerts
  WHERE ts < NOW() - INTERVAL 180 DAY;
```

**Ver/activar manualmente**
```sql
SHOW EVENTS FROM vitalband;
SET GLOBAL event_scheduler = ON;
```

---

## 4) Índices y FKs (verificación rápida)

```sql
-- Ver estructura (mira FKs y ON DELETE/UPDATE)
SHOW CREATE TABLE devices\G
SHOW CREATE TABLE readings\G
SHOW CREATE TABLE device_telemetry\G
SHOW CREATE TABLE alerts\G
SHOW CREATE TABLE thresholds\G

-- Ver índices
SHOW INDEX FROM readings;
SHOW INDEX FROM device_telemetry;
SHOW INDEX FROM alerts;
SHOW INDEX FROM thresholds;
```

Si faltara algo, crea/ajusta:

```sql
-- Índices
CREATE INDEX idx_readings_device_ts       ON readings(device_id, ts);
CREATE INDEX idx_tel_device_ts            ON device_telemetry(device_id, ts);
CREATE INDEX idx_alerts_patient_ts        ON alerts(patient_id, ts);
CREATE UNIQUE INDEX ux_threshold_patient_metric ON thresholds(patient_id, metric);

-- FKs (comportamiento)
ALTER TABLE readings
  DROP FOREIGN KEY fk_readings_device,
  ADD CONSTRAINT fk_readings_device
    FOREIGN KEY (device_id) REFERENCES devices(id)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE device_telemetry
  DROP FOREIGN KEY fk_tel_device,
  ADD CONSTRAINT fk_tel_device
    FOREIGN KEY (device_id) REFERENCES devices(id)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE devices
  DROP FOREIGN KEY fk_devices_patient,
  ADD CONSTRAINT fk_devices_patient
    FOREIGN KEY (patient_id) REFERENCES patients(id)
    ON DELETE SET NULL ON UPDATE CASCADE;
```
*(Usa el nombre real de la FK si difiere; míralo con `SHOW CREATE TABLE ...`.)*

---

## 5) Particionado por fecha (opcional, volumen alto)

> Útil con millones de filas. Ejecutar en ventana de mantenimiento (lleva tiempo).

```sql
-- Ejemplo: particionado mensual en readings
ALTER TABLE readings
PARTITION BY RANGE (TO_DAYS(ts)) (
  PARTITION p202501 VALUES LESS THAN (TO_DAYS('2025-02-01')),
  PARTITION p202502 VALUES LESS THAN (TO_DAYS('2025-03-01')),
  PARTITION p202503 VALUES LESS THAN (TO_DAYS('2025-04-01'))
);

-- Añadir partición siguiente
ALTER TABLE readings
ADD PARTITION (PARTITION p202504 VALUES LESS THAN (TO_DAYS('2025-05-01')));
```

> Con particiones, purgar histórico es instantáneo:
```sql
ALTER TABLE readings DROP PARTITION p202501;
```
*(Aplica igual a `device_telemetry`.)*

---

## 6) Consultas útiles (diagnóstico)

**Últimas 24 h de un dispositivo**
```sql
SELECT ts, heart_rate_bpm, spo2_pct, temp_c, motion_level
FROM readings
WHERE device_id = ? AND ts >= NOW() - INTERVAL 24 HOUR
ORDER BY ts DESC;
```

**Batería promedio por hora (últimas 24 h)**
```sql
SELECT DATE_FORMAT(ts, '%Y-%m-%d %H:00:00') AS hour, AVG(battery_pct) AS avg_pct
FROM device_telemetry
WHERE device_id = ? AND ts >= NOW() - INTERVAL 24 HOUR
GROUP BY hour
ORDER BY hour;
```

**Alertas por severidad (7 días)**
```sql
SELECT severity, COUNT(*) AS total
FROM alerts
WHERE ts >= NOW() - INTERVAL 7 DAY
GROUP BY severity
ORDER BY FIELD(severity,'critical','high','moderate','low');
```

---

## 7) Backups & Restore (mysqldump)

**Backup completo**
```bat
mysqldump -u root -p --routines --events --single-transaction vitalband > C:\backups\vitalband\vitalband_YYYYMMDD.sql
```

**Restore**
```bat
mysql -u root -p vitalband < C:\backups\vitalband\vitalband_YYYYMMDD.sql
```

---

## 8) Troubleshooting rápido

- **Errores de FK al importar**  
  Importa en orden: `users/patients/devices` → `readings/device_telemetry` → `thresholds/alerts`.

- **Eventos no se ejecutan**  
  `SHOW VARIABLES LIKE 'event_scheduler';` → debe estar `ON`.  
  `SHOW EVENTS FROM vitalband;` para listar.

- **Consultas lentas**  
  Verifica índices `(device_id, ts)` y considera particiones si > 10M filas.

- **Problemas de acentos/colación**  
  Asegura `utf8mb4_unicode_ci` en **BD y tablas**.
