import requests
import json

def test_api_debug():
    """Debug API response with updated headers"""
    
    base_url = "https://api-statements.tnet.ge/v1/users/company/brokers-web"
    
    # Updated headers with x-website-key
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.myhome.ge/',
        'Origin': 'https://www.myhome.ge',
        'Sec-Ch-Ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'x-website-key': 'myhome',
        'locale': 'ka'
    }
    
    print("Testing API with updated headers...")
    
    try:
        response = requests.get(
            base_url, 
            params={'page': 1, 'q': ''}, 
            headers=headers, 
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Content Length: {len(response.content)}")
        print(f"Response Content Type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            print("SUCCESS! API call worked!")
            
            # Check if response is empty
            if len(response.content) == 0:
                print("WARNING: Response is empty!")
                return False
            
            # Try to decode the response
            try:
                data = response.json()
                print(f"Response data type: {type(data)}")
                if isinstance(data, list):
                    print(f"Found {len(data)} agents in response")
                    if data:
                        print(f"First agent: {data[0]}")
                elif isinstance(data, dict):
                    print(f"Response keys: {list(data.keys())}")
                    print(f"Response data: {json.dumps(data, indent=2)[:1000]}...")
                return True
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                print(f"Raw response content: {response.text[:500]}...")
                return False
        else:
            print(f"Response text: {response.text[:500]}...")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_debug()
    if success:
        print("\n✅ API call successful!")
    else:
        print("\n❌ API call failed")
