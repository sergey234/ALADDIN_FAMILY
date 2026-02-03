try:
    from security.sfm_singleton import get_sfm
    sfm = get_sfm()
    print(f"SUCCESS: SFM loaded with {len(sfm.functions)} functions")
    print(f"Status: {sfm.status}")
    
    # Test function call
    success, result, error = sfm.execute_function("get_component_status", {"component_id": "test"})
    print(f"Function test: Success={success}")
    if result:
        print(f"Result keys: {list(result.keys())}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
