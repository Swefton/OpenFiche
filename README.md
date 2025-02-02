# **OpenFiche – A Read-First Search Engine**  
[![GitHub](https://img.shields.io/badge/GitHub-repo-blue?logo=github)](https://github.com/soham-phargade/readawiki)  

## **Overview**  
**OpenFiche** is a lightweight, **post-AI search engine** that prioritizes **high-signal, human-vetted content** over engagement-driven results. Inspired by microfiche, it indexes Wikipedia (CS-related articles), CNN, and NPR, using **PageRank + keyword scoring** to rank pages based on relevance, not SEO tricks.  

## **Features**  
✅ **Transparent Ranking** – Uses **PageRank + keyword analysis** for results  
✅ **Minimalist UI** – Built with **React** for a fast, clean experience  

## **Tech Stack**  
- **Frontend**: React 
- **Backend**: FastAPI
- **Search Algorithm**: PageRank + keyword scoring  

## **Installation & Setup**  
1. **Clone the repository**

   ```bash
   git clone https://github.com/soham-phargade/readawiki.git
   cd readawiki
   ```
3. **Install dependencies**
  
    ```bash
    npm install
    ```
3. **Run the development server**

   ```bash
    npm start
    ```
5. **Backend Setup (if running locally)
    ```bash
    pip install -r backend/requirements.txt
    python backend/main.py
    ```
5. **Access OpenFiche**
Open your browser and go to http://localhost:3000

## **Usage**
- Enter search queries in the search bar.
- OpenFiche ranks results using PageRank and query-specific keyword scores.
- Use Reader Mode for distraction-free content viewing.
- Navigate history as a graph structure.

## **License**
The project is licensed under the MIT License.
