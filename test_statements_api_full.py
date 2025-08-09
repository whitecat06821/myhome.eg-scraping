#!/usr/bin/env python3
"""
Test script for full statements API response
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper.fetcher import MyHomeFetcher
import json

def test_statements_api_full():
    """Test the statements API and analyze the full response"""
    fetcher = MyHomeFetcher()
    
    print("Testing statements API with full response...")
    
    try:
        url = f"{fetcher.base_url}/statements"
        params = {'page': 1, 'limit': 5}  # Get just 5 items for analysis
        
        response = fetcher.session.get(url, params=params, headers=fetcher.headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Response keys: {list(data.keys())}")
            
            # Save the full response for analysis
            with open("statements_api_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print("✅ Full response saved to statements_api_response.json")
            
            # Analyze the structure
            if 'data' in data:
                print(f"Data structure: {type(data['data'])}")
                if isinstance(data['data'], list):
                    print(f"Number of items: {len(data['data'])}")
                    if len(data['data']) > 0:
                        print(f"First item keys: {list(data['data'][0].keys())}")
                        print(f"First item: {json.dumps(data['data'][0], indent=2)}")
                elif isinstance(data['data'], dict):
                    print(f"Data dict keys: {list(data['data'].keys())}")
            
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    fetcher.close()

if __name__ == "__main__":
    test_statements_api_full()
