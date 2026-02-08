# 🔐 SSL Certificate Setup for ALADDIN iOS

## For Development (Test Certificates)
```bash
# 1. Create self-signed certificate for testing
openssl req -x509 -newkey rsa:2048 -keyout test_key.pem -out test_cert.pem -days 365 -nodes -subj "/C=RU/ST=Moscow/L=Moscow/O=ALADDIN/OU=Development/CN=aladdin-ai.ru"

# 2. Convert to .cer format
openssl x509 -in test_cert.pem -outform der -out ALADDIN/Certificates/aladdin_cert.cer

# 3. Create backup certificate
openssl req -x509 -newkey rsa:2048 -keyout test_key_backup.pem -out test_cert_backup.pem -days 365 -nodes -subj "/C=RU/ST=Moscow/L=Moscow/O=ALADDIN/OU=Development/CN=api.aladdin.family"
openssl x509 -in test_cert_backup.pem -outform der -out ALADDIN/Certificates/aladdin_cert_backup.cer
```

## For Production (Real Certificarom server
curl -v https://aladdin-ai.ru 2>&1 | grep "issuer\|subject"
# Use browser to export certificates in .cer format
```

## Xcode Integration
1. Add both .cer files to Xcode project
2. Ensure "Target Membership" includes ALADDIN target
3. Build and test SSL pinning functionality

## Verification
```bash
# Test SSL pinning works
- Remove certificates → should use fallback
- Add certificates → should use pinning
- Check logs for SSL pinning messages
```
