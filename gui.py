import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QTableWidget, QTableWidgetItem, QMessageBox
)
from extractor import extract_text_from_file
from database import insert_data, fetch_all_data


class InvoiceProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Processor")
        self.setGeometry(100, 100, 550, 500)
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

        self.refresh_button = QPushButton("Refresh Table")
        self.refresh_button.clicked.connect(self.load_table_data)
        self.layout.addWidget(self.refresh_button)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Customer Name", "Invoice ID", "Invoice Date", "Organization"])
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)
        self.load_table_data()

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
            insert_data(data['customer_name'], data['invoice_id'], data['invoice_date'], data['organization'])
            
            # ✅ Show extracted items
            items = data.get("items", [])
            if items:
                item_str = "\n".join([f"{name} - Qty: {qty}" for name, qty in items])
                QMessageBox.information(self, "Extracted Items", item_str)
            else:
                QMessageBox.information(self, "Extracted Items", "No items found.")

            self.load_table_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e)) 


    def load_table_data(self):
        self.table.setRowCount(0)
        all_data = fetch_all_data()
        for row_idx, row_data in enumerate(all_data):
            self.table.insertRow(row_idx)
            for col_idx, col_value in enumerate(row_data[1:]):  # skip ID
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_value)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceProcessor()
    window.show()
    sys.exit(app.exec_())
