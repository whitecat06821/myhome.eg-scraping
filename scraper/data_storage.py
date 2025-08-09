import csv
import logging
from typing import List, Dict
import pandas as pd

logger = logging.getLogger(__name__)


class DataStorage:
    """Handles data storage and CSV export."""
    
    def __init__(self):
        """Initialize data storage."""
        self.agents_data = []
        self.owners_data = []
        self.owner_phones = set()
    
    def add_agent(self, agent_data: Dict[str, str]):
        """Add agent data to storage."""
        if agent_data and self._validate_agent_data(agent_data):
            self.agents_data.append(agent_data)
            logger.debug(f"Added agent: {agent_data.get('name', 'Unknown')}")
    
    def add_owner(self, owner_data: Dict[str, str]):
        """Add owner data to storage."""
        if owner_data and self._validate_owner_data(owner_data):
            self.owners_data.append(owner_data)
            logger.debug(f"Added owner: {owner_data.get('name', 'Unknown')}")
    
    def add_owner_phone(self, phone: str):
        """Add owner phone number (phone only, no name/URL needed)"""
        try:
            if phone and phone not in self.owner_phones:
                self.owner_phones.add(phone)
                self.owners_data.append({
                    'name': 'Property Owner',
                    'phone': phone,
                    'url': ''
                })
                logger.info(f"Added owner phone: {phone}")
            else:
                logger.debug(f"Phone number already exists or invalid: {phone}")
        except Exception as e:
            logger.error(f"Error adding owner phone {phone}: {e}")

    def get_owner_phones_count(self) -> int:
        """Get count of unique owner phone numbers"""
        return len(self.owner_phones)
    
    def export_to_csv(self, agents_file: str = "agents.csv", owners_file: str = "owners.csv"):
        """Export data to CSV files with only Phone column."""
        try:
            # Export agents data (only phone numbers)
            if self.agents_data:
                self._write_csv_phone_only(agents_file, self.agents_data)
                logger.info(f"Exported {len(self.agents_data)} agents to {agents_file}")
            else:
                logger.warning("No agent data to export")
            
            # Export owners data (only phone numbers)
            if self.owners_data:
                self._write_csv_phone_only(owners_file, self.owners_data)
                logger.info(f"Exported {len(self.owners_data)} owners to {owners_file}")
            else:
                logger.warning("No owner data to export")
                
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
    
    def _write_csv_phone_only(self, filename: str, data: List[Dict]):
        """Write data to CSV file with only Phone column."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Phone'])  # Header
            
            # Write only phone numbers
            for item in data:
                phone = item.get('phone', '')
                if phone:
                    writer.writerow([phone])
    
    def _write_csv(self, filename: str, data: List[Dict], fieldnames: List[str]):
        """Write data to CSV file."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Convert data to match fieldnames
            for item in data:
                row = {}
                for field in fieldnames:
                    if field.lower() == 'name':
                        row[field] = item.get('name', '')
                    elif field.lower() == 'phone':
                        row[field] = item.get('phone', '')
                    elif field.lower() == 'url':
                        row[field] = item.get('url', '')
                writer.writerow(row)
    
    def _validate_agent_data(self, data: Dict[str, str]) -> bool:
        """Validate agent data."""
        required_fields = ['name', 'phone', 'url']
        return all(field in data and data[field] for field in required_fields)
    
    def _validate_owner_data(self, data: Dict[str, str]) -> bool:
        """Validate owner data."""
        required_fields = ['name', 'phone', 'url']
        return all(field in data and data[field] for field in required_fields)
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about collected data."""
        return {
            'agents_count': len(self.agents_data),
            'owners_count': len(self.owners_data),
            'total_records': len(self.agents_data) + len(self.owners_data)
        }
