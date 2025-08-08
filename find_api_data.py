#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from bs4 import BeautifulSoup
from scraper.fetcher import MyHomeFetcher

def find_api_data():
    fetcher = MyHomeFetcher()
    
    try:
        html = fetcher.fetch_agents_list(1)
        if not html:
            print("Failed to fetch HTML")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for any URLs or API endpoints
        all_links = soup.find_all('a', href=True)
        api_links = [link for link in all_links if 'api' in link['href'].lower()]
        print(f"Found {len(api_links)} API links")
        for link in api_links[:5]:
            print(f"API Link: {link['href']}")
        
        # Look for any fetch URLs or API calls in scripts
        scripts = soup.find_all('script')
        for i, script in enumerate(scripts):
            if script.string:
                content = script.string
                # Look for fetch calls or API URLs
                fetch_patterns = [
                    r'fetch\(["\']([^"\']+)["\']',
                    r'axios\.get\(["\']([^"\']+)["\']',
                    r'\.get\(["\']([^"\']+)["\']',
                    r'["\'](/api/[^"\']+)["\']',
                    r'["\'](/maklers/[^"\']+)["\']',
                ]
                
                for pattern in fetch_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        print(f"\nScript {i+1} contains API calls:")
                        for match in matches[:3]:
                            print(f"  {match}")
        
        # Look for any data attributes that might contain URLs
        data_url_elements = soup.find_all(attrs={"data-url": True})
        print(f"\nFound {len(data_url_elements)} elements with data-url")
        for elem in data_url_elements[:3]:
            print(f"Element: {elem.name}, data-url: {elem.get('data-url')}")
        
        # Look for any JSON-LD structured data
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        print(f"\nFound {len(json_ld_scripts)} JSON-LD scripts")
        for script in json_ld_scripts:
            if script.string:
                try:
                    data = json.loads(script.string)
                    print(f"JSON-LD data: {str(data)[:200]}...")
                except:
                    pass
        
        # Look for any window.__NEXT_DATA__ or similar
        next_data_pattern = r'window\.__NEXT_DATA__\s*=\s*({.*?});'
        for script in scripts:
            if script.string:
                matches = re.findall(next_data_pattern, script.string, re.DOTALL)
                if matches:
                    print(f"\nFound __NEXT_DATA__ in script")
                    try:
                        data = json.loads(matches[0])
                        print("Successfully parsed __NEXT_DATA__")
                        # Look for makler/agent data
                        if 'makler' in str(data).lower() or 'agent' in str(data).lower():
                            print("Contains makler/agent data!")
                    except:
                        print("Failed to parse __NEXT_DATA__")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fetcher.close()

if __name__ == "__main__":
    find_api_data()
