import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import re
from openai import OpenAI
import os
import json
import asyncio

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ANALYSIS_PROMPT = """Analyze the following website content and extract key information about the company:

Content:
{content}

Please extract and structure the following information:
1. Product lines and their features
2. Company overview
3. Market positioning
4. Technology stack (if available)
5. Key differentiators
6. Target customers
7. Revenue/valuation information (if available)

Format the response as a JSON object with these fields."""

async def scrape_company_info(url: str) -> Dict:
    """
    Scrape and analyze company information from their website.
    
    Args:
        url (str): The company's website URL
        
    Returns:
        Dict: Structured company information
    """
    try:
        # Fetch main page content
        main_content = await fetch_page_content(url)
        
        # Try to find and fetch additional important pages
        about_url = find_about_page(main_content, url)
        products_url = find_products_page(main_content, url)
        
        # Fetch additional pages concurrently
        additional_contents = await asyncio.gather(
            fetch_page_content(about_url) if about_url else asyncio.sleep(0),
            fetch_page_content(products_url) if products_url else asyncio.sleep(0)
        )
        
        # Combine all content
        all_content = main_content
        if additional_contents[0]:
            all_content += "\n\n" + additional_contents[0]
        if additional_contents[1]:
            all_content += "\n\n" + additional_contents[1]
        
        # Analyze content using OpenAI
        return await analyze_content(all_content)
        
    except Exception as e:
        raise Exception(f"Error scraping company info: {str(e)}")

async def fetch_page_content(url: Optional[str]) -> Optional[str]:
    """
    Fetch and extract text content from a webpage.
    
    Args:
        url (Optional[str]): The URL to fetch
        
    Returns:
        Optional[str]: Extracted text content
    """
    if not url:
        return None
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception:
        return None

def find_about_page(content: str, base_url: str) -> Optional[str]:
    """
    Find the URL of the company's about page.
    
    Args:
        content (str): The main page content
        base_url (str): The base URL of the company website
        
    Returns:
        Optional[str]: URL of the about page if found
    """
    soup = BeautifulSoup(content, 'html.parser')
    
    # Common patterns for about pages
    patterns = [
        r'about\b',
        r'about-us\b',
        r'company\b',
        r'who-we-are\b'
    ]
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.text.lower()
        
        if any(re.search(pattern, text) or re.search(pattern, href) for pattern in patterns):
            return make_absolute_url(href, base_url)
    
    return None

def find_products_page(content: str, base_url: str) -> Optional[str]:
    """
    Find the URL of the company's products page.
    
    Args:
        content (str): The main page content
        base_url (str): The base URL of the company website
        
    Returns:
        Optional[str]: URL of the products page if found
    """
    soup = BeautifulSoup(content, 'html.parser')
    
    # Common patterns for product pages
    patterns = [
        r'products?\b',
        r'solutions\b',
        r'services\b',
        r'platform\b'
    ]
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        text = link.text.lower()
        
        if any(re.search(pattern, text) or re.search(pattern, href) for pattern in patterns):
            return make_absolute_url(href, base_url)
    
    return None

def make_absolute_url(href: str, base_url: str) -> str:
    """
    Convert a relative URL to an absolute URL.
    
    Args:
        href (str): The relative or absolute URL
        base_url (str): The base URL of the website
        
    Returns:
        str: The absolute URL
    """
    if href.startswith('http'):
        return href
    elif href.startswith('//'):
        return f"https:{href}"
    elif href.startswith('/'):
        return f"{base_url.rstrip('/')}{href}"
    else:
        return f"{base_url.rstrip('/')}/{href.lstrip('/')}"

async def analyze_content(content: str) -> Dict:
    """
    Analyze website content using OpenAI's GPT model.
    
    Args:
        content (str): The website content to analyze
        
    Returns:
        Dict: Structured analysis of the company
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are an expert business analyst."},
                {"role": "user", "content": ANALYSIS_PROMPT.format(content=content[:10000])}  # Limit content length
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
        
    except Exception as e:
        raise Exception(f"Error analyzing content: {str(e)}") 