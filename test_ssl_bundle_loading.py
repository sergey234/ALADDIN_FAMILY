#!/usr/bin/env python3
"""
🧪 Test SSL Certificate Bundle Loading
Проверяем, что сертификаты будут правильно загружены в iOS Bundle
"""

import os
import json

def test_bundle_structure():
    """Test that certificates are properly structured for iOS Bundle"""
    print("📱 Testing iOS Bundle Certificate Loading")
    print("=" * 50)

    cert_dir = "ALADDIN/Certificates"
    cert_files = ["aladdin_cert.cer", "aladdin_cert_backup.cer"]

    results = {}

    for cert_file in cert_files:
        cert_path = os.path.join(cert_dir, cert_file)
        cert_name = cert_file.replace('.cer', '')  # iOS ищет без расширения

        print(f"🔍 Checking {cert_file}...")

        if os.path.exists(cert_path):
            size = os.path.getsize(cert_path)
            print(f"   ✅ File exists: {size} bytes")

            # Check if file is readable
            try:
                with open(cert_path, 'rb') as f:
                    data = f.read()
                    print(f"   ✅ File readable: {len(data)} bytes")

                results[cert_name] = {
                    "exists": True,
                    "size": size,
                    "readable": True,
                    "bundle_path": f"{cert_name}.cer"
                }

            except Exception as e:
                print(f"   ❌ File not readable: {e}")
                results[cert_name] = {
                    "exists": True,
                    "size": size,
                    "readable": False,
                    "error": str(e)
                }
        else:
            print("   ❌ File does not exist")
            results[cert_name] = {
                "exists": False,
                "bundle_path": f"{cert_name}.cer"
            }

    print()
    print("📋 iOS Bundle Loading Instructions:")
    print("In NetworkManager.loadCertificate(named:), iOS will:")
    print("1. Call Bundle.main.path(forResource: name, ofType: 'cer')")
    print("2. Load file from app bundle")

    print()
    print("🔧 Current Bundle Search Paths:")
    for name, info in results.items():
        if info["exists"] and info["readable"]:
            print(f"   ✅ {name} -> {info['bundle_path']} ({info['size']} bytes)")
        else:
            print(f"   ❌ {name} -> {info['bundle_path']} (NOT FOUND)")

    print()
    print("🚀 Production Behavior:")
    print("   DEBUG mode: SSL pinning disabled")
    print("   RELEASE mode: SSL pinning enabled")
    print("   If certificates not found: Falls back to standard SSL validation")

    # Save results
    with open('bundle_loading_test_result.json', 'w') as f:
        json.dump(results, f, indent=2)

    all_good = all(info.get("readable", False) for info in results.values())
    if all_good:
        print("\n🎉 BUNDLE LOADING TEST PASSED!")
        print("   Certificates are ready for iOS Bundle")
    else:
        print("\n❌ BUNDLE LOADING TEST FAILED!")
        print("   Some certificates have issues")

    return all_good

if __name__ == "__main__":
    success = test_bundle_structure()

    print("\n💾 Results saved to bundle_loading_test_result.json")
    exit(0 if success else 1)