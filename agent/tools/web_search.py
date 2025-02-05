from duckduckgo_search import DDGS
from typing import List, Dict
import re
from urllib.parse import urlparse

async def search_companies(domain: str) -> List[Dict]:
    """
    Search for companies in a specific domain using DuckDuckGo.
    
    Args:
        domain (str): The domain to search for companies in
        
    Returns:
        List[Dict]: List of company information
    """
    companies = []
    search_queries = [
        f"top companies in {domain}",
        f"startups in {domain}",
        f"leading {domain} companies",
        f"{domain} technology companies"
    ]
    
    try:
        with DDGS() as ddgs:
            for query in search_queries:
                results = ddgs.text(query, max_results=10)
                for result in results:
                    # Extract company information
                    company = {
                        "name": extract_company_name(result["title"]),
                        "description": result["body"],
                        "url": clean_url(result["link"])
                    }
                    
                    # Only add if we got a valid company name and it's not a duplicate
                    if (company["name"] and 
                        company["url"] and 
                        not any(c["name"] == company["name"] for c in companies)):
                        companies.append(company)
        
        return companies[:20]  # Return top 20 unique companies
        
    except Exception as e:
        raise Exception(f"Error searching for companies: {str(e)}")

def extract_company_name(title: str) -> str:
    """
    Extract company name from search result title.
    
    Args:
        title (str): The search result title
        
    Returns:
        str: Extracted company name or None if not found
    """
    # Common patterns to clean up titles
    patterns = [
        r"^(.*?)\s*\|",  # Remove everything after |
        r"^(.*?)\s*-",   # Remove everything after -
        r"^(.*?)\s*:",   # Remove everything after :
        r"(.*?)'s\s*.*"  # Keep only the part before 's
    ]
    
    for pattern in patterns:
        match = re.match(pattern, title)
        if match:
            return match.group(1).strip()
    
    return title.strip()

def clean_url(url: str) -> str:
    """
    Clean and validate company URL.
    
    Args:
        url (str): The URL to clean
        
    Returns:
        str: Cleaned URL or None if invalid
    """
    try:
        # Parse the URL
        parsed = urlparse(url)
        
        # Ensure it's a company website (not a news article, etc.)
        if any(domain in parsed.netloc for domain in [
            "wikipedia.org", "linkedin.com", "facebook.com", "twitter.com",
            "youtube.com", "medium.com", "github.com", "crunchbase.com"
        ]):
            return None
            
        # Return base domain
        return f"{parsed.scheme}://{parsed.netloc}"
        
    except Exception:
        return None 