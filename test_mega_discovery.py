#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test of the mega discovery system
"""

import logging
from scrape_owners_mega import MegaOwnerScraper

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_discovery():
    """Test the mega discovery system with limited scope"""
    scraper = MegaOwnerScraper()
    
    print("🔍 MEGA DISCOVERY TEST")
    print("=" * 50)
    
    # Test 1: Discover agent IDs from first 3 pages
    print("\n1️⃣ Testing agent discovery (3 pages)...")
    agent_ids = scraper.discover_all_agent_ids(max_pages=3)
    print(f"✅ Found {len(agent_ids)} agents")
    print(f"Sample agents: {list(agent_ids)[:5]}")
    
    # Test 2: Get sub-agents for first 3 agents
    print(f"\n2️⃣ Testing sub-agent discovery (first 3 agents)...")
    total_brokers = 0
    for i, agent_id in enumerate(list(agent_ids)[:3], 1):
        sub_agents = scraper.get_agent_sub_agents(agent_id)
        total_brokers += len(sub_agents)
        print(f"  Agent {agent_id}: {len(sub_agents)} brokers")
    
    print(f"✅ Total brokers from 3 agents: {total_brokers}")
    
    # Test 3: Get property URLs from first broker
    if agent_ids:
        first_agent = list(agent_ids)[0]
        brokers = scraper.get_agent_sub_agents(first_agent)
        if brokers:
            first_broker = brokers[0]
            print(f"\n3️⃣ Testing property URL discovery (broker {first_broker}, 2 pages)...")
            property_urls = scraper.get_property_urls_from_broker(first_broker, max_pages=2)
            print(f"✅ Found {len(property_urls)} property URLs")
            print(f"Sample URLs: {list(property_urls)[:3]}")
    
    # Calculate potential
    agents_per_page = len(agent_ids) / 3 if agent_ids else 0
    estimated_total_agents = agents_per_page * 200  # Assume 200 pages total
    estimated_brokers = (total_brokers / 3) * estimated_total_agents if total_brokers > 0 else 0
    estimated_properties = len(property_urls) * estimated_brokers if 'property_urls' in locals() else 0
    
    print(f"\n📊 PROJECTION:")
    print(f"  • Agents per page: ~{agents_per_page:.1f}")
    print(f"  • Estimated total agents (200 pages): ~{estimated_total_agents:.0f}")
    print(f"  • Estimated total brokers: ~{estimated_brokers:.0f}")
    print(f"  • Estimated total properties: ~{estimated_properties:.0f}")
    
    print(f"\n🎯 CONCLUSION: This approach should find {estimated_properties:.0f}+ property URLs!")
    print("   Much more than the previous 2,000 limit!")

if __name__ == "__main__":
    test_discovery()
