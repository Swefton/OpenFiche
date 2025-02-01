import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Web Search Browser")
        self.setGeometry(100, 100, 800, 600)

        # Create a web engine view to display the page
        self.browser = QWebEngineView()

        # Layout for the browser window
        layout = QVBoxLayout()

        # Create the search bar and button
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter search term...")

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.perform_search)

        # Layout for the search input and button
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # Add widgets to the main layout
        layout.addLayout(search_layout)
        layout.addWidget(self.browser)

        # Create central widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)

        # Set the central widget
        self.setCentralWidget(central_widget)

    def perform_search(self):
        # Get the search term from the input field
        search_term = self.search_input.text()
        if search_term:
            # Open the browser with the search URL (using Google as an example)
            search_url = f"https://www.google.com/search?q={search_term}"
            self.browser.setUrl(QUrl(search_url))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the main browser window
    window = BrowserWindow()
    window.show()

    sys.exit(app.exec_())
