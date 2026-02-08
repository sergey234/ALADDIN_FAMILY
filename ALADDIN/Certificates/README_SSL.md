# SSL Certificate Instructions

## Main Certificate (aladdin_cert.cer)
- Download from: https://aladdin-ai.ru SSL certificate
- Convert to .cer format using:
  `openssl x509 -in certificate.pem -outform der -out aladdin_cert.cer`

## Backup Certificate (aladdin_cert_backup.cer)  
- Secondary certificate for redundancy
- Same format and process as main certificate

## Security Notes
- Never commit real certificates to version control
- Use test certificates for development
- Real certificates should be added to production builds only

