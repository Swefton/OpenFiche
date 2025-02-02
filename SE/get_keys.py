import json
import re
import requests
import nltk
from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure NLTK dependencies are downloaded
nltk.download('stopwords')
nltk.download('wordnet')

def fetch_html(url):
    """Fetch HTML content from a webpage."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text

def extract_keywords(html_content):
    """Extract keywords from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract title and meta keywords
    title = soup.title.string if soup.title else ""
    meta_keywords = []
    for tag in soup.find_all("meta", attrs={"name": "keywords"}):
        meta_keywords += tag.get("content", "").split(",")

    # Extract headers and paragraphs
    headers = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])]
    paragraphs = [p.get_text() for p in soup.find_all('p')]

    # Combine text
    text_content = " ".join([title] + meta_keywords + headers + paragraphs)
    
    # Tokenize words and clean up
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text_content.lower())  # Filter out short words

    # Remove stop words and lemmatize
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    filtered_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]

    # Count word frequencies
    keyword_counts = Counter(filtered_words)
    common_keywords = [word for word, _ in keyword_counts.most_common(15)]  # Top 15 keywords

    return common_keywords

def generate_variations(keywords):
    """Generate keyword variations for SEO optimization."""
    variations = set()
    for word in keywords:
        variations.add(word)
        variations.add(word + "s")  # Plural
        variations.add(word.capitalize())  # Capitalized
        variations.add(word.upper())  # Uppercase
        if len(word) > 5:
            variations.add(word[:len(word) - 1])  # Shortened version
    return list(variations)

def save_to_json(data, filename="keywords_wiki.json"):
    """Save keyword variations along with URLs to a JSON file."""
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

# Example Usage
if __name__ == "__main__":
    with open("webgraph_wiki_4400.json", "r") as f:
        data = json.load(f)
    
    ma = {}
    idx = 0
    for url in data["nodes"]:
        if idx % 100 == 0: 
            print("Progress:", idx, len(data["nodes"]))
            save_to_json(ma)
        idx += 1
        try:
            html_content = fetch_html(url)

            keywords = extract_keywords(html_content)
            keyword_variations = generate_variations(keywords)
        
            # print(url, *keywords)
            ma[url] = keyword_variations
        except:
            continue
    
    save_to_json(ma)
        
        
    