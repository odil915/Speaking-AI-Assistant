from ddgs import DDGS
from rich.console import Console
from core.debug import log_debug

import random

console = Console()

def search_web(query):
    max_results = random.randint(5, 10)
    """
    Searches the web using DuckDuckGo and returns the top result.
    """
    console.print(f"[dim]Searching DuckDuckGo for: '{query}'...[/dim]")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            
        if results:
            # Combine up to 3 results with Links for citation
            formatted_results = []
            for r in results:
                link = r.get('href', '#')
                body = r.get('body', '')
                formatted_results.append(f"Source: {link}\nSnippet: {body}")
            
            combined_res = "\n---\n".join(formatted_results)
            console.print(f"[dim]Found {len(results)} results.[/dim]")
            log_debug("SEARCH RESULTS", f"Query: {query}\n\n{combined_res}")
            return combined_res
        else:
            console.print("[dim]No results found.[/dim]")
            return "No results found. Try a simpler query."
    except Exception as e:
        return f"Error searching web: {e}"

def scrape_web(url):
    """
    Visits a URL and returns the text content.
    """
    import requests
    from bs4 import BeautifulSoup
    
    console.print(f"[dim]Reading: {url}...[/dim]")
    try:
        # Fake header to look like a real browser (Chrome on Windows)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Strip script, style, and navigation elements to reduce noise
        for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "iframe", "noscript", "svg"]):
            tag.decompose()
            
        # Smart Filter: prioritization of content attributes
        # We look for Headings, Paragraphs, and List Items.
        content = []
        
        # Extract Title
        if soup.title:
            content.append(f"PAGE TITLE: {soup.title.string.strip()}\n")
            
        # Find 'article' or 'main' if possible to narrow down context
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content') or soup
        
        for element in main_content.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = element.get_text(strip=True)
            if len(text) > 20: # Filter out short noise like "Menu", "Top", etc.
                if element.name in ['h1', 'h2', 'h3']:
                    content.append(f"\n### {text.upper()} ###")
                elif element.name == 'li':
                    content.append(f"- {text}")
                else:
                    content.append(text)
                    
        cleaned_text = "\n".join(content)
        
        # Limit length to avoid crashing the brain
        return cleaned_text[:6000] + "\n...(Content Truncated)"
    except Exception as e:
        return f"Error reading page: {e}"
