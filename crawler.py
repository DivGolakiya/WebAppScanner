import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, target_url, session, verbose=False):
        self.target_url = target_url
        self.session = session
        self.target_links = set()
        self.verbose = verbose # NEW: Add verbose flag

    def discover_links(self, url=None):
        """Recursively crawls a website to discover all unique links."""
        if url is None:
            url = self.target_url
        try:
            response = self.session.get(url)
            if "text/html" not in response.headers.get('Content-Type', ''):
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                link = urljoin(url, a_tag['href'])
                
                if urlparse(self.target_url).netloc in link and link not in self.target_links:
                    self.target_links.add(link)
                    # NEW: Only print if verbose mode is on
                    if self.verbose:
                        print(f"[+] Discovered link: {link}")
                    self.discover_links(link)
        except requests.exceptions.RequestException:
            pass
        
        return self.target_links
