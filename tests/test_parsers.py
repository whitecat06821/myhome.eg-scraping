"""
Unit tests for the parser module.
Tests phone number extraction and HTML parsing logic.
"""

import pytest
from scraper.parser import MyHomeParser


class TestMyHomeParser:
    """Test cases for MyHomeParser class."""
    
    def setup_method(self):
        """Setup method for each test."""
        self.parser = MyHomeParser()
    
    def test_phone_number_validation(self):
        """Test phone number validation logic."""
        # Valid Georgian mobile numbers
        assert self.parser._is_valid_phone("+995 555 123 456")
        assert self.parser._is_valid_phone("995 555 123 456")
        assert self.parser._is_valid_phone("555 123 456")
        assert self.parser._is_valid_phone("555123456")
        
        # Invalid numbers
        assert not self.parser._is_valid_phone("123 456 789")  # Doesn't start with 5
        assert not self.parser._is_valid_phone("555 123")  # Too short
        assert not self.parser._is_valid_phone("555 123 456 789")  # Too long
    
    def test_phone_number_cleaning(self):
        """Test phone number cleaning and formatting."""
        # Test various input formats
        assert self.parser._clean_phone("+995 555 123 456") == "+995555123456"
        assert self.parser._clean_phone("995 555 123 456") == "+995555123456"
        assert self.parser._clean_phone("555 123 456") == "+995555123456"
        assert self.parser._clean_phone("555123456") == "+995555123456"
    
    def test_find_phone_in_text(self):
        """Test phone number extraction from text."""
        # Test with various phone number formats
        text_with_phone = "Contact us at +995 555 123 456 or call 555 789 012"
        phones = []
        for pattern in self.parser.phone_patterns:
            import re
            matches = re.findall(pattern, text_with_phone)
            for match in matches:
                if self.parser._is_valid_phone(match):
                    phones.append(self.parser._clean_phone(match))
        
        assert len(phones) > 0
        assert "+995555123456" in phones
    
    def test_extract_agent_id(self):
        """Test agent ID extraction from URLs."""
        # Valid agent URLs
        assert self.parser._extract_agent_id("/maklers/4756/") == "4756"
        assert self.parser._extract_agent_id("/maklers/12345/") == "12345"
        
        # Invalid URLs
        assert self.parser._extract_agent_id("/maklers/") is None
        assert self.parser._extract_agent_id("/pr/123/") is None
        assert self.parser._extract_agent_id("invalid") is None
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        # Test with extra whitespace and newlines
        dirty_text = "  John   Doe  \n\n  "
        clean_text = self.parser._clean_text(dirty_text)
        assert clean_text == "John Doe"
        
        # Test with empty text
        assert self.parser._clean_text("") == ""
        assert self.parser._clean_text(None) == ""
    
    def test_parse_agents_list_empty_html(self):
        """Test parsing agents list with empty HTML."""
        agents = self.parser.parse_agents_list("")
        assert agents == []
        
        agents = self.parser.parse_agents_list(None)
        assert agents == []
    
    def test_parse_agent_detail_empty_html(self):
        """Test parsing agent detail with empty HTML."""
        result = self.parser.parse_agent_detail("", "https://example.com")
        assert result is None
        
        result = self.parser.parse_agent_detail(None, "https://example.com")
        assert result is None
    
    def test_parse_property_detail_empty_html(self):
        """Test parsing property detail with empty HTML."""
        result = self.parser.parse_property_detail("", "https://example.com")
        assert result is None
        
        result = self.parser.parse_property_detail(None, "https://example.com")
        assert result is None


class TestPhoneNumberPatterns:
    """Test phone number regex patterns."""
    
    def setup_method(self):
        """Setup method for each test."""
        self.parser = MyHomeParser()
    
    def test_georgian_phone_patterns(self):
        """Test that regex patterns match Georgian phone numbers."""
        import re
        
        # Test pattern 1: +995 5XX XXX XXX
        pattern1 = r'\+995\s*\d{3}\s*\d{3}\s*\d{3}'
        assert re.search(pattern1, "+995 555 123 456")
        assert re.search(pattern1, "+995555123456")
        
        # Test pattern 2: 995 5XX XXX XXX
        pattern2 = r'995\s*\d{3}\s*\d{3}\s*\d{3}'
        assert re.search(pattern2, "995 555 123 456")
        assert re.search(pattern2, "995555123456")
        
        # Test pattern 3: 5XX XXX XXX
        pattern3 = r'\d{3}\s*\d{3}\s*\d{3}'
        assert re.search(pattern3, "555 123 456")
        assert re.search(pattern3, "555123456")
        
        # Test pattern 4: 9 digits
        pattern4 = r'\d{9}'
        assert re.search(pattern4, "555123456")


if __name__ == "__main__":
    pytest.main([__file__])
