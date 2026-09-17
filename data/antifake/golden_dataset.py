"""T3-05 — antifake golden regression corpus (RU/EN text, URL, audio probes)."""
from __future__ import annotations

from typing import List, Tuple

Case = Tuple[str, str]

_SCAM_RU_CORE = (
    "шокирующая правда act now переведите деньги срочно they don't want you to know",
    "ваш счёт заблокирован действуй сейчас переведите деньги на карту немедленно",
    "анонимных источников сообщают переведите деньги act now шокирующая правда",
    "срочно send money immediately ваш счёт заблокирован действуй сейчас",
)

_REAL_RU_CORE = (
    "Обычный прогноз погоды в Москве на завтра: облачно, без осадков, температура около плюс пяти градусов.",
    "Расписание электричек на выходные: отправление с Ленинградского вокзала в восемь тридцать утра.",
    "Рецепт борща: свёкла, капуста, картофель, морковь, лук — варить около полутора часов на медленном огне.",
    "Напоминание: встреча команды в понедельник в десять утра в конференц-зале на третьем этаже офиса.",
)

_SCAM_EN_CORE = (
    "act now send money immediately shocking truth they don't want you to know",
    "your account is blocked act now send money immediately urgent warning",
    "anonymous sources claim send money immediately act now shocking truth",
)

_REAL_EN_CORE = (
    "Weekly weather forecast for London: mostly cloudy, light rain possible, highs near twelve degrees.",
    "Team standup on Monday at ten AM in the third-floor conference room — please bring notes.",
    "Recipe for vegetable soup: carrots, celery, onion, tomatoes — simmer for forty-five minutes.",
)


def _expand_text(cores: Tuple[str, ...], label: str, n: int) -> List[Case]:
    out: List[Case] = []
    i = 0
    while len(out) < n:
        base = cores[i % len(cores)]
        suffix = f" ref-{len(out)}"
        out.append((f"{base}{suffix}", label))
        i += 1
    return out


def golden_text_ru() -> List[Case]:
    return _expand_text(_SCAM_RU_CORE, "likely_fake", 26) + _expand_text(_REAL_RU_CORE, "likely_real", 24)


def golden_text_en() -> List[Case]:
    return _expand_text(_SCAM_EN_CORE, "likely_fake", 26) + _expand_text(_REAL_EN_CORE, "likely_real", 24)


def golden_urls() -> List[Case]:
    fake_hosts = (
        "login-secure.evil-bank.ru.com",
        "verify-account.scam-pay.ru.com",
        "auth.client-bank.ru.com",
        "secure-wallet.fake-bank.ru.com",
        "confirm-payment.phish-bank.ru.com",
        "update-card.evil-bank.ru.com",
        "account-lock.scam-bank.ru.com",
        "client-verify.fake-pay.ru.com",
        "secure-login.evil-wallet.ru.com",
        "bank-auth.scam-client.ru.com",
    )
    real_hosts = (
        "https://www.wikipedia.org/",
        "https://www.gov.ru/",
        "https://www.cbr.ru/",
        "https://mos.ru/",
        "https://www.apple.com/",
        "https://www.microsoft.com/",
        "https://yandex.ru/",
        "https://www.rbc.ru/",
        "https://www.consultant.ru/",
        "https://www.gosuslugi.ru/",
    )
    fake: List[Case] = [
        (f"http://{host}/verify?id={i}", "likely_fake") for i, host in enumerate(fake_hosts)
    ]
    real: List[Case] = [(url, "likely_real") for url in real_hosts]
    return fake + real


def golden_urls_fuzzy() -> List[Case]:
    """TI-12b — typosquat should be catchable by fuzzy; allowlisted brands must stay safe."""
    fake = (
        "https://secure-sber-online.ru.com/login",
        "https://login-tinkoff-online.ru.com/verify",
        "https://sberbank-secure.xyz/auth",
        "https://verify-gosuslugi.top/account",
        "https://alfa-bank-login.club/secure",
        "https://vtb-online-verify.site/confirm",
    )
    # Must NOT be likely_fake from fuzzy alone (official / infra)
    real = (
        "https://www.sberbank.ru/",
        "https://www.tinkoff.ru/",
        "https://www.gosuslugi.ru/",
        "https://www.alfabank.ru/",
        "https://www.vtb.ru/",
        "https://www.ozon.ru/",
        "https://nordvpn.com/",
        "https://www.cloudflare.com/",
        "https://github.com/",
    )
    return [(u, "likely_fake") for u in fake] + [(u, "likely_real") for u in real]


def golden_rkn_edge() -> List[Case]:
    """TI-12b — RKN-only signal must stay uncertain (never auto likely_fake)."""
    # These represent domains that might appear in block lists but are not phishing.
    return [
        ("https://nordvpn.com/", "uncertain_if_rkn_only"),
        ("https://expressvpn.com/", "uncertain_if_rkn_only"),
        ("https://wikipedia.org/", "uncertain_if_rkn_only"),
    ]


def golden_sms_ru() -> List[Case]:
    """RH-B01/B03 + afhub-p0-06 — ≥20 RU SMS scam cases; expect likely_fake in mode=sms."""
    cores = (
        "Служба безопасности банка: ваш счёт заблокирован, сообщите код подтверждения",
        "Ваш счет заблокирован. Переведите код из СМС сотруднику банка немедленно",
        "СБП перевод на карту — срочно подтвердите одноразовый код",
        "Госуслуги: задолженность, оплатите штраф по ссылке иначе блокировка",
        "Тинькофф: подозрительная операция, назовите CVV и код из SMS",
        "МВД: возбуждено дело, переведите деньги на безопасный счет",
        "Ваша карта будет заблокирована через час — действуйте сейчас",
        "Служба безопасности Сбера просит реквизиты карты для проверки",
        "Вам начислен штраф ГИБДД — оплатите сейчас иначе арест счета",
        "Код подтверждения никому не сообщайте — кроме нас из службы безопасности",
        "Срочно переведите деньги родственнику на карту, он в больнице",
        "Альфа-Банк: счёт заблокирован, подтвердите перевод кодом",
        "ВТБ: одноразовый код для разблокировки счета — продиктуйте оператору",
        "Почта России: посылка задержана, оплатите пошлину по реквизитам",
        "Налоговая: долг, оплатите немедленно иначе блокировка карт",
        "Apple ID заблокирован — подтвердите карту и код из SMS",
        "Вы выиграли приз — переведите комиссию на карту для получения",
        "Служба безопасности: не говорите никому код подтверждения кроме нас",
        "Ваш счет будет арестован — срочно переведите средства на резервный счет",
        "Мошенники пытаются списать деньги — назовите код из СМС чтобы отменить",
        # afhub-p0 money+urgency colloquial
        "Я скамер-переведи мне срочно деньги на карту!",
        "Я с камер. Переведи мне деньги срочно.",
        "Срочно переведи деньги на карту",
        "Переведите мне срочно на карту",
    )
    return [(t, "likely_fake") for t in cores]


def golden_sms_en() -> List[Case]:
    """afhub-p0-06 — EN SMS scam; expect likely_fake in mode=sms."""
    cores = (
        "Send me money urgently to my card",
        "Transfer money right now to my card",
        "I'm a scammer — send money urgently!",
        "Your account is blocked — send money immediately",
        "Bank security: verify your account, send the OTP urgently",
        "Act now: transfer money to my card within an hour",
        "Limited time — wire me money right now",
        "Don't wait — send me money to unlock your account",
        "Urgent: your account is blocked, transfer now",
        "Fraud alert: send verification code and money to my card",
    )
    return [(t, "likely_fake") for t in cores]


def golden_audio_probe_sizes() -> List[int]:
    """Byte lengths for minimal WAV probe regression (≥10)."""
    return [44, 64, 128, 256, 512, 768, 1024, 1536, 2048, 4096, 8192, 12000]


def dataset_counts() -> dict[str, int]:
    return {
        "text_ru": len(golden_text_ru()),
        "text_en": len(golden_text_en()),
        "text_sms_ru": len(golden_sms_ru()),
        "text_sms_en": len(golden_sms_en()),
        "url": len(golden_urls()),
        "url_fuzzy": len(golden_urls_fuzzy()),
        "rkn_edge": len(golden_rkn_edge()),
        "audio_probes": len(golden_audio_probe_sizes()),
    }
