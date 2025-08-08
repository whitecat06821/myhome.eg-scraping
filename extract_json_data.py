#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from bs4 import BeautifulSoup
from scraper.fetcher import MyHomeFetcher

def extract_json_data():
    fetcher = MyHomeFetcher()
    
    try:
        html = fetcher.fetch_agents_list(1)
        if not html:
            print("Failed to fetch HTML")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the script tag with JSON data
        scripts = soup.find_all('script')
        
        for i, script in enumerate(scripts):
            if script.string and ('makler' in script.string.lower() or 'agent' in script.string.lower()):
                print(f"Analyzing script {i+1}...")
                
                try:
                    # Try to parse as JSON
                    data = json.loads(script.string)
                    print("Successfully parsed JSON!")
                    
                    # Look for agent/makler data in the JSON structure
                    def find_agents_in_json(obj, path=""):
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                current_path = f"{path}.{key}" if path else key
                                if 'makler' in key.lower() or 'agent' in key.lower():
                                    print(f"Found agent-related key: {current_path}")
                                    print(f"Value type: {type(value)}")
                                    if isinstance(value, list):
                                        print(f"List length: {len(value)}")
                                        if value and isinstance(value[0], dict):
                                            print(f"First item keys: {list(value[0].keys())}")
                                    elif isinstance(value, dict):
                                        print(f"Dict keys: {list(value.keys())}")
                                    print(f"Sample: {str(value)[:200]}...")
                                    print("-" * 50)
                                
                                find_agents_in_json(value, current_path)
                        elif isinstance(obj, list):
                            for j, item in enumerate(obj):
                                find_agents_in_json(item, f"{path}[{j}]")
                    
                    find_agents_in_json(data)
                    
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON: {e}")
                    # Look for JSON-like structures
                    json_pattern = r'\{[^{}]*"makler[^{}]*\}'
                    matches = re.findall(json_pattern, script.string)
                    print(f"Found {len(matches)} JSON-like matches with 'makler'")
                    for match in matches[:3]:
                        print(f"Match: {match[:200]}...")
                
                break
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        fetcher.close()

if __name__ == "__main__":
    extract_json_data()
