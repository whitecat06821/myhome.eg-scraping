#!/usr/bin/env python3
"""
Research Script for "Show Number" Button Network Analysis
Analyzes network requests when clicking "Show Number" buttons on MyHome.ge
"""

import sys
import os
import logging
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

class ShowNumberButtonResearcher:
    """Research tool for analyzing Show Number button network requests"""
    
    def __init__(self):
        self.setup_logging()
        self.driver = None
        self.init_selenium_with_network_capture()
        
        # Sample URLs provided by user
        self.test_urls = [
            "https://www.myhome.ge/pr/22017703/qiravdeba-4-otaxiani-bina-chughuretshi/",
            "https://www.myhome.ge/pr/22018490/qiravdeba-2-otaxiani-bina-chughuretshi/",
            "https://www.myhome.ge/pr/22017926/qiravdeba-3-otaxiani-bina-chughuretshi/",
            "https://www.myhome.ge/pr/22017997/qiravdeba-3-otaxiani-bina-bagebshi/"
        ]
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('show_number_research.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_selenium_with_network_capture(self):
        """Initialize Selenium with network logging enabled"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36')
            
            # Enable network logging
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Enable performance logging to capture network requests
            caps = DesiredCapabilities.CHROME
            caps['goog:loggingPrefs'] = {'performance': 'ALL'}
            
            service = webdriver.ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options, desired_capabilities=caps)
            
            # Enable Network domain for DevTools
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Page.enable', {})
            
            self.logger.info("Selenium WebDriver with network capture initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Selenium: {e}")
            self.driver = None
    
    def capture_network_requests(self):
        """Capture network requests from browser logs"""
        logs = self.driver.get_log('performance')
        network_requests = []
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                if message.get('message', {}).get('method') in ['Network.requestWillBeSent', 'Network.responseReceived']:
                    network_requests.append(message)
            except json.JSONDecodeError:
                continue
        
        return network_requests
    
    def analyze_show_number_button(self, property_url: str):
        """Analyze network requests when clicking Show Number button"""
        if not self.driver:
            self.logger.error("Selenium WebDriver not available")
            return
        
        self.logger.info(f"🔍 Analyzing Show Number button for: {property_url}")
        
        try:
            # Load the property page
            self.driver.get(property_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            self.logger.info("✅ Page loaded successfully")
            
            # Clear previous network logs
            self.driver.get_log('performance')
            
            # Find the Show Number button with the exact selector from user's DOM
            button_selectors = [
                "button.md\\:flex.inline-flex.items-center.justify-center",
                "button:has(span:contains('ნომრის ნახვა'))",  # Contains Georgian text
                "button:has(span:contains('511 131'))",      # Contains partial phone
                "button[class*='bg-primary-100']",           # Has the background class
                "button:has(svg[viewBox='0 0 24 24'])"       # Has the phone icon SVG
            ]
            
            button = None
            button_selector_used = None
            
            for selector in button_selectors:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    button_selector_used = selector
                    self.logger.info(f"✅ Found Show Number button with selector: {selector}")
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
            
            if not button:
                self.logger.error("❌ Could not find Show Number button")
                return
            
            # Get button text/content before clicking
            button_text = button.text
            self.logger.info(f"📝 Button text before click: {button_text}")
            
            # Capture network state before clicking
            self.logger.info("📡 Capturing network requests before button click...")
            requests_before = self.capture_network_requests()
            
            # Click the Show Number button
            self.logger.info("🔘 Clicking Show Number button...")
            button.click()
            
            # Wait for potential network requests and DOM updates
            time.sleep(3)
            
            # Capture network state after clicking
            self.logger.info("📡 Capturing network requests after button click...")
            requests_after = self.capture_network_requests()
            
            # Find new network requests (after click)
            new_requests = requests_after[len(requests_before):]
            
            self.logger.info(f"📊 Found {len(new_requests)} new network requests after button click")
            
            # Analyze the new network requests
            phone_related_requests = []
            
            for request in new_requests:
                try:
                    if request.get('message', {}).get('method') == 'Network.requestWillBeSent':
                        request_data = request['message']['params']['request']
                        url = request_data.get('url', '')
                        method = request_data.get('method', '')
                        headers = request_data.get('headers', {})
                        post_data = request_data.get('postData', '')
                        
                        # Check if this might be a phone-related request
                        if any(keyword in url.lower() for keyword in ['phone', 'show', 'contact', 'statement', 'api']):
                            phone_related_requests.append({
                                'url': url,
                                'method': method,
                                'headers': headers,
                                'postData': post_data
                            })
                            
                            self.logger.info(f"🔍 Phone-related request found:")
                            self.logger.info(f"   URL: {url}")
                            self.logger.info(f"   Method: {method}")
                            self.logger.info(f"   Headers: {json.dumps(headers, indent=2)}")
                            if post_data:
                                self.logger.info(f"   POST Data: {post_data}")
                            
                except Exception as e:
                    self.logger.error(f"Error analyzing request: {e}")
            
            # Check if button text changed
            new_button_text = button.text
            self.logger.info(f"📝 Button text after click: {new_button_text}")
            
            if new_button_text != button_text:
                self.logger.info("✅ Button text changed - phone number might be revealed!")
            
            # Check localStorage for phone data
            try:
                local_storage = self.driver.execute_script("return Object.entries(localStorage);")
                self.logger.info(f"💾 LocalStorage content: {local_storage}")
                
                session_storage = self.driver.execute_script("return Object.entries(sessionStorage);")
                self.logger.info(f"💾 SessionStorage content: {session_storage}")
                
            except Exception as e:
                self.logger.error(f"Error reading storage: {e}")
            
            # Save detailed analysis to file
            analysis_data = {
                'property_url': property_url,
                'button_selector_used': button_selector_used,
                'button_text_before': button_text,
                'button_text_after': new_button_text,
                'phone_related_requests': phone_related_requests,
                'total_new_requests': len(new_requests)
            }
            
            filename = f"show_number_analysis_{property_url.split('/')[-2]}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Detailed analysis saved to: {filename}")
            
        except Exception as e:
            self.logger.error(f"❌ Error analyzing Show Number button: {e}")
    
    def research_all_samples(self):
        """Research Show Number button for all sample URLs"""
        self.logger.info("🚀 Starting Show Number button research on sample URLs...")
        
        for i, url in enumerate(self.test_urls, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"📋 Testing URL {i}/{len(self.test_urls)}")
            self.analyze_show_number_button(url)
            time.sleep(2)  # Brief pause between tests
        
        self.logger.info(f"\n✅ Show Number button research completed!")
        self.logger.info("📄 Check the generated .json files for detailed network analysis")
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function to run the Show Number button research"""
    researcher = None
    try:
        print("🔬 MyHome.ge Show Number Button Network Research")
        print("=" * 55)
        
        researcher = ShowNumberButtonResearcher()
        researcher.research_all_samples()
        
    except KeyboardInterrupt:
        print("\n⚠️ Research interrupted by user")
    except Exception as e:
        print(f"❌ Error during research: {e}")
        logging.error(f"Fatal error: {e}")
    finally:
        if researcher:
            researcher.close()

if __name__ == "__main__":
    main()
