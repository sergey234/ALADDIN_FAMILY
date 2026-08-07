from __future__ import annotations

from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Страница Ckassa Market «произвольная сумма» магазина: подставляется, если CKASSA_BC_UNIVERSAL_PAYMENT_URL пуст.
DEFAULT_CKASSA_BC_UNIVERSAL_PAYMENT_URL = "https://bc.ckassa.ru/u6lfph2p6e"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    # Публичный @username магазин-бота без @ — для редиректа /r/{code} → t.me (vpn-12). Пусто = редирект 503.
    shop_bot_username: str = Field(default="", validation_alias="SHOP_BOT_USERNAME")
    admin_ids: str = Field(default="", validation_alias="ADMIN_IDS")
    # Подмножество ADMIN_IDS: финансовые действия (adm:paid/done, зачисление топапа и т.д.).
    # Пусто = все из ADMIN_IDS считаются супер-админами (как раньше).
    super_admin_ids: str = Field(default="", validation_alias="SUPER_ADMIN_IDS")

    # ₽ за 1 USD - обязателен в .env на проде (дефолт 0: без переменной бот не стартует - см. model_validator).
    usd_rub_rate: float = Field(default=0.0, validation_alias="USD_RUB_RATE")
    # ₽ за 1 USDT для резерва и подсказок (0 = использовать USD_RUB_RATE при отсутствии курса Crypto Pay).
    usdt_rub_rate: float = Field(default=0.0, validation_alias="USDT_RUB_RATE")

    @model_validator(mode="after")
    def _require_positive_usd_rub(self) -> "Settings":
        if float(self.usd_rub_rate) <= 0:
            raise ValueError(
                "USD_RUB_RATE must be > 0 (₽ per 1 USD). Set it in .env / shared/.env - "
                "see telegram_stars_shop_bot/env.example and docs/FX_RATES_RUNBOOK.md"
            )
        return self

    @model_validator(mode="after")
    def _default_ckassa_bc_universal_url(self) -> "Settings":
        u = (self.ckassa_bc_universal_payment_url or "").strip()
        if u:
            return self
        lava_ready = bool(
            (self.lava_shop_id or "").strip()
            and (self.lava_secret_key or "").strip()
            and (self.lava_hook_url or "").strip()
        )
        # Не подставляем Ckassa BC по умолчанию, если основной фиат — LAVA.
        if lava_ready:
            return self
        object.__setattr__(self, "ckassa_bc_universal_payment_url", DEFAULT_CKASSA_BC_UNIVERSAL_PAYMENT_URL)
        return self

    ref_buyer_discount_percent: float = Field(
        default=0.0, validation_alias="REF_BUYER_FIRST_ORDER_DISCOUNT_PERCENT"
    )
    ref_commission_percent: float = Field(
        default=15.0, validation_alias="REF_REFERRER_COMMISSION_FIRST_ORDER_PERCENT"
    )
    # true = бонус только VPN; false = spend на VPN+Stars+Premium (канон 2026-07-28).
    # На проде держим false; антиабуз — гейтами вывода + уровнями.
    ref_bonus_vpn_only: bool = Field(default=False, validation_alias="REF_BONUS_VPN_ONLY")

    # Админ-аналитика / чистая прибыль.
    # Legacy единый % (deprecated): используется только если per-rail не заданы / миграция.
    payment_gateway_fee_percent: float = Field(default=3.0, validation_alias="PAYMENT_GATEWAY_FEE_PERCENT")
    # FIN: комиссии по способу оплаты (%).
    fee_lava_card_percent: float = Field(default=6.0, validation_alias="FEE_LAVA_CARD_PERCENT")
    fee_sbp_percent: float = Field(default=3.4, validation_alias="FEE_SBP_PERCENT")
    fee_crypto_bot_percent: float = Field(default=3.0, validation_alias="FEE_CRYPTO_BOT_PERCENT")
    fee_xrocket_percent: float = Field(default=1.5, validation_alias="FEE_XROCKET_PERCENT")
    # Доля каталожного USD в ₽ как legacy-оценка COGS (если нет Fragment qty/months).
    auto_cogs_usd_fraction: float = Field(default=0.85, validation_alias="AUTO_COGS_USD_FRACTION")
    # Себестоимость VPN в снимке (legacy); по ТЗ FIN для VPN в snapshot = 0.
    vpn_cogs_rub: float = Field(default=0.0, validation_alias="VPN_COGS_RUB")
    # Оценка аренды серверов на бизнес-дашборде (₽/мес). 0 = не показывать «после аренды».
    vpn_rent_monthly_rub: float = Field(default=0.0, validation_alias="VPN_RENT_MONTHLY_RUB")
    # Fragment закуп USDT (1 USD ≈ 1 USDT).
    fragment_star_usdt: float = Field(default=0.015, validation_alias="FRAGMENT_STAR_USDT")
    fragment_premium_3m_usdt: float = Field(default=11.99, validation_alias="FRAGMENT_PREMIUM_3M_USDT")
    fragment_premium_6m_usdt: float = Field(default=15.99, validation_alias="FRAGMENT_PREMIUM_6M_USDT")
    fragment_premium_12m_usdt: float = Field(default=28.99, validation_alias="FRAGMENT_PREMIUM_12M_USDT")
    # Premium 1м — закуп Fragment = 11.99 USDT (как 3м); пользователю не светить.
    fragment_premium_1m_usdt: float = Field(default=11.99, validation_alias="FRAGMENT_PREMIUM_1M_USDT")

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
    # Показывать блок TON в ручной крипто-инструкции (основной канал - USDT через Crypto Pay / xRocket).
    crypto_show_ton_manual: bool = Field(default=True, validation_alias="CRYPTO_SHOW_TON_MANUAL")

    # Поддержка и документация API (для кнопок «Поддержка» / «Наш API»).
    support_username: str = Field(default="", validation_alias="SUPPORT_USERNAME")
    # Полная ссылка на поддержку (если задана - приоритет над SUPPORT_USERNAME для URL).
    support_url: str = Field(default="", validation_alias="SUPPORT_URL")
    api_docs_url: str = Field(default="", validation_alias="API_DOCS_URL")

    # ---------------------------------------------------------------------------
    # Помощник AiMonkey (ИИ-оператор поддержки) — PRD PLAN_AIMONKEY_ASSISTANT_V1
    # Kill-switch: ASSISTANT_ENABLED=false. Первая неделя: ASSISTANT_ADMIN_ONLY=true.
    # ---------------------------------------------------------------------------
    assistant_enabled: bool = Field(default=False, validation_alias="ASSISTANT_ENABLED")
    assistant_admin_only: bool = Field(default=True, validation_alias="ASSISTANT_ADMIN_ONLY")
    assistant_llm_base_url: str = Field(default="", validation_alias="ASSISTANT_LLM_BASE_URL")
    assistant_llm_api_key: str = Field(default="", validation_alias="ASSISTANT_LLM_API_KEY")
    assistant_llm_model: str = Field(default="", validation_alias="ASSISTANT_LLM_MODEL")
    # Comma-separated fallbacks (tried on 402/429/5xx). Empty + OpenRouter → built-in free chain.
    assistant_llm_fallback_models: str = Field(
        default="",
        validation_alias="ASSISTANT_LLM_FALLBACK_MODELS",
    )
    assistant_admin_chat_id: str = Field(default="", validation_alias="ASSISTANT_ADMIN_CHAT_ID")
    assistant_daily_msg_limit: int = Field(default=40, validation_alias="ASSISTANT_DAILY_MSG_LIMIT")
    assistant_session_max_turns: int = Field(default=20, validation_alias="ASSISTANT_SESSION_MAX_TURNS")
    assistant_session_ttl_min: int = Field(default=30, validation_alias="ASSISTANT_SESSION_TTL_MIN")
    assistant_max_out_tokens: int = Field(default=800, validation_alias="ASSISTANT_MAX_OUT_TOKENS")
    assistant_llm_timeout_sec: int = Field(default=45, validation_alias="ASSISTANT_LLM_TIMEOUT_SEC")
    assistant_ticket_daily_limit: int = Field(default=5, validation_alias="ASSISTANT_TICKET_DAILY_LIMIT")
    assistant_pay_sla_min: int = Field(default=30, validation_alias="ASSISTANT_PAY_SLA_MIN")
    assistant_embedding_url: str = Field(default="", validation_alias="ASSISTANT_EMBEDDING_URL")
    # Бренд-голос v1.1: few-shot эталоны + расширенные tone rules. Kill-switch без выключения всего ИИ.
    assistant_brand_voice_enabled: bool = Field(
        default=True,
        validation_alias="ASSISTANT_BRAND_VOICE_ENABLED",
    )
    # Обязателен для Partner HTTP API и выпуска ключей в боте (соль для SHA-256).
    api_key_pepper: str = Field(default="", validation_alias="API_KEY_PEPPER")
    # Через запятую origins для CORS Partner API (пусто = без CORS middleware).
    partner_api_cors_origins: str = Field(default="", validation_alias="PARTNER_API_CORS_ORIGINS")

    # Опционально: file_id вместо локального assets/branding/monkey.jpg (fallback: monkey_stars_logo.png).
    start_photo_file_id: str = Field(default="", validation_alias="START_PHOTO_FILE_ID")
    # Опционально: file_id картинки для второго экрана онбординга («Почему выбирают нас»).
    start_photo_file_id_2: str = Field(default="", validation_alias="START_PHOTO_FILE_ID_2")
    # Видео: смена региона App Store для Happ (file_id). Пусто = assets/vpn/happ_appstore_region_guide.mp4
    vpn_happ_region_video_file_id: str = Field(
        default="", validation_alias="VPN_HAPP_REGION_VIDEO_FILE_ID"
    )

    # Публичные юридические страницы (HTTPS Partner API /v1/legal/*). Пусто = не показывать кнопку в боте.
    privacy_policy_url: str = Field(
        default="https://aimonkeystars.ru/v1/legal/privacy",
        validation_alias="PRIVACY_POLICY_URL",
    )
    terms_of_service_url: str = Field(
        default="https://aimonkeystars.ru/v1/legal/terms",
        validation_alias="TERMS_OF_SERVICE_URL",
    )
    public_offer_url: str = Field(
        default="https://aimonkeystars.ru/v1/legal/offer",
        validation_alias="PUBLIC_OFFER_URL",
    )
    refund_policy_url: str = Field(
        default="https://aimonkeystars.ru/v1/legal/refund",
        validation_alias="REFUND_POLICY_URL",
    )
    # Страница/канал «Новости» в хабе. Пусто = OFFICIAL/REQUIRED_CHANNEL (t.me AiMonkey).
    # Не ставить aimonkeystars.ru/news.html — кнопка ведёт в новостной канал бота.
    news_channel_page_url: str = Field(
        default="",
        validation_alias="NEWS_CHANNEL_PAGE_URL",
    )

    # Обязательная подписка на канал перед покупкой (бот должен быть админом канала).
    # ID: @username или -100… ; пусто = проверка отключена.
    required_channel_id: str = Field(default="", validation_alias="REQUIRED_CHANNEL_ID")
    # Ссылка-приглашение t.me/… для кнопки «Подписаться».
    required_channel_invite_url: str = Field(default="", validation_alias="REQUIRED_CHANNEL_INVITE_URL")
    # Запасная ссылка на канал для текста оферты / юридических подсказок, если REQUIRED_CHANNEL_INVITE_URL пуст.
    official_channel_invite_url: str = Field(
        default="https://t.me/+xwj4zZo4bNphZjVi",
        validation_alias="OFFICIAL_CHANNEL_INVITE_URL",
    )
    # Заголовок экрана «жёсткой стены» (/start, /menu без подписки). Пусто = «Канал магазина».
    required_channel_display_name: str = Field(default="", validation_alias="REQUIRED_CHANNEL_DISPLAY_NAME")
    # Сколько маркетинга до подписки: full | short (wow+скидки) | title_only. По умолчанию short.
    required_channel_gate_marketing: str = Field(default="short", validation_alias="REQUIRED_CHANNEL_GATE_MARKETING")
    # Видимость карточек в главном меню (false = скрыть кнопку, код/роуты остаются).
    ui_show_api: bool = Field(default=True, validation_alias="UI_SHOW_API")
    ui_show_partners: bool = Field(default=True, validation_alias="UI_SHOW_PARTNERS")
    ui_show_receipts: bool = Field(default=True, validation_alias="UI_SHOW_RECEIPTS")
    # Отдельный продуктовый модуль VPN (главное меню + /vpn). Доступ после оплаты, без триала. См. docs/VPN_SHOP_INTEGRATION_PLAN.md, docs/VPN_SHOP_API.md
    ui_show_vpn: bool = Field(default=True, validation_alias="UI_SHOW_VPN")
    ui_show_gifts: bool = Field(default=False, validation_alias="UI_SHOW_GIFTS")
    vpn_api_base_url: str = Field(default="", validation_alias="VPN_API_BASE_URL")
    vpn_api_hmac_secret: str = Field(default="", validation_alias="VPN_API_HMAC_SECRET")
    # vpn-25: circuit breaker к aladdin-shop-vpn-api (in-process, один процесс бота).
    vpn_api_circuit_failure_threshold: int = Field(
        default=5, ge=1, le=50, validation_alias="VPN_API_CIRCUIT_FAILURE_THRESHOLD"
    )
    vpn_api_circuit_failure_window_seconds: int = Field(
        default=120, ge=10, le=3600, validation_alias="VPN_API_CIRCUIT_FAILURE_WINDOW_SECONDS"
    )
    vpn_api_circuit_open_seconds: int = Field(
        default=60, ge=5, le=3600, validation_alias="VPN_API_CIRCUIT_OPEN_SECONDS"
    )
    vpn_api_http_max_retries: int = Field(default=2, ge=0, le=5, validation_alias="VPN_API_HTTP_MAX_RETRIES")
    # Публичные markdown VPN (nginx → aladdin-shop-vpn-api). Без завершающего слэша.
    vpn_docs_public_base: str = Field(
        default="https://aimonkeystars.ru/v1/legal",
        validation_alias="VPN_DOCS_PUBLIC_BASE",
    )
    # Происхождение для ссылок /sub/… в тексте бота (тот же хост, что и HTTPS магазина).
    vpn_public_https_origin: str = Field(
        default="https://aimonkeystars.ru",
        validation_alias="VPN_PUBLIC_HTTPS_ORIGIN",
    )
    # Публичная витрина web-checkout (aimonkeystars; get.aladdin → 302).
    web_checkout_enabled: bool = Field(default=True, validation_alias="WEB_CHECKOUT_ENABLED")
    web_checkout_public_origin: str = Field(
        default="https://aimonkeystars.ru",
        validation_alias="WEB_CHECKOUT_PUBLIC_ORIGIN",
    )
    # Зеркало /sub/ на .com (vpn-domain-com). Пусто = кнопка скрыта.
    vpn_subscription_mirror_origin: str = Field(
        default="",
        validation_alias="VPN_SUBSCRIPTION_MIRROR_ORIGIN",
    )
    # Упрощённый UX: одна подписка из 3 профилей (vpn-ux-auto). Синхронизировать с VPN API env.
    vpn_ux_auto_enabled: bool = Field(default=False, validation_alias="VPN_UX_AUTO_ENABLED")
    vpn_sub_mirror_health_enabled: bool = Field(
        default=True, validation_alias="VPN_SUB_MIRROR_HEALTH_ENABLED"
    )
    # Кнопка «Новости» в разделе VPN. Пусто = REQUIRED_CHANNEL_INVITE_URL, иначе OFFICIAL_CHANNEL_INVITE_URL.
    vpn_news_channel_url: str = Field(default="", validation_alias="VPN_NEWS_CHANNEL_URL")
    vpn_status_channel_post_id: str = Field(
        default="", validation_alias="VPN_STATUS_CHANNEL_POST_ID"
    )
    # Опционально: внешняя страница о VPN (HTTPS). Кнопка в маркетинг-блоке; не Telegram Web App.
    vpn_marketing_landing_url: str = Field(default="", validation_alias="VPN_MARKETING_LANDING_URL")
    # Хаб длинных инструкций (Teletype / свой сайт). Кнопка «Полная инструкция» в боте; пусто = fallback на VPN_MARKETING_LANDING_URL.
    vpn_instructions_url: str = Field(default="", validation_alias="VPN_INSTRUCTIONS_URL")
    # JSON: список локаций для экрана «Локации» в боте (см. docs/VPN_LOCATIONS_JSON.md). Пусто = встроенный MVP-список.
    vpn_locations_json: str = Field(default="", validation_alias="VPN_LOCATIONS_JSON")
    # Сколько строк в свёрнутом виде при использовании VPN_LOCATIONS_JSON (1..50).
    vpn_locations_preview_n: int = Field(default=3, ge=1, le=50, validation_alias="VPN_LOCATIONS_PREVIEW_N")
    # Тянуть список локаций из VPN API (GET /internal/v1/locations/catalog) вместо только VPN_LOCATIONS_JSON в боте.
    vpn_locations_from_api: bool = Field(default=False, validation_alias="VPN_LOCATIONS_FROM_API")
    # Бонусные дни VPN при первой выданной VPN-покупке приглашённого (0 = не начислять эту сторону).
    # Платный VPN-реф: пригласивший +3, друг +7 (первая оплата VPN).
    vpn_referral_referrer_days: int = Field(default=3, validation_alias="VPN_REFERRAL_REFERRER_DAYS")
    vpn_referral_friend_days: int = Field(default=7, validation_alias="VPN_REFERRAL_FRIEND_DAYS")
    # Пробный VPN-реф: пригласивший +1, другу 3 дня trial (первая активация trial по ref_).
    vpn_trial_referral_referrer_days: int = Field(
        default=1, validation_alias="VPN_TRIAL_REFERRAL_REFERRER_DAYS"
    )
    vpn_trial_referral_friend_days: int = Field(
        default=3, validation_alias="VPN_TRIAL_REFERRAL_FRIEND_DAYS"
    )
    # Путь к vpn.db (aladdin-shop-vpn-api) для снимка peer/jobs/p95 в /admin. Пусто = блок не читается.
    vpn_db_path: str = Field(default="", validation_alias="VPN_DB_PATH")
    # После paid + provision: автоматически прислать .conf в чат (poll wg/conf).
    vpn_auto_send_wg_after_paid: bool = Field(default=True, validation_alias="VPN_AUTO_SEND_WG_AFTER_PAID")
    vpn_auto_send_happ_after_paid: bool = Field(
        default=True, validation_alias="VPN_AUTO_SEND_HAPP_AFTER_PAID"
    )
    vpn_provision_delivery_timeout_seconds: int = Field(
        default=120, ge=30, le=600, validation_alias="VPN_PROVISION_DELIVERY_TIMEOUT_SECONDS"
    )
    vpn_provision_delivery_poll_seconds: int = Field(
        default=3, ge=1, le=30, validation_alias="VPN_PROVISION_DELIVERY_POLL_SECONDS"
    )
    # После авто-📥 прислать 📷 QR (тот же .conf).
    vpn_auto_send_qr_after_paid: bool = Field(default=True, validation_alias="VPN_AUTO_SEND_QR_AFTER_PAID")
    # Фон: проверка VPN API /ready, vpn.db, алерт админам. 0 = выключено.
    vpn_ops_health_interval_seconds: int = Field(
        default=300, ge=0, le=86400, validation_alias="VPN_OPS_HEALTH_INTERVAL_SECONDS"
    )
    vpn_ops_health_stale_job_minutes: int = Field(
        default=10, ge=1, le=120, validation_alias="VPN_OPS_HEALTH_STALE_JOB_MINUTES"
    )
    vpn_ops_health_provisioning_warn_threshold: int = Field(
        default=5, ge=0, le=500, validation_alias="VPN_OPS_HEALTH_PROVISIONING_WARN_THRESHOLD"
    )
    # Проба /health и /ready: ретраи и порог CRITICAL (не спамить при 1–2 сек restart).
    vpn_ops_health_probe_retries: int = Field(
        default=3, ge=1, le=8, validation_alias="VPN_OPS_HEALTH_PROBE_RETRIES"
    )
    vpn_ops_health_probe_delay_seconds: float = Field(
        default=1.0, ge=0.2, le=10.0, validation_alias="VPN_OPS_HEALTH_PROBE_DELAY_SECONDS"
    )
    vpn_ops_health_critical_after: int = Field(
        default=2, ge=1, le=10, validation_alias="VPN_OPS_HEALTH_CRITICAL_AFTER"
    )
    # Повторный Telegram-алерт при том же degraded/critical (swap и т.п.). По умолчанию 5 ч.
    vpn_ops_health_alert_cooldown_seconds: int = Field(
        default=18000, ge=60, le=86400, validation_alias="VPN_OPS_HEALTH_ALERT_COOLDOWN_SECONDS"
    )
    # Полный дайджест метрик простым языком в ops-чат (не алерт). 0 = выкл. По умолч. 5 ч.
    vpn_path_digest_enabled: bool = Field(default=True, validation_alias="VPN_PATH_DIGEST_ENABLED")
    vpn_path_digest_interval_seconds: int = Field(
        default=3600, ge=0, le=86400, validation_alias="VPN_PATH_DIGEST_INTERVAL_SECONDS"
    )
    vpn_bridge_health_host: str = Field(
        default="37.46.134.98", validation_alias="VPN_BRIDGE_HEALTH_HOST"
    )
    vpn_bridge_health_port: int = Field(default=8444, validation_alias="VPN_BRIDGE_HEALTH_PORT")
    # JSON от vpn_bridge_peers_guard.py (зомби RU-bridge для /vpn_health и /vpn_zombies).
    vpn_bridge_peers_status_path: str = Field(
        default="/opt/aladdin-shop-vpn-api/var/bridge_peers_status.json",
        validation_alias="VPN_BRIDGE_PEERS_STATUS_PATH",
    )
    vpn_bridge_status_max_age_sec: int = Field(
        default=10800, ge=300, le=86400, validation_alias="VPN_BRIDGE_STATUS_MAX_AGE_SEC"
    )
    # /vpn_health: CSV path metrics (CF/sessions/swap/RTT). Contabo local + NEW entry via SSH.
    vpn_path_metrics_enabled: bool = Field(default=True, validation_alias="VPN_PATH_METRICS_ENABLED")
    vpn_path_metrics_csv: str = Field(
        default="/var/lib/aladdin-vpn-ops/path_host_metrics.csv",
        validation_alias="VPN_PATH_METRICS_CSV",
    )
    vpn_path_metrics_remote_host: str = Field(
        default="37.46.134.98", validation_alias="VPN_PATH_METRICS_REMOTE_HOST"
    )
    vpn_path_metrics_ssh_key: str = Field(
        default="/root/.ssh/id_ed25519", validation_alias="VPN_PATH_METRICS_SSH_KEY"
    )
    vpn_path_metrics_ssh_user: str = Field(
        default="root", validation_alias="VPN_PATH_METRICS_SSH_USER"
    )
    # Фон: повтор add-subscription-days при падении VPN API. 0 = выключено.
    vpn_referral_api_retry_interval_seconds: int = Field(
        default=300, validation_alias="VPN_REFERRAL_API_RETRY_INTERVAL_SECONDS"
    )
    vpn_referral_api_max_attempts_per_side: int = Field(
        default=12, validation_alias="VPN_REFERRAL_API_MAX_ATTEMPTS_PER_SIDE"
    )
    # Напоминания об окончании VPN (платные d7/d3/d1/h6). ≥900с для окна h6. 0 = выкл.
    vpn_expiry_notify_enabled: bool = Field(default=True, validation_alias="VPN_EXPIRY_NOTIFY_ENABLED")
    vpn_expiry_notify_interval_seconds: int = Field(
        default=900, ge=0, le=604800, validation_alias="VPN_EXPIRY_NOTIFY_INTERVAL_SECONDS"
    )
    # d10: пуш при первом /sub устройства (опрос vpn.db).
    vpn_device_first_notify_enabled: bool = Field(
        default=True, validation_alias="VPN_DEVICE_FIRST_NOTIFY_ENABLED"
    )
    vpn_device_first_notify_interval_seconds: int = Field(
        default=60, ge=0, le=3600, validation_alias="VPN_DEVICE_FIRST_NOTIFY_INTERVAL_SECONDS"
    )
    vpn_sub_access_alert_per_hour: int = Field(
        default=120, ge=0, validation_alias="VPN_SUB_ACCESS_ALERT_PER_HOUR"
    )
    vpn_trial_enabled: bool = Field(default=False, validation_alias="VPN_TRIAL_ENABLED")
    vpn_trial_hours: int = Field(default=72, ge=1, le=168, validation_alias="VPN_TRIAL_HOURS")
    vpn_trial_min_account_age_hours: int = Field(
        default=0, ge=0, validation_alias="VPN_TRIAL_MIN_ACCOUNT_AGE_HOURS"
    )
    vpn_trial_reminder_interval_seconds: int = Field(
        default=900, ge=60, le=3600, validation_alias="VPN_TRIAL_REMINDER_INTERVAL_SECONDS"
    )
    # Allowlist JSON для ops-теста 3 дня trial → +N вознаграждение (см. vpn_trial_plus7_reward).
    vpn_trial_plus7_queue_path: str = Field(
        default="/opt/aladdin-shop-vpn-api/var/vpn_trial_plus7_queue.json",
        validation_alias="VPN_TRIAL_PLUS7_QUEUE_PATH",
    )

    def resolved_vpn_db_path(self) -> Path | None:
        raw = (self.vpn_db_path or "").strip()
        if not raw:
            return None
        return Path(raw).expanduser()
    start_command_min_interval_seconds: int = Field(
        default=2, validation_alias="START_COMMAND_MIN_INTERVAL_SECONDS"
    )
    order_create_min_interval_seconds: int = Field(
        default=3, validation_alias="ORDER_CREATE_MIN_INTERVAL_SECONDS"
    )
    # После успешной капчи на чек-ауте — короткое окно (чтобы auto-finalize успел).
    # По умолчанию ~3 мин; после создания заказа окно сбрасывается (см. once_per_order).
    checkout_captcha_ttl_seconds: int = Field(default=180, validation_alias="CHECKOUT_CAPTCHA_TTL_SECONDS")
    # true: каждый новый заказ требует капчу заново (после create — clear ok_until).
    checkout_captcha_once_per_order: bool = Field(
        default=True, validation_alias="CHECKOUT_CAPTCHA_ONCE_PER_ORDER"
    )

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
    # true — этот хост делает getUpdates для Shop Bot. На MAIN (только API) — false.
    shop_bot_polling_enabled: bool = Field(default=True, validation_alias="SHOP_BOT_POLLING_ENABLED")
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
    # KPI alerts в watchdog (split-core). OPS_WATCHDOG_KPI_DAYS=0 отключает блок KPI.
    ops_watchdog_kpi_days: int = Field(default=7, validation_alias="OPS_WATCHDOG_KPI_DAYS")
    # Payment funnel: minimum paid-rate from created orders.
    ops_alert_payment_success_min_pct: float = Field(
        default=85.0, validation_alias="OPS_ALERT_PAYMENT_SUCCESS_MIN_PCT"
    )
    ops_alert_payment_min_created_orders: int = Field(
        default=20, validation_alias="OPS_ALERT_PAYMENT_MIN_CREATED_ORDERS"
    )
    # Webhook SLA: minimum success-rate and maximum p95 latency.
    ops_alert_webhook_success_min_pct: float = Field(
        default=95.0, validation_alias="OPS_ALERT_WEBHOOK_SUCCESS_MIN_PCT"
    )
    ops_alert_webhook_p95_max_sec: float = Field(
        default=60.0, validation_alias="OPS_ALERT_WEBHOOK_P95_MAX_SEC"
    )
    ops_alert_webhook_min_events: int = Field(default=20, validation_alias="OPS_ALERT_WEBHOOK_MIN_EVENTS")
    # Retention D7: minimum retention percentage for cohort with enough size.
    ops_alert_retention_d7_min_pct: float = Field(
        default=8.0, validation_alias="OPS_ALERT_RETENTION_D7_MIN_PCT"
    )
    ops_alert_retention_min_cohort: int = Field(
        default=30, validation_alias="OPS_ALERT_RETENTION_MIN_COHORT"
    )
    # CAC: maximum acceptable CAC in RUB (<=0 disables this alert).
    ops_alert_cac_max_rub: float = Field(default=0.0, validation_alias="OPS_ALERT_CAC_MAX_RUB")
    ops_alert_cac_min_paid_users: int = Field(default=5, validation_alias="OPS_ALERT_CAC_MIN_PAID_USERS")
    # Executive reports: daily(1) / weekly(7) / monthly(30) / quarterly(90) / semi(150).
    exec_report_enabled: bool = Field(default=False, validation_alias="EXEC_REPORT_ENABLED")
    # Legacy single-interval (не используется multi-loop; оставлен для совместимости .env).
    exec_report_interval_seconds: int = Field(
        default=604800, validation_alias="EXEC_REPORT_INTERVAL_SECONDS"
    )
    exec_report_days_short: int = Field(default=7, validation_alias="EXEC_REPORT_DAYS_SHORT")
    exec_report_days_long: int = Field(default=30, validation_alias="EXEC_REPORT_DAYS_LONG")
    # CSV: daily,weekly,monthly,quarterly,semi  (или all).
    exec_report_cadences: str = Field(
        default="daily,weekly,monthly,quarterly,semi",
        validation_alias="EXEC_REPORT_CADENCES",
    )
    # В executive-метриках: только реальные оплаты (fulfillment + rub>0), без админов/сид-друзей.
    exec_metrics_exclude_admins: bool = Field(
        default=True, validation_alias="EXEC_METRICS_EXCLUDE_ADMINS"
    )
    # Доп. Telegram ID через запятую (тестовые аккаунты), не попадающие в KPI.
    exec_metrics_exclude_user_ids: str = Field(
        default="", validation_alias="EXEC_METRICS_EXCLUDE_USER_IDS"
    )
    # NPS/CSAT survey automation.
    feedback_survey_enabled: bool = Field(default=False, validation_alias="FEEDBACK_SURVEY_ENABLED")
    feedback_survey_interval_seconds: int = Field(
        default=21600, validation_alias="FEEDBACK_SURVEY_INTERVAL_SECONDS"
    )
    feedback_survey_cooldown_days: int = Field(default=30, validation_alias="FEEDBACK_SURVEY_COOLDOWN_DAYS")
    feedback_survey_lookback_days: int = Field(default=45, validation_alias="FEEDBACK_SURVEY_LOOKBACK_DAYS")
    feedback_survey_batch_size: int = Field(default=50, validation_alias="FEEDBACK_SURVEY_BATCH_SIZE")
    # Feature flags / staged rollout.
    feature_split_metrics_enabled: bool = Field(default=True, validation_alias="FEATURE_SPLIT_METRICS_ENABLED")
    feature_feedback_metrics_enabled: bool = Field(default=True, validation_alias="FEATURE_FEEDBACK_METRICS_ENABLED")
    feature_feedback_collection_enabled: bool = Field(
        default=True, validation_alias="FEATURE_FEEDBACK_COLLECTION_ENABLED"
    )
    # Data quality checks for metrics layer.
    data_quality_checks_enabled: bool = Field(default=False, validation_alias="DATA_QUALITY_CHECKS_ENABLED")
    data_quality_checks_interval_seconds: int = Field(
        default=21600, validation_alias="DATA_QUALITY_CHECKS_INTERVAL_SECONDS"
    )
    data_quality_lookback_days: int = Field(default=7, validation_alias="DATA_QUALITY_LOOKBACK_DAYS")
    data_quality_max_orders_missing_kind: int = Field(
        default=0, validation_alias="DATA_QUALITY_MAX_ORDERS_MISSING_KIND"
    )
    data_quality_max_orders_missing_profit_snapshot: int = Field(
        default=0, validation_alias="DATA_QUALITY_MAX_ORDERS_MISSING_PROFIT_SNAPSHOT"
    )
    data_quality_min_event_schema_v2_pct: float = Field(
        default=95.0, validation_alias="DATA_QUALITY_MIN_EVENT_SCHEMA_V2_PCT"
    )
    data_quality_max_unattributed_paid_pct: float = Field(
        default=20.0, validation_alias="DATA_QUALITY_MAX_UNATTRIBUTED_PAID_PCT"
    )

    # Входящий вебхук «платёж подтверждён» (HMAC тела, заголовок X-Payment-Signature).
    payment_webhook_secret: str = Field(default="", validation_alias="PAYMENT_WEBHOOK_SECRET")
    # Отдельный секрет для WATA webhook (если пусто — fallback на PAYMENT_WEBHOOK_SECRET).
    wata_webhook_secret: str = Field(default="", validation_alias="WATA_WEBHOOK_SECRET")

    # LAVA Business (https://dev.lava.ru/) - фиат, СБП и др. на стороне LAVA.
    lava_shop_id: str = Field(default="", validation_alias="LAVA_SHOP_ID")
    lava_secret_key: str = Field(default="", validation_alias="LAVA_SECRET_KEY")
    # «Дополнительный ключ» из кабинета LAVA - проверка заголовка Authorization на вебхуке.
    lava_webhook_additional_secret: str = Field(default="", validation_alias="LAVA_WEBHOOK_ADDITIONAL_SECRET")
    lava_api_base: str = Field(default="", validation_alias="LAVA_API_BASE")
    # Публичный URL эндпоинта Partner API, например https://shop-api.example.com/v1/payments/lava-webhook
    lava_hook_url: str = Field(default="", validation_alias="LAVA_HOOK_URL")
    lava_success_url: str = Field(default="", validation_alias="LAVA_SUCCESS_URL")
    lava_fail_url: str = Field(default="", validation_alias="LAVA_FAIL_URL")
    lava_invoice_expire_minutes: int = Field(default=720, validation_alias="LAVA_INVOICE_EXPIRE_MINUTES")
    # Список service_id через запятую (пусто = LAVA покажет все доступные методы проекта).
    lava_include_services: str = Field(default="card,sbp", validation_alias="LAVA_INCLUDE_SERVICES")

    # Cardlink (https://cardlink.link) — фиат ₽: карта / СБП, postback на Partner API.
    cardlink_enabled: bool = Field(default=False, validation_alias="CARDLINK_ENABLED")
    cardlink_shop_id: str = Field(default="", validation_alias="CARDLINK_SHOP_ID")
    cardlink_api_token: str = Field(default="", validation_alias="CARDLINK_API_TOKEN")
    cardlink_api_base: str = Field(default="https://cardlink.link", validation_alias="CARDLINK_API_BASE")
    cardlink_success_url: str = Field(
        default="https://aladdin-ai.ru/v1/payment/success",
        validation_alias="CARDLINK_SUCCESS_URL",
    )
    cardlink_fail_url: str = Field(
        default="https://aladdin-ai.ru/v1/payment/fail",
        validation_alias="CARDLINK_FAIL_URL",
    )
    # Должен совпадать с Result URL в ЛК Cardlink (часто нельзя изменить после создания проекта).
    cardlink_hook_url: str = Field(
        default="https://aladdin-ai.ru/v1/payments/cardlink-webhook",
        validation_alias="CARDLINK_HOOK_URL",
    )
    cardlink_refund_url: str = Field(
        default="https://aladdin-ai.ru/v1/payments/cardlink-refund",
        validation_alias="CARDLINK_REFUND_URL",
    )
    cardlink_chargeback_url: str = Field(
        default="https://aladdin-ai.ru/v1/payments/cardlink-chargeback",
        validation_alias="CARDLINK_CHARGEBACK_URL",
    )
    cardlink_currency_in: str = Field(default="RUB", validation_alias="CARDLINK_CURRENCY_IN")
    cardlink_locale: str = Field(default="ru", validation_alias="CARDLINK_LOCALE")
    cardlink_bill_ttl_seconds: int = Field(default=43200, validation_alias="CARDLINK_BILL_TTL_SECONDS")
    cardlink_payer_pays_commission: int = Field(default=1, ge=0, le=1, validation_alias="CARDLINK_PAYER_PAYS_COMMISSION")
    # BANK_CARD | SBP | пусто = выбор на форме Cardlink.
    cardlink_payment_method: str = Field(default="", validation_alias="CARDLINK_PAYMENT_METHOD")
    cardlink_payment_name: str = Field(
        default="AIMonkey Stars | Premium",
        validation_alias="CARDLINK_PAYMENT_NAME",
    )
    # Deep link после оплаты на success/fail страницах (кнопка «Вернуться в бот»).
    cardlink_return_bot_url: str = Field(
        default="https://t.me/AiMonkeyStars_bot",
        validation_alias="CARDLINK_RETURN_BOT_URL",
    )

    # Ckassa (ЦК) - фиат ₽ по API как в WooCommerce-модуле: do-pay/anonymous + callback cbUrl.
    # https://api2.ckassa.ru/api-shop/rs/wordpress/do-pay/anonymous
    ckassa_enabled: bool = Field(default=False, validation_alias="CKASSA_ENABLED")
    ckassa_test_mode: bool = Field(default=False, validation_alias="CKASSA_TEST_MODE")
    ckassa_shop_token: str = Field(default="", validation_alias="CKASSA_SHOP_TOKEN")
    ckassa_secret_key: str = Field(default="", validation_alias="CKASSA_SECRET_KEY")
    # Полный URL do-pay (если пусто - prod или demo по CKASSA_TEST_MODE).
    ckassa_do_pay_url: str = Field(default="", validation_alias="CKASSA_DO_PAY_URL")
    # Публичный HTTPS Partner API для cbUrl (как LAVA_HOOK_URL): …/v1/payments/ckassa-webhook
    ckassa_callback_public_url: str = Field(default="", validation_alias="CKASSA_CALLBACK_PUBLIC_URL")
    ckassa_success_url: str = Field(default="", validation_alias="CKASSA_SUCCESS_URL")
    ckassa_fail_url: str = Field(default="", validation_alias="CKASSA_FAIL_URL")
    ckassa_country: str = Field(default="RU", validation_alias="CKASSA_COUNTRY")
    ckassa_language: str = Field(default="RU", validation_alias="CKASSA_LANGUAGE")
    ckassa_http_timeout_seconds: float = Field(default=15.0, validation_alias="CKASSA_HTTP_TIMEOUT_SECONDS")
    # Плательщик для анонимной формы (если нет email из Telegram - подставляются дефолты).
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
    # Постоянная страница Ckassa «произвольная сумма» (bc.ckassa.ru/…). Не подставляет orderId в callback бота -
    # после оплаты сверка по сумме и номеру заказа (поддержка / админ «Оплачен»). Пусто в .env → DEFAULT_CKASSA_BC_UNIVERSAL_PAYMENT_URL.
    # На экране ₽: при CKASSA_BC_SOLO_CHECKOUT=true только эта ссылка; иначе до трёх кнопок (+ Shop API + LAVA при настройке).
    ckassa_bc_universal_payment_url: str = Field(default="", validation_alias="CKASSA_BC_UNIVERSAL_PAYMENT_URL")
    # Показывать счёт LAVA одновременно со счётом Ckassa Shop API (без универсальной ссылки). По умолчанию false -
    # LAVA остаётся запасным потоком, если Ckassa API не сработал.
    fiat_parallel_ckassa_and_lava: bool = Field(default=False, validation_alias="FIAT_PARALLEL_CKASSA_AND_LAVA")
    # После кнопки «Я оплатил (универсальная Ckassa)» повторное уведомление админам не чаще, чем раз в N секунд.
    bc_payment_claim_cooldown_seconds: int = Field(default=900, validation_alias="BC_PAYMENT_CLAIM_COOLDOWN_SECONDS")
    # true: на шаге ₽ только универсальная ссылка bc (без счёта Shop API Ckassa и без LAVA). false + API/LAVA — доп. кнопки.
    ckassa_bc_solo_checkout: bool = Field(default=True, validation_alias="CKASSA_BC_SOLO_CHECKOUT")
    # Текст для покупателя: минимальная сумма платежа на универсальной странице Ckassa (часто 50 ₽ у эквайринга).
    ckassa_bc_display_min_rub: float = Field(default=50.0, validation_alias="CKASSA_BC_DISPLAY_MIN_RUB")

    # Crypto Pay (@CryptoBot / testnet @CryptoTestnetBot). При CRYPTO_PAY_ENABLED=false - сценарий счёта через API не используется.
    crypto_pay_enabled: bool = Field(default=False, validation_alias="CRYPTO_PAY_ENABLED")
    crypto_pay_api_token: str = Field(default="", validation_alias="CRYPTO_PAY_API_TOKEN")
    crypto_pay_testnet: bool = Field(default=False, validation_alias="CRYPTO_PAY_TESTNET")
    # Полный https://… или только hostname; пусто - pay.crypt.bot / testnet-pay.crypt.bot по CRYPTO_PAY_TESTNET.
    crypto_pay_api_host: str = Field(default="", validation_alias="CRYPTO_PAY_API_HOST")
    crypto_pay_default_asset: str = Field(default="USDT", validation_alias="CRYPTO_PAY_DEFAULT_ASSET")
    crypto_pay_invoice_expire_seconds: int = Field(
        default=3600, validation_alias="CRYPTO_PAY_INVOICE_EXPIRE_SECONDS"
    )
    # После оплаты счёта - кнопка «открыть бота» (https://t.me/…). Пусто = не передаём paid_btn_* в Crypto Pay.
    crypto_pay_paid_btn_url: str = Field(default="", validation_alias="CRYPTO_PAY_PAID_BTN_URL")
    # Если Crypto Pay включён и счёт не создался: показывать ли старый блок с кошельками (для отладки). В проде обычно false.
    crypto_pay_wallet_fallback: bool = Field(default=False, validation_alias="CRYPTO_PAY_WALLET_FALLBACK")

    # xRocket Pay - второй провайдер счёта USDT, см. https://docs.xrocket.tg/api/pay/pay-api-overview
    xrocket_pay_enabled: bool = Field(default=False, validation_alias="XROCKET_PAY_ENABLED")
    xrocket_pay_api_key: str = Field(default="", validation_alias="XROCKET_PAY_API_KEY")
    xrocket_pay_api_base: str = Field(
        default="https://pay.xrocket.exchange",
        validation_alias="XROCKET_PAY_API_BASE",
    )

    # Автовыдача Stars/Premium после paid (план 37). Пока только флаги и политика в коде; воркер очереди - позже.
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
    auto_fulfill_success_alerts_enabled: bool = Field(
        default=True, validation_alias="AUTO_FULFILL_SUCCESS_ALERTS_ENABLED"
    )
    # Русские ops-алерты в ALERT_TELEGRAM_CHAT_ID (один чат, не личка ADMIN_IDS).
    admin_bot_alerts_enabled: bool = Field(default=True, validation_alias="ADMIN_BOT_ALERTS_ENABLED")
    # Опрос статуса заказа iStar, если webhook не пришёл (сек). 0 = выключить.
    istar_order_poll_interval_seconds: int = Field(
        default=120, validation_alias="ISTAR_ORDER_POLL_INTERVAL_SECONDS"
    )
    istar_order_poll_min_processing_minutes: int = Field(
        default=3, validation_alias="ISTAR_ORDER_POLL_MIN_PROCESSING_MINUTES"
    )

    # ApiFragment (выдача Stars и Premium). Ключ в .env: ISTAR_API_KEY (legacy name) или через тот же alias.
    istar_api_key: str = Field(default="", validation_alias="ISTAR_API_KEY")
    istar_api_base: str = Field(
        default="https://apifragment.online",
        validation_alias="ISTAR_API_BASE",
    )
    fragment_provider: str = Field(default="apifragment", validation_alias="FRAGMENT_PROVIDER")
    apifragment_webhook_public_url: str = Field(
        default="https://aladdin-ai.ru/v1/payments/apifragment-webhook",
        validation_alias="APIFRAGMENT_WEBHOOK_PUBLIC_URL",
    )
    apifragment_webhook_secret: str = Field(default="", validation_alias="APIFRAGMENT_WEBHOOK_SECRET")
    # ton | usdt_ton — валюта списания на ApiFragment (docs: payment_method).
    apifragment_payment_method: str = Field(
        default="usdt_ton",
        validation_alias="APIFRAGMENT_PAYMENT_METHOD",
    )
    istar_wallet_type: str = Field(default="TON", validation_alias="ISTAR_WALLET_TYPE")
    # Legacy: iStar webhook больше не используется (оставлен пустым, чтобы старый .env не ломал load).
    istar_webhook_secret: str = Field(default="", validation_alias="ISTAR_WEBHOOK_SECRET")
    # Порог TON на кошельке ApiFragment: ниже — воркер не берёт заказы + ops-алерт раз в 8ч (0 = не проверять).
    istar_min_ton_balance_alert: float = Field(default=0.0, validation_alias="ISTAR_MIN_TON_BALANCE_ALERT")

    # Авто-истечение заказов в pending_payment (фоновый цикл в боте). В .env можно задать 0 - выключить.
    # По умолчанию 720 мин (как типичный срок счёта LAVA); для крипты/ручной оплаты тот же таймер.
    order_pending_payment_expire_minutes: int = Field(
        default=720, validation_alias="ORDER_PENDING_PAYMENT_EXPIRE_MINUTES"
    )
    order_pending_payment_sweep_interval_seconds: int = Field(
        default=180, validation_alias="ORDER_PENDING_PAYMENT_SWEEP_INTERVAL_SECONDS"
    )
    # Опрос LAVA invoice/status для pending_payment (fallback без webhook). 0 = выключить.
    lava_reconcile_interval_seconds: int = Field(
        default=30, validation_alias="LAVA_RECONCILE_INTERVAL_SECONDS"
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
    # Быстрый алерт: только paid без перехода в processing дольше N минут (0 = выкл.).
    stuck_paid_fast_alert_minutes: int = Field(
        default=5, validation_alias="STUCK_PAID_FAST_ALERT_MINUTES"
    )
    # Не слать stuck-алерты по этим order id (тестовые/известные зависания). CSV.
    stuck_alert_ignore_order_ids: str = Field(
        default="122,123,125,136",
        validation_alias="STUCK_ALERT_IGNORE_ORDER_IDS",
    )
    # Дедуп stuck-алертов в Telegram (по умолч. 1 час).
    stuck_alert_cooldown_seconds: int = Field(
        default=3600, ge=60, le=86400, validation_alias="STUCK_ALERT_COOLDOWN_SECONDS"
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
    topup_min_rub: float = Field(default=50.0, validation_alias="TOPUP_MIN_RUB")
    topup_max_rub: float = Field(default=500_000.0, validation_alias="TOPUP_MAX_RUB")
    topup_max_pending_per_user: int = Field(default=8, validation_alias="TOPUP_MAX_PENDING_PER_USER")
    topup_min_interval_seconds: int = Field(default=60, validation_alias="TOPUP_MIN_INTERVAL_SECONDS")
    # Заказы в ожидании оплаты на одного пользователя (0 = без лимита).
    max_pending_payment_orders_per_user: int = Field(
        default=3, validation_alias="MAX_PENDING_PAYMENT_ORDERS_PER_USER"
    )
    auto_expire_other_pending_payment_orders: bool = Field(
        default=True, validation_alias="AUTO_EXPIRE_OTHER_PENDING_ON_NEW_ORDER"
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

    def parsed_stuck_alert_ignore_order_ids(self) -> set[int]:
        return _parse_ids_csv(self.stuck_alert_ignore_order_ids)

    def resolved_exec_metrics_exclude_user_ids(self) -> set[int]:
        """Кого не считать в Weekly Executive Report (админы + явный exclude)."""
        out: set[int] = set(_parse_ids_csv(self.exec_metrics_exclude_user_ids))
        if self.exec_metrics_exclude_admins:
            out |= self.parsed_admin_ids()
        return out

    def parsed_super_admin_ids_explicit(self) -> set[int]:
        """ID из SUPER_ADMIN_IDS (без пересечения с ADMIN)."""
        return _parse_ids_csv(self.super_admin_ids)

    def admin_roles_restricted(self) -> bool:
        """True если задан непустой SUPER_ADMIN_IDS с пересечением с ADMIN - есть роль «оператор»."""
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

    def default_ops_actor_id(self) -> int | None:
        """ID для клавиатуры заказа в ops-чате (права супер-админа, если есть)."""
        supers = sorted(x for x in self.parsed_admin_ids() if self.is_super_admin(x))
        if supers:
            return supers[0]
        admins = sorted(self.parsed_admin_ids())
        return admins[0] if admins else None

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
