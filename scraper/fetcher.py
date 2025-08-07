"""
HTTP request handling and page fetching module.
Handles requests to myhome.ge with proper rate limiting and error handling.
"""

import requests
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class MyHomeFetcher:
    """Handles HTTP requests to myhome.ge with proper rate limiting and error handling."""
    
    def __init__(self, base_url: str = "https://www.myhome.ge", delay: float = 1.0):
        """
        Initialize the fetcher.
        
        Args:
            base_url: Base URL for the website
            delay: Delay between requests in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.delay = delay
        self.session = self._create_session()
        self.last_request_time = 0
        
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic and proper headers."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set headers to mimic a real browser
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _rate_limit(self):
        """Implement rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay:
            sleep_time = self.delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a web page with proper error handling and rate limiting.
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string, or None if failed
        """
        # Ensure URL is absolute
        if not url.startswith('http'):
            url = urljoin(self.base_url, url)
        
        self._rate_limit()
        
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            logger.debug(f"Successfully fetched {url} (status: {response.status_code})")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
    
    def fetch_agents_list(self, page: int = 1) -> Optional[str]:
        """
        Fetch the agents listing page.
        
        Args:
            page: Page number to fetch
            
        Returns:
            HTML content of the agents listing page
        """
        url = f"{self.base_url}/maklers/"
        if page > 1:
            url += f"?page={page}"
        
        return self.fetch_page(url)
    
    def fetch_agent_detail(self, agent_id: str) -> Optional[str]:
        """
        Fetch a specific agent's detail page.
        
        Args:
            agent_id: Agent ID from the URL
            
        Returns:
            HTML content of the agent detail page
        """
        url = f"{self.base_url}/maklers/{agent_id}/"
        return self.fetch_page(url)
    
    def fetch_property_detail(self, property_id: str) -> Optional[str]:
        """
        Fetch a specific property's detail page.
        
        Args:
            property_id: Property ID from the URL
            
        Returns:
            HTML content of the property detail page
        """
        url = f"{self.base_url}/pr/{property_id}/"
        return self.fetch_page(url)
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
