from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import json

app = Flask(__name__)
CORS(app)

with open("rev_keywords_npr.json", "r") as f:
    data = json.load(f)

with open("rev_keywords_cnn.json", "r") as f:
    data.update(json.load(f))

with open("rev_keywords_wiki.json", "r") as f:
    data.update(json.load(f))

with open("page_rank_scores_npr.json", "r") as f:
    scores = json.load(f)
    
with open("page_rank_scores_cnn.json", "r") as f:
    scores.update(json.load(f))

with open("page_rank_scores_wiki.json", "r") as f:
    l = json.load(f)
    for k in l: l[k] *= 25
    scores.update(l)

@app.route("/search", methods=["GET"])
def search():
    q = request.args.get("q", "")
    words = [t.lower()[:len(t) - 1] for t in (re.sub('[^a-zA-Z]+', ' ', q)).split()] + (re.sub('[^a-zA-Z]+', ' ', q)).split()
    poss = {}
    for w in words:
        if w not in data: 
            continue
        for l in data[w]:
            poss[l] = poss.get(l, 0) + (1 if "wikipedia" not in l else 10)

        for l in scores:
            if w in l:
                if l in poss:
                    poss[l] += 1
                else: 
                    poss[l] = 1

    results = [(poss[l] * scores[l], l) for l in poss]
    results.sort(reverse=True)  
    
    return jsonify(results[:25])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
