import re
import json

with open("rev_keywords.json", "r") as f:
    data = json.load(f)
    
q = "cow is algorithm and race?"
words = [t.lower() for t in (re.sub('[^a-zA-Z]+', ' ', q)).split()]

poss = {}
for w in words:
    if w not in data: continue
    print(w)
    li = data[w]

    for l in li:
        if l in poss:
            poss[l] += 1
        else:
            poss[l] = 1

print(poss)


