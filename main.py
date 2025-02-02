import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from PyQt5.QtCore import Qt, QUrl, QEventLoop
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget,
    QLineEdit, QPushButton, QHBoxLayout,
    QListWidget, QTabWidget, QToolBar, QAction
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
import networkx as nx
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui


class BrowserTab(QWidget):
    """
    A single browser tab that maintains its own reader mode,
    browsing history, and graph data.
    """
    def __init__(self, url="https://www.reada.wiki/"):
        super().__init__()
        
        self.reader_mode = False
        self.graph = nx.DiGraph()
        self.current_node = None
        self.current_url = url
        self.previous_url = None
        self.current_title = "Home"
        self.previous_title = ""

        # Main layout for this tab
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create widgets
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.current_url))
        
        self.reader_view = QWebEngineView()
        self.reader_view.hide()

        self.history_list = QListWidget()

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

        # Connect signals
        self.browser.urlChanged.connect(self.update_current_url)
        self.browser.loadFinished.connect(self.on_load_finished)

    def is_valid_url(self, input_text):
        """Check if the input is a valid URL."""
        parsed_url = urlparse(input_text)
        return all([parsed_url.scheme, parsed_url.netloc])

    def update_current_url(self, url: QUrl):
        """Update the URL in the search bar when the page changes."""
        self.previous_url = self.current_url
        self.current_url = url.toString()
        # Optionally update self.current_title if needed:
        # self.current_title = "Current title"  # You could extract it here
        self.search_input.setText(self.current_url)

    def perform_search(self):
        """Handle search queries from the address bar."""
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

        self.print_graph()

    def toggle_reader_mode(self):
        """Toggle between reader mode and regular browsing mode."""
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
        """Fetch the content and display it in a customized reader view."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            content = ""
            # Remove ads or sponsor sections
            for ad_tag in soup.find_all(class_=['ad-wrap', 'sponsor', 'bucket', 'secondary']):
                ad_tag.decompose()

            # Grab headings and paragraphs
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
            self.reader_view.setHtml(f"<h3 style='color: red;'>Error loading page: {e}</h3>")

    def get_title_from_url(self, url):
        page = QWebEnginePage(self)
        page.load(QUrl(url))

        loop = QEventLoop()
        title_container = {"title": None}

        def handle_load_finished():
            page.runJavaScript("document.title", lambda title: handle_title_result(title))

        def handle_title_result(title):
            title_container["title"] = title
            loop.quit()

        page.loadFinished.connect(handle_load_finished)
        loop.exec_()

        return title_container["title"]

    def toggle_history_view(self):
        """Toggle between showing the history graph and the browser/reader."""
        if hasattr(self, "graph_view") and self.graph_view.isVisible():
            self.layout.removeWidget(self.graph_view)
            self.graph_view.hide()
            if self.reader_mode:
                self.reader_view.show()
            else:
                self.browser.show()
        else:
            self.display_interactive_graph()

    def display_interactive_graph(self):
        """Display an interactive NetworkX graph using PyQtGraph."""
        if not hasattr(self, "graph_view"):
            self.graph_view = pg.GraphicsLayoutWidget()
            self.graph_view.setWindowTitle("Interactive Graph")

        self.graph_view.clear()

        plot_item = self.graph_view.addPlot()
        plot_item.setAspectLocked(True)

        pos = nx.spring_layout(self.graph, seed=42, k=0.8, scale=10)
        node_positions = {node: (pos[node][0], pos[node][1]) for node in self.graph.nodes}
        x_data, y_data = zip(*node_positions.values()) if node_positions else ([], [])

        scatter = pg.ScatterPlotItem(x_data, y_data, size=20, brush=pg.mkBrush("blue"))
        plot_item.addItem(scatter)

        # Draw edges
        for start, end in self.graph.edges:
            x_start, y_start = node_positions[start]
            x_end, y_end = node_positions[end]
            line = pg.PlotDataItem(x=[x_start, x_end], y=[y_start, y_end], pen=pg.mkPen("gray", width=2))
            plot_item.addItem(line)

            # Arrow
            arrow = pg.ArrowItem(pos=(x_end, y_end), angle=0, headLen=10, brush=pg.mkBrush("red"))
            plot_item.addItem(arrow)

        # Draw labels
        for node, (x, y) in node_positions.items():
            text = pg.TextItem(text=node, anchor=(0.5, 0.5), color="white")
            text.setPos(x, y)
            plot_item.addItem(text)

        node_mapping = {tuple(pos): node for node, pos in node_positions.items()}

        def on_node_clicked(plot, points):
            for p in points:
                clicked_pos = (p.pos().x(), p.pos().y())
                node_name = node_mapping.get(clicked_pos, None)
                if node_name:
                    self.current_node = node_name
                    node_data = self.graph.nodes.get(node_name, {})
                    url = node_data.get("url")
                    if url:
                        self.browser.setUrl(QUrl(url))
                        self.toggle_history_view()

        scatter.sigClicked.connect(on_node_clicked)

        self.layout.addWidget(self.graph_view)
        self.graph_view.show()
        self.browser.hide()
        self.reader_view.hide()

    def on_load_finished(self, success):
        """Create and link graph nodes once the page finishes loading."""
        if success:
            current_title = self.get_title_from_url(self.current_url).strip()
            # Add new node if not present
            self.graph.add_node(current_title, url=self.current_url)

            # If we had a previous node, create an edge
            if self.current_node and self.current_node != current_title:
                self.graph.add_edge(self.current_node, current_title)

            self.current_node = current_title
            # (Optional) self.print_graph()

    def print_graph(self):
        """Print and plot the current state of the graph to a Matplotlib window."""
        print("Current Graph:")
        for node in self.graph.nodes:
            print(f"Node: {node}")
        for edge in self.graph.edges:
            print(f"Edge: {edge}")

        pos = nx.spring_layout(self.graph, seed=42)
        plt.clf()
        nx.draw_networkx_edges(self.graph, pos, edge_color="gray", width=2)
        nx.draw(self.graph, pos, with_labels=False, node_size=500,
                node_color="skyblue", alpha=0.7)
        nx.draw_networkx_labels(self.graph, pos, font_size=10)
        plt.show()


class MainWindow(QMainWindow):
    """
    Main application window holding a QTabWidget
    to manage multiple BrowserTabs.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenFiche Net - Multi Tab")
        self.setGeometry(100, 100, 1200, 800)

        # Create a central widget and layout
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

        # Create a toolbar for the "New Tab" button
        toolbar = QToolBar("Tab Controls", self)
        self.addToolBar(toolbar)

        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.create_new_tab)
        toolbar.addAction(new_tab_action)

        # Create the tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        central_layout.addWidget(self.tab_widget)

        # Open one default tab
        self.create_new_tab()

    def create_new_tab(self):
        """
        Create a new BrowserTab and add it to the QTabWidget.
        By default, it loads 'https://www.reada.wiki/'.
        """
        new_tab = BrowserTab("https://www.reada.wiki/")
        index = self.tab_widget.addTab(new_tab, "New Tab")
        self.tab_widget.setCurrentIndex(index)

        # Optional: Update the tab text when title changes.
        # If you want dynamic tab titles, connect a signal:
        # new_tab.browser.titleChanged.connect(
        #     lambda title: self.tab_widget.setTabText(index, title[:15])
        # )

    def close_tab(self, index):
        """Close the requested tab."""
        tab = self.tab_widget.widget(index)
        if tab:
            self.tab_widget.removeTab(index)
            tab.deleteLater()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
