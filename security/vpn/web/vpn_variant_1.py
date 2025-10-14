#!/usr/bin/env python3
# ВАРИАНТ 1: Синий грозовой #1e3a5f (текущий)
import os
import sys
from flask import Flask, jsonify


app = Flask(__name__)


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>VPN Вариант 1</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(to bottom, #0a1128 0%, #1e3a5f 50%, #0a1128 100%);
    color: white;
}
.container { text-align: center; padding: 40px; }
h1 { font-size: 3em; color: #F59E0B; margin-bottom: 20px; }
.card { background: rgba(255,255,255,0.95); color: #1e3a5f; padding: 40px; border-radius: 20px; border: 2px solid #F59E0B; margin: 20px; }
.btn { padding: 15px 40px; border: none; border-radius: 10px; font-size: 1.2em; margin: 10px; cursor: pointer; }
.btn-red { background: linear-gradient(135deg, #EF4444, #DC2626); color: white; }
.btn-green { background: linear-gradient(135deg, #10B981, #059669); color: white; }
.color-info { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-top: 20px; }
</style>
</head>
<body>
<div class="container">
    <h1>⚡ ВАРИАНТ 1</h1>
    <div class="card">
        <h2>Синий грозовой: #1e3a5f</h2>
        <p style="margin: 20px 0;">Текущий оттенок - более глубокий и темный</p>
        <button class="btn btn-red">🔴 ОТКЛЮЧЕНО</button>
        <button class="btn btn-green">🟢 ПОДКЛЮЧЕНО</button>
    </div>
    <div class="color-info">
        <p>Фон: #0a1128 → #1e3a5f → #0a1128</p>
        <p>Характер: Глубокий, таинственный, ночная гроза</p>
    </div>
</div>
</body></html>'''


if __name__ == '__main__':
    print("\n🎨 ВАРИАНТ 1 - Синий #1e3a5f\n→ http://localhost:5001\n")
    app.run(port=5001, debug=False)
