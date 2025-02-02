import re
import json

with open("rev_keywords.json", "r") as f:
    data = json.load(f)

with open("page_rank_scores.json", "r") as f:
    scores = json.load(f)
    
q = "trump tarrifs canada"
words = [t.lower()[:len(t) - 1] for t in (re.sub('[^a-zA-Z]+', ' ', q)).split()]

poss = {}
for w in words:
    if w not in data: continue
    li = data[w]

    for l in li:
        if l in poss:
            poss[l] += 1
        else:
            poss[l] = 1
li = []
for l in poss:
    li.append((poss[l] * scores[l], l))

li.sort()

for a in li: print(a)




