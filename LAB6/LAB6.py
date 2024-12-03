import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QWidget, QComboBox, QLineEdit, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns


class DataAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.data = None  # Placeholder for the data

    def initUI(self):
        self.setWindowTitle("Data Analysis Tool")
        self.setGeometry(100, 100, 800, 600)

        # Main container widget
        container = QWidget()
        self.setCentralWidget(container)

        # Layouts
        self.layout = QVBoxLayout()
        container.setLayout(self.layout)

        # Button to load data
        self.loadButton = QPushButton("Load CSV File")
        self.loadButton.clicked.connect(self.load_data)
        self.layout.addWidget(self.loadButton)

        # Label to show statistics
        self.statsLabel = QLabel("Dataset statistics will appear here")
        self.layout.addWidget(self.statsLabel)

        # Dropdown for chart selection
        self.chartSelector = QComboBox()
        self.chartSelector.addItems(["Line Chart", "Histogram", "Pie Chart"])
        self.chartSelector.currentIndexChanged.connect(self.update_chart)
        self.layout.addWidget(self.chartSelector)

        # Canvas for matplotlib
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)

        # Controls for real-time data addition
        self.dataInputLayout = QHBoxLayout()
        self.newValueInput = QLineEdit()
        self.newValueInput.setPlaceholderText("Enter new value")
        self.addButton = QPushButton("Add Value")
        self.addButton.clicked.connect(self.add_new_value)
        self.dataInputLayout.addWidget(self.newValueInput)
        self.dataInputLayout.addWidget(self.addButton)
        self.layout.addLayout(self.dataInputLayout)

    def load_data(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
        if filePath:
            self.data = pd.read_csv(filePath)
            self.display_statistics()
            self.update_chart()

    def display_statistics(self):
        if self.data is not None:
            # Выбираем только числовые столбцы
            numeric_data = self.data.select_dtypes(include=['number'])
        
            stats = (
                f"Rows: {self.data.shape[0]}, Columns: {self.data.shape[1]}\n"
                f"Min Values:\n{numeric_data.min()}\n"
                f"Max Values:\n{numeric_data.max()}\n"
                f"Mean Values:\n{numeric_data.mean()}\n"
            )
            self.statsLabel.setText(stats)


    def update_chart(self):
        if self.data is None:
            return

        # Сброс графика
        self.ax.clear()

        chartType = self.chartSelector.currentText()

        if chartType == "Line Chart":
            if "Date" in self.data.columns and "Value1" in self.data.columns:
                # Убедимся, что "Date" — это даты
                self.data["Date"] = pd.to_datetime(self.data["Date"], errors='coerce')
                self.data = self.data.dropna(subset=["Date", "Value1"])  # Убираем строки с NaN
                self.data.sort_values("Date", inplace=True)  # Сортируем по дате
            
                # Построение графика
                self.ax.plot(self.data["Date"], self.data["Value1"], label="Value1", marker='o')
                self.ax.set_title("Line Chart: Date vs Value1")
                self.ax.set_xlabel("Date")
                self.ax.set_ylabel("Value1")
                self.ax.tick_params(axis='x', rotation=45)  # Поворот подписей на оси X для читаемости
                self.ax.legend()
    
                # Сброс пропорций графика
                self.ax.set_aspect('auto')  # Масштабируем график автоматически
                self.ax.autoscale()        # Включаем автоматическое масштабирование осей
    
        elif chartType == "Histogram":
            if "Value2" in self.data.columns:
                sns.histplot(data=self.data, x="Value2", ax=self.ax, kde=True)
                self.ax.set_title("Histogram of Value2")
                self.ax.set_xlabel("Value2")
                self.ax.set_ylabel("Frequency")
    
        elif chartType == "Pie Chart":
            if "Category" in self.data.columns:
                self.data["Category"].value_counts().plot.pie(
                    ax=self.ax, autopct='%1.1f%%', startangle=90, cmap="Pastel1"
                )
                self.ax.set_ylabel("")  # Убираем подпись оси Y
                self.ax.set_title("Category Distribution")
    
        # Обновляем график
        self.canvas.draw()




    def add_new_value(self):
        if self.data is None:
            return

        newValue = self.newValueInput.text()
        chartType = self.chartSelector.currentText()

        if chartType == "Line Chart" and "Value1" in self.data.columns:
            new_row = pd.DataFrame({"Date": [pd.Timestamp.now()], "Value1": [float(newValue)]})
            self.data = pd.concat([self.data, new_row], ignore_index=True)
        elif chartType == "Histogram" and "Value2" in self.data.columns:
            new_row = pd.DataFrame({"Value2": [float(newValue)]})
            self.data = pd.concat([self.data, new_row], ignore_index=True)

        self.update_chart()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = DataAnalysisApp()
    mainWin.show()
    sys.exit(app.exec_())
