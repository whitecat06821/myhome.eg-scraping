#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor progress of all running scrapers
"""

import os
import time
import glob
from datetime import datetime

def count_csv_lines(filename):
    """Count lines in CSV file (excluding header)"""
    try:
        if not os.path.exists(filename):
            return 0
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return max(0, len(lines) - 1)  # Exclude header
    except Exception:
        return 0

def get_file_size(filename):
    """Get file size in MB"""
    try:
        if os.path.exists(filename):
            size_bytes = os.path.getsize(filename)
            return size_bytes / (1024 * 1024)
        return 0
    except Exception:
        return 0

def monitor_scrapers():
    """Monitor all scrapers and show progress"""
    print("🔍 SCRAPER PROGRESS MONITOR")
    print("=" * 60)
    
    # CSV files to monitor
    csv_files = [
        'agents.csv',
        'owners.csv', 
        'owners_direct.csv',
        'owners_mega.csv',
        'owners_api_mega.csv'
    ]
    
    # Log files to check
    log_files = [
        'scraper.log',
        'scraper_mega.log',
        'scraper_api_mega.log'
    ]
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"🔍 SCRAPER PROGRESS MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        # Check CSV files
        print("\n📊 CSV FILES:")
        total_phones = 0
        for csv_file in csv_files:
            count = count_csv_lines(csv_file)
            size_mb = get_file_size(csv_file)
            status = "✅" if count > 0 else "⏳"
            print(f"  {status} {csv_file:<20} {count:>6} phones ({size_mb:.1f} MB)")
            total_phones += count
        
        print(f"\n🎯 TOTAL PHONES COLLECTED: {total_phones}")
        
        # Target progress
        agent_target = 700
        owner_target = 700
        
        agents_count = count_csv_lines('agents.csv')
        owners_count = max(
            count_csv_lines('owners.csv'),
            count_csv_lines('owners_direct.csv'),
            count_csv_lines('owners_mega.csv'),
            count_csv_lines('owners_api_mega.csv')
        )
        
        print(f"\n📈 TARGET PROGRESS:")
        print(f"  Agents: {agents_count}/{agent_target} ({agents_count/agent_target*100:.1f}%)")
        print(f"  Owners: {owners_count}/{owner_target} ({owners_count/owner_target*100:.1f}%)")
        
        # Check log files for recent activity
        print("\n📋 LOG FILES:")
        for log_file in log_files:
            if os.path.exists(log_file):
                size_mb = get_file_size(log_file)
                mtime = os.path.getmtime(log_file)
                age = time.time() - mtime
                status = "🟢" if age < 60 else "🟡" if age < 300 else "🔴"
                print(f"  {status} {log_file:<20} {size_mb:.1f} MB (updated {age:.0f}s ago)")
        
        # Check if targets are reached
        if agents_count >= agent_target and owners_count >= owner_target:
            print(f"\n🎉 SUCCESS! Both targets reached!")
            print(f"   Agents: {agents_count} ✅")
            print(f"   Owners: {owners_count} ✅")
            break
        
        print(f"\n⏳ Refreshing in 30 seconds... (Ctrl+C to stop)")
        time.sleep(30)

if __name__ == "__main__":
    try:
        monitor_scrapers()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
