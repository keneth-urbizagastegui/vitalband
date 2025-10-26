INSERT INTO patients (full_name, email) VALUES
('Alice Doe', 'alice@example.com'),
('Bob Roe', 'bob@example.com');

INSERT INTO devices (serial, patient_id) VALUES
('VB-0001', 1),
('VB-0002', 2);

INSERT INTO metrics (device_id, heart_rate, spo2) VALUES
(1, 72, 98),
(1, 88, 96),
(2, 65, 99);

INSERT INTO alerts (patient_id, kind, message) VALUES
(1, 'tachycardia', 'HR > 120'),
(2, 'hypoxia', 'SpO2 < 92');
