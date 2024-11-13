import sys
import asyncio
import aiohttp
import sqlite3
import threading
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QTextEdit, QProgressBar, QLabel)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    async def fetch_data(self):
        self.progress.emit(0)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://jsonplaceholder.typicode.com/posts") as response:
                await asyncio.sleep(2)  # Добавляем искусственную задержку для демонстрации
                data = await response.json()
                threading.Thread(target=self.save_data, args=(data,)).start()
                self.progress.emit(50)

    def save_data(self, data):
        time.sleep(2)  # Искусственная задержка для демонстрации
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        # Удаление и создание таблицы
        cursor.execute("DROP TABLE IF EXISTS posts")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY,
                userId INTEGER,
                title TEXT,
                body TEXT
            )
        """)
        for post in data:
            try:
                cursor.execute("""
                    INSERT INTO posts (id, userId, title, body) 
                    VALUES (?, ?, ?, ?)
                """, (post['id'], post['userId'], post['title'], post['body']))
            except sqlite3.IntegrityError:
                print(f"Запись с id={post['id']} уже существует, пропускаем...")

        conn.commit()
        conn.close()
        self.progress.emit(100)
        self.finished.emit()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.button = QPushButton("Загрузить данные")
        self.button.clicked.connect(self.start_loading)

        self.text = QTextEdit()
        self.progress_bar = QProgressBar()
        self.status_label = QLabel("Статус: Ожидание")

        self.layout.addWidget(self.button)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)

        self.worker = Worker()
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)

        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(10000)  # Обновление каждые 10 секунд

    def start_loading(self):
        self.status_label.setText("Статус: Загрузка...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_in_executor(None, lambda: loop.run_until_complete(self.worker.fetch_data()))

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_finished(self):
        self.status_label.setText("Статус: Готово")
        self.load_data_from_db()

    def load_data_from_db(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")
        rows = cursor.fetchall()
        conn.close()

        self.text.clear()
        for row in rows:
            self.text.append(f"ID: {row[0]}, UserID: {row[1]}, Title: {row[2]}, Body: {row[3]}")

    def check_for_updates(self):
        self.status_label.setText("Статус: Проверка обновлений...")
        asyncio.run(self.async_check_for_updates())

    async def async_check_for_updates(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://jsonplaceholder.typicode.com/posts") as response:
                if response.status == 200:
                    self.status_label.setText("Статус: Данные актуальны")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
