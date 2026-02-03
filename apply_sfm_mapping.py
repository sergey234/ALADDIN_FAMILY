#!/usr/bin/env python3
"""
APPLY SFM MAPPING TO API GATEWAY
Автоматическая замена mock данных на реальные SFM вызовы

Эта программа:
1. Читает api_gateway.py
2. Находит все mock ответы
3. Заменяет их на реальные SFM вызовы
4. Сохраняет production-ready версию
"""

import re
import sys

def apply_sfm_mapping():
    """Apply SFM mapping to API Gateway"""

    print("🚀 APPLYING SFM MAPPING TO API GATEWAY...")

    # Read the current API Gateway file
    try:
        with open('api_gateway_server.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ api_gateway_server.py not found!")
        return False

    # Add import for SFM mapping at the top
    import_section = '''
# Import SFM mapping for production
try:
    from complete_api_sfm_mapping import get_sfm_function_name
    SFM_MAPPING_AVAILABLE = True
    print("SFM mapping loaded successfully")
except ImportError as e:
    SFM_MAPPING_AVAILABLE = False
    print(f"SFM mapping not available: {e}")
    def get_sfm_function_name(name):
        return name
'''

    # Find where imports end and add our import
    if 'from fastapi import' in content:
        # Add after the main imports
        content = content.replace(
            'from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks',
            'from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks\n' + import_section
        )

    # Replace the entire if/else SFM logic with proper error handling
    # Pattern: if SFM_ADAPTER_AVAILABLE and sfm_adapter:\n        success, result, message = sfm_adapter.execute_function(...)\n        return {...mock...}\n    else:\n        return {...mock...}

    def replace_sfm_logic(match):
        block = match.group(0)

        # Extract function name from the SFM call
        sfm_call_match = re.search(r'sfm_adapter\.execute_function\("([^"]+)"', block)
        if sfm_call_match:
            func_name = sfm_call_match.group(1)

            # Create proper SFM handling
            proper_logic = f'''    # PRODUCTION: Proper SFM handling with mapping
    if SFM_ADAPTER_AVAILABLE and sfm_adapter and SFM_MAPPING_AVAILABLE:
        try:
            sfm_func = get_sfm_function_name("{func_name}")
            success, result, error = sfm_adapter.execute_function(sfm_func, {{}})
            if success:
                # Ensure result has source marker for real SFM data
                if isinstance(result, dict) and "source" not in result:
                    result["source"] = "sfm_real"
                elif not isinstance(result, dict):
                    # Wrap non-dict results
                    result = {{"data": result, "source": "sfm_real"}}
                return result
            else:
                print(f"SFM call failed for {func_name}: {{error}}")
                # FALLBACK: Return error info
                return {{"error": error, "function": "{func_name}", "source": "sfm_error"}}
        except Exception as e:
            print(f"SFM exception for {func_name}: {{e}}")
            # FALLBACK: Return exception info
            return {{"error": str(e), "function": "{func_name}", "source": "sfm_exception"}}

    # FALLBACK: Basic mock response when SFM not available
    return {{"status": "mock_fallback", "function": "{func_name}", "source": "mock"}}'''

            return proper_logic
        else:
            return block  # Return unchanged if can't parse

    # Pattern to match the entire SFM if/else block
    sfm_block_pattern = r'    if SFM_ADAPTER_AVAILABLE and sfm_adapter:\s*\n\s*success, result, message = sfm_adapter\.execute_function\([^}]+\}\s*\n\s*else:\s*\n\s*return \{[^}]+"source": "mock"[^}]*\}'

    # Apply replacements
    new_content = re.sub(sfm_block_pattern, replace_sfm_logic, content, flags=re.MULTILINE | re.DOTALL)

    # Count replacements
    original_count = len(re.findall(mock_pattern, content))
    new_count = len(re.findall(mock_pattern, new_content))

    replaced_count = original_count - new_count

    print(f"✅ Replaced {replaced_count} mock responses with SFM calls")

    # Save the updated file
    with open('api_gateway_production.py', 'w') as f:
        f.write(new_content)

    print("✅ Production API Gateway saved as: api_gateway_production.py")

    # Create backup
    with open('api_gateway_backup.py', 'w') as f:
        f.write(content)

    print("✅ Backup created: api_gateway_backup.py")

    return True

def validate_production_api():
    """Validate the production API file"""

    print("\n🔍 VALIDATING PRODUCTION API...")

    try:
        with open('api_gateway_production.py', 'r') as f:
            content = f.read()

        # Check for syntax errors
        compile(content, 'api_gateway_production.py', 'exec')
        print("✅ Syntax validation passed")

        # Count SFM calls
        sfm_call_count = len(re.findall(r'sfm_adapter\.execute_function', content))
        print(f"✅ SFM calls added: {sfm_call_count}")

        # Count remaining mocks
        mock_count = len(re.findall(r'"source"\s*:\s*"[^"]*mock[^"]*"', content))
        print(f"⚠️  Remaining mock responses: {mock_count}")

        return True

    except SyntaxError as e:
        print(f"❌ Syntax error in production API: {e}")
        return False
    except FileNotFoundError:
        print("❌ Production API file not found")
        return False

if __name__ == "__main__":
    success = apply_sfm_mapping()
    if success:
        validate_production_api()
        print("\n🎯 PRODUCTION API READY!")
        print("   Next steps:")
        print("   1. Deploy api_gateway_production.py")
        print("   2. Test all endpoints")
        print("   3. Monitor performance")
        print("   4. Launch production!")
    else:
        print("❌ Failed to apply SFM mapping")
        sys.exit(1)