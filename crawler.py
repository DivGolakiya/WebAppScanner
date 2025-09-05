import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, target_url, session, page_limit=50, verbose=False):
        self.target_url = target_url
        self.session = session
        self.target_links = set()
        self.verbose = verbose
        # The page limit is now passed in
        self.page_limit = page_limit

    def discover_links(self, url=None):
        """Recursively crawls a website up to a page limit."""
        if len(self.target_links) >= self.page_limit:
            return

        if url is None:
            url = self.target_url
        try:
            response = self.session.get(url, timeout=5)
            if "text/html" not in response.headers.get('Content-Type', ''):
                return

            soup = BeautifulSoup(response.content, 'html.parser')
            for a_tag in soup.find_all('a', href=True):
                link = urljoin(url, a_tag['href'])
                
                if urlparse(self.target_url).netloc in link and link not in self.target_links:
                    self.target_links.add(link)
                    if self.verbose:
                        print(f"[+] Discovered link: {link}")
                    # Recursive call
                    self.discover_links(link)
        except requests.exceptions.RequestException:
            pass
        
        return self.target_links
