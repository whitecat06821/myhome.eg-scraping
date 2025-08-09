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
    
    def __init__(self):
        self.session = self._create_session()
        self.base_url = "https://api-statements.tnet.ge/v1"
        # Updated headers based on successful browser requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'identity',  # Request uncompressed content to avoid Brotli issues
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
    
    def _create_session(self):
        """Create a requests session with retry logic"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        return session
    
    def _rate_limit(self):
        """Simple rate limiting to be polite to the server"""
        time.sleep(1)
    
    def fetch_agents_api(self, page: int = 1, query: str = "") -> Optional[Dict[str, Any]]:
        """Fetch agents data directly from the API endpoint"""
        try:
            url = f"{self.base_url}/users/company/brokers-web"
            params = {
                'page': page,
                'q': query
            }
            
            logger.info(f"Fetching agents from API: page {page}")
            self._rate_limit()
            
            response = self.session.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched API data for page {page}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching agents API page {page}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching agents API page {page}: {e}")
            return None
    
    def fetch_agent_detail_api(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Fetch individual agent detail from API (if available)"""
        try:
            url = f"{self.base_url}/users/company/brokers/{agent_id}"
            
            logger.info(f"Fetching agent detail from API: {agent_id}")
            self._rate_limit()
            
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched agent detail for {agent_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching agent detail API {agent_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching agent detail API {agent_id}: {e}")
            return None
    
    def fetch_agent_sub_agents_api(self, agent_id: str, page: int = 1) -> Optional[Dict[str, Any]]:
        """Fetch sub-agents for a specific agent from API"""
        try:
            url = f"{self.base_url}/users/company/brokers-web/{agent_id}/agents"
            params = {
                'page': page,
                'q': ''
            }
            
            logger.info(f"Fetching sub-agents from API: agent {agent_id}, page {page}")
            self._rate_limit()
            
            response = self.session.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched sub-agents for agent {agent_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching sub-agents API agent {agent_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching sub-agents API agent {agent_id}: {e}")
            return None
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a regular web page"""
        try:
            self._rate_limit()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching page {url}: {e}")
            return None
    
    def fetch_agents_list(self, page: int = 1) -> Optional[str]:
        """Fetch agents list page (legacy method)"""
        url = f"https://www.myhome.ge/maklers/?page={page}"
        return self.fetch_page(url)
    
    def fetch_agent_detail(self, agent_url: str) -> Optional[str]:
        """Fetch agent detail page (legacy method)"""
        return self.fetch_page(agent_url)
    
    def fetch_property_detail(self, property_url: str) -> Optional[str]:
        """Fetch property detail page"""
        return self.fetch_page(property_url)
    
    def fetch_property_listings(self, page: int = 1) -> Optional[str]:
        """Fetch property listings page"""
        # Use rental properties URL since we want owner phone numbers
        url = f"https://www.myhome.ge/pr/rent/?page={page}"
        return self.fetch_page(url)
    
    def fetch_property_phone_api(self, statement_uuid: str) -> Optional[Dict[str, Any]]:
        """Fetch property phone number from API using statement UUID"""
        try:
            url = f"{self.base_url}/statements/phone/show?statement_uuid={statement_uuid}"
            
            logger.info(f"Fetching property phone from API: {statement_uuid}")
            self._rate_limit()
            
            # Send empty JSON body as per the network analysis
            response = self.session.post(url, json={}, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched property phone for {statement_uuid}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching property phone API {statement_uuid}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching property phone API {statement_uuid}: {e}")
            return None

    def fetch_property_listings_api(self, page: int = 1, endpoint: str = "/statements") -> Optional[Dict[str, Any]]:
        """Fetch property listings from various API endpoints"""
        try:
            # Handle both full endpoints and partial ones
            if endpoint.startswith('/'):
                url = f"{self.base_url}{endpoint}"
            else:
                url = f"{self.base_url}/{endpoint}"
            
            params = {'page': page, 'limit': 50}
            
            # Parse existing query parameters from endpoint
            if '?' in endpoint:
                base_endpoint, query_string = endpoint.split('?', 1)
                url = f"{self.base_url}{base_endpoint}"
                # Parse query parameters
                query_params = {}
                for param in query_string.split('&'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        query_params[key] = value
                params.update(query_params)
            
            logger.info(f"Fetching property listings from API: {endpoint} page {page}")
            self._rate_limit()
            
            response = self.session.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched property listings for {endpoint} page {page}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching property listings API {endpoint} page {page}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching property listings API {endpoint} page {page}: {e}")
            return None
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
