import requests
import json

def test_exact_headers():
    """Test with exact headers from browser screenshots"""
    
    base_url = "https://api-statements.tnet.ge/v1/users/company/brokers-web"
    
    # Exact headers from the successful browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.myhome.ge/',
        'Origin': 'https://www.myhome.ge',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site'
    }
    
    print("Testing with exact headers from browser...")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    
    try:
        response = requests.get(
            base_url, 
            params={'page': 1, 'q': ''}, 
            headers=headers, 
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("SUCCESS! API call worked!")
            data = response.json()
            print(f"Response data type: {type(data)}")
            if isinstance(data, list):
                print(f"Found {len(data)} agents in response")
                if data:
                    print(f"First agent: {data[0]}")
            elif isinstance(data, dict):
                print(f"Response keys: {list(data.keys())}")
            return True
        else:
            print(f"Response text: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_exact_headers()
    if success:
        print("\n✅ API call successful!")
    else:
        print("\n❌ API call failed")
