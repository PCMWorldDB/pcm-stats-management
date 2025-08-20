import os

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
                                   retry_delays=None, enable_ssl_warnings=False, **kwargs):
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
        **kwargs: Additional arguments to pass to requests.get()
        
    Returns:
        tuple: (response_content, success_boolean, error_message)
    """
    try:
        import requests
        import urllib3
        import time
        
        # Suppress SSL warnings if requested
        if not enable_ssl_warnings:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Check if running in GitHub Actions
        is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        if is_github_actions:
            print("⚠️  Running in GitHub Actions - using proxy rotation to avoid IP blocks")
        
        # Set default headers if none provided
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        
        # Set default retry delays
        if retry_delays is None:
            retry_delays = [2, 5, 10]
        
        # Get proxy list for rotation
        proxy_list = get_proxy_list(limit=proxy_limit, timeout=10)
        
        # Calculate max retries
        max_retries = max(len(proxy_list) + 1, 3) if proxy_list else 3
        
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
                response = requests.get(
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
                        error_msg = f"Access denied (403) for {url}. This may be due to:\n" \
                                  f"   • IP blocking (tried {len(proxy_list)} proxies + direct connection)\n" \
                                  f"   • Rate limiting from the website\n" \
                                  f"   • Anti-bot protection\n" \
                                  f"   Consider using a different proxy service or running locally."
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
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error accessing {url}: {str(e)}"
        print(f"❌ {error_msg}")
        return None, False, error_msg
    except Exception as e:
        error_msg = f"Error making request to {url}: {str(e)}"
        print(f"❌ {error_msg}")
        return None, False, error_msg

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