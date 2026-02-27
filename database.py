import sqlite3

def init_db():
    conn = sqlite3.connect("agri.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            moisture REAL,
            temperature REAL,
            humidity REAL,
            rainfall REAL,
            crop TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()