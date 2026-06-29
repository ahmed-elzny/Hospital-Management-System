CREATE TABLE IF NOT EXISTS DOCTORS (
    doctor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name  TEXT    NOT NULL,
    last_name   TEXT    NOT NULL,
    specialty   TEXT,
    phone       TEXT,
    email       TEXT
);

CREATE TABLE IF NOT EXISTS PATIENTS (
    patient_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT    NOT NULL,
    last_name     TEXT    NOT NULL,
    date_of_birth TEXT,
    gender        TEXT    CHECK(gender IN ('Male','Female')),
    phone         TEXT
);

CREATE TABLE IF NOT EXISTS APPOINTMENTS (
    appointment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id        INTEGER NOT NULL,
    patient_id       INTEGER NOT NULL,
    appointment_date TEXT    NOT NULL,
    status           TEXT    DEFAULT 'Pending'
                             CHECK(status IN ('Pending','Confirmed','Completed','Cancelled')),
    notes            TEXT,
    FOREIGN KEY (doctor_id)  REFERENCES DOCTORS(doctor_id),
    FOREIGN KEY (patient_id) REFERENCES PATIENTS(patient_id)
);

CREATE TABLE IF NOT EXISTS PRESCRIPTIONS (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id  INTEGER NOT NULL,
    issue_date      TEXT    NOT NULL,
    diagnosis       TEXT,
    FOREIGN KEY (appointment_id) REFERENCES APPOINTMENTS(appointment_id)
);

CREATE TABLE IF NOT EXISTS MEDICATIONS (
    medication_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    category      TEXT,
    unit          TEXT,
    price         REAL    CHECK(price >= 0)
);




INSERT INTO DOCTORS (first_name, last_name, specialty, phone, email) VALUES
    ('Ahmed',   'Mahmoud', 'Cardiology',       '01012345678', 'ahmed@hospital.com'),
    ('Sara',    'Ali',     'Pediatrics',        '01098765432', 'sara@hospital.com'),
    ('Mohamed', 'Hassan',  'General Surgery',   '01155544433', 'mohamed@hospital.com'),
    ('Nadia',   'Kamal',   'Neurology',         '01223344556', 'nadia@hospital.com');

INSERT INTO PATIENTS (first_name, last_name, date_of_birth, gender, phone) VALUES
    ('Karim',  'Abdullah', '1990-05-15', 'Male',   '01234567890'),
    ('Nour',   'Ibrahim',  '1985-11-20', 'Female', '01987654321'),
    ('Tarek',  'Saeed',    '2000-03-08', 'Male',   '01112223344'),
    ('Hana',   'Mostafa',  '1995-07-25', 'Female', '01556677889');

INSERT INTO APPOINTMENTS (doctor_id, patient_id, appointment_date, status, notes) VALUES
    (1, 1, '2026-05-12', 'Confirmed',  'Routine checkup'),
    (2, 2, '2026-05-13', 'Pending',    'First visit'),
    (3, 3, '2026-05-14', 'Completed',  'Post-op follow up'),
    (1, 4, '2026-05-15', 'Cancelled',  'Patient request'),
    (4, 1, '2026-05-16', 'Confirmed',  'MRI results review');

INSERT INTO PRESCRIPTIONS (appointment_id, issue_date, diagnosis) VALUES
    (3, '2026-05-14', 'Acute appendicitis - post surgery'),
    (1, '2026-05-12', 'Hypertension - stage 1');

INSERT INTO MEDICATIONS (name, category, unit, price) VALUES
    ('Amoxicillin',  'Antibiotic',    'Tablet',  15.50),
    ('Paracetamol',  'Analgesic',     'Tablet',   5.00),
    ('Omeprazole',   'Antacid',       'Capsule', 22.75),
    ('Metformin',    'Antidiabetic',  'Tablet',  18.00),
    ('Amlodipine',   'Antihypert.',   'Tablet',  30.00);



-- All doctors
SELECT * FROM DOCTORS;

-- All patients
SELECT * FROM PATIENTS;

-- All appointments with doctor & patient names (JOIN)
SELECT
    a.appointment_id,
    d.first_name || ' ' || d.last_name  AS doctor_name,
    p.first_name || ' ' || p.last_name  AS patient_name,
    a.appointment_date,
    a.status,
    a.notes
FROM APPOINTMENTS a
JOIN DOCTORS  d ON a.doctor_id  = d.doctor_id
JOIN PATIENTS p ON a.patient_id = p.patient_id;

-- All prescriptions with appointment info
SELECT
    pr.prescription_id,
    pr.appointment_id,
    pr.issue_date,
    pr.diagnosis,
    d.first_name || ' ' || d.last_name AS doctor_name,
    p.first_name || ' ' || p.last_name AS patient_name
FROM PRESCRIPTIONS pr
JOIN APPOINTMENTS a ON pr.appointment_id = a.appointment_id
JOIN DOCTORS      d ON a.doctor_id       = d.doctor_id
JOIN PATIENTS     p ON a.patient_id      = p.patient_id;

-- All medications
SELECT * FROM MEDICATIONS;




-- Update appointment status
UPDATE APPOINTMENTS
SET    status = 'Completed'
WHERE  appointment_id = 1;

-- Update doctor phone
UPDATE DOCTORS
SET    phone = '01099998888'
WHERE  doctor_id = 1;

-- Update medication price
UPDATE MEDICATIONS
SET    price = 20.00
WHERE  name  = 'Paracetamol';




-- Add 'address' column to PATIENTS
ALTER TABLE PATIENTS
ADD COLUMN address TEXT;

-- Add 'notes' column to PRESCRIPTIONS
ALTER TABLE PRESCRIPTIONS
ADD COLUMN notes TEXT;

-- Add 'available' flag to DOCTORS
ALTER TABLE DOCTORS
ADD COLUMN available INTEGER DEFAULT 1;




-- Delete a cancelled appointment
DELETE FROM APPOINTMENTS
WHERE  status = 'Cancelled';

-- Delete specific medication
DELETE FROM MEDICATIONS
WHERE  medication_id = 5;
