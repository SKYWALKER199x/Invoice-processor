import sqlite3
from PyQt5.QtWidgets import QMessageBox

# Create or connect to the database
conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    invoice_id TEXT,
    invoice_date TEXT,
    organization TEXT
)
''')
conn.commit()
conn.close()


def insert_data(customer_name, invoice_id, invoice_date, organization):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM invoices WHERE invoice_id = ?", (invoice_id,))
    existing = cursor.fetchone()

    if existing:
        return False  # already exists
    else:
        cursor.execute(
            "INSERT INTO invoices (customer_name, invoice_id, invoice_date, organization) VALUES (?, ?, ?, ?)",
            (customer_name, invoice_id, invoice_date, organization)
        )
        conn.commit()
        return True



def fetch_all_data():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM invoices')
    rows = cursor.fetchall()
    conn.close()
    return rows
