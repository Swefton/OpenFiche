import re
import json

with open("rev_keywords_wiki.json", "r") as f:
    data = json.load(f)

with open("page_rank_scores_wiki.json", "r") as f:
    scores = json.load(f)
    
q = "president"
words = [t.lower()[:len(t) - 1] for t in (re.sub('[^a-zA-Z]+', ' ', q)).split()]

#print(words)

poss = {}
for w in words:
    if w not in data: continue
    #print(w)
    li = data[w]

    for l in li:
        if l in poss:
            poss[l] += 1
        else:
            poss[l] = 1
            
    for l in scores:
        if w in l:
            if l in poss:
                poss[l] += 1
            else: 
                poss[l] = 1
    
li = []
for l in poss:
    li.append((poss[l] * scores[l], l))

li.sort()
#li = li[::-1]
for a in li: print(a)




