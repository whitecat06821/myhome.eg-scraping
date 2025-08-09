import re
import logging
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class MyHomeParser:
    def __init__(self):
        self.phone_patterns = [
            r'\+995\s*\d{3}\s*\d{3}\s*\d{3}',
            r'995\s*\d{3}\s*\d{3}\s*\d{3}',
            r'\d{3}\s*\d{3}\s*\d{3}',
            r'\d{9}',
        ]
    
    def parse_agents_api_response(self, api_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Parse the API response to extract agent information"""
        agents = []
        
        try:
            if not api_data:
                logger.warning("No data found in API response")
                return agents
            
            # Handle the actual API response structure: {"result": true, "data": {"data": [...]}}
            if isinstance(api_data, dict) and 'result' in api_data and api_data['result']:
                data = api_data.get('data', {})
                if isinstance(data, dict) and 'data' in data:
                    agent_list = data['data']
                    logger.info(f"Found {len(agent_list)} agents in API response")
                    
                    for agent in agent_list:
                        try:
                            agent_info = self._extract_agent_from_api(agent)
                            if agent_info:
                                agents.append(agent_info)
                        except Exception as e:
                            logger.error(f"Error parsing agent from API: {e}")
                            continue
                    
                    logger.info(f"Successfully parsed {len(agents)} agents from API")
                    return agents
            
            # Fallback for other structures
            if isinstance(api_data, list):
                agent_list = api_data
            elif isinstance(api_data, dict) and 'data' in api_data:
                data = api_data['data']
                if isinstance(data, list):
                    agent_list = data
                elif isinstance(data, dict) and 'items' in data:
                    agent_list = data['items']
                elif isinstance(data, dict) and 'brokers' in data:
                    agent_list = data['brokers']
                else:
                    logger.warning(f"Unexpected API data structure: {type(data)}")
                    return agents
            else:
                logger.warning(f"Unexpected API response structure: {type(api_data)}")
                return agents
            
            logger.info(f"Found {len(agent_list)} agents in API response")
            
            for agent in agent_list:
                try:
                    agent_info = self._extract_agent_from_api(agent)
                    if agent_info:
                        agents.append(agent_info)
                except Exception as e:
                    logger.error(f"Error parsing agent from API: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(agents)} agents from API")
            return agents
            
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
            return agents
    
    def parse_sub_agents_api_response(self, api_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Parse the sub-agents API response to extract individual agent information"""
        agents = []
        
        try:
            if not api_data or 'data' not in api_data:
                logger.warning("No data found in sub-agents API response")
                return agents
            
            data = api_data['data']
            
            # Handle the nested data structure from sub-agents API
            if isinstance(data, dict) and 'data' in data:
                agent_list = data['data']
            elif isinstance(data, list):
                agent_list = data
            else:
                logger.warning(f"Unexpected sub-agents API data structure: {type(data)}")
                return agents
            
            logger.info(f"Found {len(agent_list)} sub-agents in API response")
            
            for agent in agent_list:
                try:
                    agent_info = self._extract_sub_agent_from_api(agent)
                    if agent_info:
                        agents.append(agent_info)
                except Exception as e:
                    logger.error(f"Error parsing sub-agent from API: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(agents)} sub-agents from API")
            return agents
            
        except Exception as e:
            logger.error(f"Error parsing sub-agents API response: {e}")
            return agents
    
    def _extract_agent_from_api(self, agent_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract agent information from API data structure"""
        try:
            # Extract basic information based on the JSON structure from screenshots
            agent_id = str(agent_data.get('id', ''))
            name = agent_data.get('name', '') or agent_data.get('company_name', '') or agent_data.get('title', '')
            phone = agent_data.get('phone_number', '') or agent_data.get('phone', '') or agent_data.get('mobile', '') or agent_data.get('contact_phone', '')
            
            # Clean and validate data
            if not name or not phone:
                logger.debug(f"Missing name or phone for agent {agent_id}")
                return None
            
            # Clean phone number
            phone = self._clean_phone(phone)
            if not self._is_valid_phone(phone):
                logger.debug(f"Invalid phone number for agent {name}: {phone}")
                return None
            
            # Create agent URL
            agent_url = f"https://www.myhome.ge/maklers/{agent_id}/"
            
            return {
                'id': agent_id,
                'name': self._clean_text(name),
                'phone': phone,
                'url': agent_url
            }
            
        except Exception as e:
            logger.error(f"Error extracting agent from API data: {e}")
            return None
    
    def _extract_sub_agent_from_api(self, agent_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract sub-agent information from API data structure"""
        try:
            # Extract basic information for sub-agents
            agent_id = str(agent_data.get('id', ''))
            name = agent_data.get('name', '')
            phone = agent_data.get('phone_number', '') or agent_data.get('phone', '')
            
            # Clean and validate data
            if not name or not phone:
                logger.debug(f"Missing name or phone for sub-agent {agent_id}")
                return None
            
            # Clean phone number
            phone = self._clean_phone(phone)
            if not self._is_valid_phone(phone):
                logger.debug(f"Invalid phone number for sub-agent {name}: {phone}")
                return None
            
            # Create agent URL
            agent_url = f"https://www.myhome.ge/maklers/{agent_id}/"
            
            return {
                'id': agent_id,
                'name': self._clean_text(name),
                'phone': phone,
                'url': agent_url
            }
            
        except Exception as e:
            logger.error(f"Error extracting sub-agent from API data: {e}")
            return None
    
    def extract_agent_links_from_list(self, html: str) -> List[str]:
        """Extract agent detail page URLs from the agents listing page."""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        agent_links = []
        
        try:
            # Look for agent links with href containing /maklers/
            links = soup.find_all('a', href=re.compile(r'/maklers/\d+/'))
            
            for link in links:
                href = link.get('href', '')
                # Filter out navigation links and only get agent detail links
                if href and '/maklers/' in href and href.count('/') >= 3:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = f"https://www.myhome.ge{href}"
                    agent_links.append(href)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in agent_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)
            
            logger.info(f"Found {len(unique_links)} unique agent links")
            return unique_links
            
        except Exception as e:
            logger.error(f"Error extracting agent links: {e}")
            return []
    
    def extract_property_links_from_list(self, html: str) -> List[str]:
        """Extract property detail page URLs from the property listings page."""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        property_links = []
        
        try:
            # Look for property links with href containing /pr/
            links = soup.find_all('a', href=re.compile(r'/pr/\d+/'))
            
            for link in links:
                href = link.get('href', '')
                # Filter out navigation links and only get property detail links
                if href and '/pr/' in href and href.count('/') >= 3:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = f"https://www.myhome.ge{href}"
                    property_links.append(href)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in property_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)
            
            logger.info(f"Found {len(unique_links)} unique property links")
            return unique_links
            
        except Exception as e:
            logger.error(f"Error extracting property links: {e}")
            return []
    
    def parse_agents_list(self, html: str) -> List[Dict[str, str]]:
        """Parse the agents listing page to extract agent information."""
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        agents = []
        
        try:
            # Look for agent cards/links on the listing page
            agent_links = soup.find_all('a', href=re.compile(r'/maklers/\d+/'))
            
            for link in agent_links:
                agent_id = self._extract_agent_id(link.get('href', ''))
                if agent_id:
                    agent_info = {
                        'id': agent_id,
                        'url': link.get('href'),
                        'name': self._extract_text(link),
                    }
                    agents.append(agent_info)
            
            # If no links found, try alternative selectors
            if not agents:
                # Look for agent cards with phone numbers directly visible
                agent_cards = soup.find_all('div', class_=re.compile(r'agent|makler|card'))
                for card in agent_cards:
                    name = self._extract_agent_name_from_card(card)
                    phone = self._extract_phone_from_card(card)
                    if name and phone:
                        agents.append({
                            'name': name,
                            'phone': phone,
                            'url': f"/maklers/{self._extract_agent_id_from_card(card)}/"
                        })
        
        except Exception as e:
            logger.error(f"Error parsing agents list: {e}")
        
        return agents
    
    def parse_agent_detail(self, html: str, agent_url: str) -> Optional[Dict[str, str]]:
        """Parse agent detail page to extract name and phone number."""
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            name = self._extract_agent_name(soup)
            phone = self._extract_phone_number(soup)
            
            if name and phone:
                return {
                    'name': name,
                    'phone': phone,
                    'url': agent_url
                }
                
        except Exception as e:
            logger.error(f"Error parsing agent detail: {e}")
        
        return None
    
    def parse_property_detail(self, html: str, property_url: str) -> Optional[Dict[str, str]]:
        """Parse property detail page to extract owner name and phone number."""
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            owner_name = self._extract_owner_name(soup)
            phone = self._extract_phone_number(soup)
            
            if phone:
                return {
                    'name': owner_name or 'Property Owner',
                    'phone': phone,
                    'url': property_url
                }
                
        except Exception as e:
            logger.error(f"Error parsing property detail: {e}")
        
        return None
    
    def _extract_agent_id(self, url: str) -> Optional[str]:
        """Extract agent ID from URL."""
        match = re.search(r'/maklers/(\d+)/', url)
        return match.group(1) if match else None
    
    def _extract_agent_id_from_card(self, card) -> Optional[str]:
        """Extract agent ID from agent card element."""
        # Look for ID in various attributes
        for attr in ['data-id', 'data-agent-id', 'id']:
            value = card.get(attr)
            if value and re.match(r'\d+', value):
                return value
        
        # Look for ID in child elements
        id_elements = card.find_all(['span', 'div'], string=re.compile(r'\d+'))
        for element in id_elements:
            text = element.get_text().strip()
            if re.match(r'^\d+$', text):
                return text
        
        return None
    
    def _extract_agent_name_from_card(self, card) -> Optional[str]:
        """Extract agent name from agent card element."""
        # Common selectors for agent names
        name_selectors = [
            '.agent-name', '.makler-name', '.name', 
            'h3', 'h4', 'h5', 'strong', 'b',
            '[class*="name"]', '[class*="agent"]'
        ]
        
        for selector in name_selectors:
            element = card.select_one(selector)
            if element:
                name = self._clean_text(element.get_text())
                if name and len(name) > 2:
                    return name
        
        return None
    
    def _extract_phone_from_card(self, card) -> Optional[str]:
        """Extract phone number from agent card element."""
        # Look for phone in text content
        phone = self._find_phone_in_text(card.get_text())
        if phone:
            return phone
        
        # Look for phone in specific elements
        phone_selectors = [
            '.phone', '.tel', '.contact-phone',
            '[class*="phone"]', '[class*="tel"]',
            'a[href^="tel:"]', 'a[href^="callto:"]'
        ]
        
        for selector in phone_selectors:
            elements = card.select(selector)
            for element in elements:
                # Check href attribute
                href = element.get('href', '')
                if href.startswith('tel:') or href.startswith('callto:'):
                    phone = href.replace('tel:', '').replace('callto:', '')
                    if self._is_valid_phone(phone):
                        return self._clean_phone(phone)
                
                # Check text content
                phone = self._find_phone_in_text(element.get_text())
                if phone:
                    return phone
        
        return None
    
    def _extract_agent_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract agent name from detail page."""
        selectors = [
            'h1', '.agent-name', '.profile-name', '.name',
            '[class*="name"]', '[class*="agent"]', 'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = self._clean_text(element.get_text())
                if name and len(name) > 2:
                    return name
        return None
    
    def _extract_owner_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract owner name from property page."""
        selectors = [
            '.owner-name', '.contact-name', '.property-owner',
            '[class*="owner"]', '[class*="contact"]', '[class*="name"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                name = self._clean_text(element.get_text())
                if name and len(name) > 2:
                    return name
        return None
    
    def _extract_phone_number(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract phone number from page content."""
        # First try to find phone in text content
        phone = self._find_phone_in_text(soup.get_text())
        if phone:
            return phone
        
        # Look for phone in specific elements
        phone_selectors = [
            '.phone', '.tel', '.contact-phone', '.agent-phone',
            '[class*="phone"]', '[class*="tel"]', '[class*="contact"]',
            'a[href^="tel:"]', 'a[href^="callto:"]'
        ]
        
        for selector in phone_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Check href attribute for tel: links
                href = element.get('href', '')
                if href.startswith('tel:') or href.startswith('callto:'):
                    phone = href.replace('tel:', '').replace('callto:', '')
                    if self._is_valid_phone(phone):
                        return self._clean_phone(phone)
                
                # Check text content
                phone = self._find_phone_in_text(element.get_text())
                if phone:
                    return phone
        
        return None
    
    def _find_phone_in_text(self, text: str) -> Optional[str]:
        """Find phone number in text using regex patterns."""
        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if self._is_valid_phone(match):
                    return self._clean_phone(match)
        return None
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Validate if a phone number is a valid Georgian number."""
        digits = re.sub(r'\D', '', phone)
        
        # Georgian mobile numbers: 9 digits starting with 5
        if len(digits) == 9 and digits.startswith('5'):
            return True
        
        # Georgian numbers with country code: 12 digits starting with 995
        if len(digits) == 12 and digits.startswith('995'):
            return True
        
        return False
    
    def _clean_phone(self, phone: str) -> str:
        """Clean and format phone number."""
        digits = re.sub(r'\D', '', phone)
        
        # Format as international Georgian number
        if len(digits) == 12 and digits.startswith('995'):
            return f"+{digits}"
        
        if len(digits) == 9:
            return f"+995{digits}"
        
        return phone
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace."""
        if not text:
            return ""
        cleaned = re.sub(r'\s+', ' ', text.strip())
        return cleaned
    
    def _extract_text(self, element) -> str:
        """Extract and clean text from an element."""
        if not element:
            return ""
        text = element.get_text()
        return self._clean_text(text)

    def parse_property_phone_api_response(self, api_data: Dict[str, Any]) -> Optional[str]:
        """Parse the API response to extract phone number"""
        try:
            if not api_data:
                logger.warning("No data found in property phone API response")
                return None
            
            # Handle the API response structure: {"result": true, "data": {"phone_number": "..."}}
            if isinstance(api_data, dict) and 'result' in api_data and api_data['result']:
                data = api_data.get('data', {})
                if isinstance(data, dict) and 'phone_number' in data:
                    phone = data['phone_number']
                    logger.info(f"Found phone number in API response: {phone}")
                    
                    # Clean and validate phone number
                    phone = self._clean_phone(phone)
                    if self._is_valid_phone(phone):
                        return phone
                    else:
                        logger.warning(f"Invalid phone number from API: {phone}")
                        return None
            
            logger.warning(f"Unexpected property phone API response structure: {type(api_data)}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing property phone API response: {e}")
            return None

    def extract_statement_uuid_from_url(self, property_url: str, fetcher=None) -> Optional[str]:
        """Extract statement UUID from property URL by fetching the page first"""
        try:
            # First, fetch the property page to get the statement UUID
            if not fetcher:
                logger.warning("Fetcher not provided, cannot extract statement UUID")
                return None
            
            html_content = fetcher.fetch_page(property_url)
            if not html_content:
                logger.error(f"Failed to fetch property page: {property_url}")
                return None
            
            # Look for UUID pattern in the page content
            import re
            
            # Pattern for UUID: 8bba42bb-1077-42bc-af89-d242b70a632a
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            matches = re.findall(uuid_pattern, html_content, re.IGNORECASE)
            
            if matches:
                # Use the first UUID found (usually the statement UUID)
                statement_uuid = matches[0]
                logger.info(f"Found statement UUID: {statement_uuid}")
                return statement_uuid
            
            # Also look for statementId pattern as fallback
            statement_id_pattern = r'"statementId":"(\d+)"'
            match = re.search(statement_id_pattern, html_content)
            
            if match:
                statement_id = match.group(1)
                logger.info(f"Found statement ID (fallback): {statement_id}")
                return statement_id
            
            # Final fallback: extract from URL
            url_match = re.search(r'/pr/(\d+)/', property_url)
            if url_match:
                property_id = url_match.group(1)
                logger.info(f"Using property ID as statement ID (fallback): {property_id}")
                return property_id
            
            logger.warning(f"No statement UUID found in property page: {property_url}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting statement UUID from URL {property_url}: {e}")
            return None

    def parse_property_listings_api_response(self, api_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Parse the API response to extract property information"""
        properties = []
        
        try:
            if not api_data:
                logger.warning("No data found in property listings API response")
                return properties
            
            # Handle the API response structure
            if isinstance(api_data, dict) and 'result' in api_data and api_data['result']:
                data = api_data.get('data', {})
                if isinstance(data, dict) and 'data' in data:
                    property_list = data['data']
                    logger.info(f"Found {len(property_list)} properties in API response")
                    
                    for property_item in property_list:
                        try:
                            property_info = self._extract_property_from_api(property_item)
                            if property_info:
                                properties.append(property_info)
                        except Exception as e:
                            logger.error(f"Error parsing property from API: {e}")
                            continue
                    
                    logger.info(f"Successfully parsed {len(properties)} properties from API")
                    return properties
            
            logger.warning(f"Unexpected property listings API response structure: {type(api_data)}")
            return properties
            
        except Exception as e:
            logger.error(f"Error parsing property listings API response: {e}")
            return properties

    def _extract_property_from_api(self, property_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extract property information from API data structure"""
        try:
            # Extract basic information
            property_id = str(property_data.get('id', ''))
            uuid = property_data.get('uuid', '')
            
            if not property_id or not uuid:
                logger.debug(f"Missing ID or UUID for property")
                return None
            
            # Create property URL
            property_url = f"https://www.myhome.ge/pr/{property_id}/"
            
            return {
                'id': property_id,
                'uuid': uuid,
                'url': property_url
            }
            
        except Exception as e:
            logger.error(f"Error extracting property from API data: {e}")
            return None
