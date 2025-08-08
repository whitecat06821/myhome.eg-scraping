import logging
from selenium_handler import SeleniumHandler

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_myhome_agents():
    """Test if Selenium can load myhome.ge agents page"""
    handler = SeleniumHandler()
    
    try:
        logger.info("Starting Selenium...")
        success = handler.start_driver()
        
        if not success:
            logger.error("Failed to start Selenium driver")
            return False
            
        logger.info("Selenium started successfully!")
        
        # Test loading myhome.ge agents page
        logger.info("Loading myhome.ge agents page...")
        html = handler.get_page_with_phone("https://www.myhome.ge/maklers/")
        
        if html:
            logger.info(f"Successfully loaded page, HTML length: {len(html)}")
            
            # Check if we can find agent links
            if "maklers" in html and "group" in html:
                logger.info("Found agent-related content in HTML!")
                
                # Save HTML for inspection
                with open("myhome_agents_page.html", "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info("Saved HTML to myhome_agents_page.html")
                
                # Look for agent links
                import re
                agent_links = re.findall(r'href="/maklers/\d+/"', html)
                logger.info(f"Found {len(agent_links)} agent links in HTML")
                
                if agent_links:
                    logger.info("Sample agent links:")
                    for link in agent_links[:5]:
                        logger.info(f"  {link}")
                
                return True
            else:
                logger.warning("No agent content found in HTML")
                return False
        else:
            logger.error("Failed to load page")
            return False
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        return False
    finally:
        handler.close()

if __name__ == "__main__":
    test_myhome_agents()
