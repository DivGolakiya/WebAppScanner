def generate_report(target_url, xss_vulns, sqli_vulns):
    """Generates and returns the scan report as a string."""
    report = f"--- Scan Report for {target_url} ---\n\n"
    
    if xss_vulns:
        report += f"[!!!] Discovered {len(xss_vulns)} unique XSS vulnerabilities:\n"
        for url, method in xss_vulns:
            report += f"      - Form at: {url} (Method: {method.upper()})\n"
    else:
        report += "[+] No XSS vulnerabilities found.\n"
        
    if sqli_vulns:
        report += f"\n[!!!] Discovered {len(sqli_vulns)} unique SQL Injection vulnerabilities:\n"
        for url in sqli_vulns:
            report += f"      - URL: {url}\n"
    else:
        report += "[+] No SQL Injection vulnerabilities found.\n"
    
    return report
