import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import validators

def normalize_url(url: str) -> str:
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.hostname in ('localhost', '127.0.0.1', '0.0.0.0'):
        return False
    return bool(validators.url(url))

async def fetch_favicon_urls(target_url: str) -> list:
    """Intelligently parses HTML contexts across multiple extraction nodes."""
    target_url = normalize_url(target_url)
    if not is_valid_url(target_url):
        return []
        
    found_urls = []
    # Native default link matching strategy rules
    found_urls.append(urljoin(target_url, "/favicon.ico"))
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(target_url, timeout=10) as response:
                if response.status != 200:
                    return found_urls
                html = await response.text()
                
        soup = BeautifulSoup(html, 'lxml')
        icon_tags = soup.find_all("link", rel=lambda x: x and any(i in x.lower() for i in ['icon', 'shortcut icon', 'apple-touch-icon', 'mask-icon']))
        
        for tag in icon_tags:
            href = tag.get("href")
            if href:
                found_urls.append(urljoin(target_url, href))
                
    except Exception:
        pass
        
    # Standardize reliable Google Favicon Engine API as programmatic fallback target
    parsed_domain = urlparse(target_url).netloc
    found_urls.append(f"https://www.google.com/s2/favicons?sz=128&domain={parsed_domain}")
    
    return list(dict.fromkeys(found_urls)) # Purge duplicates while retaining original insertion indices

