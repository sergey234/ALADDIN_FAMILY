# Курсы USD / USDT и регламент обновления (магазин-бот)

## Зачем два параметра

| Переменная | Смысл | Где используется |
|------------|--------|------------------|
| **`USD_RUB_RATE`** | Сколько **₽ за 1 USD** | Каталог: `price_usd` в `products.yaml` → цена в ₽ (`pricing.quote_product`), заказы в ₽. **Обязательна** (`> 0`), иначе бот и Partner API не стартуют. |
| **`USDT_RUB_RATE`** | Сколько **₽ за 1 USDT** (резерв) | Если включён Crypto Pay, сначала берётся курс из **`getExchangeRates`**, иначе — `USDT_RUB_RATE`, если `> 0`, иначе подставляется **`USD_RUB_RATE`** (прокси; USDT ≠ USD). |

Источник логики: `bot/services/pricing.py`, `bot/services/crypto_pay_api.py` (`resolve_rub_per_usdt`), `bot/services/fx_display.py`.

## Откуда брать «правильные» числа

1. **`USD_RUB_RATE`** — официальный курс ЦБ РФ на дату (или ваша политика: ЦБ+N%, курс банка и т.д.).  
   XML на дату: `https://www.cbr.ru/scripts/XML_daily.asp?date_req=DD.MM.YYYY` (в ответе `USD`, поле `Value` — **₽ за 1 доллар**, запятая в XML = десятичный разделитель).  
   Числовой пример в комментариях см. актуальный `env.example` (значение меняют при выкладке / авто-апдейте).

2. **`USDT_RUB_RATE`** — ЦБ USDT не публикует. **Рекомендация для честного UI:** **`USDT_RUB_RATE=0`** — тогда ориентир «₽ → USDT» в чек-ауте совпадает с курсом прайса (**`USD_RUB_RATE`**), без второго «тайного» числа. Альтернатива: задать вручную (биржа / внутренний спред), если осознанно хотите другой ориентир USDT, чем ₽-прайс. Для **суммы в реальном инвойсе** Crypto Pay / xRocket см. `resolve_rub_per_usdt` в `crypto_pay_api.py`.

## Регламент на проде (`shared/.env`)

| Частота | Действие |
|---------|----------|
| **Ежедневно** (или в день сильной волатильности) | Обновить **`USD_RUB_RATE`** с актуального курса ЦБ (или вашего источника). |
| **При изменении спреда USDT** | Обновить **`USDT_RUB_RATE`**, если используете явное значение. |
| **После правки `.env`** | `systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service` (см. `ML_SYSTEM_HANDOFF_FINAL.md`). |

Проверка: тестовый заказ — сумма в ₽ в боте согласована с ожидаемым `price_usd × USD_RUB_RATE` (с учётом скидок); при крипто-счёте — сумма USDT в инвойсе согласована с `resolve_rub_per_usdt` / политикой в `CRYPTO_PAY_SPEC.md` §3.

## Автоматический режим: ЦБ + 5 ₽

Если хотите поддерживать курс автоматически по политике "официальный ЦБ + 5 ₽":

1. Установите service/timer:

```bash
cp /opt/aladdin-telegram-shop-bot/current_app/docs/fx-rate-sync.service /etc/systemd/system/fx-rate-sync.service
cp /opt/aladdin-telegram-shop-bot/current_app/docs/fx-rate-sync.timer /etc/systemd/system/fx-rate-sync.timer
systemctl daemon-reload
systemctl enable --now fx-rate-sync.timer
systemctl status --no-pager fx-rate-sync.timer
```

2. Ручной прогон:

```bash
systemctl start fx-rate-sync.service
journalctl -u fx-rate-sync.service -n 50 --no-pager
grep '^USD_RUB_RATE=' /opt/aladdin-telegram-shop-bot/shared/.env
```

Как это работает:
- скрипт `scripts/update_usd_rub_rate.py` читает курс USD из XML ЦБ РФ;
- считает `effective = cbr + 5` (порог `--markup-rub`);
- перезаписывает `USD_RUB_RATE` в `shared/.env`;
- флаг **`--usdt-rub-mode`**: в юните `fx-rate-sync.service` по умолчанию **`zero`** — в тот же файл пишется **`USDT_RUB_RATE=0`**, чтобы ориентир USDT в боте не расходился с ежедневно обновляемым ₽-курсом; варианты **`keep`** (не трогать USDT) и **`match-usd`** (подставить то же число, что и `USD_RUB_RATE`);
- перезапускает `aladdin-telegram-bot`, `aladdin-partner-api`, `aladdin-webhook-worker`.

Витрина в боте: **`format_shop_quote_money_html`** в `pricing.py` — при оформлении показывает ₽, эквивалент USD по **`USD_RUB_RATE`** и отдельно номинал из каталога; блок подсказок USDT — **`fx_display.fx_payment_hints_html`** (с пояснением про фиксацию суммы провайдером в счёте).

## Чего не делать

- Не оставлять **`USD_RUB_RATE`** пустым или `0` на проде — процессы упадут при старте с понятной ошибкой из `Settings`.
- Не подменять **`shared/.env`** целиком файлом из git: секреты только на сервере.
