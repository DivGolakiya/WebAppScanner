import requests
import argparse
from crawler import Crawler
from vulnerabilities import scan_xss, scan_sqli
from report_generator import generate_report

def main():
    parser = argparse.ArgumentParser(description="A simple Web Application Vulnerability Scanner.")
    parser.add_argument("url", help="The target URL to scan.")
    parser.add_argument("-o", "--output", help="File path to save the report.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output for the crawler.")
    # NEW: Add an argument for the page limit
    parser.add_argument("--max-pages", type=int, default=50, help="The maximum number of pages to crawl. Default is 50.")
    args = parser.parse_args()

    target_url = args.url
    session = requests.Session()

    print(f"[*] Starting crawler for {target_url} (limit: {args.max_pages} pages)...")
    # NEW: Pass the max_pages argument to the Crawler
    crawler = Crawler(target_url, session, page_limit=args.max_pages, verbose=args.verbose)
    links = crawler.discover_links()
    print(f"\n[+] Crawling complete. Found {len(links)} unique links.")

    # ... (rest of the script is the same)
    print("\n[*] Starting XSS and SQLi Scans...")
    xss_vulnerabilities = set()
    sqli_vulnerabilities = set()
    for link in list(links):
        xss_vulnerabilities.update(scan_xss(session, link))
        if scan_sqli(session, link):
            sqli_vulnerabilities.add(link)
    print("[+] Scans complete.")

    final_report = generate_report(target_url, xss_vulnerabilities, sqli_vulnerabilities)
    print("\n" + final_report)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(final_report)
        print(f"[+] Report saved to {args.output}")

if __name__ == "__main__":
    main()
