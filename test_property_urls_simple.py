#!/usr/bin/env python3
"""
Simple test for property listing URLs
"""

import requests
import time

def test_property_urls():
    """Test different property listing URLs"""
    
    urls_to_test = [
        "https://www.myhome.ge/pr/",
        "https://www.myhome.ge/pr/rent/",
        "https://www.myhome.ge/pr/sale/",
        "https://www.myhome.ge/pr/rent/?page=1",
        "https://www.myhome.ge/pr/sale/?page=1",
        "https://www.myhome.ge/pr/rent/details/",
        "https://www.myhome.ge/pr/sale/details/"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
    }
    
    for url in urls_to_test:
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                content = response.text
                # Look for property links
                import re
                pr_links = re.findall(r'href="([^"]*pr/[^"]*)"', content)
                print(f"Found {len(pr_links)} property links")
                for i, link in enumerate(pr_links[:3]):
                    print(f"  {i+1}. {link}")
            time.sleep(1)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_property_urls()
