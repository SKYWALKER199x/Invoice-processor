from PyQt5.QtWidgets import QApplication
import sys
from gui import InvoiceProcessor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceProcessor()
    window.show()
    sys.exit(app.exec_())
