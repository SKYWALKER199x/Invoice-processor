import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QTableWidget, QTableWidgetItem, QMessageBox, QTabWidget,
    QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from extractor import extract_text_from_file
from database import insert_data, fetch_all_invoices, fetch_invoice_items, check_invoice_exists

class ItemDetailsDialog(QDialog):
    def __init__(self, invoice_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Items for Invoice {invoice_id}")
        self.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Item Name", "Quantity", "Price"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Fetch items from database
        from database import fetch_invoice_items  # Import here or at top of file
        items = fetch_invoice_items(invoice_id)
        
        self.table.setRowCount(len(items))
        for row_idx, (name, qty, price) in enumerate(items):
            self.table.setItem(row_idx, 0, QTableWidgetItem(name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(qty)))
            # Remove any dollar signs from price and format as plain number
            clean_price = str(price).replace('$', '').replace(',', '')
            try:
                self.table.setItem(row_idx, 2, QTableWidgetItem(f"{float(clean_price):.2f}"))
            except ValueError:
                self.table.setItem(row_idx, 2, QTableWidgetItem(str(price)))
        
        layout.addWidget(self.table)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)

class InvoiceProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Processor")
        self.setGeometry(100, 100, 800, 600)
        self.file_path = ""

        self.layout = QVBoxLayout()

        self.label = QLabel("No file selected")
        self.layout.addWidget(self.label)

        self.select_button = QPushButton("Select Invoice")
        self.select_button.clicked.connect(self.select_file)
        self.layout.addWidget(self.select_button)

        self.extract_button = QPushButton("Extract and Save Info")
        self.extract_button.clicked.connect(self.extract_info)
        self.layout.addWidget(self.extract_button)

        self.tabs = QTabWidget()
        
        # Invoice Table
        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(5)
        self.invoice_table.setHorizontalHeaderLabels(["Customer", "Invoice ID", "Date", "Organization", "Total"])
        self.invoice_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.invoice_table.cellDoubleClicked.connect(self.show_items)
        self.tabs.addTab(self.invoice_table, "Invoices")
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
        self.load_invoice_data()

        self.check_duplicate_button = QPushButton("Check for Duplicate")
        self.check_duplicate_button.clicked.connect(self.check_duplicate)
        self.layout.addWidget(self.check_duplicate_button)

    # New method to check duplicates:
    def check_duplicate(self):
        """Check if the currently selected file is a duplicate"""
        if not self.file_path:
            QMessageBox.warning(self, "No File", "Please select a file first.")
            return
        
        try:
            # First extract the data from the file
            data = extract_text_from_file(self.file_path)
            
            # Then check for duplicates using database.py functions
            from database import check_invoice_exists  # Import if not already at top
            
            # Check by both invoice ID and customer_name + date combination
            duplicate_found = check_invoice_exists(
                invoice_id=data.get('invoice_id'),
                customer_name=data.get('customer_name'),
                invoice_date=data.get('invoice_date')
            )
            
            if duplicate_found:
                QMessageBox.warning(self, "Duplicate Found", 
                                  "This invoice already exists in the database.")
            else:
                QMessageBox.information(self, "No Duplicate", 
                                      "This invoice appears to be new.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to check duplicate: {str(e)}")
    def select_file(self):
        file_dialog = QFileDialog()
        path, _ = file_dialog.getOpenFileName(self, "Select Invoice File", "", "All Files (*.*)")
        if path:
            self.file_path = path
            self.label.setText(f"Selected File: {os.path.basename(path)}")

    def extract_info(self):
        if not self.file_path:
            QMessageBox.warning(self, "No File", "Please select a file first.")
            return

        try:
            data = extract_text_from_file(self.file_path)
            
            # Calculate total if not provided
            if data["total_amount"] <= 0 and data["items"]:
                total = sum(item["price"] * item["quantity"] for item in data["items"])
                data["total_amount"] = total
            
            # Check for duplicates before insertion
            if check_invoice_exists(invoice_id=data['invoice_id']) or \
                check_invoice_exists(customer_name=data['customer_name'], 
                                    invoice_date=data['invoice_date']):
                    QMessageBox.warning(self, "Duplicate Invoice", 
                                    "This invoice already exists in the database.")
                    return
                
            success = insert_data(
                data['customer_name'],
                data['invoice_id'],
                data['invoice_date'],
                data['organization'],
                data['total_amount'],
                data['items']
            )
            
            if success:
                QMessageBox.information(self, "Success", "Invoice data saved successfully!")
                self.load_invoice_data()
            else:
                QMessageBox.warning(self, "Error", "Failed to save invoice data.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def load_invoice_data(self):
        self.invoice_table.setRowCount(0)
        invoices = fetch_all_invoices()
        for row_idx, invoice in enumerate(invoices):
            self.invoice_table.insertRow(row_idx)
            for col_idx, value in enumerate(invoice[1:]):  # Skip ID
                if col_idx == 4:  # Total amount column
                    # Remove any existing dollar signs and format as plain number
                    clean_value = str(value).replace('$', '').replace(',', '')
                    try:
                        # Format with 2 decimal places but no currency symbol
                        self.invoice_table.setItem(row_idx, col_idx, QTableWidgetItem(f"{float(clean_value):.2f}"))
                    except ValueError:
                        self.invoice_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
                else:
                    self.invoice_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        
        self.invoice_table.resizeColumnsToContents()

    def show_items(self, row, column):
        invoice_id = self.invoice_table.item(row, 1).text()
        dialog = ItemDetailsDialog(invoice_id, self)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceProcessor()
    window.show()
    sys.exit(app.exec_())