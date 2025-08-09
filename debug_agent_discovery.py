#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug agent discovery to see what HTML we're getting
"""

import re
from scraper.fetcher import MyHomeFetcher
from bs4 import BeautifulSoup

def debug_agent_page():
    fetcher = MyHomeFetcher()
    
    print("🔍 Debugging agent discovery...")
    
    # Try to fetch the first page
    url = "https://www.myhome.ge/maklers/?page=1"
    print(f"Fetching: {url}")
    
    response = fetcher.fetch_page(url)
    if not response:
        print("❌ Failed to fetch page")
        return
    
    print(f"✅ Got response: {len(response)} characters")
    
    # Look for the text we know should be there
    if "აგენტები" in response:
        print("✅ Found Georgian text 'აგენტები' (Agents)")
    else:
        print("❌ No Georgian text found")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(response, 'html.parser')
    
    # Look for various agent link patterns
    patterns = [
        r'/maklers/\d+/?',
        r'/maklers/\d+/',
        r'maklers/\d+',
        r'href="/maklers/',
    ]
    
    print(f"\n🔍 Searching for agent links...")
    for pattern in patterns:
        matches = re.findall(pattern, response)
        print(f"Pattern '{pattern}': {len(matches)} matches")
        if matches:
            print(f"  Examples: {matches[:5]}")
    
    # Look for all links
    all_links = soup.find_all('a')
    agent_links = []
    for link in all_links:
        href = link.get('href', '')
        if '/maklers/' in href and href.count('/') >= 2:
            agent_links.append(href)
    
    print(f"\n🔍 Found {len(agent_links)} potential agent links")
    if agent_links:
        print(f"Examples: {agent_links[:10]}")
    
    # Extract agent IDs
    agent_ids = set()
    for href in agent_links:
        match = re.search(r'/maklers/(\d+)', href)
        if match:
            agent_ids.add(match.group(1))
    
    print(f"\n✅ Extracted {len(agent_ids)} unique agent IDs")
    print(f"Agent IDs: {list(agent_ids)[:10]}")
    
    # Let's save a sample of the HTML to see what we're getting
    print(f"\n💾 Saving HTML sample...")
    with open('agent_page_sample.html', 'w', encoding='utf-8') as f:
        f.write(response[:5000])  # First 5000 characters
    print("Saved first 5000 characters to agent_page_sample.html")

if __name__ == "__main__":
    debug_agent_page()
