#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import time
from datetime import datetime

def check_progress():
    """Check the progress of the scraper"""
    
    print("=== MyHome Scraper Progress Check ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if agents.csv exists
    if os.path.exists('agents.csv'):
        with open('agents.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            agents = list(reader)
        
        print(f"✅ Agents collected: {len(agents)}")
        
        if agents:
            print(f"📞 Sample agents:")
            for i, agent in enumerate(agents[:5]):
                print(f"   {i+1}. {agent.get('Name', 'Unknown')} - {agent.get('Phone', 'No phone')}")
            
            if len(agents) > 5:
                print(f"   ... and {len(agents) - 5} more")
        
        # Check for unique phone numbers
        phones = set()
        for agent in agents:
            phone = agent.get('Phone', '').strip()
            if phone:
                phones.add(phone)
        
        print(f"📱 Unique phone numbers: {len(phones)}")
        
    else:
        print("❌ No agents.csv file found yet")
    
    # Check log file for progress
    if os.path.exists('scraper.log'):
        with open('scraper.log', 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        if lines:
            print(f"\n📋 Recent log entries:")
            for line in lines[-10:]:  # Last 10 lines
                line = line.strip()
                if line and ('Added main agent' in line or 'Added sub-agent' in line or 'Scraping agents page' in line):
                    print(f"   {line}")
    
    print(f"\n🎯 Target: 7,000-10,000 phone numbers")
    print(f"📊 Progress: {len(agents) if 'agents' in locals() else 0} agents collected")

if __name__ == "__main__":
    check_progress()
