import sqlite3
from PyQt5.QtWidgets import QMessageBox

# Create or connect to the database
conn = sqlite3.connect("invoices.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    invoice_id TEXT UNIQUE,
    invoice_date TEXT,
    organization TEXT,
    total_amount REAL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id TEXT,
    item_name TEXT,
    quantity INTEGER,
    price REAL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
)
''')

conn.commit()
conn.close()

def insert_data(customer_name, invoice_id, invoice_date, organization, total_amount, items):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    
    # Check for duplicates using multiple criteria
    if check_invoice_exists(invoice_id=invoice_id) or \
       check_invoice_exists(customer_name=customer_name, invoice_date=invoice_date):
        return False  # Duplicate exists
    
    try:
        # Insert invoice data
        cursor.execute(
            """INSERT INTO invoices 
            (customer_name, invoice_id, invoice_date, organization, total_amount) 
            VALUES (?, ?, ?, ?, ?)""",
            (customer_name, invoice_id, invoice_date, organization, total_amount)
        )
        
        # Insert items
        for item in items:
            cursor.execute(
                "INSERT INTO invoice_items (invoice_id, item_name, quantity, price) VALUES (?, ?, ?, ?)",
                (invoice_id, item['name'], item['quantity'], item['price'])
            )
        
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def fetch_all_invoices():
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM invoices')
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_invoice_items(invoice_id):
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    cursor.execute('SELECT item_name, quantity, price FROM invoice_items WHERE invoice_id = ?', (invoice_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def check_invoice_exists(invoice_id=None, customer_name=None, invoice_date=None):
    """Check if an invoice already exists using multiple criteria"""
    conn = sqlite3.connect("invoices.db")
    cursor = conn.cursor()
    
    query = "SELECT 1 FROM invoices WHERE"
    conditions = []
    params = []
    
    if invoice_id:
        conditions.append("invoice_id = ?")
        params.append(invoice_id)
    if customer_name:
        conditions.append("customer_name = ?")
        params.append(customer_name)
    if invoice_date:
        conditions.append("invoice_date = ?")
        params.append(invoice_date)
    
    if not conditions:
        return False
    
    query += " " + " AND ".join(conditions)
    cursor.execute(query, params)
    exists = cursor.fetchone() is not None
    conn.close()
    return exists