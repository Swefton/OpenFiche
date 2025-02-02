from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtCore import QUrl, QCoreApplication
from PyQt5.QtWidgets import QApplication
import sys

class TitleFetcher:
    def __init__(self, app):
        self.app = app

    def get_title_from_url(self, url):
        page = QWebEnginePage()  # Headless, no UI
        page.load(QUrl(url))

        def handle_load_finished():
            page.runJavaScript("document.title", lambda title: self.handle_title_result(title, url))

        page.loadFinished.connect(handle_load_finished)

    def handle_title_result(self, title, url):
        print(f"URL: {url}")
        print(f"Page Title: {title}")
        self.app.quit()  # Exit the app after fetching the title

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fetcher = TitleFetcher(app)

    # Test URL
    test_url = "https://www.google.com/search?q=apple"
    fetcher.get_title_from_url(test_url)

    # Run the event loop
    sys.exit(app.exec_())
