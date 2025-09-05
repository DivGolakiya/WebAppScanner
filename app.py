import streamlit as st
import requests
from crawler import Crawler
from vulnerabilities import scan_xss, scan_sqli
from report_generator import generate_report
from urllib.parse import urlparse

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Web Vulnerability Scanner", page_icon="🛡️", layout="wide")

st.title("🛡️ Web Application Vulnerability Scanner")
st.write("Enter the full URL of a website you are authorized to test, and the scanner will check for common vulnerabilities like XSS and SQL Injection.")
st.warning("**Disclaimer:** This tool is for educational purposes only. Only use it on websites you own or have explicit permission to test. Unauthorized scanning is illegal.", icon="⚠️")

# --- Initialize Session State ---
# This will run only once at the start of the session.
if 'scan_results' not in st.session_state:
    st.session_state.scan_results = None

# --- UI Elements ---
target_url = st.text_input("Enter Target URL", placeholder="e.g., http://testphp.vulnweb.com/")
max_pages = st.number_input("Max pages to crawl", min_value=1, max_value=500, value=50, help="Set the maximum number of pages the crawler will discover.")

if st.button("Start Scan", type="primary"):
    if target_url:
        with st.spinner("Scanning in progress... This may take a while."):
            session = requests.Session()
            
            # Run all scans and store the results in a dictionary
            crawler = Crawler(target_url, session, page_limit=max_pages)
            links = crawler.discover_links()
            xss_vulnerabilities = set()
            sqli_vulnerabilities = set()
            for link in list(links):
                xss_vulnerabilities.update(scan_xss(session, link))
                if scan_sqli(session, link):
                    sqli_vulnerabilities.add(link)
            
            final_report = generate_report(target_url, xss_vulnerabilities, sqli_vulnerabilities)
            
            # Save all necessary info to the session state
            st.session_state.scan_results = {
                "links": links,
                "report": final_report,
                "url": target_url
            }
    else:
        st.error("Please enter a target URL to start the scan.")

# --- Display Results (only if they exist in the session state) ---
if st.session_state.scan_results:
    results = st.session_state.scan_results
    
    st.subheader(f"Crawling complete. Found {len(results['links'])} unique links.")
    with st.expander("Show Discovered Links"):
        for link in list(results['links']):
            st.write(link)
    
    st.subheader("Vulnerability scan complete.")
    
    st.divider()
    st.header("Scan Report")
    st.code(results['report'], language=None)
    
    st.download_button(
        label="Download Report",
        data=results['report'],
        file_name=f"scan_report_{urlparse(results['url']).netloc}.txt",
        mime="text/plain"
    )
