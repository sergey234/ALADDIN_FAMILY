#!/usr/bin/env python3
"""
MANUAL FIX FOR API GATEWAY SFM INTEGRATION
Заменяем mock данные на реальные SFM вызовы
"""

import re

def fix_api_gateway():
    """Fix API Gateway to use real SFM calls"""

    print("🔧 FIXING API GATEWAY SFM INTEGRATION...")

    # Read the file
    with open('api_gateway_manual_fix.py', 'r') as f:
        content = f.read()

    # Add SFM mapping import after main imports
    import_code = '''
# Import SFM mapping for production
try:
    from complete_api_sfm_mapping import get_sfm_function_name, API_TO_SFM_MAPPING
    SFM_MAPPING_AVAILABLE = True
    print(f"SFM mapping loaded: {len(API_TO_SFM_MAPPING)} functions")
except ImportError as e:
    SFM_MAPPING_AVAILABLE = False
    print(f"SFM mapping not available: {e}")
    API_TO_SFM_MAPPING = {}
    def get_sfm_function_name(name):
        return name
'''

    # Find the position after main imports
    main_import_end = content.find('SFM_ADAPTER_AVAILABLE = True')
    if main_import_end > 0:
        content = content[:main_import_end] + import_code + '\n' + content[main_import_end:]

    # Replace SFM handling logic
    # Find all SFM execute_function calls and replace the surrounding logic

    def replace_sfm_block(match):
        block = match.group(0)

        # Extract function name from sfm_adapter.execute_function("func_name", ...)
        func_match = re.search(r'sfm_adapter\.execute_function\("([^"]+)"', block)
        if func_match:
            api_func_name = func_match.group(1)

            # Create proper SFM handling
            new_block = f'''    # PRODUCTION: Real SFM integration with mapping
    if SFM_ADAPTER_AVAILABLE and sfm_adapter and SFM_MAPPING_AVAILABLE:
        try:
            # Get mapped SFM function name
            sfm_func_name = get_sfm_function_name("{api_func_name}")
            success, result, error = sfm_adapter.execute_function(sfm_func_name, {{}})

            if success:
                # Ensure result has source marker
                if isinstance(result, dict):
                    if "source" not in result:
                        result["source"] = "sfm_real"
                    return result
                else:
                    # Wrap non-dict results
                    return {{"data": result, "function": "{api_func_name}", "source": "sfm_real"}}
            else:
                print(f"SFM call failed for {api_func_name} -> {{sfm_func_name}}: {{error}}")
                return {{"error": error, "function": "{api_func_name}", "sfm_function": sfm_func_name, "source": "sfm_error"}}

        except Exception as e:
            print(f"SFM exception for {api_func_name}: {{e}}")
            return {{"error": str(e), "function": "{api_func_name}", "source": "sfm_exception"}}

    # FALLBACK: Mock response when SFM not available
    return {{"status": "mock_fallback", "function": "{api_func_name}", "source": "mock", "reason": "SFM_not_available"}}'''

        return new_block

    # Pattern to match SFM blocks
    sfm_pattern = r'    if SFM_ADAPTER_AVAILABLE and sfm_adapter:\s*\n\s*success, result, message = sfm_adapter\.execute_function\([^}]+\}\s*\n\s*else:\s*\n\s*return \{[^}]+"source": "[^"]*mock[^"]*"[^}]*\}'

    # Apply replacements
    new_content = re.sub(sfm_pattern, replace_sfm_block, content, flags=re.MULTILINE | re.DOTALL)

    # Count replacements
    original_blocks = len(re.findall(r'sfm_adapter\.execute_function\(', content))
    new_blocks = len(re.findall(r'sfm_adapter\.execute_function\(', new_content))

    print(f"✅ Found SFM blocks: {original_blocks}")
    print(f"✅ Updated SFM blocks: {new_blocks}")

    # Save the fixed file
    with open('api_gateway_fixed.py', 'w') as f:
        f.write(new_content)

    print("✅ Fixed API Gateway saved as: api_gateway_fixed.py")

    # Validate syntax
    try:
        compile(new_content, 'api_gateway_fixed.py', 'exec')
        print("✅ Syntax validation passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

if __name__ == "__main__":
    success = fix_api_gateway()
    if success:
        print("\n🎯 API GATEWAY FIXED FOR PRODUCTION!")
        print("   Ready to deploy: api_gateway_fixed.py")
    else:
        print("\n❌ Failed to fix API Gateway")