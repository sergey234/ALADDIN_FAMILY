#!/usr/bin/env node
const { readStdin } = require('./aladdin-adapter');
readStdin().then((raw) => {
  try {
    const input = JSON.parse(raw || '{}');
    const filePath = input.file_path || '';
    if (/\.(env|key|pem)$|\.env\.|credentials|secret/i.test(filePath)) {
      console.error('[ALADDIN] WARNING: Reading sensitive file: ' + filePath);
    }
  } catch (error) {
    console.error('[ALADDIN] beforeReadFile hook parse warning: ' + error.message);
  }
  process.stdout.write('{"permission":"allow"}\n');
}).catch((error) => {
  console.error('[ALADDIN] beforeReadFile hook failed: ' + error.message);
  process.stdout.write('{"permission":"allow"}\n');
});
