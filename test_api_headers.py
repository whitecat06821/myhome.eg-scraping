import requests
import json

def test_api_headers():
    """Test different headers to access the API"""
    
    base_url = "https://api-statements.tnet.ge/v1/users/company/brokers-web"
    
    # Test different header combinations
    header_sets = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.myhome.ge/maklers/',
            'Origin': 'https://www.myhome.ge'
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ka,en;q=0.9',
            'Referer': 'https://www.myhome.ge/maklers/',
            'Origin': 'https://www.myhome.ge',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site'
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'ka,en;q=0.9',
            'Referer': 'https://www.myhome.ge/',
            'Origin': 'https://www.myhome.ge'
        }
    ]
    
    for i, headers in enumerate(header_sets):
        print(f"\n--- Testing Header Set {i+1} ---")
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
                print(f"Response data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return headers
            else:
                print(f"Response text: {response.text[:200]}...")
                
        except Exception as e:
            print(f"Error: {e}")
    
    return None

if __name__ == "__main__":
    working_headers = test_api_headers()
    if working_headers:
        print(f"\n✅ Working headers found: {working_headers}")
    else:
        print("\n❌ No working headers found")
