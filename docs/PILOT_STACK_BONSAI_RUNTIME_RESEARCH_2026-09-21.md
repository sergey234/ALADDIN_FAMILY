# Bonsai 2 runtime research — без install (`ps-b-01`)

**Дата:** 2026-09-21  
**Источники:** [HF collection Bonsai-2](https://huggingface.co/collections/prism-ml/bonsai-2) · [GGUF card](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf) · [MLX card](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-mlx-2bit)  
**Канон пилота:** `docs/ML_SYSTEM_LOCAL_LLM_BONSAI_PILOT.md`

---

## 1. Что это

| | |
|--|--|
| Модель | Ternary Bonsai 2 **27B** (из Qwen3.8-27B) |
| Качество | ~**98.2%** среднего FP16 на 14 бенчах; coding ≈ уровня базы |
| Размер LM | ~**5.9 GB** (GGUF PTQ1_0) / ~**7.2 GB** (PQ2_0) |
| Контекст | до **262K** (на практике ставить меньше под RAM) |
| Multimodal | vision tower отдельно (~0.6–0.9 GB); для draft кода **не обязателен** |
| Лицензия | Apache 2.0 |

---

## 2. Критично: наш Mac

| Факт | Значение |
|------|----------|
| CPU | **Intel** Core i7-4850HQ |
| RAM | **16 GB** |
| Arch | x86_64 |

### Следствия

| Вариант | Подходит? |
|---------|-----------|
| **MLX** (`…-mlx-2bit`) | ❌ только Apple Silicon |
| **llama.cpp Metal** | ❌ Metal = Apple GPU |
| **PrismML llama.cpp fork + CPU** (или CUDA если есть eGPU — у нас нет) | ⚠️ **единственный реалистичный путь** |
| Stock Ollama / stock llama.cpp | ❌ ternary PTQ1_0/PQ2_0 **не** едят / дают мусор |
| Текущий Ollama `qwen2.5-0.5b` | ✅ уже есть, но это **не** Bonsai |

**Ожидание на Intel 16 GB:** модель влезет в RAM с трудом; скорость будет **низкая** (не 28–47 tok/s как на M-series). Пилот всё ещё полезен для «offline draft / night cheap», но не как замена Claude по скорости.

---

## 3. Правильный runtime (когда будет GO)

**SSOT запуска у PrismML:** репо `PrismML-Eng/Bonsai-demo` (pinned binaries).  
**Fork llama.cpp:** `https://github.com/PrismML-Eng/llama.cpp` + [releases](https://github.com/PrismML-Eng/llama.cpp/releases/latest).

Рекомендуемый pack для Mac Intel:

1. Скачать **prebuilt** `llama-*-bin-*` под платформу **или** собрать fork **без** CUDA.  
2. Веса: `prism-ml/Ternary-Bonsai-2-27B-gguf` → файл **`Ternary-Bonsai-2-27B-PQ2_0.gguf`** (~7.2 GB; на Apple измеряли PQ2_0; на CPU тоже ок) **или** PTQ1_0 (~5.95 GB) если места впритык.  
3. Каталог весов: **`/Volumes/Disk/ALADDIN_LOCAL_LLM/bonsai2/weights/`** (не `~/`, не git).  
4. Smoke (после GO):

```bash
./bin/llama-cli -m …/Ternary-Bonsai-2-27B-PTQ1_0.gguf \
  -ngl 0 -c 8192 \
  --temp 1.0 --top-p 0.95 --top-k 20 \
  -p "Say hello in one sentence." -n 64
```

**GGUF на 16 GB RAM:** предпочитать **PTQ1_0 (~5.95 GB)**, не PQ2_0 (~7.2), пока smoke не докажет запас RAM.

`-ngl 0` = CPU-only на Intel. Контекст начать с **8K–16K**, не 262K.

### Orch wire (ещё более поздний GO `ps-b-06`)

- Сейчас draft → binary `ollama`.  
- Варианты: (a) HTTP server из fork (`llama-server`) + новый adapter; (b) wrapper script как harness.  
- Review/merge → **никогда** на Bonsai (`require_premium_review: true`).

---

## 4. Чеклист install (не выполнять без GO)

- [ ] Прочитан этот файл + pilot doc  
- [ ] Владелец: `GO Bonsai runtime`  
- [ ] Создать `~/ALADDIN_LOCAL_LLM/` (gitignore / вне репо)  
- [ ] Скачать PrismML llama.cpp release  
- [ ] `hf download` GGUF PQ2_0 или PTQ1_0  
- [ ] Smoke prompt + замер tok/s и RSS  
- [ ] Записать в journal → затем ждать `GO Bonsai orch wire`

---

## 5. Статус `ps-b-01`

✅ Research закрыт. Install = `ps-b-02+` только с GO.
