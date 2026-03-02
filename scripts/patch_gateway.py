import sys

file_path = sys.argv[1]

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
imported = False
for line in lines:
    if not imported and 'from jose import JWTError, jwt' in line:
        new_lines.append(line)
        new_lines.append("from app.security import verify_payload_signature\n")
        imported = True
        continue
    
    new_lines.append(line)
    
    if 'payload = jwt.decode(' in line and ('SECRET_KEY' in line or 'JWT_SECRET' in line):
        # Find indent
        indent = line[:line.find('payload')]
        new_lines.append(f"{indent}# HMAC Signature Verification\n")
        new_lines.append(f"{indent}if 'subscription' in payload:\n")
        new_lines.append(f"{indent}    sig = payload.get('signature')\n")
        new_lines.append(f"{indent}    if sig and not verify_payload_signature(payload['subscription'], sig):\n")
        new_lines.append(f"{indent}        raise HTTPException(status_code=401, detail='JWT Signature mismatch')\n")

with open(file_path, 'w') as f:
    f.writelines(new_lines)
