#!/usr/bin/env python3
# ВАРИАНТ 2: Синий грозовой #1E3A8A (новый предложенный)
import os
import sys
from flask import Flask, jsonify


app = Flask(__name__)


@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>VPN Вариант 2</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, sans-serif;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(to bottom, #0f172a 0%, #1E3A8A 50%, #0f172a 100%);
    color: white;
}
.container { text-align: center; padding: 40px; }
h1 { font-size: 3em; color: #F59E0B; margin-bottom: 20px; }
.card { background: rgba(255,255,255,0.95); color: #1E3A8A; padding: 40px; border-radius: 20px; border: 2px solid #F59E0B; margin: 20px; }
.btn { padding: 15px 40px; border: none; border-radius: 10px; font-size: 1.2em; margin: 10px; cursor: pointer; }
.btn-red { background: linear-gradient(135deg, #EF4444, #DC2626); color: white; }
.btn-green { background: linear-gradient(135deg, #10B981, #059669); color: white; }
.color-info { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-top: 20px; }
</style>
</head>
<body>
<div class="container">
    <h1>⚡ ВАРИАНТ 2</h1>
    <div class="card">
        <h2>Синий грозовой: #1E3A8A</h2>
        <p style="margin: 20px 0;">Новый оттенок - более яркий и насыщенный</p>
        <button class="btn btn-red">🔴 ОТКЛЮЧЕНО</button>
        <button class="btn btn-green">🟢 ПОДКЛЮЧЕНО</button>
    </div>
    <div class="color-info">
        <p>Фон: #0f172a → #1E3A8A → #0f172a</p>
        <p>Характер: Яркий, энергичный, вечерняя гроза</p>
    </div>
</div>
</body></html>'''


if __name__ == '__main__':
    print("\n🎨 ВАРИАНТ 2 - Синий #1E3A8A\n→ http://localhost:5002\n")
    app.run(port=5002, debug=False)
