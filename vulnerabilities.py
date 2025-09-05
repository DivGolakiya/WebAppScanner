import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scan_xss(session, url):
    """Scans a given URL for Reflected XSS vulnerabilities and returns findings."""
    vulnerabilities = set()
    try:
        # Add a timeout to the request
        response = session.get(url, timeout=5)
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
                # Add a timeout to the request
                response = session.post(post_url, data=post_data, timeout=5)
            else:
                # Add a timeout to the request
                response = session.get(post_url, params=post_data, timeout=5)

            if "<script>test</script>" in response.text:
                vulnerabilities.add((post_url, method))
    except requests.exceptions.RequestException:
        pass
    return vulnerabilities

def scan_sqli(session, url):
    """Scans a given URL for basic, error-based SQLi vulnerabilities."""
    is_vulnerable = False
    try:
        sqli_test_url = f"{url}'"
        # Add a timeout to the request
        response = session.get(sqli_test_url, timeout=5)
        sql_errors = {"you have an error in your sql syntax", "warning: mysql_fetch_array()", "unclosed quotation mark after the character string"}
        for error in sql_errors:
            if error in response.text.lower():
                is_vulnerable = True
                break
    except requests.exceptions.RequestException:
        pass
    return is_vulnerable
