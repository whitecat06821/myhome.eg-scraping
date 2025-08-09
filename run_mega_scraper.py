#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 MEGA SCRAPER LAUNCHER
One-click script to start all scrapers for 16,000 unique phones
"""

import subprocess
import time
import os
import sys
from datetime import datetime

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🚀 MYHOME.GE MEGA PHONE SCRAPER")
    print("=" * 80)
    print("TARGET: 16,000 UNIQUE PHONE NUMBERS")
    print("  • 8,000 Agent Phones")
    print("  • 8,000 Owner Phones") 
    print("  • Zero Duplicates")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def check_dependencies():
    """Check if required packages are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'requests', 'beautifulsoup4', 'selenium', 
        'pandas', 'openpyxl', 'webdriver_manager'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies ready!")
    return True

def get_user_choice():
    """Get user's choice for scraping mode"""
    print("\n🎯 SCRAPING OPTIONS:")
    print("1. 🚀 FULL MEGA MODE (16,000 phones - agents + owners)")
    print("2. 👥 AGENTS ONLY (8,000 agent phones)")
    print("3. 🏠 OWNERS ONLY (8,000 owner phones)")
    print("4. 📊 MONITOR ONLY (track existing progress)")
    print("5. 🔧 DEDUPLICATE ONLY (process existing files)")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        if choice in ['1', '2', '3', '4', '5']:
            return int(choice)
        print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

def start_process(script_name, description):
    """Start a Python script in background"""
    try:
        print(f"🚀 Starting {description}...")
        
        # For Windows
        if os.name == 'nt':
            process = subprocess.Popen(
                [sys.executable, script_name],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            # For Linux/Mac
            process = subprocess.Popen([sys.executable, script_name])
        
        print(f"✅ {description} started (PID: {process.pid})")
        return process
    
    except Exception as e:
        print(f"❌ Failed to start {description}: {e}")
        return None

def show_progress_info():
    """Show information about monitoring progress"""
    print("\n📊 MONITORING PROGRESS:")
    print("  • Monitor files: mega_monitor.py")
    print("  • Log files: *.log")
    print("  • Output files: *.csv")
    print("  • Progress updates every 30 seconds")
    
def main():
    """Main launcher function"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return
    
    # Get user choice
    choice = get_user_choice()
    
    processes = []
    
    if choice == 1:  # Full mega mode
        print("\n🚀 LAUNCHING FULL MEGA MODE...")
        
        # Start agent scraper
        agent_process = start_process("mega_agent_scraper.py", "Mega Agent Scraper")
        if agent_process:
            processes.append(("Agent Scraper", agent_process))
        
        time.sleep(2)
        
        # Start owner scraper
        owner_process = start_process("turbo_owner_scraper.py", "Turbo Owner Scraper")
        if owner_process:
            processes.append(("Owner Scraper", owner_process))
        
        time.sleep(2)
        
        # Start monitor
        print("🔍 Starting progress monitor...")
        monitor_process = start_process("mega_monitor.py", "Progress Monitor")
        if monitor_process:
            processes.append(("Monitor", monitor_process))
    
    elif choice == 2:  # Agents only
        print("\n👥 LAUNCHING AGENT SCRAPER...")
        agent_process = start_process("mega_agent_scraper.py", "Mega Agent Scraper")
        if agent_process:
            processes.append(("Agent Scraper", agent_process))
    
    elif choice == 3:  # Owners only
        print("\n🏠 LAUNCHING OWNER SCRAPER...")
        owner_process = start_process("turbo_owner_scraper.py", "Turbo Owner Scraper")
        if owner_process:
            processes.append(("Owner Scraper", owner_process))
    
    elif choice == 4:  # Monitor only
        print("\n📊 LAUNCHING MONITOR...")
        monitor_process = start_process("mega_monitor.py", "Progress Monitor")
        if monitor_process:
            processes.append(("Monitor", monitor_process))
    
    elif choice == 5:  # Deduplicate only
        print("\n🔧 RUNNING DEDUPLICATION...")
        try:
            print("Running master deduplicator...")
            subprocess.run([sys.executable, "master_deduplicator.py"], check=True)
            print("Running Excel formatter...")
            subprocess.run([sys.executable, "fix_excel_format.py"], check=True)
            print("✅ Deduplication complete!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Deduplication failed: {e}")
        input("\nPress Enter to exit...")
        return
    
    # Show process information
    if processes:
        print(f"\n✅ LAUNCHED {len(processes)} PROCESSES:")
        for name, process in processes:
            print(f"  • {name} (PID: {process.pid})")
        
        show_progress_info()
        
        print("\n" + "=" * 80)
        print("🎯 SCRAPING IN PROGRESS...")
        print("=" * 80)
        print("📋 What's happening:")
        
        if choice == 1:
            print("  1. Agent scraper collecting 8,000 agent phones")
            print("  2. Owner scraper collecting 8,000 owner phones") 
            print("  3. Monitor showing real-time progress")
            print("  4. Auto-deduplication preventing duplicates")
            print("\n⏱️  Expected completion: 6-8 hours")
            print("📊 Monitor will show when targets are reached")
        
        elif choice == 2:
            print("  • Collecting 8,000 unique agent phone numbers")
            print("  • Progress saved to mega_agents.csv")
            print("\n⏱️  Expected completion: 2-4 hours")
        
        elif choice == 3:
            print("  • Collecting 8,000 unique owner phone numbers")
            print("  • Progress saved to turbo_owners.csv")
            print("\n⏱️  Expected completion: 4-6 hours")
        
        print("\n💡 TIPS:")
        print("  • Check *.log files for detailed progress")
        print("  • Run 'python master_deduplicator.py' when done")
        print("  • Final files will be in Excel-compatible format")
        print("  • Press Ctrl+C to stop monitoring (scrapers continue)")
        
        print("\n" + "=" * 80)
        print("🚀 MEGA SCRAPER RUNNING - TARGETING 16,000 UNIQUE PHONES!")
        print("=" * 80)
    
    input("\nPress Enter to exit launcher (scrapers continue running)...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Launcher stopped. Scrapers continue running in background.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("Press Enter to exit...")
