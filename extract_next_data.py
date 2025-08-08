import json
import re

def extract_next_data():
    """Extract and analyze __NEXT_DATA__ from the HTML file"""
    
    # Read the HTML file
    with open("myhome_agents_page.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    
    # Find the __NEXT_DATA__ script tag
    pattern = r'<script id="__NEXT_DATA__" type="application/json" crossorigin="">(.*?)</script>'
    match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        json_data = match.group(1)
        try:
            data = json.loads(json_data)
            print("Successfully extracted __NEXT_DATA__")
            
            # Save the JSON data for inspection
            with open("next_data.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Saved next_data.json")
            
            # Look for agent-related data
            def search_for_agents(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        if "agent" in key.lower() or "makler" in key.lower():
                            print(f"Found potential agent data at {current_path}: {value}")
                        elif isinstance(value, (dict, list)):
                            search_for_agents(value, current_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        current_path = f"{path}[{i}]"
                        if isinstance(item, (dict, list)):
                            search_for_agents(item, current_path)
            
            search_for_agents(data)
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("__NEXT_DATA__ not found in HTML")
        return None

if __name__ == "__main__":
    extract_next_data()
