import json

def save_to_json(data, filename="rev_keywords_npr.json"):
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


with open("keywords_npr.json", "r") as f:
    data = json.load(f)

ma = {}
for entry in data:
    ke = data[entry]
    for ki in ke:
        k = ki.lower()
        if ma.get(k) is not None and entry not in ma.get(k):
            ma[k].append(entry)
        else:
            ma[k] = [entry]

save_to_json(ma)

