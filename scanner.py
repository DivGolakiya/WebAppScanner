import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class VulnerabilityScanner:
    def __init__(self, target_url):
        self.target_url = target_url
        self.target_links = set()
        self.session = requests.Session()
        # --- NEW: Sets to store unique vulnerability findings ---
        self.xss_vulnerabilities = set()
        self.sqli_vulnerabilities = set()

    def crawl(self, url=None):
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
                    self.crawl(link)
        except requests.exceptions.RequestException:
            pass

    def scan_xss(self, url):
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action')
                post_url = urljoin(url, action)
                method = form.get('method', 'get').lower()
                inputs_list = form.find_all('input')
                post_data = {}
                for input_tag in inputs_list:
                    name = input_tag.get('name')
                    input_type = input_tag.get('type', 'text')
                    value = input_tag.get('value', '')
                    if input_type == 'text':
                        value = "<script>test</script>"
                    if name:
                        post_data[name] = value
                if method == 'post':
                    response = self.session.post(post_url, data=post_data)
                else:
                    response = self.session.get(post_url, params=post_data)
                if "<script>test</script>" in response.text:
                    # Store a unique tuple of (action, method)
                    self.xss_vulnerabilities.add((post_url, method))
        except requests.exceptions.RequestException:
            pass
            
    # --- NEW: SQL Injection Scanner ---
    def scan_sqli(self, url):
        """Scans a given URL for basic, error-based SQLi vulnerabilities."""
        try:
            # Add a single quote to the end of the URL to test for SQLi
            sqli_test_url = f"{url}'"
            response = self.session.get(sqli_test_url)
            
            # Common SQL error messages
            sql_errors = {
                "you have an error in your sql syntax",
                "warning: mysql_fetch_array()",
                "unclosed quotation mark after the character string"
            }

            for error in sql_errors:
                if error in response.text.lower():
                    # Store the original, clean URL
                    self.sqli_vulnerabilities.add(url)
                    break # Found an error, no need to check for more on this URL
        except requests.exceptions.RequestException:
            pass

    def run_scanner(self):
        print(f"[*] Starting crawler for {self.target_url}...")
        self.crawl()
        print(f"\n[+] Crawling complete. Found {len(self.target_links)} unique links.")
        
        print("\n[*] Starting XSS and SQLi Scans...")
        for link in list(self.target_links): # Use a list copy to iterate
            self.scan_xss(link)
            self.scan_sqli(link)
        print("[+] Scans complete.")
        
        # --- NEW: Consolidated Reporting ---
        print("\n--- Scan Report ---")
        if self.xss_vulnerabilities:
            print(f"[!!!] Discovered {len(self.xss_vulnerabilities)} unique XSS vulnerabilities:")
            for url, method in self.xss_vulnerabilities:
                print(f"      - Form at: {url} (Method: {method.upper()})")
        else:
            print("[+] No XSS vulnerabilities found.")
            
        if self.sqli_vulnerabilities:
            print(f"\n[!!!] Discovered {len(self.sqli_vulnerabilities)} unique SQL Injection vulnerabilities:")
            for url in self.sqli_vulnerabilities:
                print(f"      - URL: {url}")
        else:
            print("[+] No SQL Injection vulnerabilities found.")


# --- Main execution block ---
if __name__ == "__main__":
    target_website = "http://testphp.vulnweb.com/"
    
    scanner = VulnerabilityScanner(target_website)
    scanner.run_scanner()
