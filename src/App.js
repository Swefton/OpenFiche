import React, { useState, useEffect } from 'react';
import './App.css';

/**
 * HistorySidebar Component
 *
 * Displays the search history as a one‑level tree. Each query node shows the search query,
 * and its only children (leaf nodes) are the articles the user clicked.
 *
 * The header displays a label ("Search History") and a history icon.
 * Clicking anywhere on the header toggles the collapse/expand state.
 */
function HistorySidebar({
  history,
  expandedNodes,
  onToggle,
  onQueryClick,
  onDelete,
  activeQueryId,
  isOpen,
  onToggleSidebar,
}) {
  return (
    <div className={`sidebar ${isOpen ? 'open' : 'collapsed'}`}>
      <div className="sidebar-header" onClick={onToggleSidebar}>
        {isOpen ? (
          <>
            <h2 className="sidebar-title">Search History</h2>
            <span className="sidebar-icon">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                viewBox="0 0 24 24"
              >
                <polyline points="12 8 12 12 14 14"></polyline>
                <path d="M21 12a9 9 0 1 1-3.5-7.5"></path>
              </svg>
            </span>
          </>
        ) : (
          <span className="sidebar-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              viewBox="0 0 24 24"
            >
              <polyline points="12 8 12 12 14 14"></polyline>
              <path d="M21 12a9 9 0 1 1-3.5-7.5"></path>
            </svg>
          </span>
        )}
      </div>
      {isOpen && (
        <ul className="history-tree">
          {history.map((queryItem) => {
            // By default, a query's articles list is expanded if no value is set.
            const isExpanded =
              expandedNodes[queryItem.id] === undefined
                ? true
                : expandedNodes[queryItem.id];
            return (
              <li
                key={queryItem.id}
                className={`tree-node ${
                  activeQueryId === queryItem.id ? 'active' : ''
                }`}
              >
                <div
                  className="node-content"
                  onClick={() => onQueryClick(queryItem)}
                >
                  {queryItem.articles.length > 0 && (
                    <span
                      className="toggle-icon"
                      onClick={(e) => {
                        e.stopPropagation();
                        onToggle(
                          queryItem.id,
                          expandedNodes[queryItem.id] === undefined
                            ? false
                            : !expandedNodes[queryItem.id]
                        );
                      }}
                      style={{
                        transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                        transition: 'transform 0.3s ease',
                      }}
                    >
                      ▶
                    </span>
                  )}
                  <span className="node-label">{queryItem.query}</span>
                  <button
                    className="delete-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(queryItem.id, 'query');
                    }}
                  >
                    🚮
                  </button>
                </div>
                {queryItem.articles && queryItem.articles.length > 0 && (
                  <ul
                    className="tree-children"
                    style={{
                      maxHeight: isExpanded ? '500px' : '0',
                      transition: 'max-height 0.5s ease',
                      overflow: 'hidden',
                    }}
                  >
                    {queryItem.articles.map((article) => (
                      <li key={article.id} className="child-node">
                        <div
                          className="node-content"
                          onClick={() => onQueryClick(article)}
                        >
                          <span className="node-label">{article.title}</span>
                          <button
                            className="delete-button"
                            onClick={(e) => {
                              e.stopPropagation();
                              onDelete(article.id, 'link', queryItem.id);
                            }}
                          >
                            🚮
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

/**
 * Fetch the metadata (title and description) for a given URL by fetching its HTML
 * and parsing the metatags.
 */
// async function fetchMetadata(url) {
//   try {
//     const response = await fetch(url);
//     const htmlText = await response.text();
//     const parser = new DOMParser();
//     const doc = parser.parseFromString(htmlText, 'text/html');
//     const metaTitle = doc.querySelector('title')?.textContent || '';
//     const metaDescription =
//       doc.querySelector('meta[name="description"]')?.getAttribute('content') ||
//       doc.querySelector('meta[property="og:description"]')?.getAttribute('content') ||
//       '';
//     return { title: metaTitle, description: metaDescription };
//   } catch (error) {
//     console.error('Error fetching metadata for', url, error);
//     return { title: '', description: '' };
//   }
// }

async function fetchMetadata(url) {
  try {
    const response = await fetch(url);
    const htmlText = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, 'text/html');

    const metaTitle = doc.querySelector('title')?.textContent || '';

    const metaDescription =
      doc.querySelector('meta[name="description"]')?.getAttribute('content') ||
      doc.querySelector('meta[property="og:description"]')?.getAttribute('content') ||
      doc.querySelector('meta[name="twitter:description"]')?.getAttribute('content') || 
      '';

    return { title: metaTitle, description: metaDescription };
  } catch (error) {
    console.error('Error fetching metadata for', url, error);
    return { title: '', description: '' };
  }
}


/**
 * App Component
 *
 * – When the user submits a search, a new query node is created and added at the top of the history.
 * – The active query (the most recent search) is used for adding clicked article links as leaf nodes.
 * – Clicking a query in the sidebar re‑runs that search.
 */
function App() {
  // History is an array of query objects: { id, query, articles: [ { id, title, url } ] }
  const [history, setHistory] = useState([]);
  // activeQueryId is the id of the currently active search query.
  const [activeQueryId, setActiveQueryId] = useState(null);
  // Search input and results state
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // Sidebar open/collapsed state and node expansion state
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [expandedNodes, setExpandedNodes] = useState({});

  // Load saved history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('searchHistory');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('searchHistory', JSON.stringify(history));
  }, [history]);

  // Execute a search query using the custom search engine API.
  const doSearch = async (searchQuery) => {
    setLoading(true);
    setError(null);
    try {
      // Convert the search query so that spaces become plus signs.
      const formattedQuery = searchQuery.trim().replace(/\s+/g, '+');
      const response = await fetch(
        `http://35.11.25.188:5000/search?q=${formattedQuery}`
      );
      const data = await response.json();
      // Data is in the format:
      // [ [ score, "url" ], [ score, "url" ], ... ]
      // Map the data to objects, assign a logo based on the domain, and extract an initial title.
      const resultsData = data.map((item) => {
        const [/*score*/, url] = item; // remove score
        let title = url;
        let logoUrl = '';
        try {
          const urlObj = new URL(url);
          // Determine logo based on domain
          if (urlObj.hostname.includes('cnn')) {
            logoUrl =
              'https://upload.wikimedia.org/wikipedia/commons/b/b1/CNN.svg';
          } else if (urlObj.hostname.includes('wikipedia')) {
            logoUrl =
              'https://upload.wikimedia.org/wikipedia/commons/4/46/Wikipedia-W-visual-balanced.svg';
          } else if (urlObj.hostname.includes('npr')) {
            logoUrl =
              'https://upload.wikimedia.org/wikipedia/commons/d/d7/National_Public_Radio_logo.svg';
          }
          // Extract a candidate title from the URL's pathname.
          const parts = urlObj.pathname.split('/').filter(Boolean);
          if (parts.length > 0) {
            // Use the second-to-last part if the last part is "index"
            let candidate = parts[parts.length - 1].split('.')[0];
            if (candidate.toLowerCase() === 'index' && parts.length > 1) {
              candidate = parts[parts.length - 2];
            }
            // Replace dashes/underscores with spaces and apply Title Case.
            candidate = candidate.replace(/[-_]/g, ' ');
            title = candidate
              .split(' ')
              .map(
                (word) =>
                  word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
              )
              .join(' ');
          }
        } catch (err) {
          title = url;
        }
        return { url, title, logoUrl, description: '' };
      });
      setResults(resultsData);

      // For each result, fetch its metadata (title and description) from the URL.
      resultsData.forEach((result) => {
        fetchMetadata(result.url).then((metadata) => {
          setResults((prevResults) =>
            prevResults.map((r) =>
              r.url === result.url
                ? {
                    ...r,
                    // Use the fetched title if available; otherwise keep the fallback.
                    title: metadata.title || r.title,
                    description: metadata.description,
                  }
                : r
            )
          );
        });
      });
    } catch (err) {
      setError('Error fetching results');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // When the user submits a search, create a new query node.
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    await doSearch(query);
    const newQueryNode = {
      id: Date.now().toString(),
      query: query,
      articles: [],
    };
    setHistory((prev) => [newQueryNode, ...prev]);
    setActiveQueryId(newQueryNode.id);
  };

  // When a result is clicked, add it as a leaf under the active query and open it.
  const handleResultClick = (result) => {
    if (!activeQueryId) return;
    const newArticle = {
      id: Date.now().toString(),
      title: result.title,
      url: result.url,
    };
    setHistory((prev) =>
      prev.map((q) => {
        if (q.id === activeQueryId) {
          if (!q.articles.find((a) => a.url === newArticle.url)) {
            return { ...q, articles: [...q.articles, newArticle] };
          }
        }
        return q;
      })
    );
    window.open(newArticle.url, '_blank');
  };

  // When a query (or its article) in the sidebar is clicked:
  // – If it’s a query node, set it as active and re‑run the search.
  // – If it’s an article node, open its URL.
  const handleQueryClick = (item) => {
    if (item.url) {
      window.open(item.url, '_blank');
    } else {
      setActiveQueryId(item.id);
      setQuery(item.query);
      doSearch(item.query);
    }
  };

  // Delete a node from the history.
  // For type "query", remove the entire query node.
  // For type "link", remove that article from the parent query.
  const handleDelete = (id, type, parentId = null) => {
    if (type === 'query') {
      setHistory((prev) => prev.filter((q) => q.id !== id));
      if (activeQueryId === id) {
        setActiveQueryId(null);
      }
    } else if (type === 'link' && parentId) {
      setHistory((prev) =>
        prev.map((q) => {
          if (q.id === parentId) {
            return { ...q, articles: q.articles.filter((a) => a.id !== id) };
          }
          return q;
        })
      );
    }
  };

  // Toggle the sidebar open/collapsed.
  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  // Toggle expansion of a query node's articles list.
  const toggleNodeExpansion = (id, newValue) => {
    setExpandedNodes((prev) => ({ ...prev, [id]: newValue }));
  };

  return (
    <div className="app-container">
      <HistorySidebar
        history={history}
        expandedNodes={expandedNodes}
        onToggle={toggleNodeExpansion}
        onQueryClick={handleQueryClick}
        onDelete={handleDelete}
        activeQueryId={activeQueryId}
        isOpen={isSidebarOpen}
        onToggleSidebar={toggleSidebar}
      />
      <div className="main-content">
        <header className="app-header">
          <div className="title-and-icon">
          <h1 className="app-title">OpenFiche Search</h1>
          <img src="/icon.ico" alt="OpenFiche Icon" className="app-icon" />
          </div>
          <form className="search-form" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="Search with OpenFiche..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="search-button" aria-label="Search">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                viewBox="0 0 24 24"
                className="search-icon"
              >
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
            </button>
          </form>
        </header>
        <section className="results">
          {loading && <p className="loading">Loading...</p>}
          {error && <p className="error">{error}</p>}
          {results.map((result, index) => (
            <div key={result.url || index} className="result-item">
              <img src={result.logoUrl} alt="logo" className="result-logo" />
              <div className="result-content">
                <h2 className="result-title">
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={() => handleResultClick(result)}
                  >
                    {result.title}
                  </a>
                </h2>
                {result.description && (
                  <p className="result-description">{result.description}</p>
                )}
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="result-link"
                  onClick={() => handleResultClick(result)}
                >
                  Read more
                </a>
              </div>
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}

export default App;
