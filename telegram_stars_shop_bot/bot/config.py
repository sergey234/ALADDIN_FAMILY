from __future__ import annotations

from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    admin_ids: str = Field(default="", validation_alias="ADMIN_IDS")
    # Подмножество ADMIN_IDS: финансовые действия (adm:paid/done, зачисление топапа, завершение выкупа и т.д.).
    # Пусто = все из ADMIN_IDS считаются супер-админами (как раньше).
    super_admin_ids: str = Field(default="", validation_alias="SUPER_ADMIN_IDS")

    # ₽ за 1 USD — обязателен в .env на проде (дефолт 0: без переменной бот не стартует — см. model_validator).
    usd_rub_rate: float = Field(default=0.0, validation_alias="USD_RUB_RATE")
    # ₽ за 1 USDT для резерва и подсказок (0 = использовать USD_RUB_RATE при отсутствии курса Crypto Pay).
    usdt_rub_rate: float = Field(default=0.0, validation_alias="USDT_RUB_RATE")

    @model_validator(mode="after")
    def _require_positive_usd_rub(self) -> "Settings":
        if float(self.usd_rub_rate) <= 0:
            raise ValueError(
                "USD_RUB_RATE must be > 0 (₽ per 1 USD). Set it in .env / shared/.env — "
                "see telegram_stars_shop_bot/env.example and docs/FX_RATES_RUNBOOK.md"
            )
        return self

    ref_buyer_discount_percent: float = Field(
        default=7.0, validation_alias="REF_BUYER_FIRST_ORDER_DISCOUNT_PERCENT"
    )
    ref_commission_percent: float = Field(
        default=15.0, validation_alias="REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT"
    )

    # Маркетинг «до X%» на экране 1 (согласуйте с реальной макс. скидкой по акциям).
    marketing_max_discount_percent: float = Field(
        default=47.0, validation_alias="MARKETING_MAX_DISCOUNT_PERCENT"
    )

    stars_wholesale_threshold: int = Field(
        default=500, validation_alias="STARS_WHOLESALE_THRESHOLD"
    )
    stars_wholesale_discount_percent: float = Field(
        default=5.0, validation_alias="STARS_WHOLESALE_DISCOUNT_PERCENT"
    )

    crypto_usdt_trc20: str = Field(default="", validation_alias="CRYPTO_USDT_TRC20")
    crypto_ton: str = Field(default="", validation_alias="CRYPTO_TON")
    # Показывать блок TON в ручной крипто-инструкции (основной канал — USDT TRC20 через Crypto Pay / xRocket).
    crypto_show_ton_manual: bool = Field(default=True, validation_alias="CRYPTO_SHOW_TON_MANUAL")

    # Поддержка и документация API (для кнопок «Поддержка» / «Наш API»).
    support_username: str = Field(default="", validation_alias="SUPPORT_USERNAME")
    # Полная ссылка на поддержку (если задана — приоритет над SUPPORT_USERNAME для URL).
    support_url: str = Field(default="", validation_alias="SUPPORT_URL")
    api_docs_url: str = Field(default="", validation_alias="API_DOCS_URL")
    # Обязателен для Partner HTTP API и выпуска ключей в боте (соль для SHA-256).
    api_key_pepper: str = Field(default="", validation_alias="API_KEY_PEPPER")
    # Через запятую origins для CORS Partner API (пусто = без CORS middleware).
    partner_api_cors_origins: str = Field(default="", validation_alias="PARTNER_API_CORS_ORIGINS")

    # Выкуп Stars: ориентир ₽ за 100 ⭐ для заявки «Продать» (до уточнения оператором).
    sell_offer_rub_per_100_stars: float = Field(
        default=750.0, validation_alias="SELL_OFFER_RUB_PER_100_STARS"
    )
    sell_min_stars: int = Field(default=100, validation_alias="SELL_MIN_STARS")
    sell_max_stars: int = Field(default=50_000, validation_alias="SELL_MAX_STARS")

    # Опционально: file_id картинки для /start (получите через бота и вставьте в .env).
    start_photo_file_id: str = Field(default="", validation_alias="START_PHOTO_FILE_ID")
    # Опционально: file_id картинки для второго экрана онбординга («Почему выбирают нас»).
    start_photo_file_id_2: str = Field(default="", validation_alias="START_PHOTO_FILE_ID_2")

    # Публичные юридические страницы (Telegraph и др.). Пусто = не показывать кнопку в боте.
    privacy_policy_url: str = Field(
        default="https://telegra.ph/Politika-konfidencialnosti-03-24-56",
        validation_alias="PRIVACY_POLICY_URL",
    )
    terms_of_service_url: str = Field(
        default="https://telegra.ph/Polzovatelskoe-soglashenie-03-24-40",
        validation_alias="TERMS_OF_SERVICE_URL",
    )

    # Обязательная подписка на канал перед покупкой (бот должен быть админом канала).
    # ID: @username или -100… ; пусто = проверка отключена.
    required_channel_id: str = Field(default="", validation_alias="REQUIRED_CHANNEL_ID")
    # Ссылка-приглашение t.me/… для кнопки «Подписаться».
    required_channel_invite_url: str = Field(default="", validation_alias="REQUIRED_CHANNEL_INVITE_URL")
    # Заголовок экрана «жёсткой стены» (/start, /menu без подписки). Пусто = «Канал магазина».
    required_channel_display_name: str = Field(default="", validation_alias="REQUIRED_CHANNEL_DISPLAY_NAME")
    # Сколько маркетинга до подписки: full | short (wow+скидки) | title_only. По умолчанию short.
    required_channel_gate_marketing: str = Field(default="short", validation_alias="REQUIRED_CHANNEL_GATE_MARKETING")
    # Видимость карточек в главном меню (false = скрыть кнопку, код/роуты остаются).
    ui_show_api: bool = Field(default=True, validation_alias="UI_SHOW_API")
    ui_show_partners: bool = Field(default=True, validation_alias="UI_SHOW_PARTNERS")
    ui_show_receipts: bool = Field(default=True, validation_alias="UI_SHOW_RECEIPTS")

    # Sentry (бот и Partner API; пустой DSN = выключено).
    sentry_dsn: str = Field(default="", validation_alias="SENTRY_DSN")
    sentry_environment: str = Field(default="", validation_alias="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(default=0.0, validation_alias="SENTRY_TRACES_SAMPLE_RATE")

    # OPS alerts (Telegram/PagerDuty). ALERTS_ENABLED=false => только логи.
    alerts_enabled: bool = Field(default=False, validation_alias="ALERTS_ENABLED")
    alert_telegram_bot_token: str = Field(default="", validation_alias="ALERT_TELEGRAM_BOT_TOKEN")
    alert_telegram_chat_id: str = Field(default="", validation_alias="ALERT_TELEGRAM_CHAT_ID")
    pagerduty_routing_key: str = Field(default="", validation_alias="PAGERDUTY_ROUTING_KEY")
    alert_cooldown_seconds: int = Field(default=300, validation_alias="ALERT_COOLDOWN_SECONDS")
    ops_watchdog_enabled: bool = Field(default=False, validation_alias="OPS_WATCHDOG_ENABLED")
    ops_watchdog_log_scan_lines: int = Field(default=300, validation_alias="OPS_WATCHDOG_LOG_SCAN_LINES")
    ops_watchdog_error_burst_threshold: int = Field(
        default=5, validation_alias="OPS_WATCHDOG_ERROR_BURST_THRESHOLD"
    )
    ops_watchdog_webhook_backlog_warn: int = Field(
        default=50, validation_alias="OPS_WATCHDOG_WEBHOOK_BACKLOG_WARN"
    )
    ops_heartbeat_interval_seconds: int = Field(
        default=1800, validation_alias="OPS_HEARTBEAT_INTERVAL_SECONDS"
    )

    # Входящий вебхук «платёж подтверждён» (HMAC тела, заголовок X-Payment-Signature).
    payment_webhook_secret: str = Field(default="", validation_alias="PAYMENT_WEBHOOK_SECRET")

    # LAVA Business (https://dev.lava.ru/) — фиат, СБП и др. на стороне LAVA.
    lava_shop_id: str = Field(default="", validation_alias="LAVA_SHOP_ID")
    lava_secret_key: str = Field(default="", validation_alias="LAVA_SECRET_KEY")
    # «Дополнительный ключ» из кабинета LAVA — проверка заголовка Authorization на вебхуке.
    lava_webhook_additional_secret: str = Field(default="", validation_alias="LAVA_WEBHOOK_ADDITIONAL_SECRET")
    lava_api_base: str = Field(default="", validation_alias="LAVA_API_BASE")
    # Публичный URL эндпоинта Partner API, например https://shop-api.example.com/v1/payments/lava-webhook
    lava_hook_url: str = Field(default="", validation_alias="LAVA_HOOK_URL")
    lava_success_url: str = Field(default="", validation_alias="LAVA_SUCCESS_URL")
    lava_fail_url: str = Field(default="", validation_alias="LAVA_FAIL_URL")
    lava_invoice_expire_minutes: int = Field(default=720, validation_alias="LAVA_INVOICE_EXPIRE_MINUTES")
    # Список service_id через запятую (пусто = LAVA покажет все доступные методы проекта).
    lava_include_services: str = Field(default="card,sbp", validation_alias="LAVA_INCLUDE_SERVICES")

    # Ckassa (ЦК) — фиат ₽ по API как в WooCommerce-модуле: do-pay/anonymous + callback cbUrl.
    # https://api2.ckassa.ru/api-shop/rs/wordpress/do-pay/anonymous
    ckassa_enabled: bool = Field(default=False, validation_alias="CKASSA_ENABLED")
    ckassa_test_mode: bool = Field(default=False, validation_alias="CKASSA_TEST_MODE")
    ckassa_shop_token: str = Field(default="", validation_alias="CKASSA_SHOP_TOKEN")
    ckassa_secret_key: str = Field(default="", validation_alias="CKASSA_SECRET_KEY")
    # Полный URL do-pay (если пусто — prod или demo по CKASSA_TEST_MODE).
    ckassa_do_pay_url: str = Field(default="", validation_alias="CKASSA_DO_PAY_URL")
    # Публичный HTTPS Partner API для cbUrl (как LAVA_HOOK_URL): …/v1/payments/ckassa-webhook
    ckassa_callback_public_url: str = Field(default="", validation_alias="CKASSA_CALLBACK_PUBLIC_URL")
    ckassa_success_url: str = Field(default="", validation_alias="CKASSA_SUCCESS_URL")
    ckassa_fail_url: str = Field(default="", validation_alias="CKASSA_FAIL_URL")
    ckassa_country: str = Field(default="RU", validation_alias="CKASSA_COUNTRY")
    ckassa_language: str = Field(default="RU", validation_alias="CKASSA_LANGUAGE")
    ckassa_http_timeout_seconds: float = Field(default=15.0, validation_alias="CKASSA_HTTP_TIMEOUT_SECONDS")
    # Плательщик для анонимной формы (если нет email из Telegram — подставляются дефолты).
    ckassa_default_email: str = Field(default="", validation_alias="CKASSA_DEFAULT_EMAIL")
    ckassa_default_phone: str = Field(default="+79990000000", validation_alias="CKASSA_DEFAULT_PHONE")
    ckassa_default_fio: str = Field(default="Покупатель Telegram", validation_alias="CKASSA_DEFAULT_FIO")
    # Поля чека 54-ФЗ для RU (см. WooCommerce Ckassa: taxation, tax, payment_method, payment_object).
    ckassa_receipt_taxation: str = Field(default="usn_income", validation_alias="CKASSA_RECEIPT_TAXATION")
    ckassa_receipt_tax: str = Field(default="none", validation_alias="CKASSA_RECEIPT_TAX")
    ckassa_receipt_payment_method: str = Field(
        default="full_prepayment", validation_alias="CKASSA_RECEIPT_PAYMENT_METHOD"
    )
    ckassa_receipt_payment_object: str = Field(default="service", validation_alias="CKASSA_RECEIPT_PAYMENT_OBJECT")

    # Crypto Pay (@CryptoBot / testnet @CryptoTestnetBot). При CRYPTO_PAY_ENABLED=false — сценарий счёта через API не используется.
    crypto_pay_enabled: bool = Field(default=False, validation_alias="CRYPTO_PAY_ENABLED")
    crypto_pay_api_token: str = Field(default="", validation_alias="CRYPTO_PAY_API_TOKEN")
    crypto_pay_testnet: bool = Field(default=False, validation_alias="CRYPTO_PAY_TESTNET")
    # Полный https://… или только hostname; пусто — pay.crypt.bot / testnet-pay.crypt.bot по CRYPTO_PAY_TESTNET.
    crypto_pay_api_host: str = Field(default="", validation_alias="CRYPTO_PAY_API_HOST")
    crypto_pay_default_asset: str = Field(default="USDT", validation_alias="CRYPTO_PAY_DEFAULT_ASSET")
    crypto_pay_invoice_expire_seconds: int = Field(
        default=3600, validation_alias="CRYPTO_PAY_INVOICE_EXPIRE_SECONDS"
    )
    # После оплаты счёта — кнопка «открыть бота» (https://t.me/…). Пусто = не передаём paid_btn_* в Crypto Pay.
    crypto_pay_paid_btn_url: str = Field(default="", validation_alias="CRYPTO_PAY_PAID_BTN_URL")
    # Если Crypto Pay включён и счёт не создался: показывать ли старый блок с кошельками (для отладки). В проде обычно false.
    crypto_pay_wallet_fallback: bool = Field(default=False, validation_alias="CRYPTO_PAY_WALLET_FALLBACK")

    # xRocket Pay — второй провайдер счёта USDT (TRC20), см. https://docs.xrocket.tg/api/pay/pay-api-overview
    xrocket_pay_enabled: bool = Field(default=False, validation_alias="XROCKET_PAY_ENABLED")
    xrocket_pay_api_key: str = Field(default="", validation_alias="XROCKET_PAY_API_KEY")
    xrocket_pay_api_base: str = Field(
        default="https://pay.xrocket.exchange",
        validation_alias="XROCKET_PAY_API_BASE",
    )

    # Автовыдача Stars/Premium после paid (план 37). Пока только флаги и политика в коде; воркер очереди — позже.
    auto_fulfill_enabled: bool = Field(default=False, validation_alias="AUTO_FULFILL_ENABLED")
    auto_fulfill_stars_enabled: bool = Field(default=False, validation_alias="AUTO_FULFILL_STARS_ENABLED")
    auto_fulfill_premium_enabled: bool = Field(default=False, validation_alias="AUTO_FULFILL_PREMIUM_ENABLED")
    # 0 = без потолка; иначе заказы с rub_after_discounts строго выше порога не берутся в авто (только оператор).
    auto_fulfill_max_order_rub: float = Field(default=0.0, validation_alias="AUTO_FULFILL_MAX_ORDER_RUB")
    auto_fulfill_max_attempts: int = Field(default=5, validation_alias="AUTO_FULFILL_MAX_ATTEMPTS")
    auto_fulfill_poll_interval_seconds: int = Field(
        default=60, validation_alias="AUTO_FULFILL_POLL_INTERVAL_SECONDS"
    )
    # При сбое create у iStar (откат в paid): ops-алерт в ALERT_TELEGRAM_* / PagerDuty (если ALERTS_ENABLED).
    auto_fulfill_failure_alerts_enabled: bool = Field(
        default=True, validation_alias="AUTO_FULFILL_FAILURE_ALERTS_ENABLED"
    )

    # iStar partner API (выдача Stars и Premium). Секреты только в .env на сервере.
    istar_api_key: str = Field(default="", validation_alias="ISTAR_API_KEY")
    istar_api_base: str = Field(
        default="https://v1.fragmentapi.com/api/v1/partner",
        validation_alias="ISTAR_API_BASE",
    )
    istar_wallet_type: str = Field(default="TON", validation_alias="ISTAR_WALLET_TYPE")
    # Подпись вебхука iStar: HMAC-SHA256(raw_body, secret) hex → заголовок X-iStar-Signature (см. istar.fragmentapi.com/docs).
    istar_webhook_secret: str = Field(default="", validation_alias="ISTAR_WEBHOOK_SECRET")

    # Авто-истечение заказов в pending_payment (фоновый цикл в боте). В .env можно задать 0 — выключить.
    # По умолчанию 720 мин (как типичный срок счёта LAVA); для крипты/ручной оплаты тот же таймер.
    order_pending_payment_expire_minutes: int = Field(
        default=720, validation_alias="ORDER_PENDING_PAYMENT_EXPIRE_MINUTES"
    )
    order_pending_payment_sweep_interval_seconds: int = Field(
        default=180, validation_alias="ORDER_PENDING_PAYMENT_SWEEP_INTERVAL_SECONDS"
    )

    # Partner API: in-memory rate limit (окно 60 с). 0 = отключить класс лимита.
    partner_api_rate_limit_api_per_minute: int = Field(
        default=120, validation_alias="PARTNER_API_RATE_LIMIT_API_PER_MINUTE"
    )
    partner_api_rate_limit_webhook_per_minute: int = Field(
        default=90, validation_alias="PARTNER_API_RATE_LIMIT_WEBHOOK_PER_MINUTE"
    )
    partner_api_rate_limit_public_per_minute: int = Field(
        default=400, validation_alias="PARTNER_API_RATE_LIMIT_PUBLIC_PER_MINUTE"
    )
    # Backend хранилища rate-limit: memory (по умолчанию) или redis.
    partner_api_rate_limit_backend: str = Field(
        default="memory", validation_alias="PARTNER_API_RATE_LIMIT_BACKEND"
    )
    redis_url: str = Field(default="", validation_alias="REDIS_URL")
    redis_host: str = Field(default="", validation_alias="REDIS_HOST")
    redis_port: int = Field(default=6379, validation_alias="REDIS_PORT")
    redis_db: int = Field(default=0, validation_alias="REDIS_DB")
    redis_password: str = Field(default="", validation_alias="REDIS_PASSWORD")

    # Мониторинг «paid/processing без движения» (лог WARNING в боте). 0 = выключить цикл.
    stuck_paid_alert_hours: int = Field(default=24, validation_alias="STUCK_PAID_ALERT_HOURS")
    stuck_paid_check_interval_seconds: int = Field(
        default=3600, validation_alias="STUCK_PAID_CHECK_INTERVAL_SECONDS"
    )
    # Отдельный алерт: только processing без обновления дольше N минут (0 = не проверять).
    stuck_processing_alert_minutes: int = Field(
        default=0, validation_alias="STUCK_PROCESSING_ALERT_MINUTES"
    )
    # Порог «долго в работе» для команды /admqueue (список заказов для оператора).
    operator_queue_processing_idle_minutes: int = Field(
        default=30, validation_alias="OPERATOR_QUEUE_PROCESSING_IDLE_MINUTES"
    )

    # Break-glass отчёт по операциям adm:paidbg (0 = выключено).
    break_glass_report_interval_seconds: int = Field(
        default=86400, validation_alias="BREAK_GLASS_REPORT_INTERVAL_SECONDS"
    )
    break_glass_report_lookback_hours: int = Field(
        default=24, validation_alias="BREAK_GLASS_REPORT_LOOKBACK_HOURS"
    )
    # Политический порог для правила «вторые глаза» (док/алерт), 0 = только audit+alert без порога.
    break_glass_two_eyes_threshold_rub: float = Field(
        default=0.0, validation_alias="BREAK_GLASS_TWO_EYES_THRESHOLD_RUB"
    )

    # Повторный запрос счёта LAVA/Crypto для того же order_id: минимальный интервал (0 = без ограничения).
    payment_checkout_invoice_cooldown_seconds: int = Field(
        default=45, validation_alias="PAYMENT_CHECKOUT_INVOICE_COOLDOWN_SECONDS"
    )

    # Топап баланса: сумма и антифрод (0 у лимитов счётчиков = без ограничения).
    topup_min_rub: float = Field(default=100.0, validation_alias="TOPUP_MIN_RUB")
    topup_max_rub: float = Field(default=500_000.0, validation_alias="TOPUP_MAX_RUB")
    topup_max_pending_per_user: int = Field(default=8, validation_alias="TOPUP_MAX_PENDING_PER_USER")
    topup_min_interval_seconds: int = Field(default=60, validation_alias="TOPUP_MIN_INTERVAL_SECONDS")
    # Заказы в ожидании оплаты на одного пользователя (0 = без лимита).
    max_pending_payment_orders_per_user: int = Field(
        default=15, validation_alias="MAX_PENDING_PAYMENT_ORDERS_PER_USER"
    )

    products_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "products.yaml"
    )
    database_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "data" / "shop.db",
        validation_alias="DATABASE_PATH",
    )

    def parsed_admin_ids(self) -> set[int]:
        return _parse_ids_csv(self.admin_ids)

    def parsed_super_admin_ids_explicit(self) -> set[int]:
        """ID из SUPER_ADMIN_IDS (без пересечения с ADMIN)."""
        return _parse_ids_csv(self.super_admin_ids)

    def admin_roles_restricted(self) -> bool:
        """True если задан непустой SUPER_ADMIN_IDS с пересечением с ADMIN — есть роль «оператор»."""
        s = self.parsed_super_admin_ids_explicit()
        if not s:
            return False
        return bool(s & self.parsed_admin_ids())

    def is_super_admin(self, user_id: int) -> bool:
        """Доступ к финансовым / критичным действиям в админке."""
        admins = self.parsed_admin_ids()
        if user_id not in admins:
            return False
        s = self.parsed_super_admin_ids_explicit()
        if not s:
            return True
        effective = s & admins
        if not effective:
            return True
        return user_id in effective

    def lava_include_services_list(self) -> list[str]:
        raw = (self.lava_include_services or "").replace(";", ",")
        return [p.strip() for p in raw.split(",") if p.strip()]

    def auto_fulfill_master_on(self) -> bool:
        """Глобальный переключатель авто-выдачи (воркер ещё может не быть подключён)."""
        return bool(self.auto_fulfill_enabled)

    def crypto_pay_api_origin(self) -> str:
        """Origin без завершающего слэша для вызовов вида {origin}/api/{{method}}."""
        raw = (self.crypto_pay_api_host or "").strip()
        if raw:
            if raw.startswith("http://") or raw.startswith("https://"):
                return raw.rstrip("/")
            return f"https://{raw.rstrip('/')}"
        host = "testnet-pay.crypt.bot" if self.crypto_pay_testnet else "pay.crypt.bot"
        return f"https://{host}"


def _parse_ids_csv(raw: str) -> set[int]:
    out: set[int] = set()
    for part in (raw or "").replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.add(int(part))
        except ValueError:
            continue
    return out


def load_settings() -> Settings:
    return Settings()
