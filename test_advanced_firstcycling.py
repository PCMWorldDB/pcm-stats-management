#!/usr/bin/env python3
"""
Test script to try advanced methods for FirstCycling.com access.
"""

import sys
import os

# Add src to path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.commons import make_request_with_proxy_rotation, try_alternative_access_methods, fetch_with_selenium

def test_advanced_firstcycling():
    """Test advanced methods for FirstCycling.com access"""
    
    # Test URL - Tour de France 2025 (race ID 18, year 2025)
    test_url = "https://firstcycling.com/race.php?r=18&y=2025&pcm=1"
    
    print("🧪 Testing advanced FirstCycling.com access methods...")
    print(f"URL: {test_url}")
    print("=" * 70)
    
    # Method 1: Enhanced commons function with new features
    print("\n🔄 Method 1: Enhanced commons function")
    print("-" * 50)
    content, success, error = make_request_with_proxy_rotation(
        url=test_url,
        timeout=30,
        verify=False,
        use_proxies=False,  # Start with direct connection
        use_session=True
    )
    
    if success:
        print(f"✅ Method 1 Success! Got {len(content)} bytes")
        return True
    else:
        print(f"❌ Method 1 Failed: {error}")
    
    # Method 2: Direct alternative methods
    print("\n🔄 Method 2: Alternative access methods")
    print("-" * 50)
    content, success, error = try_alternative_access_methods(
        url=test_url,
        timeout=30,
        verify=False
    )
    
    if success:
        print(f"✅ Method 2 Success! Got {len(content)} bytes")
        return True
    else:
        print(f"❌ Method 2 Failed: {error}")
    
    # Method 3: Try with proxies enabled
    print("\n🔄 Method 3: With proxy rotation")
    print("-" * 50)
    content, success, error = make_request_with_proxy_rotation(
        url=test_url,
        timeout=30,
        verify=False,
        use_proxies=True,  # Force proxy usage
        use_session=True,
        proxy_limit=3  # Limit to 3 proxies for faster testing
    )
    
    if success:
        print(f"✅ Method 3 Success! Got {len(content)} bytes")
        return True
    else:
        print(f"❌ Method 3 Failed: {error}")
    
    # Method 4: Try Selenium WebDriver
    print("\n🔄 Method 4: Selenium WebDriver")
    print("-" * 50)
    content, success, error = fetch_with_selenium(
        url=test_url,
        timeout=30,
        headless=True
    )
    
    if success:
        print(f"✅ Method 4 Success! Got {len(content)} bytes")
        return True
    else:
        print(f"❌ Method 4 Failed: {error}")
    
    return False

if __name__ == "__main__":
    success = test_advanced_firstcycling()
    
    if success:
        print("\n🎉 Successfully accessed FirstCycling.com!")
        sys.exit(0)
    else:
        print("\n❌ All methods failed. FirstCycling.com has very strong anti-bot protection.")
        print("💡 Consider:")
        print("   • Using a VPN")
        print("   • Accessing from a different network")
        print("   • Using paid proxy services")
        print("   • Running in GitHub Actions (different IP range)")
        sys.exit(1)
