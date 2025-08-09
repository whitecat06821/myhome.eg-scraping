#!/usr/bin/env python3
"""
Run both agents and owners scrapers simultaneously
"""

import threading
import subprocess
import sys
import time

def run_agents_scraper():
    """Run the agents scraper"""
    print("🚀 Starting Agents Scraper...")
    try:
        result = subprocess.run([sys.executable, "scrape_agents.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ Agents scraper completed successfully")
            print(result.stdout)
        else:
            print("❌ Agents scraper failed")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running agents scraper: {e}")

def run_owners_scraper():
    """Run the owners scraper"""
    print("🚀 Starting Owners Scraper...")
    try:
        result = subprocess.run([sys.executable, "scrape_owners_direct.py"], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("✅ Owners scraper completed successfully")
            print(result.stdout)
        else:
            print("❌ Owners scraper failed")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error running owners scraper: {e}")

def main():
    """Main function to run both scrapers"""
    print("🏠 MyHome.ge Phone Numbers Scraper")
    print("=" * 50)
    print("Running agents and owners scrapers simultaneously...")
    
    # Create threads for both scrapers
    agents_thread = threading.Thread(target=run_agents_scraper, name="AgentsThread")
    owners_thread = threading.Thread(target=run_owners_scraper, name="OwnersThread")
    
    # Start both threads
    start_time = time.time()
    agents_thread.start()
    owners_thread.start()
    
    # Wait for both to complete
    agents_thread.join()
    owners_thread.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n✅ Both scrapers completed in {total_time:.2f} seconds")
    print("📄 Check agents.csv and owners_direct.csv for results")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
