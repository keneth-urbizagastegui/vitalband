-- Esquema mínimo equivalente a los modelos SQLAlchemy (si no usas Alembic).
CREATE TABLE IF NOT EXISTS patients (
  id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(120) NOT NULL,
  email VARCHAR(120) UNIQUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS devices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  serial VARCHAR(64) NOT NULL UNIQUE,
  patient_id INT,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS metrics (
  id INT AUTO_INCREMENT PRIMARY KEY,
  device_id INT NOT NULL,
  ts DATETIME DEFAULT CURRENT_TIMESTAMP,
  heart_rate INT,
  spo2 INT,
  INDEX (ts),
  FOREIGN KEY (device_id) REFERENCES devices(id)
);

CREATE TABLE IF NOT EXISTS alerts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NOT NULL,
  kind VARCHAR(50) NOT NULL,
  message VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS thresholds (
  id INT AUTO_INCREMENT PRIMARY KEY,
  patient_id INT NULL,
  metric VARCHAR(50) NOT NULL,
  min_value INT NULL,
  max_value INT NULL,
  FOREIGN KEY (patient_id) REFERENCES patients(id)
);
