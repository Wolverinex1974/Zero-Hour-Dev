# =========================================================
# ZERO HOUR CORE: MOD XML SCRAPER - v20.8
# =========================================================
# ROLE: Metadata Extraction from ModInfo.xml (V1 & V2)
# STRATEGY: Full Vertical Source - No Semicolons - No Shorthand
# =========================================================
# PHASE 14: Industrial Intelligence
# FEATURE: Support for Legacy (A21-) and V2 (A22/V1.0+) XMLs.
# FEATURE: Author, Description, and Version extraction.
# FEATURE: User alerting for missing or legacy formatting.
# =========================================================
import os
import logging
import xml.etree.ElementTree as ET

# Initialize standard Paradoxal Logger
log = logging.getLogger("Paradoxal")

def scrape_mod_metadata(mod_directory):
    """
    Surgically extracts metadata from a mod's ModInfo.xml file.
    Identifies if the mod is Standard (V2), Legacy (V1), or Corrupt.
    """
    # Standard fallback values if extraction fails
    folder_name = os.path.basename(mod_directory)
    
    metadata = {
        "name": folder_name,
        "display_name": folder_name,
        "version": "1.0.0",
        "author": "Unknown Author",
        "description": "No description provided in ModInfo.xml",
        "xml_status": "MISSING"
    }

    # Step 1: Locate the XML file (Case-Insensitive Search)
    target_files = ["ModInfo.xml", "modinfo.xml", "MODINFO.XML"]
    xml_path = None

    for filename in target_files:
        temp_path = os.path.join(mod_directory, filename)
        
        if os.path.exists(temp_path):
            xml_path = temp_path
            break

    if not xml_path:
        log.warning(f"[SCRAPER] No ModInfo found for: {folder_name}")
        metadata["xml_status"] = "MISSING"
        return metadata

    # Step 2: Attempt to Parse XML
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Step 3: Determine Schema Version
        # V2 (A22/V1.0) usually has children named 'Version', 'DisplayName', etc.
        # with a 'value' attribute.
        # V1 (Legacy) has simple text nodes.

        is_v2 = False
        
        # Check for V2 Signature: any child having a 'value' attribute
        for child in root:
            if "value" in child.attrib:
                is_v2 = True
                break

        if is_v2:
            # --- V2 SCHEMA PROCESSING ---
            metadata["xml_status"] = "STANDARD"
            log.info(f"[SCRAPER] Detected V2 XML for: {folder_name}")
            
            for child in root:
                tag = child.tag.lower()
                val = child.attrib.get("value", "")
                
                if tag == "name":
                    metadata["name"] = val
                    
                if tag == "displayname":
                    metadata["display_name"] = val
                    
                if tag == "version":
                    metadata["version"] = val
                    
                if tag == "author":
                    metadata["author"] = val
                    
                if tag == "description":
                    metadata["description"] = val
        else:
            # --- V1 SCHEMA PROCESSING (Legacy) ---
            metadata["xml_status"] = "LEGACY"
            log.warning(f"[SCRAPER] Detected LEGACY XML for: {folder_name}")
            
            for child in root:
                tag = child.tag.lower()
                text = child.text if child.text else ""
                
                if tag == "name":
                    metadata["name"] = text
                    
                if tag == "displayname":
                    metadata["display_name"] = text
                    
                if tag == "version":
                    metadata["version"] = text
                    
                if tag == "author":
                    metadata["author"] = text
                    
                if tag == "description":
                    metadata["description"] = text

    except ET.ParseError as e:
        log.error(f"[SCRAPER] XML Syntax Error in {folder_name}: {str(e)}")
        metadata["xml_status"] = "CORRUPT"
        
    except Exception as e:
        log.error(f"[SCRAPER] Unexpected error scraping {folder_name}: {str(e)}")
        metadata["xml_status"] = "ERROR"

    # Step 4: Sanitize Output
    # Ensure no None types or empty strings leak into the manifest
    for key in metadata:
        if not metadata[key]:
            metadata[key] = f"Unknown {key}"
            
    return metadata

def check_mod_health(mod_directory):
    """
    A quick pulse-check used by the One-Click UI to color-code the 
    deployment list based on XML standards.
    """
    metadata = scrape_mod_metadata(mod_directory)
    
    if metadata["xml_status"] == "STANDARD":
        return "GREEN"
        
    if metadata["xml_status"] == "LEGACY":
        return "YELLOW"
        
    return "RED"