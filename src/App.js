import React, { useState, useEffect } from 'react';
import './App.css';

/**
 * HistorySidebar Component
 *
 * Displays two separate header elements:
 *  - expanded-header (icon + "Search History") when isOpen is true
 *  - collapsed-header (icon only) when isOpen is false
 * Below that, we only render the history list if isOpen is true.
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
      {isOpen ? (
        <div className="expanded-header" onClick={onToggleSidebar}>
          <span className="sidebar-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
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
          <h2 className="sidebar-title">Search History</h2>
        </div>
      ) : (
        <div className="collapsed-header" onClick={onToggleSidebar}>
          <span className="sidebar-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="30"
              height="30"
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
        </div>
      )}

      {isOpen && (
        <ul className="history-tree">
          {history.map((queryItem) => {
            // Is this query expanded or collapsed?
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
 * Fetch metadata (title, description) for a given URL.
 *  - If it's a Wikipedia link, parse the article title from the URL
 *    and use the REST summary endpoint to get the 'extract'.
 *  - Otherwise, fetch the HTML and parse out standard meta tags or fallback paragraph.
 */
async function fetchMetadata(url) {
  try {
    const isWikipedia = url.includes('wikipedia.org');
    if (isWikipedia) {
      // Wikipedia approach using the REST summary endpoint
      const articleTitle = extractWikiArticleTitle(url); // see helper below
      const apiUrl = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(
        articleTitle
      )}`;

      const resp = await fetch(apiUrl);
      const json = await resp.json();

      // The summary API returns `title` and `extract`
      const wikiTitle = json.title || articleTitle;
      const wikiExtract = json.extract || '';

      return { title: wikiTitle, description: wikiExtract };
    } else {
      // Non-Wikipedia approach
      const response = await fetch(url);
      const htmlText = await response.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(htmlText, 'text/html');

      // Gather meta data
      const metaTitle = doc.querySelector('title')?.textContent.trim() || '';
      let metaDescription =
        doc
          .querySelector('meta[name="description"]')
          ?.getAttribute('content') ||
        doc
          .querySelector('meta[property="og:description"]')
          ?.getAttribute('content') ||
        doc
          .querySelector('meta[name="twitter:description"]')
          ?.getAttribute('content') ||
        '';

      // FALLBACK: if no meta description found, try the first paragraph
      if (!metaDescription) {
        const fallbackParagraph =
          doc.querySelector('article p') ||
          doc.querySelector('main p') ||
          doc.querySelector('body p');
        if (fallbackParagraph) {
          metaDescription = fallbackParagraph.textContent.trim();
        }
      }

      return {
        title: metaTitle,
        description: metaDescription,
      };
    }
  } catch (error) {
    console.error('Error fetching metadata for', url, error);
    return { title: '', description: '' };
  }
}

/**
 * Helper to extract the Wikipedia article title from a URL like:
 *  https://en.wikipedia.org/wiki/The_Washington_Post
 *  returns "The_Washington_Post"
 *
 * We handle both "en.wikipedia.org" and "en.m.wikipedia.org" and any subpath.
 */
function extractWikiArticleTitle(url) {
  try {
    const urlObj = new URL(url);
    // Path is something like /wiki/The_Washington_Post
    // Remove leading "/wiki/"
    const pathParts = urlObj.pathname.split('/');
    // find the "wiki" part, then the next part is the article
    // e.g. ['', 'wiki', 'The_Washington_Post']
    const wikiIndex = pathParts.indexOf('wiki');
    if (wikiIndex >= 0 && wikiIndex < pathParts.length - 1) {
      // Rejoin the rest in case article name has slashes
      const articlePart = pathParts.slice(wikiIndex + 1).join('/');
      return decodeURIComponent(articlePart);
    }
    return urlObj.pathname; // fallback
  } catch (e) {
    // fallback if parse fails
    return url;
  }
}

/**
 * App Component
 *  - Manages search state, results, history, etc.
 */
function App() {
  const [history, setHistory] = useState([]);
  const [activeQueryId, setActiveQueryId] = useState(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
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

  // Perform the search using your backend search API
  const doSearch = async (searchQuery) => {
    setLoading(true);
    setError(null);

    try {
      const formattedQuery = searchQuery.trim().replace(/\s+/g, '+');
      const response = await fetch(
        `https://openfiche-896b9969619d.herokuapp.com/search?q=${formattedQuery}`
      );
      const data = await response.json();

      // Data looks like [ [score, "url"], [score, "url"], ... ]
      // Convert to your results structure
      const resultsData = data.map((item) => {
        const [/*score*/, url] = item;
        let title = url;
        let logoUrl = '';

        try {
          const urlObj = new URL(url);

          // Domain-based approach to set a fallback logo
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

          // Derive a fallback title from the URL path
          const parts = urlObj.pathname.split('/').filter(Boolean);
          if (parts.length > 0) {
            let candidate = parts[parts.length - 1].split('.')[0];
            if (candidate.toLowerCase() === 'index' && parts.length > 1) {
              candidate = parts[parts.length - 2];
            }
            candidate = candidate.replace(/[-_]/g, ' ');
            title = candidate
              .split(' ')
              .map(
                (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
              )
              .join(' ');
          }
        } catch (err) {
          title = url;
        }

        return { url, title, logoUrl, description: '' };
      });

      setResults(resultsData);

      // Fetch metadata (title and description) asynchronously
      resultsData.forEach((result) => {
        fetchMetadata(result.url).then((metadata) => {
          setResults((prev) =>
            prev.map((r) =>
              r.url === result.url
                ? {
                    ...r,
                    // Use the fetched title if available; otherwise keep the fallback
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

  // Handle the user's search submission
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

  // When a result is clicked, open it and add it to the active query
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
          // Avoid duplicates
          if (!q.articles.find((a) => a.url === newArticle.url)) {
            return { ...q, articles: [...q.articles, newArticle] };
          }
        }
        return q;
      })
    );

    window.open(newArticle.url, '_blank');
  };

  // Clicking an item in the history sidebar
  // - If it's a query, we re-run that search
  // - If it's an article link, open that link
  const handleQueryClick = (item) => {
    if (item.url) {
      window.open(item.url, '_blank');
    } else {
      setActiveQueryId(item.id);
      setQuery(item.query);
      doSearch(item.query);
    }
  };

  // Delete a query node or an article link
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

  // Toggle the sidebar open/collapsed
  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  // Toggle expansion for a query node's articles
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
              {result.logoUrl && (
                <img src={result.logoUrl} alt="logo" className="result-logo" />
              )}
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
