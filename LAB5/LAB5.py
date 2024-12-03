import sys
import sqlite3
import requests
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout,
    QLabel, QProgressBar, QWidget, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer


# --- Поток для загрузки данных ---
class DataFetchThread(QThread):
    update_progress = pyqtSignal(int)
    data_fetched = pyqtSignal(list)

    def run(self):
        self.update_progress.emit(0)
        url = "https://jsonplaceholder.typicode.com/posts"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.update_progress.emit(100)
                time.sleep(1)  # эмуляция задержки
                self.data_fetched.emit(data)
            else:
                self.data_fetched.emit([])
        except Exception as e:
            print(f"Error fetching data: {e}")
            self.data_fetched.emit([])


# --- Поток для сохранения данных в базу ---
class SaveDataThread(QThread):
    data_saved = pyqtSignal()
    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                userId INTEGER,
                title TEXT,
                body TEXT
            )
        """)
        for item in self.data:
            cursor.execute("""
                INSERT OR IGNORE INTO posts (id, userId, title, body)
                VALUES (?, ?, ?, ?)
            """, (item["id"], item["userId"], item["title"], item["body"]))
        conn.commit()
        conn.close()
        time.sleep(1)  # эмуляция задержки
        self.data_saved.emit()


# --- Основное окно ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Асинхронность и потоки")
        self.resize(800, 600)

        # --- Виджеты ---
        self.progress_label = QLabel("Статус: Готов")
        self.progress_bar = QProgressBar()
        self.load_button = QPushButton("Загрузить данные")
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "User ID", "Title", "Body"])
        self.status_label = QLabel("Обновлений пока нет.")

        # --- Расположение ---
        layout = QVBoxLayout()
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.load_button)
        layout.addWidget(self.table)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # --- Связь сигналов и слотов ---
        self.load_button.clicked.connect(self.fetch_data)
        self.data_thread = None
        self.save_thread = None

        # --- Таймер для обновления ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_data)
        self.timer.start(10000)  # каждые 10 секунд

    def fetch_data(self):
        self.progress_label.setText("Статус: Загрузка данных...")
        self.progress_bar.setValue(0)
        self.data_thread = DataFetchThread()
        self.data_thread.update_progress.connect(self.progress_bar.setValue)
        self.data_thread.data_fetched.connect(self.on_data_fetched)
        self.data_thread.start()

    def on_data_fetched(self, data):
        if not data:
            self.progress_label.setText("Ошибка загрузки данных.")
            return

        self.progress_label.setText("Данные успешно загружены.")
        self.save_data_to_db(data)

    def save_data_to_db(self, data):
        self.progress_label.setText("Статус: Сохранение данных в базу...")
        self.save_thread = SaveDataThread(data)
        self.save_thread.data_saved.connect(self.on_data_saved)
        self.save_thread.start()

    def on_data_saved(self):
        self.progress_label.setText("Данные сохранены в базу.")
        self.update_ui_from_db()

    def update_ui_from_db(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)
        for row_data in rows:
            row_number = self.table.rowCount()
            self.table.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(cell_data)))

        self.status_label.setText(f"Данные обновлены: {len(rows)} записей.")


# --- Запуск приложения ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
