import time
import os
import networkx as nx
import requests
from bs4 import BeautifulSoup
import json
import re

# Define allowed domains and language filter
ALLOWED_DOMAINS = ["https://www.cnn.com"]
pattern = r"^https://www\.cnn\.com/\d{4}/\d{2}/\d{2}/.*$"

# Function to check if a URL belongs to allowed domains
def is_allowed(url):
    return any(url.startswith(f"https://{domain}") for domain in ALLOWED_DOMAINS)

# Function to fetch and parse links from a webpage
def get_links(url):
    print(url)
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = set()
        for a_tag in soup.find_all("a", href=True):
            link = a_tag["href"]
            if re.match(pattern, link):
                links.add(link)
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return set()

# Function to build a web graph with depth control
def build_web_graph(start_urls, max_depth, save_interval=10):
    graph = nx.DiGraph()
    queue = [(url, 0) for url in start_urls]  # (URL, depth)
    visited = set()
    processed_count = 0

    while queue:
        url, depth = queue.pop(0)
        if url in visited or depth > max_depth:
            continue
        visited.add(url)
        graph.add_node(url)
        links = get_links(url)
        for link in links:
            graph.add_edge(url, link)
            if link not in visited and all(l != link for l, _ in queue):
                queue.append((link, depth + 1))

        processed_count += 1

        # Save progress every 'save_interval' URLs
        if processed_count % save_interval == 0:
            os.system("rm webgraph_cnn.json")
            print(f"Saving progress at {processed_count} URLs processed...")
            save_graph(graph, "webgraph_cnn.json")

    return graph


# Function to save the graph to JSON
def save_graph(graph, filename="webgraph_cnn.json"):
    data = {
        "nodes": list(graph.nodes),
        "edges": list(graph.edges)
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# Example usage
if __name__ == "__main__":
    start_urls = ["https://www.cnn.com"]
    web_graph = build_web_graph(start_urls, max_depth=7)
    save_graph(web_graph)
    print("Web graph saved to webgraph.json")
