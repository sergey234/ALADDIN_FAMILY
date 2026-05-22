# -*- coding: utf-8 -*-
"""100 off-topic prompts for R4.1 precision gate (ALADDIN must deflect, not general ChatGPT)."""
from __future__ import annotations

# (case_id, message, ui_context)
OFFTOPIC_CASES: list[tuple[str, str, str]] = []

_SEEDS = [
    ("погода в москве завтра", "general"),
    ("сколько градусов в санкт-петербурге", "general"),
    ("рецепт борща пошагово", "general"),
    ("как сварить пельмени", "general"),
    ("диагноз по симптомам температуры", "general"),
    ("какое лекарство от головной боли", "general"),
    ("кто выиграл чемпионат по футболу", "general"),
    ("счёт матча реал мадрид", "general"),
    ("напиши стих про любовь", "general"),
    ("переведи на английский длинный текст про космос", "general"),
    ("курс доллара к рублю", "general"),
    ("когда выборы в сша", "general"),
    ("как починить стиральную машину", "general"),
    ("лучший ноутбук для игр 2026", "general"),
    ("напиши код на python сортировка", "general"),
    ("объясни теорию относительности", "general"),
    ("сколько планет в солнечной системе", "general"),
    ("как вырастить томаты на балконе", "general"),
    ("гороскоп на сегодня овен", "general"),
    ("как познакомиться с девушкой", "general"),
    ("what is the weather in london", "general"),
    ("recipe for chocolate cake", "general"),
    ("who won the super bowl", "general"),
    ("write a poem about the ocean", "general"),
    ("stock price of apple", "general"),
    ("how to fix a leaky faucet", "general"),
    ("best programming language for beginners", "general"),
    ("explain quantum physics simply", "general"),
    ("meditation techniques for sleep", "general"),
    ("travel itinerary for paris 5 days", "general"),
]

for i, (msg, ctx) in enumerate(_SEEDS, start=1):
    OFFTOPIC_CASES.append((f"OT{i:03d}", msg, ctx))

# Дополняем до 100 вариациями (тот же off-topic, другая формулировка)
_EXTRAS = [
    "расскажи про космос подробно",
    "как готовить пиццу",
    "симптомы гриппа что делать",
    "прогноз погоды на неделю",
    "кто президент франции",
    "напиши резюме программиста",
    "как инвестировать в акции",
    "лучшие фильмы 2025",
    "как научиться играть на гитаре",
    "математика интегралы решение",
    "история древнего рима кратко",
    "как похудеть за месяц",
    "йога для начинающих",
    "как выбрать автомобиль",
    "настройка wordpress сайта",
    "криптовалюта bitcoin прогноз",
    "как завести кота",
    "садоводство весной советы",
    "make me a diet plan",
    "translate hello how are you to spanish",
    "nba finals winner",
    "javascript async await tutorial",
    "climate change essay",
    "best hotels in tokyo",
    "how to learn french fast",
    "vitamin d dosage",
    "marathon training schedule",
    "wedding speech template",
    "dog training tips",
    "coffee brewing methods",
    "tell me a joke about politics",
    "who is elon musk biography",
    "calculus homework help",
    "minecraft building ideas",
    "instagram growth hacks",
    "tax declaration help russia",
    "mortgage calculator explain",
    "astrology compatibility scorpio",
    "philosophy of kant summary",
    "chess opening strategy",
    "photo editing lightroom",
    "knitting pattern scarf",
    "wine pairing with steak",
    "baby sleep schedule",
    "electric car comparison",
    "home workout without equipment",
    "spanish grammar subjunctive",
    "climate in dubai december",
    "how to write a novel",
    "best sci-fi books list",
    "garden pests tomatoes",
    "piano chords beginner",
    "networking career advice",
    "public speaking fear",
    "time management techniques",
    "renewable energy overview",
    "ocean animals facts",
    "volcano eruption causes",
    "medieval europe map",
    "french revolution causes",
    "machine learning vs deep learning",
    "cloud computing aws basics",
    "database sql join explain",
    "mobile game recommendations",
    "anime plot ideas",
    "fashion trends spring",
    "interior design small apartment",
    "legal advice divorce",
    "immigration visa usa",
    "language learning app compare",
    "podcast topic ideas",
    "birthday gift ideas teen",
    "camping gear list",
    "scuba diving certification",
]

idx = len(OFFTOPIC_CASES) + 1
for msg in _EXTRAS:
    if len(OFFTOPIC_CASES) >= 100:
        break
    OFFTOPIC_CASES.append((f"OT{idx:03d}", msg, "general"))
    idx += 1

assert len(OFFTOPIC_CASES) == 100, len(OFFTOPIC_CASES)
