#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from bs4 import BeautifulSoup
from scraper.fetcher import MyHomeFetcher

def analyze_html():
    fetcher = MyHomeFetcher()
    
    try:
        html = fetcher.fetch_agents_list(1)
        if not html:
            print("Failed to fetch HTML")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for any JSON data in script tags
        scripts = soup.find_all('script')
        print(f"Found {len(scripts)} script tags")
        
        for i, script in enumerate(scripts):
            if script.string:
                content = script.string
                # Look for JSON data
                if 'makler' in content.lower() or 'agent' in content.lower():
                    print(f"\nScript {i+1} contains makler/agent data:")
                    print(content[:500])
                    print("..." if len(content) > 500 else "")
        
        # Look for any divs with agent-related classes
        agent_divs = soup.find_all('div', class_=re.compile(r'agent|makler', re.I))
        print(f"\nFound {len(agent_divs)} divs with agent/makler classes")
        
        for i, div in enumerate(agent_divs[:3]):
            print(f"\nAgent div {i+1}:")
            print(f"Classes: {div.get('class', [])}")
            print(f"Text: {div.get_text()[:200]}")
        
        # Look for any links containing maklers
        makler_links = soup.find_all('a', href=re.compile(r'maklers'))
        print(f"\nFound {len(makler_links)} links containing 'maklers'")
        
        for i, link in enumerate(makler_links[:5]):
            print(f"Link {i+1}: {link.get('href')} - Text: {link.get_text()[:50]}")
        
        # Look for phone numbers in the entire page
        phone_pattern = re.compile(r'\+?995\s*\d{3}\s*\d{3}\s*\d{3}|\d{3}\s*\d{3}\s*\d{3}')
        phones = phone_pattern.findall(soup.get_text())
        print(f"\nFound {len(phones)} potential phone numbers:")
        for phone in phones[:10]:
            print(f"  {phone}")
        
        # Look for any data attributes that might contain agent info
        data_elements = soup.find_all(attrs={"data-": True})
        print(f"\nFound {len(data_elements)} elements with data attributes")
        
        for elem in data_elements[:5]:
            data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
            if data_attrs:
                print(f"Element: {elem.name}, Data attrs: {data_attrs}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fetcher.close()

if __name__ == "__main__":
    analyze_html()
