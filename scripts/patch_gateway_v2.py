import sys

file_path = sys.argv[1]

with open(file_path, 'r') as f:
    lines = f.readlines()

new_lines = []
imported_sig = False
imported_rl = False
for line in lines:
    if not imported_sig and 'from jose import JWTError, jwt' in line:
        new_lines.append(line)
        new_lines.append("from app.security import verify_payload_signature\n")
        imported_sig = True
        continue
    
    if not imported_rl and 'from fastapi import FastAPI' in line:
        new_lines.append(line)
        new_lines.append("from app.services.rate_limit_service import RateLimitService\n")
        imported_rl = True
        continue

    new_lines.append(line)
    
    if 'payload = jwt.decode(' in line and ('SECRET_KEY' in line or 'JWT_SECRET' in line):
        indent = line[:line.find('payload')]
        new_lines.append(f"{indent}# HMAC Signature Verification & State enrichment\n")
        new_lines.append(f"{indent}if 'subscription' in payload:\n")
        new_lines.append(f"{indent}    sub_data = payload['subscription']\n")
        new_lines.append(f"{indent}    sig = payload.get('signature')\n")
        new_lines.append(f"{indent}    if sig and not verify_payload_signature(sub_data, sig):\n")
        new_lines.append(f"{indent}        raise HTTPException(status_code=401, detail='JWT Signature mismatch')\n")
        new_lines.append(f"{indent}    request.state.subscription_level = sub_data.get('level', 'free')\n")
        new_lines.append(f"{indent}    request.state.subscription_status = sub_data.get('status', 'active')\n")

    if 'app = FastAPI(' in line:
        new_lines.append("\nrate_limiter = RateLimitService()\n")
        new_lines.append("\n@app.middleware('http')\n")
        new_lines.append("async def rate_limit_middleware(request, call_next):\n")
        new_lines.append("    if hasattr(request.state, 'user_id'):\n")
        new_lines.append("        user_id = request.state.user_id\n")
        new_lines.append("        level = getattr(request.state, 'subscription_level', 'free')\n")
        new_lines.append("        allowed, remaining, retry_after = rate_limiter.is_allowed(user_id, level)\n")
        new_lines.append("        if not allowed:\n")
        new_lines.append("            from fastapi.responses import JSONResponse\n")
        new_lines.append("            return JSONResponse(\n")
        new_lines.append("                status_code=429,\n")
        new_lines.append("                content={'detail': 'Rate limit exceeded', 'retry_after': retry_after},\n")
        new_lines.append("                headers={'Retry-After': str(retry_after)}\n")
        new_lines.append("            )\n")
        new_lines.append("    return await call_next(request)\n")

with open(file_path, 'w') as f:
    f.writelines(new_lines)
