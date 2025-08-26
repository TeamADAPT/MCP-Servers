FireCrawl

Tools (8)
Resources (0)
Errors (0)

firecrawl_scrape
Scrape a single webpage with advanced options for content extraction
Parameters
url*
The URL to scrape
formats
Content formats to extract (default: ['markdown'])
onlyMainContent
Extract only the main content, filtering out navigation, footers, etc.
includeTags
HTML tags to specifically include in extraction
excludeTags
HTML tags to exclude from extraction
waitFor
Time in milliseconds to wait for dynamic content to load
timeout
Maximum time in milliseconds to wait for the page to load
actions
List of actions to perform before scraping
mobile
Use mobile viewport
skipTlsVerification
Skip TLS certificate verification

firecrawl_map
Discover URLs from a starting point
Parameters
url*
Starting URL for URL discovery
search
Optional search term to filter URLs
ignoreSitemap
Skip sitemap.xml discovery and only use HTML links
sitemapOnly
Only use sitemap.xml for discovery, ignore HTML links
includeSubdomains
Include URLs from subdomains in results
limit
Maximum number of URLs to return

firecrawl_crawl
Start an asynchronous crawl of multiple pages from a starting URL
Parameters
url*
Starting URL for the crawl
excludePaths
URL paths to exclude from crawling
includePaths
Only crawl these URL paths
maxDepth
Maximum link depth to crawl
ignoreSitemap
Skip sitemap.xml discovery
limit
Maximum number of pages to crawl
allowBackwardLinks
Allow crawling links that point to parent directories
allowExternalLinks
Allow crawling links to external domains
webhook
Webhook URL to notify when crawl is complete
deduplicateSimilarURLs
Remove similar URLs during crawl
ignoreQueryParameters
Ignore query parameters when comparing URLs
scrapeOptions
Options for scraping each page

firecrawl_check_crawl_status
Check the status of a crawl job
Parameters
id*
Crawl job ID to check

firecrawl_search
Search and retrieve content from web pages with optional scraping
Parameters
query*
Search query string
limit
Maximum number of results to return (default: 5)
lang
Language code for search results (default: en)
country
Country code for search results (default: us)
tbs
Time-based search filter
filter
Search filter
location
Location settings for search
scrapeOptions
Options for scraping search results

firecrawl_extract
Extract structured information from web pages using LLM
Parameters
urls*
List of URLs to extract information from
prompt
Prompt for the LLM extraction
systemPrompt
System prompt for LLM extraction
schema
JSON schema for structured data extraction
allowExternalLinks
Allow extraction from external links
enableWebSearch
Enable web search for additional context
includeSubdomains
Include subdomains in extraction

firecrawl_deep_research
Conduct deep research on a query using web crawling, search, and AI analysis
Parameters
query*
The query to research
maxDepth
Maximum depth of research iterations (1-10)
timeLimit
Time limit in seconds (30-300)
maxUrls
Maximum number of URLs to analyze (1-1000)

firecrawl_generate_llmstxt
Generate standardized LLMs.txt file for a given URL
Parameters
url*
The URL to generate LLMs.txt from
maxUrls
Maximum number of URLs to process (1-100, default: 10)
showFullText
Whether to show the full LLMs-full.txt in the response