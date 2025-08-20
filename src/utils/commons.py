import os
import requests
import urllib3
import time
import random

STAT_KEYS = ['fla', 'mo', 'mm', 'dh', 'cob', 'tt', 'prl', 'spr', 'acc', 'end', 'res', 'rec', 'hil', 'att']
DATA_PATH = os.path.join('data')
MODEL_DIR_PATH = os.path.join('src', 'model')

PATH_TYPES = ['root', 'changes_dir', 'stats_file', 'tracking_db', 'cdb']

def get_proxy_list(limit=10, timeout=10):
    """
    Fetch a list of free HTTP proxies from proxyscrape.com API.
    
    Args:
        limit (int): Maximum number of proxies to fetch (default: 10)
        timeout (int): Request timeout in seconds (default: 10)
        
    Returns:
        list: List of proxy dictionaries with 'host' and 'port' keys
    """
    try:
        import requests
        
        print(f"🔄 Fetching proxy list from proxyscrape.com API (limit: {limit})...")
        proxy_api_url = f"https://api.proxyscrape.com/v4/free-proxy-list/get?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all&skip=0&limit={limit}"
        
        # Simple request to get proxy list
        proxy_response = requests.get(proxy_api_url, timeout=timeout)
        proxy_response.raise_for_status()
        
        # Parse proxy list (should be one proxy per line in "host:port" format)
        proxy_text = proxy_response.text.strip()
        proxy_list = []
        
        if proxy_text:
            proxy_lines = [line.strip() for line in proxy_text.split('\n') if line.strip()]
            
            for line in proxy_lines:
                if ':' in line:
                    try:
                        host, port = line.split(':', 1)
                        proxy_list.append({
                            'host': host.strip(),
                            'port': int(port.strip())
                        })
                    except (ValueError, IndexError):
                        continue  # Skip invalid proxy entries
            
            print(f"   - Successfully parsed {len(proxy_list)} valid proxies")
        else:
            print("   - No proxies returned from API")
            
        return proxy_list
        
    except Exception as e:
        print(f"⚠️  Could not fetch proxies: {e}")
        return []

def make_request_with_proxy_rotation(url, headers=None, timeout=30, verify=True, proxy_limit=10, 
                                   retry_delays=None, enable_ssl_warnings=False, use_proxies=None, 
                                   use_session=True, **kwargs):
    """
    Make an HTTP request with automatic proxy rotation and retry logic.
    
    Args:
        url (str): URL to request
        headers (dict, optional): HTTP headers to send
        timeout (int): Request timeout in seconds (default: 30)
        verify (bool): Whether to verify SSL certificates (default: True)
        proxy_limit (int): Maximum number of proxies to fetch (default: 10)
        retry_delays (list, optional): Delay between retries in seconds (default: [2, 5, 10])
        enable_ssl_warnings (bool): Whether to show SSL warnings (default: False)
        use_proxies (bool, optional): Whether to use proxies. If None, auto-detect based on environment
        use_session (bool): Whether to use a session for the request (default: True)
        **kwargs: Additional arguments to pass to requests.get()
        
    Returns:
        tuple: (response_content, success_boolean, error_message)
    """
    try: 
        # Suppress SSL warnings if requested
        if not enable_ssl_warnings:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Check if running in GitHub Actions or determine proxy usage
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        
        # Determine if we should use proxies
        if use_proxies is None:
            # Auto-detect: use proxies in GitHub Actions, skip locally by default
            use_proxies = is_github_actions
        
        if is_github_actions:
            print("⚠️  Running in GitHub Actions - using proxy rotation to avoid IP blocks")
        elif use_proxies:
            print("🔄 Proxy usage enabled")
        else:
            print("🔗 Direct connection mode (proxies disabled)")
        
        # Set default headers if none provided - simple but effective browser-like headers
        if headers is None:
            # Use a single reliable user agent instead of randomizing
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        
        # Set default retry delays
        if retry_delays is None:
            retry_delays = [2, 5, 10]
        
        # Get proxy list for rotation (only if we want to use proxies)
        proxy_list = []
        if use_proxies:
            proxy_list = get_proxy_list(limit=proxy_limit, timeout=10)
        
        # Calculate max retries - always try direct connection at least once
        max_retries = max(len(proxy_list) + 1, 3) if proxy_list else 3
        
        # Create session if requested for better connection handling
        session = requests.Session() if use_session else requests
        
        # For FirstCycling.com, try to establish a session by visiting homepage first
        if use_session and 'firstcycling.com' in url.lower():
            try:
                print("🏠 Visiting FirstCycling homepage first to establish session...")
                homepage_response = session.get(
                    'https://firstcycling.com/',
                    headers=headers,
                    timeout=timeout,
                    verify=verify,
                    proxies=None  # Always try homepage without proxy first
                )
                if homepage_response.status_code == 200:
                    print("   ✅ Homepage visit successful")
                    # Add a small delay to mimic human behavior
                    time.sleep(random.uniform(1, 3))
                else:
                    print(f"   ⚠️  Homepage returned {homepage_response.status_code}")
            except Exception as e:
                print(f"   ⚠️  Homepage visit failed: {e}")
                # Continue anyway, might still work
        
        for attempt in range(max_retries):
            try:
                # Add delay between retries
                if attempt > 0:
                    delay = retry_delays[min(attempt - 1, len(retry_delays) - 1)]
                    print(f"⏳ Retrying in {delay} seconds (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(delay)
                
                # Setup proxy for this attempt
                proxies = None
                current_proxy = None
                
                if proxy_list and len(proxy_list) > 0 and attempt < len(proxy_list):
                    try:
                        current_proxy = proxy_list[attempt]
                        # Ensure proxy dict has required keys
                        if isinstance(current_proxy, dict) and 'host' in current_proxy and 'port' in current_proxy:
                            proxy_url = f"http://{current_proxy['host']}:{current_proxy['port']}"
                            proxies = {
                                'http': proxy_url,
                                'https': proxy_url
                            }
                            print(f"🔄 Using proxy: {current_proxy['host']}:{current_proxy['port']}")
                        else:
                            print(f"⚠️  Invalid proxy dict at index {attempt}, using direct connection")
                    except (KeyError, IndexError, TypeError) as e:
                        print(f"⚠️  Error accessing proxy at index {attempt}: {e}, using direct connection")
                elif attempt == 0 and (not proxy_list or len(proxy_list) == 0):
                    print("🔗 Attempting direct connection (no proxies available)")
                else:
                    print("🔗 Attempting direct connection (no more proxies)")
                
                # Make the request
                response = session.get(
                    url,
                    headers=headers,
                    timeout=timeout,
                    verify=verify,
                    proxies=proxies,
                    **kwargs
                )
                response.raise_for_status()
                
                # Success message
                success_msg = f"✅ Successfully fetched content ({len(response.content)} bytes)"
                if proxies and isinstance(current_proxy, dict):
                    success_msg += f" via proxy {current_proxy['host']}:{current_proxy['port']}"
                print(success_msg)
                
                return response.content, True, None
                
            except requests.exceptions.HTTPError as e:
                proxy_info = f" via proxy {current_proxy['host']}:{current_proxy['port']}" if proxies and isinstance(current_proxy, dict) else " (direct connection)"
                
                if e.response.status_code == 403:
                    if attempt == max_retries - 1:
                        # Final attempt for 403
                        error_msg = f"Access denied (403) for {url}." 
                        print(f"❌ {error_msg}")
                        return None, False, error_msg
                    else:
                        print(f"❌ 403 Forbidden on attempt {attempt + 1}{proxy_info}, trying next...")
                        continue
                else:
                    # Other HTTP errors, don't retry
                    raise e
                    
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout, 
                    requests.exceptions.ConnectionError) as e:
                proxy_info = f" via proxy {current_proxy['host']}:{current_proxy['port']}" if proxies and isinstance(current_proxy, dict) else " (direct connection)"
                
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise e
                else:
                    print(f"❌ Connection error on attempt {attempt + 1}{proxy_info}: {str(e)}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                proxy_info = f" via proxy {current_proxy['host']}:{current_proxy['port']}" if proxies and isinstance(current_proxy, dict) else " (direct connection)"
                
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise e
                else:
                    print(f"❌ Network error on attempt {attempt + 1}{proxy_info}: {str(e)}")
                    continue
        
        # If all proxy attempts failed and it's FirstCycling, try Selenium as last resort
        if 'firstcycling.com' in url.lower():
            print("🔄 All standard methods failed, trying Selenium WebDriver as last resort...")
            return fetch_with_selenium(url, timeout)
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error accessing {url}: {str(e)}"
        print(f"❌ {error_msg}")
        return None, False, error_msg
    except Exception as e:
        error_msg = f"Error making request to {url}: {str(e)}"
        print(f"❌ {error_msg}")
        return None, False, error_msg

def fetch_with_selenium(url, timeout=30, headless=True):
    """
    Fetch content using Selenium WebDriver to mimic real browser behavior.
    
    Args:
        url (str): URL to fetch
        timeout (int): Page load timeout
        headless (bool): Whether to run browser in headless mode
        
    Returns:
        tuple: (html_content, success, error_message)
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, WebDriverException
        
        print(f"🌐 Using Selenium WebDriver to fetch: {url}")
        
        # Configure Chrome options
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Anti-detection options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Create driver
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except ImportError:
            # Fallback to default Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Execute script to hide WebDriver
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Visit homepage first
            print("🏠 Visiting FirstCycling homepage...")
            driver.get("https://firstcycling.com/")
            
            # Random delay to mimic human behavior
            time.sleep(random.uniform(2, 5))
            
            # Navigate to target URL
            print(f"🎯 Navigating to target page...")
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get page source
            html_content = driver.page_source
            
            print(f"✅ Successfully fetched {len(html_content)} characters with Selenium")
            return html_content.encode('utf-8'), True, None
            
        finally:
            driver.quit()
            
    except ImportError:
        return None, False, "Selenium not installed. Install with: pip install selenium"
    except WebDriverException as e:
        if "chromedriver" in str(e).lower():
            return None, False, "ChromeDriver not found. Install ChromeDriver or use webdriver-manager: pip install webdriver-manager"
        else:
            return None, False, f"WebDriver error: {str(e)}"
    except Exception as e:
        return None, False, f"Selenium error: {str(e)}"

def get_path(namespace, path_type):
    assert path_type in PATH_TYPES, f"Invalid path_type: {path_type}"
    if path_type == 'root':
        return os.path.join(DATA_PATH, namespace)
    elif path_type == 'changes_dir':
        return os.path.join(DATA_PATH, namespace, 'changes')
    elif path_type == 'stats_file':
        return os.path.join(DATA_PATH, namespace, 'stats.yaml')
    elif path_type == 'tracking_db':
        return os.path.join(DATA_PATH, namespace, 'tracking_db.sqlite')
    elif path_type == 'cdb':
        return os.path.join(DATA_PATH, namespace, 'cdb')


def get_available_namespaces():
    """
    Discover all available namespaces by scanning the data directory.
    
    Returns:
        list: List of namespace directory names
    """
    if not os.path.exists(DATA_PATH):
        return []
    
    namespaces = []
    for item in os.listdir(DATA_PATH):
        item_path = os.path.join(DATA_PATH, item)
        if os.path.isdir(item_path):
            namespaces.append(item)
    
    return sorted(namespaces)