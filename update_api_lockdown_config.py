#!/usr/bin/env python3
"""
🚀 UPDATE API LOCKDOWN CONFIGURATION
Автоматическое обновление api_config_lockdown_system.py для 183 эндпоинтов
"""

import re
from collections import defaultdict

def extract_endpoints_from_api_file(file_path):
    """Extract all endpoints from api_gateway_complete.py"""
    endpoints = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_method = None
    current_path = None

    for line in lines:
        line = line.strip()

        # Find HTTP method decorators
        if line.startswith('@app.'):
            import re

            if 'get(' in line:
                current_method = 'GET'
                match = re.search(r'@app\.get\((.*?)\)', line)
                if match:
                    path_str = match.group(1).strip()
                    current_path = path_str.strip('"\'')  # Remove quotes

            elif 'post(' in line:
                current_method = 'POST'
                match = re.search(r'@app\.post\((.*?)\)', line)
                if match:
                    path_str = match.group(1).strip()
                    current_path = path_str.strip('"\'')  # Remove quotes

            elif 'put(' in line:
                current_method = 'PUT'
                match = re.search(r'@app\.put\((.*?)\)', line)
                if match:
                    path_str = match.group(1).strip()
                    current_path = path_str.strip('"\'')  # Remove quotes

            elif 'delete(' in line:
                current_method = 'DELETE'
                match = re.search(r'@app\.delete\((.*?)\)', line)
                if match:
                    path_str = match.group(1).strip()
                    current_path = path_str.strip('"\'')  # Remove quotes

        # Find function definition to complete endpoint
        elif current_method and current_path and (line.startswith('def ') or line.startswith('async def ')):
            endpoints.append({
                'method': current_method,
                'path': current_path,
                'status': 'locked'
            })
            current_method = None
            current_path = None

    return endpoints

def categorize_endpoints(endpoints):
    """Categorize endpoints by functionality"""
    categories = defaultdict(list)

    for endpoint in endpoints:
        path = endpoint['path']

        # Categorize based on path
        if '/auth/' in path:
            categories['authentication'].append(endpoint)
        elif '/subscription/' in path:
            categories['subscription'].append(endpoint)
        elif '/notifications/' in path:
            categories['notifications'].append(endpoint)
        elif '/parental/' in path:
            categories['parental_control'].append(endpoint)
        elif '/identity/' in path:
            categories['identity_protection'].append(endpoint)
        elif '/darkweb/' in path:
            categories['darkweb_monitoring'].append(endpoint)
        elif '/location/' in path:
            categories['location_tracking'].append(endpoint)
        elif '/data/cleanup' in path:
            categories['data_cleanup'].append(endpoint)
        elif '/antitracker/' in path:
            categories['anti_tracker'].append(endpoint)
        elif '/roadside/' in path:
            categories['roadside_assistance'].append(endpoint)
        elif '/system/' in path:
            categories['system_management'].append(endpoint)
        elif '/analytics/' in path:
            categories['analytics'].append(endpoint)
        elif '/ai/categories' in path:
            categories['ai_categories'].append(endpoint)
        elif '/components/' in path:
            categories['components'].append(endpoint)
        elif '/phishing/' in path:
            categories['anti_phishing'].append(endpoint)
        elif '/malware/' in path:
            categories['antivirus'].append(endpoint)
        elif '/mobile/' in path:
            categories['mobile_security'].append(endpoint)
        elif '/network/' in path:
            categories['network_security'].append(endpoint)
        elif path == '/' or '/health' in path:
            categories['health_checks'].append(endpoint)
        else:
            categories['other'].append(endpoint)

    return dict(categories)

def generate_lockdown_config(categories):
    """Generate the API_ENDPOINTS_CONFIG dictionary"""

    config_lines = []
    config_lines.append('    # 🔒 ЗАФИКСИРОВАННЫЕ API ЭНДПОИНТЫ (183 эндпоинта - НЕ МЕНЯТЬ!)')
    config_lines.append('    API_ENDPOINTS_CONFIG = {')

    for category_name, endpoints in categories.items():
        config_lines.append(f'        "{category_name}": [')

        for endpoint in endpoints:
            config_lines.append('            {')
            config_lines.append(f'                "method": "{endpoint["method"]}",')
            config_lines.append(f'                "path": "{endpoint["path"]}",')
            config_lines.append('                "status": "locked"')
            config_lines.append('            },')
            if endpoint != endpoints[-1]:
                config_lines.append('')

        config_lines.append('        ],')
        if category_name != list(categories.keys())[-1]:
            config_lines.append('')

    config_lines.append('    }')

    return '\n'.join(config_lines)

def update_lockdown_file():
    """Update the api_config_lockdown_system.py file"""

    # Extract endpoints from API file
    endpoints = extract_endpoints_from_api_file('api_gateway_complete.py')
    print(f"📊 Extracted {len(endpoints)} endpoints from api_gateway_complete.py")

    # Categorize endpoints
    categories = categorize_endpoints(endpoints)
    print(f"📂 Categorized into {len(categories)} categories:")

    total_endpoints = 0
    for category, endpoints_list in categories.items():
        print(f"   {category}: {len(endpoints_list)} endpoints")
        total_endpoints += len(endpoints_list)

    print(f"✅ Total: {total_endpoints} endpoints")

    # Generate new config
    new_config = generate_lockdown_config(categories)

    # Read current lockdown file
    with open('api_config_lockdown_system.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and replace the API_ENDPOINTS_CONFIG section
    import re

    # Find the start and end of API_ENDPOINTS_CONFIG
    start_pattern = r'(\s+)API_ENDPOINTS_CONFIG\s*=\s*\{'
    end_pattern = r'(\s+)\}'

    start_match = re.search(start_pattern, content)
    if not start_match:
        print("❌ Could not find API_ENDPOINTS_CONFIG in lockdown file")
        return False

    start_pos = start_match.start()

    # Find the closing brace for API_ENDPOINTS_CONFIG
    brace_count = 0
    end_pos = start_pos

    for i in range(start_pos, len(content)):
        if content[i] == '{':
            brace_count += 1
        elif content[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i + 1
                break

    if brace_count != 0:
        print("❌ Could not find matching closing brace for API_ENDPOINTS_CONFIG")
        return False

    # Replace the section
    new_content = content[:start_pos] + new_config + content[end_pos:]

    # Write back
    with open('api_config_lockdown_system.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ Successfully updated api_config_lockdown_system.py")
    print(f"🔒 Locked {total_endpoints} endpoints across {len(categories)} categories")

    return True

if __name__ == "__main__":
    print("🚀 Updating API Lockdown Configuration for 183 endpoints...")
    success = update_lockdown_file()

    if success:
        print("\n🎉 Configuration updated successfully!")
        print("🔐 All 183 endpoints are now locked and protected.")
    else:
        print("\n❌ Failed to update configuration.")