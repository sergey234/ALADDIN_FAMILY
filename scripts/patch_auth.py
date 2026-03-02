import sys

file_path = sys.argv[1]

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if 'payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])' in line:
        indent = line[:line.find('payload')]
        new_lines.append(f"{indent}# HMAC Signature Verification for anti-tampering\n")
        new_lines.append(f"{indent}if 'subscription' in payload:\n")
        new_lines.append(f"{indent}    sig = payload.get('signature')\n")
        new_lines.append(f"{indent}    if sig and not verify_payload_signature(payload['subscription'], sig):\n")
        new_lines.append(f"{indent}        return None\n")

with open(file_path, 'w') as f:
    f.writelines(new_lines)
