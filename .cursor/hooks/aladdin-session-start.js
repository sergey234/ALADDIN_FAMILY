#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { readStdin, getIosRoot } = require('./aladdin-adapter');

const ROOT = getIosRoot();
const SUMMARY = path.join(ROOT, '.cursor', 'session', 'last-summary.md');

function gitLine(cmd, args) {
  try {
    return execFileSync(cmd, args, { cwd: ROOT, encoding: 'utf8' }).trim();
  } catch {
    return '';
  }
}

readStdin().then((raw) => {
  const branch = gitLine('git', ['branch', '--show-current']);
  const toplevel = gitLine('git', ['rev-parse', '--show-toplevel']);
  const lines = [
    '## ALADDIN session context (auto)',
    `- Root: \`${ROOT}\``,
    `- Git top-level: \`${toplevel || 'n/a'}\``,
    `- Branch: \`${branch || 'n/a'}\``,
    '- Rules: `prod-no-mock-bypass`, `ios-working-root`, `aladdin-server-connection`',
    '- iOS backup: `./scripts/create_clean_mobile_backup.sh`',
    '- Bot backup: `./scripts/create_telegram_bot_backup.sh` (separate from iOS)',
  ];
  if (fs.existsSync(SUMMARY)) {
    const prev = fs.readFileSync(SUMMARY, 'utf8').trim();
    if (prev) lines.push('', '### Previous session summary', prev);
  }
  process.stderr.write('[ALADDIN] SessionStart context loaded\n');
  process.stdout.write(`${lines.join('\n')}\n`);
  if (raw) process.stdout.write(raw.endsWith('\n') ? raw : `${raw}\n`);
}).catch(() => process.exit(0));
