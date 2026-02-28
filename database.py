import sqlite3

DB_NAME = "autocare.db"

def init_db():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # 🏥 Patients table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        gender TEXT,
        phone TEXT UNIQUE,
        surgery_type TEXT,
        doctor_name TEXT,
        doctor_phone TEXT
    )
    """)

    # 📊 Responses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_phone TEXT,
        severe_pain TEXT,
        swelling TEXT,
        fever TEXT,
        mobility TEXT,
        infection TEXT,
        score INTEGER,
        risk TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()