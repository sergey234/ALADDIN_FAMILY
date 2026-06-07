#!/usr/bin/env node
const { readStdin } = require('./aladdin-adapter');
readStdin().then((raw) => {
  try {
    const input = JSON.parse(raw || '{}');
    const filePath = input.path || input.file || '';
    if (/\.(env|key|pem)$|\.env\.|credentials|secret/i.test(filePath)) {
      console.error('[ALADDIN] WARNING: Reading sensitive file: ' + filePath);
    }
  } catch {}
  process.stdout.write(raw || '');
}).catch(() => process.exit(0));
