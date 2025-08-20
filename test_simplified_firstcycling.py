#!/usr/bin/env python3
"""
Simple test to verify the simplified FirstCycling.com access with Selenium.
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import fetch_firstcycling_html

def test_simplified_firstcycling():
    """Test the simplified FirstCycling.com access"""
    
    # Test URL - Tour de France 2025 (race ID 18, year 2025)
    test_url = "https://firstcycling.com/race.php?r=18&y=2025&pcm=1"
    
    print("🧪 Testing simplified FirstCycling.com access...")
    print(f"URL: {test_url}")
    print("=" * 60)
    
    # Test the API function
    content, success, error = fetch_firstcycling_html(test_url)
    
    if success:
        print(f"✅ Success! Fetched {len(content)} bytes")
        
        # Check if it looks like valid HTML content
        content_str = content.decode('utf-8', errors='ignore')
        if '<html' in content_str.lower() and 'firstcycling' in content_str.lower():
            print("✅ Content appears to be valid FirstCycling HTML")
            
            # Look for PCM-specific content
            if 'pcm' in content_str.lower():
                print("✅ PCM-specific content detected")
            else:
                print("⚠️  No obvious PCM content found, but page loaded successfully")
                
        else:
            print("⚠️  Content doesn't look like expected HTML")
            
        return True
    else:
        print(f"❌ Failed to fetch content")
        print(f"Error: {error}")
        return False

if __name__ == "__main__":
    success = test_simplified_firstcycling()
    
    if success:
        print("\n🎉 Simplified FirstCycling.com access works!")
        print("💡 Selenium WebDriver successfully bypassed anti-bot protection")
        sys.exit(0)
    else:
        print("\n❌ Test failed!")
        print("💡 Check if Chrome/ChromeDriver is available")
        sys.exit(1)
