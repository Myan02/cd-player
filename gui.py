from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PyQt6.QtCore import QSize, Qt


class MainDisplay(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CD Player Window")
        self.setFixedSize(QSize(128, 64))

        layout = QVBoxLayout()
        self.displayText = QLabel("")
        layout.addWidget(self.displayText)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        main_widget = QWidget()
        main_widget.setLayout(layout)

        self.setCentralWidget(main_widget)
    
    def updateDisplay(self, text):
        self.displayText.setText(text)


def test_gui():
    app = QApplication([])
    
    window = MainDisplay()
    window.updateDisplay("test screen")
    window.show()
    
    app.exec()


if __name__ == "__main__":
    test_gui()