-- VitalBand – esquema completo (2 perfiles: admin y client)
-- Motor y colación
CREATE DATABASE IF NOT EXISTS vitalband
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE vitalband;

-- 1) Usuarios
CREATE TABLE IF NOT EXISTS users (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  name       VARCHAR(120) NOT NULL,
  email      VARCHAR(150) NOT NULL UNIQUE,
  pass_hash  VARCHAR(255) NOT NULL,
  role       ENUM('admin','client') NOT NULL DEFAULT 'client',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2) Pacientes (1:1 con users cuando role=client)
CREATE TABLE IF NOT EXISTS patients (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL UNIQUE,
  first_name  VARCHAR(80)  NOT NULL,
  last_name   VARCHAR(120) NOT NULL,
  email       VARCHAR(150) NULL UNIQUE,
  phone       VARCHAR(30)  NULL,
  birthdate   DATE         NULL,
  sex         ENUM('male','female','other','unknown') NOT NULL DEFAULT 'unknown',
  height_cm   DECIMAL(5,2) NULL,
  weight_kg   DECIMAL(5,2) NULL,
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_patients_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 3) Dispositivos
CREATE TABLE IF NOT EXISTS devices (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  patient_id    INT NULL,
  model         VARCHAR(80)  NOT NULL,
  serial        VARCHAR(64)  NOT NULL UNIQUE,
  status        ENUM('new','active','lost','retired','service') NOT NULL DEFAULT 'new',
  registered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_devices_patient
    FOREIGN KEY (patient_id) REFERENCES patients(id)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 4) Lecturas biométricas
CREATE TABLE IF NOT EXISTS readings (
  id             BIGINT AUTO_INCREMENT PRIMARY KEY,
  device_id      INT NOT NULL,
  ts             DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  heart_rate_bpm SMALLINT NULL,
  temp_c         DECIMAL(4,1) NULL,
  spo2_pct       TINYINT NULL,
  motion_level   TINYINT NULL,
  CONSTRAINT fk_readings_device
    FOREIGN KEY (device_id) REFERENCES devices(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_readings_device_ts (device_id, ts),
  INDEX idx_readings_ts (ts)
) ENGINE=InnoDB;

-- 5) Umbrales (globales o por paciente)
CREATE TABLE IF NOT EXISTS thresholds (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NULL,  -- NULL = global
  metric     ENUM('heart_rate','temperature','spo2') NOT NULL,
  min_value  DECIMAL(6,2) NULL,
  max_value  DECIMAL(6,2) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY ux_threshold_patient_metric (patient_id, metric),
  CONSTRAINT fk_thresholds_patient
    FOREIGN KEY (patient_id) REFERENCES patients(id)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 6) Alertas
CREATE TABLE IF NOT EXISTS alerts (
  id              BIGINT AUTO_INCREMENT PRIMARY KEY,
  patient_id      INT NOT NULL,
  ts              DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  type            ENUM('tachycardia','bradycardia','fever','hypoxia','custom') NOT NULL,
  severity        ENUM('low','moderate','high','critical') NOT NULL DEFAULT 'low',
  message         VARCHAR(255) NULL,
  acknowledged_by INT NULL,
  acknowledged_at DATETIME NULL,
  CONSTRAINT fk_alerts_patient
    FOREIGN KEY (patient_id) REFERENCES patients(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_alerts_ack_user
    FOREIGN KEY (acknowledged_by) REFERENCES users(id)
    ON DELETE SET NULL ON UPDATE CASCADE,
  INDEX idx_alerts_patient_ts (patient_id, ts)
) ENGINE=InnoDB;

-- 7) Telemetría del dispositivo
CREATE TABLE IF NOT EXISTS device_telemetry (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  device_id     INT NOT NULL,
  ts            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  battery_mv    SMALLINT  NULL,     -- 3300–4300 aprox.
  battery_pct   TINYINT   NULL,     -- 0–100
  charging      TINYINT(1) NULL,    -- 0/1
  rssi_dbm      SMALLINT  NULL,     -- opcional
  board_temp_c  DECIMAL(4,1) NULL,  -- opcional
  CONSTRAINT fk_tel_device
    FOREIGN KEY (device_id) REFERENCES devices(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_tel_device_ts (device_id, ts)
) ENGINE=InnoDB;
