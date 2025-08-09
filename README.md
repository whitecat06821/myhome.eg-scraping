# 🚀 MyHome.ge MEGA Phone Scraper

**Professional-grade phone number scraping system for MyHome.ge**  
**Target: 16,000 unique phone numbers (8,000 agents + 8,000 owners)**

## 📊 Overview

This is a comprehensive scraping system designed to extract **16,000 unique phone numbers** from MyHome.ge:
- **8,000 unique agent phone numbers** from real estate agents and their sub-agents
- **8,000 unique owner phone numbers** from property listings
- **Zero duplicates** through advanced deduplication system
- **Excel-compatible format** with proper phone number formatting

## 🎯 Current Status

✅ **812 unique agent phones** already collected  
✅ **29 unique owner phones** already collected  
✅ **6,560+ properties** discovered by mega scraper  
🎯 **Target: 16,000 unique phones total**

## 📁 Project Structure

```
myhome/
├── README.md                    # This guide
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── scraper/                    # Core scraping modules
│   ├── __init__.py
│   ├── fetcher.py              # HTTP requests and API calls
│   ├── parser.py               # HTML/JSON parsing
│   └── selenium_handler.py     # Browser automation
│
├── mega_agent_scraper.py       # 🎯 Agent scraper (target: 8,000)
├── turbo_owner_scraper.py      # 🎯 Owner scraper (target: 8,000)
├── scrape_owners_api_mega.py   # Alternative owner scraper
├── master_deduplicator.py      # Deduplication system
├── mega_monitor.py             # Progress monitoring
│
├── excel_utils.py              # Excel formatting utilities
├── fix_excel_format.py         # Convert existing files
│
└── Output Files/
    ├── agents.csv              # Current agent phones
    ├── mega_agents.csv         # Mega agent output
    ├── turbo_owners.csv        # Turbo owner output
    ├── master_phones_unique.csv # Final deduplicated output
    └── *.xlsx                  # Excel-formatted files
```

## 🚀 Quick Start Guide

### 1. Prerequisites

**Python Version:** 3.9 or higher

**Install Dependencies:**
```bash
pip install -r requirements.txt
```

**Required Packages:**
- requests>=2.31.0
- beautifulsoup4>=4.12.0
- selenium>=4.15.0
- pandas>=2.1.0
- openpyxl>=3.1.5
- webdriver-manager>=4.0.0

### 2. Single Command to Get 16,000 Phones

**Option A: Run Individual Scrapers (Recommended)**
```bash
# Terminal 1: Agent scraper (target: 8,000)
python mega_agent_scraper.py

# Terminal 2: Owner scraper (target: 8,000) 
python turbo_owner_scraper.py

# Terminal 3: Monitor progress
python mega_monitor.py
```

**Option B: Alternative Owner Scraper**
```bash
# If turbo scraper has issues, use this instead:
python scrape_owners_api_mega.py
```

### 3. Final Deduplication and Export

```bash
# After scrapers finish, deduplicate and create final files
python master_deduplicator.py

# Fix Excel formatting for client delivery
python fix_excel_format.py
```

## 📋 Detailed Instructions

### Phase 1: Agent Phone Collection (Target: 8,000)

**Start the mega agent scraper:**
```bash
python mega_agent_scraper.py
```

**What it does:**
- Discovers all agent IDs from API (500+ pages)
- For each agent, gets main agent + all sub-agents
- Extracts phone numbers from agent data
- Saves progress every 200 phones to `mega_agents.csv`
- Automatic deduplication prevents duplicates
- Stops at 8,000 unique agent phones

**Expected output:**
- File: `mega_agents.csv`
- Format: `+995 571 233 844` (Excel-compatible)
- Timeline: 2-4 hours for 8,000 phones

### Phase 2: Owner Phone Collection (Target: 8,000)

**Start the turbo owner scraper:**
```bash
python turbo_owner_scraper.py
```

**What it does:**
- Gets 20,000+ property URLs from multiple API endpoints
- Scrapes each property page for phone numbers
- Uses multiple extraction methods (JSON, HTML, regex)
- Saves progress every 100 phones to `turbo_owners.csv`
- Automatic deduplication prevents duplicates
- Stops at 8,000 unique owner phones

**Expected output:**
- File: `turbo_owners.csv`
- Format: `+995 571 233 844` (Excel-compatible)
- Timeline: 4-6 hours for 8,000 phones

### Phase 3: Monitoring Progress

**Start the monitor:**
```bash
python mega_monitor.py
```

**What you'll see:**
```
🚀 MEGA SCRAPER MONITOR - TARGET: 16,000 UNIQUE PHONES
================================================================================

📞 AGENT PHONES:
  🟢 agents.csv              812 phones (0.0 MB)
  🟢 mega_agents.csv        2543 phones (0.1 MB)

📱 OWNER PHONES:
  🟢 turbo_owners.csv       1876 phones (0.1 MB)

🎯 PROGRESS SUMMARY:
  Unique Agent Phones:    3355 / 8,000  ( 41.9%)
  Unique Owner Phones:    1876 / 8,000  ( 23.5%)
  Total Unique Phones:    5231 / 16,000 ( 32.7%)
```

### Phase 4: Final Processing

**1. Deduplicate all sources:**
```bash
python master_deduplicator.py
```

**2. Create Excel files:**
```bash
python fix_excel_format.py
```

**Final output files:**
- `master_phones_unique.csv` - All unique phones with source tracking
- `master_phones_only.csv` - Phone numbers only (client format)
- `master_phones_only.xlsx` - Excel file with perfect formatting

## ⚙️ Configuration Options

### Adjusting Targets

**Edit mega_agent_scraper.py:**
```python
self.target_phones = 8000  # Change agent target
```

**Edit turbo_owner_scraper.py:**
```python
self.target_phones = 8000  # Change owner target
```

### Rate Limiting

**Slow down requests (if getting blocked):**
```python
time.sleep(1.0)  # Increase from 0.5 to 1.0 seconds
```

**Speed up requests (if working well):**
```python
time.sleep(0.2)  # Decrease to 0.2 seconds
```

### File Paths

All output files are saved in the project root. To change:
```python
filename = 'custom_path/mega_agents.csv'
```

## 🔧 Troubleshooting

### Common Issues

**1. "Module not found" errors:**
```bash
pip install -r requirements.txt
```

**2. Chrome driver issues:**
- The system auto-downloads ChromeDriver
- If fails, download manually from https://chromedriver.chromium.org/

**3. API rate limiting (403 errors):**
- Increase `time.sleep()` values in scrapers
- Check internet connection
- Wait 10-15 minutes and retry

**4. No phones found:**
- Check log files: `mega_agent_scraper.log`, `turbo_scraper.log`
- Verify internet connection
- Check if website structure changed

**5. Duplicate phones:**
- Run `master_deduplicator.py` to clean all files
- Check `master_phones_unique.csv` for final deduplicated list

### Log Files

**Monitor scraper activity:**
- `mega_agent_scraper.log` - Agent scraper progress
- `turbo_scraper.log` - Owner scraper progress  
- `scraper_api_mega.log` - API mega scraper (if running)

**Check latest activity:**
```bash
# Windows
type mega_agent_scraper.log | findstr "INFO" | more

# Linux/Mac
tail -f mega_agent_scraper.log | grep "INFO"
```

## 📊 Performance Expectations

### Typical Performance

**Agent Scraper:**
- Speed: ~50-100 phones/hour
- Total time: 2-4 hours for 8,000 phones
- Success rate: ~85% (depends on API response quality)

**Owner Scraper:**
- Speed: ~100-200 phones/hour  
- Total time: 4-6 hours for 8,000 phones
- Success rate: ~15-20% (depends on properties having phones)

**Combined System:**
- Total time: 6-8 hours for 16,000 unique phones
- Memory usage: <500MB
- CPU usage: Low (network-bound)

### Optimization Tips

**1. Run multiple scrapers in parallel:**
```bash
# Terminal 1
python mega_agent_scraper.py

# Terminal 2  
python turbo_owner_scraper.py

# Terminal 3
python scrape_owners_api_mega.py  # Additional owner scraper
```

**2. Adjust rate limiting based on performance:**
- If getting errors: Increase delays
- If working smoothly: Decrease delays

**3. Monitor system resources:**
- Watch RAM usage (should stay under 1GB)
- Check network activity (should be consistent)

## 🎯 Quality Assurance

### Phone Number Format

**Input formats handled:**
- `995571233844` (raw Georgian)
- `571233844` (mobile without country code)
- `+995 571 233 844` (formatted)
- `+995-571-233-844` (hyphenated)

**Output format (all files):**
```
+995 571 233 844
```

### Deduplication Logic

**Normalization process:**
1. Remove all non-digits
2. Add +995 prefix if missing
3. Standardize to 13-digit format
4. Store in set for uniqueness

**Example:**
```
Input:  571233844, +995571233844, 995-571-233-844
Output: +995 571 233 844 (single entry)
```

### Excel Compatibility

**Formatting features:**
- Numbers stored as text (prevents scientific notation)
- Spaces added for readability
- Compatible with Excel 2016+
- No leading apostrophes in final files

## 📞 Support

### If You Need Help

**1. Check log files first:**
```bash
# Look for ERROR messages
type mega_agent_scraper.log | findstr "ERROR"
type turbo_scraper.log | findstr "ERROR"
```

**2. Verify current progress:**
```bash
python master_deduplicator.py
```

**3. Test individual components:**
```bash
# Test API connectivity
python -c "from scraper.fetcher import MyHomeFetcher; print('API working:', MyHomeFetcher().fetch_agents_api(1) is not None)"

# Test deduplication
python -c "from master_deduplicator import MasterDeduplicator; d = MasterDeduplicator(); print('Deduplicator ready')"
```

### System Requirements

**Minimum:**
- Python 3.9+
- 4GB RAM
- 1GB free disk space
- Stable internet connection (10+ Mbps recommended)

**Recommended:**
- Python 3.11+
- 8GB RAM
- SSD storage
- High-speed internet (50+ Mbps)

## 🏁 Success Criteria

**Project completed successfully when:**
- ✅ `master_phones_unique.csv` contains 16,000+ unique phones
- ✅ `master_phones_only.xlsx` properly formatted for Excel
- ✅ Agent phones: 8,000+ unique
- ✅ Owner phones: 8,000+ unique  
- ✅ Zero duplicate phone numbers
- ✅ All phones in format: `+995 571 233 844`

**Delivery files:**
1. `master_phones_only.xlsx` - Final Excel file for client
2. `master_phones_unique.csv` - Backup with source tracking
3. `agents.csv` + `mega_agents.csv` - Agent phone sources
4. `turbo_owners.csv` - Owner phone sources

---

## 🚀 Ready to Start?

**Run these commands in order:**

```bash
# 1. Start agent scraper (Terminal 1)
python mega_agent_scraper.py

# 2. Start owner scraper (Terminal 2)  
python turbo_owner_scraper.py

# 3. Monitor progress (Terminal 3)
python mega_monitor.py

# 4. When both reach targets, finalize:
python master_deduplicator.py
python fix_excel_format.py
```

**🎯 Target: 16,000 unique phone numbers achieved in 6-8 hours!**