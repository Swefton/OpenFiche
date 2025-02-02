import time
import os
import networkx as nx
import requests
from bs4 import BeautifulSoup
import json

ALLOWED_DOMAINS = ["en.wikipedia.org"]

def is_allowed(url):
    return any(url.startswith(f"https://{domain}") for domain in ALLOWED_DOMAINS)

def get_links(url):
    print(url)
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        links = set()
        for a_tag in soup.find_all("a", href=True):
            link = a_tag["href"]
            if link[:5] == "/wiki" and "Special:" not in link and "Wikipedia:" not in link and "Category:" not in link and "Help:" not in link and "File:" not in link and "Portal:" not in link and "Template:" not in link and "Template_talk:" not in link and "Talk:" not in link:
                links.add("https://en.wikipedia.org/" + link)
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return set()

def build_web_graph(start_urls, max_depth, save_interval=100):
    graph = nx.DiGraph()
    queue = [(url, 0) for url in start_urls]
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

        if processed_count % save_interval == 0:
            os.system("rm webgraph.json")
            print(f"Saving progress at {processed_count} URLs processed...")
            save_graph(graph, "webgraph.json")

    return graph

def save_graph(graph, filename="webgraph.json"):
    data = {
        "nodes": list(graph.nodes),
        "edges": list(graph.edges)
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    start_urls = ["https://en.wikipedia.org/wiki/Web_graph"]
    web_graph = build_web_graph(start_urls, max_depth=3)
    save_graph(web_graph)
    print("Web graph saved to webgraph.json")
