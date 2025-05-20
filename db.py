import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("enquiry_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            mobile TEXT,
            email TEXT,
            category TEXT,
            course TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_enquiry(name, mobile, email, category, course):
    conn = sqlite3.connect("enquiry_data.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO enquiries (name, mobile, email, category, course, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                   (name, mobile, email, category, course, timestamp))
    conn.commit()
    conn.close()
