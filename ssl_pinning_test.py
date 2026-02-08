#!/usr/bin/env python3
"""
🛡️ SSL Pinning Test for ALADDIN iOS
Проверка работы SSL pinning с реальными сертификатами
"""

import requests
import ssl
import socket
import json
from urllib.parse import urlparse

# Configuration
TARGET_URL = "https://aladdin-ai.ru/api/health"
CERT_FILE = "ALADDIN/Certificates/aladdin_cert.cer"
BACKUP_CERT_FILE = "ALADDIN/Certificates/aladdin_cert_backup.cer"

def load_certificate_from_file(filepath):
    """Load certificate data from file"""
    try:
        with open(filepath, 'rb') as f:
            cert_data = f.read()
            print(f"✅ Certificate loaded: {filepath} ({len(cert_data)} bytes)")
            return cert_data
    except Exception as e:
        print(f"❌ Failed to load certificate {filepath}: {e}")
        return None

def get_server_certificate(hostname, port=443):
    """Get server certificate from hostname"""
    try:
        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Connect and get certificate
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert_der = ssock.getpeercert(binary_form=True)
                print(f"✅ Server certificate retrieved: {hostname}:{port} ({len(cert_der)} bytes)")
                return cert_der
    except Exception as e:
        print(f"❌ Failed to get server certificate from {hostname}:{port}: {e}")
        return None

def certificates_match(cert1_data, cert2_data):
    """Check if two certificates match"""
    return cert1_data == cert2_data

def test_ssl_pinning():
    """Main SSL pinning test"""
    print("🛡️ ALADDIN SSL Pinning Test")
    print("=" * 50)

    # Parse target URL
    parsed_url = urlparse(TARGET_URL)
    hostname = parsed_url.hostname

    print(f"🎯 Target: {TARGET_URL}")
    print(f"   Hostname: {hostname}")
    print()

    # Load local certificates
    print("📄 Loading local certificates...")
    local_cert = load_certificate_from_file(CERT_FILE)
    local_backup_cert = load_certificate_from_file(BACKUP_CERT_FILE)

    if not local_cert and not local_backup_cert:
        print("❌ No local certificates found!")
        return False

    print()

    # Get server certificate
    print("🌐 Getting server certificate...")
    server_cert = get_server_certificate(hostname)

    if not server_cert:
        print("❌ Could not retrieve server certificate!")
        return False

    print()

    # Compare certificates
    print("🔍 Comparing certificates...")

    matches = []
    if local_cert:
        main_match = certificates_match(local_cert, server_cert)
        matches.append(("Main certificate", main_match))
        print(f"   Main cert match: {'✅' if main_match else '❌'}")

    if local_backup_cert:
        backup_match = certificates_match(local_backup_cert, server_cert)
        matches.append(("Backup certificate", backup_match))
        print(f"   Backup cert match: {'✅' if backup_match else '❌'}")

    print()

    # Test API connection
    print("🔗 Testing API connection...")
    try:
        response = requests.get(TARGET_URL, timeout=10, verify=True)
        if response.status_code == 200:
            print("✅ API connection successful")
            try:
                data = response.json()
                print(f"   Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}...")
        else:
            print(f"⚠️ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

    print()

    # Final result
    any_match = any(match for _, match in matches)
    if any_match:
        print("🎉 SSL PINNING TEST PASSED!")
        print("   Server certificate matches local certificate(s)")
        print("   SSL pinning should work correctly in the iOS app")
        return True
    else:
        print("❌ SSL PINNING TEST FAILED!")
        print("   Server certificate does NOT match any local certificate")
        print("   SSL pinning will fail in the iOS app")
        print("   Check if certificates are up to date")
        return False

if __name__ == "__main__":
    success = test_ssl_pinning()

    # Save results
    result = {
        "test_passed": success,
        "target_url": TARGET_URL,
        "cert_files": [CERT_FILE, BACKUP_CERT_FILE],
        "timestamp": str(__import__('datetime').datetime.now())
    }

    with open('ssl_pinning_test_result.json', 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\n💾 Results saved to ssl_pinning_test_result.json")
    exit(0 if success else 1)