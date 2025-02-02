from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os


# test cnn, npr, wikipedia

class ReaderModeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reader Mode Example")
        self.setGeometry(100, 100, 800, 600)

        self.web_view = QWebEngineView()

        self.toggle_button = QPushButton("Reload Reader Mode")
        self.toggle_button.clicked.connect(self.load_local_file)

        layout = QVBoxLayout()
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.web_view)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Load the local HTML file initially
        self.load_local_file()

    def load_local_file(self):
        local_file_path = os.path.abspath("reader_mode_test.html")
        if os.path.exists(local_file_path):
            self.web_view.load(QUrl.fromLocalFile(local_file_path))
        else:
            self.web_view.setHtml("<h2 style='color: red;'>File not found: reader_mode_test.html</h2>")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ReaderModeApp()
    window.show()
    sys.exit(app.exec_())
