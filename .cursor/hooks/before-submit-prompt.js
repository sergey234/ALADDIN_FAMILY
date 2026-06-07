#!/usr/bin/env node
const { readStdin } = require('./aladdin-adapter');
const SECRET_PATTERNS = [
  /sk-[a-zA-Z0-9]{20,}/,
  /ghp_[a-zA-Z0-9]{36,}/,
  /AKIA[A-Z0-9]{16}/,
  /xox[bpsa]-[a-zA-Z0-9-]+/,
  /-----BEGIN (RSA |EC )?PRIVATE KEY-----/,
];
readStdin().then((raw) => {
  try {
    const input = JSON.parse(raw || '{}');
    const prompt = input.prompt || input.content || input.message || '';
    if (SECRET_PATTERNS.some((p) => p.test(prompt))) {
      console.error('[ALADDIN] WARNING: Potential secret in prompt — use env vars, not chat.');
    }
  } catch {}
  process.stdout.write(raw || '');
}).catch(() => process.exit(0));
