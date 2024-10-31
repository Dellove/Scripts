import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTableView, 
    QPushButton, QLineEdit, QMessageBox, QFormLayout, QDialog, QLabel, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant

class Database:
    def __init__(self, db_name="data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """CREATE TABLE IF NOT EXISTS records (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       user_id INTEGER,
                       title TEXT,
                       body TEXT
                   )"""
        self.conn.execute(query)
        self.conn.commit()

    def fetch_records(self):
        query = "SELECT * FROM records"
        result = self.conn.execute(query).fetchall()
        return result

    def add_record(self, user_id, title, body):
        query = "INSERT INTO records (user_id, title, body) VALUES (?, ?, ?)"
        self.conn.execute(query, (user_id, title, body))
        self.conn.commit()

    def delete_record(self, record_id):
        query = "DELETE FROM records WHERE id = ?"
        self.conn.execute(query, (record_id,))
        self.conn.commit()

class TableModel(QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0]) if self._data else 0

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        return QVariant()

    def headerData(self, section, orientation, role):
        headers = ["ID", "User ID", "Title", "Body"]
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return headers[section]
        return QVariant()

class AddRecordDialog(QDialog):
    def __init__(self, parent=None):
        super(AddRecordDialog, self).__init__(parent)
        self.setWindowTitle("Add Record")
        
        layout = QFormLayout()
        self.user_id_input = QLineEdit()
        self.title_input = QLineEdit()
        self.body_input = QLineEdit()

        layout.addRow("User ID:", self.user_id_input)
        layout.addRow("Title:", self.title_input)
        layout.addRow("Body:", self.body_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_data(self):
        return self.user_id_input.text(), self.title_input.text(), self.body_input.text()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Database App")

        self.db = Database()

        self.layout = QVBoxLayout()
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by title...")
        self.search_bar.textChanged.connect(self.filter_data)

        self.table_view = QTableView()
        self.load_data()

        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_data)
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_record)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.delete_record)

        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)

        self.layout.addWidget(self.search_bar)
        self.layout.addWidget(self.table_view)
        self.layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def load_data(self):
        records = self.db.fetch_records()
        self.model = TableModel(records)
        self.table_view.setModel(self.model)

    def filter_data(self):
        query = self.search_bar.text().lower()
        records = self.db.fetch_records()
        filtered_records = [record for record in records if query in record[2].lower()]
        self.model = TableModel(filtered_records)
        self.table_view.setModel(self.model)

    def add_record(self):
        dialog = AddRecordDialog(self)
        if dialog.exec() == QDialog.Accepted:
            user_id, title, body = dialog.get_data()
            if user_id and title and body:
                self.db.add_record(int(user_id), title, body)
                self.load_data()

    def delete_record(self):
        selected = self.table_view.selectionModel().selectedRows()
        if selected:
            record_id = selected[0].data()
            confirm = QMessageBox.question(self, "Confirm Deletion", "Delete this record?")
            if confirm == QMessageBox.Yes:
                self.db.delete_record(record_id)
                self.load_data()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
