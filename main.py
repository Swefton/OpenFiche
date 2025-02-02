import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLineEdit, QPushButton, QHBoxLayout, QTextBrowser,
    QListWidget, QListWidgetItem
)
from PyQt5.QtWebEngineWidgets import QWebEngineView


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Reader Mode with History")
        self.setGeometry(100, 100, 900, 700)

        self.reader_mode = False
        self.history = []  # Store visited links

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.reada.wiki/"))
        self.current_url = "https://www.reada.wiki/"
        self.reader_view = QWebEngineView()
        self.reader_view.hide()

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_from_history)

        # Main layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)


        # Search bar and buttons
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter URL or search term...")

        self.search_button = QPushButton("Go", self)
        self.search_button.clicked.connect(self.perform_search)

        self.reader_mode_button = QPushButton("Toggle Reader Mode", self)
        self.reader_mode_button.clicked.connect(self.toggle_reader_mode)

        self.history_button = QPushButton("View History", self)
        self.history_button.clicked.connect(self.toggle_history_view)

        # Layout for search controls
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.reader_mode_button)
        search_layout.addWidget(self.history_button)
        
        

        self.layout.addLayout(search_layout)
        self.layout.addWidget(self.browser)
        self.layout.addWidget(self.reader_view)

        # Central widget
        self.central_widget = QWidget(self)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.browser.urlChanged.connect(self.update_current_url)
        
        # Debugging lines
        # self.browser.setStyleSheet("border: 2px solid red;")
        # self.reader_view.setStyleSheet("border: 2px solid blue;")
        # self.history_list.setStyleSheet("border: 2px solid green;")
        # self.central_widget.setStyleSheet("border: 2px solid yellow;")

    def is_valid_url(self, input_text):
        """Check if the input is a valid URL."""
        parsed_url = urlparse(input_text)
        return all([parsed_url.scheme, parsed_url.netloc])
    
    def update_current_url(self, url: QUrl):
        """Update the URL in the search bar when the page changes."""
        self.current_url = url.toString()
        self.search_input.setText(self.current_url)  # Update URL bar
        # Optionally, add to history if it's a new URL
        if self.current_url and (not self.history or self.current_url != self.history[-1]):
            self.history.append(self.current_url)
            self.add_to_history_list(self.current_url)


    def perform_search(self):
        search_input = self.search_input.text().strip()
        if not search_input:
            return

        if self.is_valid_url(search_input):
            self.browser.setUrl(QUrl(search_input))
        elif search_input.startswith("www."):
            self.browser.setUrl(QUrl(f"https://{search_input}"))
        else:
            search_url = f"https://www.google.com/search?q={search_input}"
            self.browser.setUrl(QUrl(search_url))

    def update_current_url(self, url: QUrl):
        self.current_url = url.toString()

        # Add to history if it's a new URL
        if self.current_url and (not self.history or self.current_url != self.history[-1]):
            self.history.append(self.current_url)
            self.add_to_history_list(self.current_url)

    def add_to_history_list(self, url):
        """Add a URL to the QListWidget for display."""
        item = QListWidgetItem(url)
        self.history_list.addItem(item)

    def reader_mode_on(self):
        self.reader_mode = True

        if self.current_url:
            self.fetch_and_display_content(self.current_url)
            self.browser.hide()
            self.reader_view.show()

    def toggle_reader_mode(self):
        self.reader_mode = not self.reader_mode

        if self.reader_mode:
            if self.current_url:
                self.fetch_and_display_content(self.current_url)
                self.browser.hide()
                self.reader_view.show()
        else:
            self.reader_view.hide()
            self.browser.show()

    def fetch_and_display_content(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            content = ""
            
            # Filter out unwanted elements like advertisements, sidebars, or sponsor messages
            for ad_tag in soup.find_all(class_=['ad-wrap', 'sponsor', 'bucket', 'secondary']):
                ad_tag.decompose()  # Removes the unwanted tag from the tree

            # Extract desired tags: h1, h2, h3, p (headings and paragraphs)
            for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
                # Skip unwanted elements by excluding specific text or classes
                if tag.name in ['h1', 'h2', 'h3']:
                    content += f"<h2 style='color:#FFFFFF;'>{tag.get_text()}</h2>"
                elif tag.name == 'p':
                    # Ensure we are getting the right paragraphs (skip non-content or small text)
                    if not tag.find_parent(class_='footer') and not tag.find_parent(class_='ad-wrap'):
                        content += f"<p style='color:#DDDDDD; line-height:1.6;'>{tag.get_text()}</p>"

            # Final HTML structure with dark mode styling
            dark_mode_html = f"""
            <html>
                <body style='font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; background-color: #333333;'>
                    <div style='width: 100%; max-width: 60%; padding: 20px; background-color: #1e1e1e; box-sizing: border-box;'>
                        {content}
                    </div>
                </body>
            </html>
            """
            
            # Display in the QTextBrowser
            self.reader_view.setHtml(dark_mode_html)

        except requests.RequestException as e:
            self.reader_view.setText(f"Error loading page: {e}")


    def toggle_history_view(self):
        """Dynamically add or remove the history panel."""
        if self.history_list.isVisible():
            self.layout.removeWidget(self.history_list)
            self.history_list.hide()
            self.browser.show()
            if self.reader_mode:
                self.reader_mode_on()
            
        else:
            self.layout.addWidget(self.history_list)
            self.history_list.show()
            self.browser.hide()
            self.reader_view.hide()

    def load_from_history(self, item):
        """Load a URL from the history when clicked."""
        url = item.text()
        self.browser.setUrl(QUrl(url))
        self.toggle_history_view()  # Hide history after selecting


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())
