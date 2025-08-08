import logging
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeleniumAPIInterceptor:
    def __init__(self):
        self.driver = None
        self.api_responses = []
        
    def start_driver(self):
        """Start Chrome WebDriver with network interception"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Enable network interception
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            # Use the correct ChromeDriver path
            driver_path = r"C:\Users\Success\.wdm\drivers\chromedriver\win64\139.0.7258.66\chromedriver-win32\chromedriver.exe"
            service = Service(driver_path)
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
            logger.info("Chrome WebDriver started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Chrome WebDriver: {e}")
            return False
    
    def intercept_api_calls(self, url: str):
        """Navigate to page and intercept API calls"""
        try:
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load and API calls to be made
            time.sleep(5)
            
            # Get performance logs
            logs = self.driver.get_log('performance')
            
            # Extract API responses
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    if 'message' in message and message['message']['method'] == 'Network.responseReceived':
                        response_url = message['message']['params']['response']['url']
                        if 'api-statements.tnet.ge' in response_url and 'brokers-web' in response_url:
                            logger.info(f"Found API response: {response_url}")
                            self._extract_response_data(message['message']['params']['requestId'])
                except Exception as e:
                    continue
            
            return True
            
        except Exception as e:
            logger.error(f"Error intercepting API calls: {e}")
            return False
    
    def _extract_response_data(self, request_id):
        """Extract response data for a specific request"""
        try:
            # Get response body
            response_body = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
            if response_body and 'body' in response_body:
                data = json.loads(response_body['body'])
                self.api_responses.append(data)
                logger.info(f"Extracted API response data: {len(data) if isinstance(data, list) else 'dict'}")
        except Exception as e:
            logger.error(f"Error extracting response data: {e}")
    
    def get_agents_data(self):
        """Get all collected agents data"""
        all_agents = []
        
        for response in self.api_responses:
            if isinstance(response, list):
                all_agents.extend(response)
            elif isinstance(response, dict) and 'data' in response:
                data = response['data']
                if isinstance(data, list):
                    all_agents.extend(data)
        
        return all_agents
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed successfully")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None

def main():
    """Test API interception"""
    interceptor = SeleniumAPIInterceptor()
    
    try:
        if interceptor.start_driver():
            # Navigate to agents page to trigger API calls
            success = interceptor.intercept_api_calls("https://www.myhome.ge/maklers/")
            
            if success:
                agents_data = interceptor.get_agents_data()
                logger.info(f"Found {len(agents_data)} agents through API interception")
                
                if agents_data:
                    logger.info("Sample agent data:")
                    for i, agent in enumerate(agents_data[:3]):
                        logger.info(f"  {i+1}. {agent.get('name', 'Unknown')} - {agent.get('phone_number', 'No phone')}")
                
                # Save the data
                with open("intercepted_agents.json", "w", encoding="utf-8") as f:
                    json.dump(agents_data, f, indent=2, ensure_ascii=False)
                logger.info("Saved intercepted agents data to intercepted_agents.json")
            
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        interceptor.close()

if __name__ == "__main__":
    main()
