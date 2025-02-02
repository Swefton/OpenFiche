import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLineEdit, QPushButton, QHBoxLayout,
    QListWidget, QListWidgetItem
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
import networkx as nx 
import matplotlib.pyplot as plt

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Reader Mode with History")
        self.setGeometry(100, 100, 900, 700)

        self.reader_mode = False
        self.graph = nx.DiGraph()
        self.current_url = "https://www.reada.wiki/"
        self.previous_url = None

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.current_url))
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

    def is_valid_url(self, input_text):
        """Check if the input is a valid URL."""
        parsed_url = urlparse(input_text)
        return all([parsed_url.scheme, parsed_url.netloc])

    def update_current_url(self, url: QUrl):
        """Update the URL in the search bar when the page changes."""
        self.previous_url = self.current_url  # Store the previous URL
        self.current_url = url.toString()
        self.search_input.setText(self.current_url)

        # Add the current page to the graph if it's a valid navigation
        if self.previous_url:
            self.graph.add_edge(self.previous_url, self.current_url)

        # Print the current state of the graph for debugging
        self.print_graph()

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

    def add_to_history_list(self, url):
        """Add a URL to the QListWidget for display."""
        item = QListWidgetItem(url)
        self.history_list.addItem(item)

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
            for ad_tag in soup.find_all(class_=['ad-wrap', 'sponsor', 'bucket', 'secondary']):
                ad_tag.decompose()

            for tag in soup.find_all(['h1', 'h2', 'h3', 'p']):
                if tag.name in ['h1', 'h2', 'h3']:
                    content += f"<h2 style='color:#FFFFFF;'>{tag.get_text()}</h2>"
                elif tag.name == 'p':
                    if not tag.find_parent(class_='footer') and not tag.find_parent(class_='ad-wrap'):
                        content += f"<p style='color:#DDDDDD; line-height:1.6;'>{tag.get_text()}</p>"

            dark_mode_html = f"""
            <html>
                <body style='font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; background-color: #333333;'>
                    <div style='width: 100%; max-width: 60%; padding: 20px; background-color: #1e1e1e; box-sizing: border-box;'>
                        {content}
                    </div>
                </body>
            </html>
            """
            self.reader_view.setHtml(dark_mode_html)

        except requests.RequestException as e:
            self.reader_view.setText(f"Error loading page: {e}")

    def toggle_history_view(self):
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
        url = item.text()
        self.browser.setUrl(QUrl(url))
        self.toggle_history_view()

    def print_graph(self):
        """Print the current state of the graph to the terminal."""
        print("Current Graph:")
        for node in self.graph.nodes:
            print(f"Node: {node}")
        for edge in self.graph.edges:
            print(f"Edge: {edge}")
        
        # Use a layout to get positions for the nodes
        pos = nx.spring_layout(self.graph)  # This generates node positions automatically

        # Customize node appearance
        nx.draw(self.graph, pos, with_labels=True, node_size=500, node_color="skyblue", node_shape="o", alpha=0.7)

        # Customize edge appearance
        nx.draw_networkx_edges(self.graph, pos, edge_color="gray", width=2)

        # Display the plot
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())
