#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');
const { readStdin, getIosRoot } = require('./aladdin-adapter');

const ROOT = getIosRoot();
const SESSION_DIR = path.join(ROOT, '.cursor', 'session');
const SUMMARY = path.join(SESSION_DIR, 'last-summary.md');

function gitLine(cmd, args) {
  try {
    return execFileSync(cmd, args, { cwd: ROOT, encoding: 'utf8' }).trim();
  } catch {
    return '';
  }
}

readStdin().then((raw) => {
  fs.mkdirSync(SESSION_DIR, { recursive: true });
  const stamp = new Date().toISOString();
  const branch = gitLine('git', ['branch', '--show-current']);
  const status = gitLine('git', ['status', '--short']);
  const shortStatus = status.split('\n').filter(Boolean).slice(0, 12).join('\n');
  const body = [
    `Saved: ${stamp}`,
    `Branch: ${branch || 'n/a'}`,
    shortStatus ? `Git status (first lines):\n${shortStatus}` : 'Git status: clean or n/a',
  ].join('\n');
  fs.writeFileSync(SUMMARY, `${body}\n`, 'utf8');
  process.stderr.write(`[ALADDIN] Session summary → .cursor/session/last-summary.md\n`);
  process.stdout.write(raw || '');
}).catch(() => process.exit(0));
