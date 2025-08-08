#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re

def setup_logging():
    logging.basicConfig(level=logging.INFO)

def test_selenium():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        # Start driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        
        logger.info("Chrome WebDriver started successfully")
        
        # Navigate to the agents page
        url = "https://www.myhome.ge/maklers/"
        logger.info(f"Navigating to: {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Get the page source
        html = driver.page_source
        logger.info(f"Page loaded, HTML length: {len(html)}")
        
        # Save HTML for analysis
        with open('selenium_agents_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info("Saved HTML to selenium_agents_page.html")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for agent cards or links
        agent_links = soup.find_all('a', href=re.compile(r'/maklers/\d+/'))
        logger.info(f"Found {len(agent_links)} agent links")
        
        for i, link in enumerate(agent_links[:5]):
            href = link.get('href')
            text = link.get_text().strip()
            logger.info(f"Agent {i+1}: {href} - {text}")
        
        # Look for phone numbers
        phone_pattern = re.compile(r'\+?995\s*\d{3}\s*\d{3}\s*\d{3}|\d{3}\s*\d{3}\s*\d{3}')
        phones = phone_pattern.findall(soup.get_text())
        logger.info(f"Found {len(phones)} potential phone numbers")
        
        for i, phone in enumerate(phones[:10]):
            logger.info(f"Phone {i+1}: {phone}")
        
        # Look for any divs with agent-related content
        agent_divs = soup.find_all('div', class_=re.compile(r'agent|makler|card', re.I))
        logger.info(f"Found {len(agent_divs)} divs with agent/makler/card classes")
        
        for i, div in enumerate(agent_divs[:3]):
            classes = div.get('class', [])
            text = div.get_text()[:100]
            logger.info(f"Div {i+1} classes: {classes}")
            logger.info(f"Div {i+1} text: {text}")
        
        driver.quit()
        logger.info("Test completed successfully")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    test_selenium()
