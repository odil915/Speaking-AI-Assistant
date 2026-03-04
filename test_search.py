from ddgs import DDGS
from core.tools import scrape_web
import json

def test_search():
    query = "Cristiano Ronaldo total career goals current stats"
    print(f"Searching for: '{query}'...")
    
    try:
        # 1. Search
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            
        if results:
            print(f"Found {len(results)} results.")
            for i, r in enumerate(results):
                print(f"\n--- Result {i+1} ---")
                link = r.get('href')
                print(f"Link: {link}")
                
                # Deep Read (Scrape)
                print(f"Reading content...")
                content = scrape_web(link)
                # Show a good chunk to verify cleanliness
                print(f"Clean Text Snippet:\n{content[:800]}...\n")
            
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
