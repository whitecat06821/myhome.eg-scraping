#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MEGA MONITOR - Track progress toward 16,000 unique phones
8,000 agents + 8,000 owners = 16,000 total
"""

import os
import time
import csv
import re
from datetime import datetime
from typing import Set

def normalize_phone(phone: str) -> str:
    """Normalize phone for deduplication"""
    if not phone:
        return ""
    
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 9 and digits.startswith('5'):
        return f"+995{digits}"
    elif len(digits) == 12 and digits.startswith('995'):
        return f"+{digits}"
    elif len(digits) >= 9:
        return f"+995{digits[-9:]}"
    
    return ""

def count_unique_phones_in_csv(filename: str) -> int:
    """Count unique normalized phones in CSV"""
    if not os.path.exists(filename):
        return 0
    
    unique_phones = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                phone = row.get('Phone', '').strip()
                if phone:
                    normalized = normalize_phone(phone)
                    if normalized:
                        unique_phones.add(normalized)
        return len(unique_phones)
    except Exception:
        return 0

def get_file_info(filename: str) -> dict:
    """Get file size and modification time"""
    try:
        if os.path.exists(filename):
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            mtime = os.path.getmtime(filename)
            age = time.time() - mtime
            return {'size_mb': size_mb, 'age': age, 'exists': True}
        return {'size_mb': 0, 'age': float('inf'), 'exists': False}
    except Exception:
        return {'size_mb': 0, 'age': float('inf'), 'exists': False}

def monitor_mega_progress():
    """Monitor all mega scrapers"""
    print("🚀 MEGA SCRAPER MONITOR - TARGET: 16,000 UNIQUE PHONES")
    print("=" * 80)
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"🚀 MEGA SCRAPER MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
        print("TARGET: 8,000 Agents + 8,000 Owners = 16,000 Total Unique Phones")
        print("=" * 80)
        
        # Agent files
        agent_files = [
            'agents.csv',
            'mega_agents.csv',
        ]
        
        # Owner files  
        owner_files = [
            'owners_direct.csv',
            'owners_api_mega.csv',
            'turbo_owners.csv',
        ]
        
        # Count unique agent phones
        all_agent_phones = set()
        print("\n📞 AGENT PHONES:")
        for filename in agent_files:
            count = count_unique_phones_in_csv(filename)
            info = get_file_info(filename)
            status = "🟢" if info['age'] < 60 else "🟡" if info['age'] < 300 else "🔴" if info['exists'] else "⚫"
            
            if count > 0:
                # Add to master set
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            phone = row.get('Phone', '').strip()
                            if phone:
                                normalized = normalize_phone(phone)
                                if normalized:
                                    all_agent_phones.add(normalized)
                except Exception:
                    pass
            
            print(f"  {status} {filename:<20} {count:>6} phones ({info['size_mb']:.1f} MB)")
        
        # Count unique owner phones
        all_owner_phones = set()
        print(f"\n📱 OWNER PHONES:")
        for filename in owner_files:
            count = count_unique_phones_in_csv(filename)
            info = get_file_info(filename)
            status = "🟢" if info['age'] < 60 else "🟡" if info['age'] < 300 else "🔴" if info['exists'] else "⚫"
            
            if count > 0:
                # Add to master set
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            phone = row.get('Phone', '').strip()
                            if phone:
                                normalized = normalize_phone(phone)
                                if normalized:
                                    all_owner_phones.add(normalized)
                except Exception:
                    pass
            
            print(f"  {status} {filename:<20} {count:>6} phones ({info['size_mb']:.1f} MB)")
        
        # Calculate totals with deduplication
        unique_agents = len(all_agent_phones)
        unique_owners = len(all_owner_phones)
        
        # Check for overlap between agents and owners
        overlap = len(all_agent_phones.intersection(all_owner_phones))
        total_unique = len(all_agent_phones.union(all_owner_phones))
        
        print(f"\n🎯 PROGRESS SUMMARY:")
        print(f"  Unique Agent Phones:  {unique_agents:>6} / 8,000  ({unique_agents/8000*100:>5.1f}%)")
        print(f"  Unique Owner Phones:  {unique_owners:>6} / 8,000  ({unique_owners/8000*100:>5.1f}%)")
        print(f"  Phone Overlap:        {overlap:>6}")
        print(f"  Total Unique Phones:  {total_unique:>6} / 16,000 ({total_unique/16000*100:>5.1f}%)")
        
        # Progress bars
        agent_bar = "█" * int(unique_agents/8000*50) + "░" * (50 - int(unique_agents/8000*50))
        owner_bar = "█" * int(unique_owners/8000*50) + "░" * (50 - int(unique_owners/8000*50))
        total_bar = "█" * int(total_unique/16000*50) + "░" * (50 - int(total_unique/16000*50))
        
        print(f"\n📊 PROGRESS BARS:")
        print(f"  Agents: [{agent_bar}] {unique_agents}/8,000")
        print(f"  Owners: [{owner_bar}] {unique_owners}/8,000") 
        print(f"  Total:  [{total_bar}] {total_unique}/16,000")
        
        # Check log activity
        log_files = [
            'mega_agent_scraper.log',
            'turbo_scraper.log', 
            'scraper_api_mega.log'
        ]
        
        print(f"\n📋 SCRAPER STATUS:")
        for log_file in log_files:
            info = get_file_info(log_file)
            status = "🟢 ACTIVE" if info['age'] < 60 else "🟡 SLOW" if info['age'] < 300 else "🔴 STOPPED" if info['exists'] else "⚫ NOT STARTED"
            print(f"  {log_file:<25} {status} ({info['size_mb']:.1f} MB, {info['age']:.0f}s ago)")
        
        # Success check
        if unique_agents >= 8000 and unique_owners >= 8000:
            print(f"\n🎉 SUCCESS! TARGET ACHIEVED!")
            print(f"   ✅ Agents: {unique_agents} >= 8,000")
            print(f"   ✅ Owners: {unique_owners} >= 8,000") 
            print(f"   🎯 Total: {total_unique} unique phones")
            break
        elif total_unique >= 16000:
            print(f"\n🎉 TOTAL TARGET ACHIEVED!")
            print(f"   🎯 Total: {total_unique} >= 16,000 unique phones")
            break
        
        print(f"\n⏳ Refreshing in 30 seconds... (Ctrl+C to stop)")
        time.sleep(30)

if __name__ == "__main__":
    try:
        monitor_mega_progress()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
