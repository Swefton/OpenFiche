import sys
import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLineEdit, QPushButton, QHBoxLayout, QTextBrowser, QScrollArea
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Reader Mode")
        self.setGeometry(100, 100, 900, 700)

        # Track current URL and Reader Mode status
        self.current_url = ""
        self.reader_mode = False

        # Create the web engine view
        self.browser = QWebEngineView()

        # Reader mode view (initially hidden)
        self.reader_view = QTextBrowser()
        self.reader_view.hide()

        # Layout for the browser window
        layout = QVBoxLayout()

        # Search bar and buttons
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter search term...")

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.perform_search)

        self.reader_mode_button = QPushButton("Toggle Reader Mode", self)
        self.reader_mode_button.clicked.connect(self.toggle_reader_mode)

        # Layout for the search bar and buttons
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reader_mode_button)

        # Add widgets to the main layout
        layout.addLayout(search_layout)
        layout.addWidget(self.browser)
        layout.addWidget(self.reader_view)

        # Central widget
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Track URL changes
        self.browser.urlChanged.connect(self.update_current_url)

    def perform_search(self):
        search_term = self.search_input.text()
        if search_term:
            search_url = f"https://www.google.com/search?q={search_term}"
            self.browser.setUrl(QUrl(search_url))

    def update_current_url(self, url: QUrl):
        self.current_url = url.toString()

    def toggle_reader_mode(self):
        self.reader_mode = not self.reader_mode

        if self.reader_mode:
            # Activate Reader Mode
            if self.current_url:
                self.fetch_and_display_content(self.current_url)
                self.browser.hide()
                self.reader_view.show()
        else:
            # Exit Reader Mode
            self.reader_view.hide()
            self.browser.show()

    def fetch_and_display_content(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract headers, paragraphs, and images
            content = ""
            for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
                if tag.name in ['h1', 'h2', 'h3']:
                    content += f"<h2 style='color:#FFFFFF;'>{tag.get_text()}</h2>"
                elif tag.name == 'p':
                    content += f"<p style='color:#DDDDDD; line-height:1.6;'>{tag.get_text()}</p>"

            # Apply dark mode styling
            dark_mode_html = f"""
                <html>
                <body style='background-color:#121212; padding:20px; font-family:Arial, sans-serif;'>
                    {content}
                </body>
                </html>
            """

            self.reader_view.setHtml(dark_mode_html)

        except requests.RequestException as e:
            self.reader_view.setText(f"Error loading page: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())
