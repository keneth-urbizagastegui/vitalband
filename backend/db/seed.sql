USE vitalband;

-- Hash de ejemplo (reemplaza luego por tu propio hash seguro)
-- Contraseña de demo para ambos: Admin123!
-- (Luego cámbiala y usa generate_password_hash en Python)
SET @demo_hash = 'pbkdf2:sha256:29000$CB0f3uEWIVds1gAK$c96764f2ebf01ac4642bda3e097d301673e97c8b29124b3561e1a53764b12d8c';

-- Admin
INSERT INTO users (name, email, pass_hash, role)
VALUES ('Admin', 'admin@vitalband.local', @demo_hash, 'admin')
ON DUPLICATE KEY UPDATE email=email;

-- Cliente (user) + Paciente 1:1
INSERT INTO users (name, email, pass_hash, role)
VALUES ('Ana Perez', 'ana@demo.com', @demo_hash, 'client')
ON DUPLICATE KEY UPDATE email=email;

-- Paciente asociado al último user client insertado (si ya existía, ajusta el user_id manualmente)
SET @client_id = (SELECT id FROM users WHERE email='ana@demo.com' LIMIT 1);
INSERT INTO patients (user_id, first_name, last_name, email, sex, height_cm, weight_kg)
VALUES (@client_id, 'Ana', 'Perez', 'ana@demo.com', 'female', 165.0, 64.5)
ON DUPLICATE KEY UPDATE user_id=user_id;

-- Dispositivo asignado
INSERT INTO devices (patient_id, model, serial, status)
VALUES ((SELECT id FROM patients WHERE user_id=@client_id), 'VB-01', 'VB-0001', 'active')
ON DUPLICATE KEY UPDATE serial=serial;

-- Lecturas de ejemplo
INSERT INTO readings (device_id, ts, heart_rate_bpm, spo2_pct, temp_c, motion_level) VALUES
  (1, NOW() - INTERVAL 10 MINUTE, 82, 98, 36.7, 2),
  (1, NOW() - INTERVAL 5 MINUTE,  88, 97, 36.8, 3),
  (1, NOW(),                      79, 99, 36.6, 1);

-- Telemetría de ejemplo
INSERT INTO device_telemetry (device_id, ts, battery_mv, battery_pct, charging, rssi_dbm) VALUES
  (1, NOW() - INTERVAL 30 MINUTE, 4010, 90, 0, -55),
  (1, NOW() - INTERVAL 5 MINUTE,  3920, 78, 0, -60),
  (1, NOW(),                      3885, 74, 0, -58);

-- Umbral global HR
INSERT INTO thresholds (patient_id, metric, min_value, max_value)
VALUES (NULL, 'heart_rate', 50, 120)
ON DUPLICATE KEY UPDATE metric=metric;

-- Alerta de ejemplo
INSERT INTO alerts (patient_id, ts, type, severity, message)
VALUES ((SELECT id FROM patients WHERE user_id=@client_id), NOW(), 'tachycardia', 'moderate', 'HR > 120 detectado');
