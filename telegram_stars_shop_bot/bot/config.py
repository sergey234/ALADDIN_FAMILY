from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    admin_ids: str = Field(default="", validation_alias="ADMIN_IDS")

    usd_rub_rate: float = Field(default=97.5, validation_alias="USD_RUB_RATE")
    # ₽ за 1 USDT для подсказки «сколько USDT» (0 = использовать USD_RUB_RATE).
    usdt_rub_rate: float = Field(default=0.0, validation_alias="USDT_RUB_RATE")
    # Ориентир для пользователя: сколько UAH за 1 USD (0 = не показывать строку UAH).
    display_usd_uah_rate: float = Field(default=0.0, validation_alias="DISPLAY_USD_UAH_RATE")
    # Ориентир: сколько BYN за 1 USD (0 = не показывать строку BYN).
    display_usd_byn_rate: float = Field(default=0.0, validation_alias="DISPLAY_USD_BYN_RATE")

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

    # Обязательная подписка на канал перед покупкой (бот должен быть админом канала).
    # ID: @username или -100… ; пусто = проверка отключена.
    required_channel_id: str = Field(default="", validation_alias="REQUIRED_CHANNEL_ID")
    # Ссылка-приглашение t.me/… для кнопки «Подписаться».
    required_channel_invite_url: str = Field(default="", validation_alias="REQUIRED_CHANNEL_INVITE_URL")

    # Sentry (бот и Partner API; пустой DSN = выключено).
    sentry_dsn: str = Field(default="", validation_alias="SENTRY_DSN")
    sentry_environment: str = Field(default="", validation_alias="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(default=0.0, validation_alias="SENTRY_TRACES_SAMPLE_RATE")

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

    products_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent / "products.yaml"
    )
    database_path: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parents[1] / "data" / "shop.db",
        validation_alias="DATABASE_PATH",
    )

    def parsed_admin_ids(self) -> set[int]:
        raw = (self.admin_ids or "").replace(";", ",")
        out: set[int] = set()
        for part in raw.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                out.add(int(part))
            except ValueError:
                continue
        return out

    def lava_include_services_list(self) -> list[str]:
        raw = (self.lava_include_services or "").replace(";", ",")
        return [p.strip() for p in raw.split(",") if p.strip()]


def load_settings() -> Settings:
    return Settings()
