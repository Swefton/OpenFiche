import json
import networkx as nx
import matplotlib.pyplot as plt

with open("webgraph_npr.json", "r") as f:
    data = json.load(f)
    
def save_to_json(data, filename="page_rank_scores_npr.json"):
    try:
        with open(filename, "r") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {}

    # Add new data to the existing JSON data
    existing_data.update(data)

    # Write the updated data back to the file
    with open(filename, "w") as file:
        json.dump(existing_data, file, indent=4)

into = {}
outof = {}

for edge in data["edges"]:
    if outof.get(edge[0]) is not None: outof[edge[0]].append(edge[1])
    else: outof[edge[0]] = [edge[1]]
    if into.get(edge[1]) is not None: into[edge[1]].append(edge[0])
    else: into[edge[1]] = [edge[0]]

# Ensure all nodes are present
nodes = set(outof.keys()) | set(into.keys())
for node in nodes:
    outof.setdefault(node, [])  # Ensure all nodes have an out-degree entry
    into.setdefault(node, [])  # Ensure all nodes have an in-degree entry

# PageRank Parameters
damping_factor = 0.85
num_iterations = 100
tolerance = 1e-6
num_nodes = len(nodes)

# Initialize PageRank values
pagerank = {node: 1 / num_nodes for node in nodes}

# PageRank Iteration
for _ in range(num_iterations):
    new_pagerank = {}
    max_delta = 0

    for node in nodes:
        rank_sum = sum(pagerank[in_node] / len(outof[in_node]) for in_node in into[node] if len(outof[in_node]) > 0)
        new_pagerank[node] = (1 - damping_factor) / num_nodes + damping_factor * rank_sum
        max_delta = max(max_delta, abs(new_pagerank[node] - pagerank[node]))

    pagerank = new_pagerank  # Update ranks
    if max_delta < tolerance:  # Check for convergence
        break

ma = {}
# Sort and Display Results
sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
for node, rank in sorted_pagerank:  # Show top 10 ranked pages
    ma[node] = rank * 10**(5)

save_to_json(ma)
