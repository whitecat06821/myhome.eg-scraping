#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Phone Number Deduplicator
Combines all sources and removes duplicates for final output
"""

import csv
import re
import os
from typing import Set, List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MasterDeduplicator:
    """Combines all phone sources and creates deduplicated master lists"""
    
    def __init__(self):
        self.unique_phones = set()
        self.phone_sources = {}  # Track which source each phone came from
        
    def normalize_phone(self, phone: str) -> str:
        """Normalize phone number format for deduplication"""
        if not phone:
            return ""
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Handle Georgian format
        if len(digits) == 9 and digits.startswith('5'):
            # 511234567 -> +995511234567
            return f"+995{digits}"
        elif len(digits) == 12 and digits.startswith('995'):
            # 995511234567 -> +995511234567
            return f"+{digits}"
        elif len(digits) >= 9:
            # Take last 9 digits and add +995
            return f"+995{digits[-9:]}"
        
        return phone  # Return as-is if can't normalize
    
    def add_phones_from_csv(self, filename: str, source_name: str) -> int:
        """Add phones from a CSV file"""
        added_count = 0
        
        if not os.path.exists(filename):
            logger.warning(f"File not found: {filename}")
            return 0
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    phone = row.get('Phone', '').strip()
                    if phone:
                        normalized = self.normalize_phone(phone)
                        if normalized and normalized not in self.unique_phones:
                            self.unique_phones.add(normalized)
                            self.phone_sources[normalized] = source_name
                            added_count += 1
                        
            logger.info(f"Added {added_count} unique phones from {filename} ({source_name})")
            return added_count
            
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            return 0
    
    def format_phone_for_excel(self, phone: str) -> str:
        """Format phone for Excel display: +995 571 233 844"""
        # Remove + and spaces
        digits = re.sub(r'[^\d]', '', phone)
        
        if len(digits) >= 12 and digits.startswith('995'):
            # +995 571 233 844
            return f"+995 {digits[3:6]} {digits[6:9]} {digits[9:12]}"
        elif len(digits) >= 9:
            # Assume it's Georgian mobile
            return f"+995 {digits[-9:-6]} {digits[-6:-3]} {digits[-3:]}"
        
        return phone
    
    def export_master_csv(self, filename: str = 'master_phones_unique.csv'):
        """Export all unique phones to master CSV"""
        try:
            sorted_phones = sorted(self.unique_phones)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Phone', 'Source'])
                
                for phone in sorted_phones:
                    formatted_phone = self.format_phone_for_excel(phone)
                    source = self.phone_sources.get(phone, 'Unknown')
                    writer.writerow([formatted_phone, source])
            
            logger.info(f"✅ Exported {len(sorted_phones)} unique phones to {filename}")
            return len(sorted_phones)
            
        except Exception as e:
            logger.error(f"Error exporting master CSV: {e}")
            return 0
    
    def export_phone_only_csv(self, filename: str = 'master_phones_only.csv'):
        """Export only phone numbers (client format)"""
        try:
            sorted_phones = sorted(self.unique_phones)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Phone'])
                
                for phone in sorted_phones:
                    formatted_phone = self.format_phone_for_excel(phone)
                    writer.writerow([formatted_phone])
            
            logger.info(f"✅ Exported {len(sorted_phones)} unique phones to {filename}")
            return len(sorted_phones)
            
        except Exception as e:
            logger.error(f"Error exporting phone-only CSV: {e}")
            return 0
    
    def get_stats(self) -> Dict:
        """Get statistics about collected phones"""
        return {
            'total_unique': len(self.unique_phones),
            'sources': len(set(self.phone_sources.values())),
            'source_breakdown': {}
        }

def main():
    """Main deduplication process"""
    print("🔧 MASTER PHONE DEDUPLICATOR")
    print("=" * 50)
    
    deduplicator = MasterDeduplicator()
    
    # All possible CSV sources
    csv_sources = [
        ('agents.csv', 'Agents'),
        ('owners.csv', 'Owners'),
        ('owners_direct.csv', 'Owners Direct'),
        ('owners_mega.csv', 'Owners Mega'),
        ('owners_api_mega.csv', 'Owners API Mega'),
        ('agents_fixed.csv', 'Agents Fixed'),
        ('owners_fixed.csv', 'Owners Fixed'),
    ]
    
    total_added = 0
    
    print("\n📥 PROCESSING SOURCE FILES:")
    for filename, source_name in csv_sources:
        added = deduplicator.add_phones_from_csv(filename, source_name)
        total_added += added
        if added > 0:
            print(f"  ✅ {filename}: {added} unique phones")
        else:
            print(f"  ⏹️  {filename}: not found or no new phones")
    
    total_unique = len(deduplicator.unique_phones)
    
    print(f"\n📊 DEDUPLICATION RESULTS:")
    print(f"  Total unique phones: {total_unique}")
    print(f"  Total files processed: {len([f for f, s in csv_sources if os.path.exists(f)])}")
    
    if total_unique > 0:
        print(f"\n💾 EXPORTING MASTER FILES:")
        master_count = deduplicator.export_master_csv()
        phone_only_count = deduplicator.export_phone_only_csv()
        
        print(f"  ✅ master_phones_unique.csv: {master_count} phones with sources")
        print(f"  ✅ master_phones_only.csv: {phone_only_count} phones (client format)")
        
        # Target assessment
        target = 8000
        print(f"\n🎯 TARGET ASSESSMENT:")
        print(f"  Current unique phones: {total_unique}")
        print(f"  Target: {target}")
        print(f"  Progress: {total_unique/target*100:.1f}%")
        
        if total_unique >= target:
            print(f"  🎉 TARGET ACHIEVED! We have {total_unique} unique phones!")
        else:
            needed = target - total_unique
            print(f"  ⏳ Need {needed} more unique phones to reach target")
    else:
        print("  ❌ No phones found to deduplicate")

if __name__ == "__main__":
    main()
