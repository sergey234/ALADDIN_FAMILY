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

    vpn_api_hmac_secret: str = Field(default="", validation_alias="VPN_API_HMAC_SECRET")
    vpn_db_path: Path = Field(default=Path("./var/vpn.db"), validation_alias="VPN_DB_PATH")
    vpn_wg_interface: str = Field(default="", validation_alias="VPN_WG_INTERFACE")
    vpn_dev_stub_wg: bool = Field(default=False, validation_alias="VPN_DEV_STUB_WG")
    # Опционально: исполняемый путь; после успешного provision воркере вызывается с argv[1]=telegram_user_id (vpn-04 hook).
    vpn_wg_post_provision_script: str = Field(default="", validation_alias="VPN_WG_POST_PROVISION_SCRIPT")
    # Опционально: после перевода аккаунта в vpn_expired по paid_until (тот же тик воркера).
    vpn_wg_post_expire_script: str = Field(default="", validation_alias="VPN_WG_POST_EXPIRE_SCRIPT")
    vpn_xray_post_provision_script: str = Field(default="", validation_alias="VPN_XRAY_POST_PROVISION_SCRIPT")
    vpn_xray_post_expire_script: str = Field(default="", validation_alias="VPN_XRAY_POST_EXPIRE_SCRIPT")
    # P3: алерт если один opaque_token (успешные GET /sub/) > N за час (шаринг ссылки).
    vpn_sub_access_alert_per_hour: int = Field(default=120, ge=0, validation_alias="VPN_SUB_ACCESS_ALERT_PER_HOUR")
    # Опционально: UTF-8 файл тела подписки для GET /sub/<opaque> (плейсхолдеры {opaque_token}, {xray_uuid}, …). Пусто = 501 (vpn-05).
    vpn_subscribe_body_file: str = Field(default="", validation_alias="VPN_SUBSCRIBE_BODY_FILE")
    # Одна строка VLESS (приоритет над файлом): те же плейсхолдеры, что в subscription_util.
    vpn_subscribe_vless_template: str = Field(default="", validation_alias="VPN_SUBSCRIBE_VLESS_TEMPLATE")
    vpn_xray_public_host: str = Field(default="", validation_alias="VPN_XRAY_PUBLIC_HOST")
    vpn_xray_port: int = Field(default=8443, validation_alias="VPN_XRAY_PORT")
    vpn_xray_default_client_uuid: str = Field(default="", validation_alias="VPN_XRAY_DEFAULT_CLIENT_UUID")
    vpn_xray_reality_public_key: str = Field(default="", validation_alias="VPN_XRAY_REALITY_PUBLIC_KEY")
    vpn_xray_reality_short_id: str = Field(default="", validation_alias="VPN_XRAY_REALITY_SHORT_ID")
    vpn_xray_reality_sni: str = Field(default="www.microsoft.com", validation_alias="VPN_XRAY_REALITY_SNI")
    vpn_xray_reality_fingerprint: str = Field(default="chrome", validation_alias="VPN_XRAY_REALITY_FINGERPRINT")
    # Готовность ко 2-й VPS: JSON-массив нод (см. deploy/VPN30_SINGLE_NODE_MAX.md).
    vpn_egress_nodes_json: str = Field(default="", validation_alias="VPN_EGRESS_NODES_JSON")
    vpn_wg_client_mtu: int = Field(default=1280, ge=1280, le=1500, validation_alias="VPN_WG_CLIENT_MTU")
    # Тот же формат, что в боте: список локаций для GET /internal/v1/locations/catalog (пусто = встроенный каталог).
    vpn_locations_json: str = Field(default="", validation_alias="VPN_LOCATIONS_JSON")
    vpn_locations_preview_n: int = Field(default=3, ge=1, le=50, validation_alias="VPN_LOCATIONS_PREVIEW_N")
    # Endpoint в клиентском WG [Peer] (DNS-имя или IP; порт — VPN_WG_LISTEN_PORT).
    vpn_wg_endpoint_host: str = Field(default="", validation_alias="VPN_WG_ENDPOINT_HOST")
    vpn_wg_listen_port: int = Field(default=51820, validation_alias="VPN_WG_LISTEN_PORT")
    vpn_wg_server_public_key_path: str = Field(
        default="/etc/wireguard/server_public.key",
        validation_alias="VPN_WG_SERVER_PUBLIC_KEY_PATH",
    )
    wg_keys_dir: str = Field(default="", validation_alias="WG_KEYS_DIR")
    # Шаблон .ovpn с плейсхолдерами {remote_host} {remote_port} (vpn-10). Пусто = 503.
    vpn_ovpn_client_template_file: str = Field(
        default="", validation_alias="VPN_OVPN_CLIENT_TEMPLATE_FILE"
    )
    vpn_ovpn_remote_port: int = Field(default=1194, validation_alias="VPN_OVPN_REMOTE_PORT")
    vpn_ovpn_profiles_dir: str = Field(
        default="/opt/aladdin-shop-vpn-api/var/ovpn-profiles",
        validation_alias="VPN_OVPN_PROFILES_DIR",
    )
    vpn_ovpn_client_issue_script: str = Field(
        default="", validation_alias="VPN_OVPN_CLIENT_ISSUE_SCRIPT"
    )
    # vpn-26: повтор failed jobs с экспоненциальным next_run_at (воркер).
    vpn_job_max_attempts: int = Field(default=5, ge=1, le=20, validation_alias="VPN_JOB_MAX_ATTEMPTS")

    sentry_dsn: str = Field(default="", validation_alias="SENTRY_DSN")
    sentry_environment: str = Field(default="", validation_alias="SENTRY_ENVIRONMENT")
    sentry_traces_sample_rate: float = Field(default=0.0, validation_alias="SENTRY_TRACES_SAMPLE_RATE")

    @model_validator(mode="after")
    def _require_secret(self) -> "Settings":
        if not (self.vpn_api_hmac_secret or "").strip():
            raise ValueError(
                "VPN_API_HMAC_SECRET must be set (same value as in telegram shop shared/.env)"
            )
        return self


def load_settings() -> Settings:
    return Settings()
