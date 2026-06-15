from __future__ import annotations

import logging
import re

_log = logging.getLogger(__name__)

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.keyboards.shop_kb import (
    cardlink_payment_kb,
    ckassa_payment_kb,
    confirm_order_kb,
    crypto_providers_kb,
    fiat_checkout_options_kb,
    hub_menu_kb,
    lava_payment_kb,
    payment_methods_kb,
    premium_dest_kb,
    verify_username_kb,
    vpn_invoice_pay_url_kb,
    vpn_order_invoice_kb,
)
from bot.services import analytics_repo, balance_repo, emoji_captcha, orders_repo, users_repo
from bot.services.operator_payment_memo import operator_bc_manual_checklist_html
from bot.services.invoice_checkout_cooldown import allow_checkout_invoice_attempt
from bot.services.catalog import Product, product_order_columns, products_by_id
from bot.services.crypto_pay_api import (
    create_crypto_pay_invoice_checkout_meta,
    crypto_pay_invoice_api_ready,
)
from bot.services.cardlink_api import cardlink_checkout_configured, create_cardlink_bill_meta
from bot.services.ckassa_api import ckassa_checkout_configured, create_ckassa_payment_meta
from bot.services.lava_api import create_invoice_payment_meta, lava_checkout_configured
from bot.services.xrocket_pay_api import create_xrocket_invoice_checkout_meta, xrocket_invoice_api_ready
from bot.services.payments_stub import crypto_payment_block_html, fiat_placeholder_html
from bot.services.fx_display import fx_payment_hints_html
from bot.services.pricing import (
    format_shop_quote_money_html,
    quote_product,
    referral_discount_percent_snapshot,
    rub_per_100_stars_display,
)
from bot.states.checkout import CheckoutStates
from bot.support_links import support_order_question_url
from bot.util_html import esc

router = Router(name="shop")

_USERNAME_RE = re.compile(r"^@?[a-zA-Z0-9_]{4,32}$")


def _fmt_quote_html(p: Product, q, settings: Settings) -> str:
    lines = [
        f"{p.emoji} <b>{esc(p.title)}</b>",
        "",
        f"База: <b>{format_shop_quote_money_html(settings, q.rub_list, q.usd)}</b>",
    ]
    if q.rub_referral_discount > 0:
        lines.append(f"Скидка по приглашению: <b>−{esc(f'{q.rub_referral_discount:.2f}')} ₽</b>")
    if q.rub_wholesale_discount > 0:
        lines.append(f"Опт Stars: <b>−{esc(f'{q.rub_wholesale_discount:.2f}')} ₽</b>")
    lines.append(f"К оплате: <b>{format_shop_quote_money_html(settings, q.rub_final, q.usd)}</b>")
    body = "\n".join(lines)
    fx = fx_payment_hints_html(settings, rub_final=q.rub_final, usd_base=q.usd)
    return body + fx


async def _is_first_purchase(conn, user_id: int) -> bool:
    """Реф. скидка до первого выданного (completed) заказа - см. pricing.quote_product."""
    return await orders_repo.count_user_completed_orders(conn, user_id) == 0


def _payment_kb(product: Product, balance: float, rub_final: float):
    show_full = balance + 1e-6 >= rub_final
    show_partial = (not show_full) and balance >= 0.01 and (rub_final - balance) > 0.01
    from bot.services.vpn_nav import VPN_FLOW_MAIN_CALLBACK

    back_cb = VPN_FLOW_MAIN_CALLBACK if (product.kind or "").strip().lower() == "vpn" else None
    return payment_methods_kb(
        product.id,
        show_full_balance=show_full,
        show_partial_mix=show_partial,
        balance=balance,
        rub_final=rub_final,
        back_callback=back_cb,
    )


async def _present_fiat_checkout(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    *,
    order_id: int,
    rub_due: float,
    intro_html: str,
    usd_base: float,
    buyer_user_id: int,
) -> None:
    """
    После создания заказа со статусом «ожидает оплаты»:
    - если задана CKASSA_BC_UNIVERSAL_PAYMENT_URL или FIAT_PARALLEL_CKASSA_AND_LAVA - экран с ссылкой bc и кодом ORDER{id}
      для назначения платежа; при CKASSA_BC_SOLO_CHECKOUT=true только ссылка (без Shop API и LAVA);
      иначе плюс счёт Shop API Ckassa и LAVA при настройке;
    - иначе по старой схеме: Ckassa Shop API, затем LAVA, затем текстовая инструкция.
    """
    ok_cd, wait_s = await allow_checkout_invoice_attempt(
        conn, order_id, settings.payment_checkout_invoice_cooldown_seconds
    )
    if not ok_cd:
        await cb.answer(
            f"Повторный счёт можно запросить примерно через {int(wait_s) + 1} с.",
            show_alert=True,
        )
        return
    fx = fx_payment_hints_html(settings, rub_final=rub_due, usd_base=usd_base)
    row = await orders_repo.get_order(conn, order_id)
    product_title = str(row["product_title"]) if row else f"Заказ #{order_id}"
    un = (cb.from_user.username or "").strip()
    fn = (cb.from_user.first_name or "").strip()
    ln = (cb.from_user.last_name or "").strip()
    fio = (f"{fn} {ln}".strip() or (f"@{un}" if un else f"Telegram user {buyer_user_id}"))[:200]
    payer_email = f"tg{buyer_user_id}@telegram.invalid"
    payer_phone = (settings.ckassa_default_phone or "").strip() or "+79990000000"

    univers = (getattr(settings, "ckassa_bc_universal_payment_url", "") or "").strip()
    solo_bc = bool(univers) and bool(getattr(settings, "ckassa_bc_solo_checkout", False))
    multi_lane = bool(univers) or bool(getattr(settings, "fiat_parallel_ckassa_and_lava", False))
    ck_url: str | None = None
    ck_ext: str | None = None
    pay_lava: str | None = None
    ext_lava: str | None = None
    pay_cardlink: str | None = None
    ext_cardlink: str | None = None

    if cardlink_checkout_configured(settings):
        pay_cardlink, ext_cardlink = await create_cardlink_bill_meta(
            settings,
            order_id=order_id,
            sum_rub=rub_due,
            description=product_title,
            telegram_user_id=buyer_user_id,
            telegram_username=un or None,
        )

    if multi_lane:
        if not solo_bc:
            if ckassa_checkout_configured(settings):
                ck_url, ck_ext = await create_ckassa_payment_meta(
                    settings,
                    order_id=order_id,
                    rub_due=rub_due,
                    product_title=product_title,
                    payer_email=payer_email,
                    payer_phone=payer_phone,
                    payer_fio=fio,
                )
            if lava_checkout_configured(settings):
                memo = f"ORDER{order_id}"
                pay_lava, ext_lava, _lava_qr = await create_invoice_payment_meta(
                    settings,
                    order_id=order_id,
                    sum_rub=rub_due,
                    comment=memo[:255],
                )
            if pay_cardlink:
                await orders_repo.set_invoice_provider_metadata(
                    conn, order_id=order_id, provider="cardlink", external_id=ext_cardlink
                )
            elif ck_url and pay_lava:
                await orders_repo.set_invoice_provider_metadata(
                    conn, order_id=order_id, provider="multi", external_id=None
                )
            elif ck_url:
                await orders_repo.set_invoice_provider_metadata(
                    conn, order_id=order_id, provider="ckassa", external_id=ck_ext
                )
            elif pay_lava:
                await orders_repo.set_invoice_provider_metadata(
                    conn, order_id=order_id, provider="lava", external_id=ext_lava
                )
        else:
            if pay_cardlink:
                await orders_repo.set_invoice_provider_metadata(
                    conn, order_id=order_id, provider="cardlink", external_id=ext_cardlink
                )
            else:
                await orders_repo.set_invoice_provider_metadata(
                    conn, order_id=order_id, provider="ckassa_bc", external_id=None
                )

        if univers or ck_url or pay_lava or pay_cardlink:
            rub_s = esc(f"{float(rub_due):.2f}")
            oid_s = esc(str(order_id))
            order_memo = f"ORDER{order_id}"
            order_memo_esc = esc(order_memo)
            sup_u = support_order_question_url(settings, order_id)
            sup_href = esc(sup_u) if sup_u else ""
            bc_min = float(getattr(settings, "ckassa_bc_display_min_rub", 50.0) or 50.0)
            if bc_min < 1.0:
                bc_min = 50.0
            bc_min_s = esc(f"{bc_min:.0f}")
            parts: list[str] = [
                fx,
                "",
                f"<b>Сумма заказа: {rub_s} ₽</b>",
                "",
                "<b>Как оплатить</b>",
            ]
            if solo_bc:
                parts.append(
                    "Сейчас доступна <b>оплата по ссылке</b> ниже. Счёт Ckassa с готовой суммой и LAVA "
                    "(авто-статус «Оплачен» по webhook) подключим позже - скажем в канале / закрепе."
                )
            else:
                parts.append("Нажмите <b>одну</b> кнопку оплаты ниже (два раза платить не нужно).")
            if univers:
                under_min = float(rub_due) + 1e-6 < bc_min
                parts.extend(
                    [
                        "",
                        "<b>⭐ Оплата по ссылке Ckassa (пошагово)</b>",
                        f"• <b>Минимум на странице оплаты</b> - обычно <b>{bc_min_s} ₽</b> (ограничение банка/эквайринга). "
                        "Если заказ меньше - уточните в поддержке или доплатите до минимума одним платежом.",
                        f"• <b>Сумма</b> - введите на странице <b>ровно {rub_s} ₽</b>, как в заказе выше.",
                        "• <b>Один платёж</b> - не оплачивайте дважды разными кнопками.",
                        f"• <b>ID заказа в боте</b> - <code>{oid_s}</code> (тот же номер в «Заказы»).",
                        "• <b>Назначение платежа</b> - если банк даёт поле «назначение» / «комментарий», вставьте "
                        "(нажмите на строку ниже в Telegram - скопируется):",
                        f"<code>{order_memo_esc}</code>",
                        "  Так проще найти ваш платёж в выписке.",
                        "• Нажмите кнопку <b>«⭐ Ckassa…»</b>, завершите оплату картой или СБП.",
                        "• Вернитесь сюда и нажмите <b>«Я оплатил»</b> - оператор сверит платёж в кабинете.",
                        f"• Статус <b>«Оплачен»</b> появится в <b>«Заказы»</b> после проверки (часто до 15-30 минут в нерабочее время).",
                        "• <b>Выдача Stars / Premium</b> - только после «Оплачен», затем «В работе» / «Выдан» по очереди магазина.",
                    ]
                )
                if under_min:
                    parts.append(
                        f"\n<b>Внимание:</b> сумма заказа ниже типичного минимума {bc_min_s} ₽ - страница оплаты может не принять. "
                        "Напишите в поддержку до оплаты."
                    )
                if sup_u:
                    parts.append(f'<a href="{sup_href}">Написать в поддержку по заказу #{oid_s}</a>')
                else:
                    parts.append("Вопросы - раздел <b>«Поддержка»</b> в главном меню, укажите номер заказа.")
                parts.append(
                    "<i>Нет поля «назначение» - всё равно нажмите «Я оплатил» после оплаты или напишите в поддержку.</i>"
                )
            if ck_url:
                parts.extend(
                    [
                        "",
                        "<b>💳 Ckassa с готовой суммой</b>",
                        "Сумма уже подставлена. Часто статус «Оплачен» обновляется сам, без кнопки «Я оплатил».",
                    ]
                )
            if pay_lava:
                parts.extend(
                    [
                        "",
                        "<b>💳 LAVA</b>",
                        "Другой способ оплаты картой или СБП. Статус обновится после оплаты по данным LAVA.",
                    ]
                )
            if pay_cardlink:
                parts.extend(
                    [
                        "",
                        "<b>💳 Cardlink</b>",
                        "Оплата картой или СБП. Статус «Оплачен» обновится автоматически после webhook.",
                    ]
                )
            ru = esc((settings.refund_policy_url or "https://aladdin-ai.ru/v1/legal/refund").strip())
            parts.append(
                "\n<i>Цифровые товары, оказанные в полном объёме («выдан»), — возврату не подлежат. "
                f"До выдачи — <a href=\"{ru}\">политика возвратов</a>.</i>"
            )
            await cb.message.edit_text(
                intro_html + "\n".join(parts),
                reply_markup=fiat_checkout_options_kb(
                    universal_url=univers or None,
                    ckassa_shop_url=ck_url,
                    lava_url=pay_lava,
                    cardlink_url=pay_cardlink,
                    bc_claim_order_id=order_id if univers else None,
                    support_order_url=sup_u,
                ),
            )
            return

        missing_multi = (
            "\n\n<b>Онлайн-оплата сейчас не открылась.</b> "
            "Напишите в <b>Поддержку</b> с номером заказа или попробуйте позже."
        )
        _log.warning(
            "fiat_checkout_no_urls_multi_lane order_id=%s univers=%s solo_bc=%s ck_url=%s pay_lava=%s "
            "ckassa_cfg=%s lava_cfg=%s",
            order_id,
            bool(univers),
            solo_bc,
            bool(ck_url),
            bool(pay_lava),
            ckassa_checkout_configured(settings),
            lava_checkout_configured(settings),
        )
        instr = fiat_placeholder_html(settings, order_id=order_id, rub=rub_due)
        await cb.message.edit_text(
            intro_html + fx + missing_multi + f"\n\n<b>{esc(instr.title)}</b>\n{instr.body_html}",
            reply_markup=hub_menu_kb(),
        )
        return

    if pay_cardlink:
        await orders_repo.set_invoice_provider_metadata(
            conn, order_id=order_id, provider="cardlink", external_id=ext_cardlink
        )
        rub_s = esc(f"{float(rub_due):.2f}")
        tail = (
            fx
            + f"\n\n<b>Сумма: {rub_s} ₽</b> — на странице проверьте ту же сумму.\n"
            "После оплаты заказ <b>встанет в очередь</b> на выдачу Stars, Premium или VPN.\n"
            "<b>Что сделать:</b>\n"
            "1) Нажмите <b>«Оплатить в ₽ (Cardlink)»</b> ниже.\n"
            "2) Оплатите картой или СБП на странице Cardlink.\n"
            "3) <b>«Мои заказы»</b> — ждите <b>«Оплачен»</b> (обычно 1–2 минуты).\n"
            "4) Статус не сменился — <b>Поддержка</b> с номером заказа.\n"
            "\n<i>Защищённый эквайринг Cardlink. Дальше — автоматическая или ручная выдача по политике магазина.</i>"
        )
        await cb.message.edit_text(intro_html + tail, reply_markup=cardlink_payment_kb(pay_cardlink))
        return

    if ckassa_checkout_configured(settings):
        ck_url, ck_ext = await create_ckassa_payment_meta(
            settings,
            order_id=order_id,
            rub_due=rub_due,
            product_title=product_title,
            payer_email=payer_email,
            payer_phone=payer_phone,
            payer_fio=fio,
        )
        if ck_url:
            await orders_repo.set_invoice_provider_metadata(
                conn, order_id=order_id, provider="ckassa", external_id=ck_ext
            )
            rub_s = esc(f"{float(rub_due):.2f}")
            tail = (
                fx
                + f"\n\n<b>Сумма: {rub_s} ₽</b> - на странице оплаты должна быть <b>та же сумма</b>.\n"
                "После оплаты в боте заказ <b>встанет в очередь</b> на выдачу: Stars, Premium или подарок - что вы "
                "выбрали. Срок - от нагрузки, обычно недолго.\n"
                "<b>Что сделать:</b>\n"
                "1) Нажмите <b>«Оплатить в ₽ (карта / СБП)»</b> ниже.\n"
                "2) Оплатите на открывшейся странице: карта, СБП и др. - как предложит банк.\n"
                "3) Откройте <b>«Мои заказы»</b> - дождитесь <b>«Оплачен»</b> (часто 1-2 минуты).\n"
                "4) Если <b>«Оплачен»</b> нет - напишите в <b>Поддержку</b> с номером заказа.\n"
                "\n<i>Защищённый эквайринг (партнёры Ckassa / LAVA - у магазина настраивается один поток). "
                "Дальше - выдача Stars / Premium: автоматом или вручную, по политике магазина.</i>"
            )
            await cb.message.edit_text(intro_html + tail, reply_markup=ckassa_payment_kb(ck_url))
            return
        miss = "\n\n<b>Ссылка на оплату не открылась.</b> Пробуем запасной способ - подождите пару секунд."
        intro_html = intro_html + miss

    memo = f"ORDER{order_id}"
    pay_url, ext_id, _lava_qr = await create_invoice_payment_meta(
        settings,
        order_id=order_id,
        sum_rub=rub_due,
        comment=memo[:255],
    )
    if pay_url:
        await orders_repo.set_invoice_provider_metadata(
            conn, order_id=order_id, provider="lava", external_id=ext_id
        )
    if pay_url:
        rub_s = esc(f"{float(rub_due):.2f}")
        tail = (
            fx
            + f"\n\n<b>Сумма: {rub_s} ₽</b> - на странице проверьте ту же сумму.\n"
            "После оплаты в боте заказ <b>встанет в очередь</b> на выдачу: Stars, Premium или подарок - что в заказе. "
            "Срок - от нагрузки, обычно недолго.\n"
            "<b>Что сделать:</b>\n"
            "1) Нажмите <b>«Оплатить в ₽ (карта / СБП)»</b> ниже.\n"
            "2) Оплатите на открывшейся странице (карта / СБП - что предложит банк).\n"
            "3) <b>«Мои заказы»</b> - ждите <b>«Оплачен»</b>.\n"
            "4) Статус не сменился - <b>Поддержка</b> с номером заказа.\n"
            "\n<i>Дальше - выдача Stars / Premium: автоматом или вручную, по политике магазина.</i>"
        )
        await cb.message.edit_text(intro_html + tail, reply_markup=lava_payment_kb(pay_url))
        return
    missing_lava = ""
    if not lava_checkout_configured(settings) and not ckassa_checkout_configured(settings):
        missing_lava = (
            "\n\n<b>Онлайн-оплата сейчас недоступна.</b> "
            "Напишите в <b>Поддержку</b> - укажите номер заказа, вам подскажут, как оплатить."
        )
    elif ckassa_checkout_configured(settings) and not lava_checkout_configured(settings):
        missing_lava = (
            "\n\n<b>Оплата картой/СБП сейчас не открылась.</b> "
            "Заказ сохранён. Напишите в <b>Поддержку</b> с номером заказа или попробуйте позже."
        )
    else:
        missing_lava = (
            "\n\n<b>Ссылка на оплату не создалась.</b> "
            "Попробуйте через несколько минут или напишите в <b>Поддержку</b> (номер заказа пригодится)."
        )
    _log.warning(
        "fiat_checkout_placeholder_sequential order_id=%s univers_nonempty=%s ckassa_cfg=%s lava_cfg=%s",
        order_id,
        bool((getattr(settings, "ckassa_bc_universal_payment_url", "") or "").strip()),
        ckassa_checkout_configured(settings),
        lava_checkout_configured(settings),
    )
    instr = fiat_placeholder_html(settings, order_id=order_id, rub=rub_due)
    await cb.message.edit_text(
        intro_html
        + fx
        + missing_lava
        + f"\n\n<b>{esc(instr.title)}</b>\n{instr.body_html}",
        reply_markup=hub_menu_kb(),
    )


async def _present_crypto_checkout(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    *,
    order_id: int,
    due_rub: float,
    intro_html: str,
    usd_for_fx: float,
) -> None:
    """
    Счета USDT (TRC20): Crypto Pay (@CryptoBot) и/или xRocket Pay - URL-кнопки.
    Если провайдеры выключены или не настроены - ручной блок USDT из .env (TON в том же блоке при CRYPTO_SHOW_TON_MANUAL и заполненном CRYPTO_TON).
    """
    ok_cd, wait_s = await allow_checkout_invoice_attempt(
        conn, order_id, settings.payment_checkout_invoice_cooldown_seconds
    )
    if not ok_cd:
        await cb.answer(
            f"Повторный счёт можно запросить примерно через {int(wait_s) + 1} с.",
            show_alert=True,
        )
        return
    fx = fx_payment_hints_html(settings, rub_final=due_rub, usd_base=usd_for_fx) if usd_for_fx > 0 else ""

    desc = f"Заказ #{order_id}"
    urls: list[tuple[str, str]] = []
    tried_providers = False

    if crypto_pay_invoice_api_ready(settings):
        tried_providers = True
        u, ext = await create_crypto_pay_invoice_checkout_meta(
            settings, order_id=order_id, due_rub=due_rub, description=desc
        )
        if u:
            urls.append(("💎 Crypto Pay (@CryptoBot), USDT TRC20", u))
            await orders_repo.set_invoice_provider_metadata(
                conn, order_id=order_id, provider="crypto_pay", external_id=ext
            )

    if xrocket_invoice_api_ready(settings):
        tried_providers = True
        u, ext = await create_xrocket_invoice_checkout_meta(
            settings, order_id=order_id, due_rub=due_rub, description=desc
        )
        if u:
            urls.append(("🚀 xRocket Pay, USDT TRC20", u))
            await orders_repo.set_invoice_provider_metadata(
                conn, order_id=order_id, provider="xrocket", external_id=ext
            )

    if urls:
        tail = (
            fx
            + "\n\n<b>Сумма: оплата в USDT (TRC20) по счёту</b> - в Telegram откроется счёт выбранного сервиса. "
            "Сумма в USDT в счёте - от провайдера.\n"
            "После оплаты в боте заказ <b>встанет в очередь</b> на выдачу: Stars, Premium - как в заказе.\n"
            "<b>Что сделать:</b>\n"
            "1) Нажмите кнопку Crypto Pay и/или xRocket ниже - откроется счёт в Telegram.\n"
            "2) Оплатите по счёту. Дождитесь, пока статус в боте станет <b>«Оплачен»</b> (часто быстро).\n"
            "3) <b>«Мои заказы»</b> - проверяйте статус.\n"
            "4) <b>«Оплачен»</b> нет - напишите в <b>Поддержку</b> с номером заказа.\n"
            "\n<i>Дальше - выдача по очереди, оператор переведёт заказ в <b>«В работе»</b> и <b>«Выдан»</b> "
            "когда будет готово.</i>\n"
        )
        await cb.message.edit_text(intro_html + tail, reply_markup=crypto_providers_kb(urls))
        return

    if tried_providers:
        _log.warning(
            "crypto_checkout: invoice not created (providers tried), order_id=%s - check rates/API in env, logs",
            order_id,
        )
        fail = (
            "\n\n<b>Счёт в Telegram не открылся.</b> Заказ ждёт оплаты. "
            "Попробуйте через пару минут или напишите в <b>Поддержку</b> (номер заказа). "
        )
        if settings.crypto_pay_wallet_fallback:
            pay = crypto_payment_block_html(settings, order_id=order_id, rub=due_rub, usd_for_fx=usd_for_fx)
            await cb.message.edit_text(intro_html + fail + pay, reply_markup=hub_menu_kb())
            return
        await cb.message.edit_text(intro_html + fail + fx, reply_markup=hub_menu_kb())
        return

    pay = crypto_payment_block_html(settings, order_id=order_id, rub=due_rub, usd_for_fx=usd_for_fx)
    await cb.message.edit_text(intro_html + pay, reply_markup=hub_menu_kb())


def _order_row_str(row, key: str, default: str = "") -> str:
    """sqlite3.Row не имеет .get() — только индексация по имени колонки."""
    try:
        val = row[key]
    except (KeyError, IndexError, TypeError):
        return default
    if val is None:
        return default
    return str(val).strip()


def _parse_pay_inv(data: str) -> tuple[str, int] | None:
    parts = (data or "").split(":")
    if len(parts) < 4 or parts[0] != "pay" or parts[1] != "inv":
        return None
    try:
        return parts[2], int(parts[3])
    except ValueError:
        return None


async def _require_pending_vpn_order(
    cb: CallbackQuery,
    conn,
    order_id: int,
    user_id: int,
):
    row = await orders_repo.get_order(conn, order_id)
    if not row or int(row["user_id"]) != user_id:
        await cb.answer("Заказ не найден", show_alert=True)
        return None
    if _order_row_str(row, "product_kind").lower() != "vpn":
        await cb.answer("Это не заказ VPN", show_alert=True)
        return None
    if _order_row_str(row, "status").lower() != "pending_payment":
        await cb.answer("Заказ уже оплачен или закрыт", show_alert=True)
        return None
    return row


async def _present_vpn_order_invoice(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    *,
    order_id: int,
) -> None:
    from bot.services.vpn_invoice_screen import vpn_invoice_screen_html

    row = await _require_pending_vpn_order(cb, conn, order_id, cb.from_user.id)
    if not row:
        return
    pmap = products_by_id(products)
    p = pmap.get(str(row["product_id"] or ""))
    if not p:
        await cb.answer("Товар не найден", show_alert=True)
        return
    due = orders_repo.amount_due_external(row)
    try:
        bap = float(row["balance_applied_rub"] or 0)
    except (KeyError, TypeError):
        bap = 0.0
    pm = _order_row_str(row, "payment_method", "fiat").lower()
    html = await vpn_invoice_screen_html(
        settings,
        conn,
        order_id=order_id,
        rub_due=due,
        product=p,
        telegram_user_id=cb.from_user.id,
        payment_method=pm,
        balance_applied=bap,
    )
    await cb.message.edit_text(
        html,
        reply_markup=vpn_order_invoice_kb(settings, order_id, pm),
    )


async def _pay_inv_lava_channel(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    *,
    order_id: int,
    lava_service: str,
    channel: str,
) -> None:
    from bot.services.vpn_payment_copy import (
        vpn_invoice_card_checkout_html,
        vpn_invoice_sbp_checkout_html,
    )

    row = await _require_pending_vpn_order(cb, conn, order_id, cb.from_user.id)
    if not row:
        return
    ok_cd, wait_s = await allow_checkout_invoice_attempt(
        conn, order_id, settings.payment_checkout_invoice_cooldown_seconds
    )
    if not ok_cd:
        await cb.answer(
            f"Повторный счёт можно запросить примерно через {int(wait_s) + 1} с.",
            show_alert=True,
        )
        return
    due = orders_repo.amount_due_external(row)
    memo = f"ORDER{order_id}"
    pay_url, ext, qr_url = await create_invoice_payment_meta(
        settings,
        order_id=order_id,
        sum_rub=due,
        comment=memo[:255],
        include_service=[lava_service],
    )
    if not pay_url:
        await cb.answer("Не удалось открыть оплату. Попробуйте позже.", show_alert=True)
        return
    await orders_repo.set_invoice_provider_metadata(
        conn, order_id=order_id, provider="lava", external_id=ext
    )
    ch = (channel or lava_service).strip().lower()
    if ch == "sbp":
        html = vpn_invoice_sbp_checkout_html(
            order_id=order_id, rub_due=due, qr_in_chat=True
        )
    else:
        html = vpn_invoice_card_checkout_html(order_id=order_id, rub_due=due)
    await cb.message.edit_text(
        html,
        reply_markup=vpn_invoice_pay_url_kb(
            pay_url,
            back_callback=f"pay:inv:view:{order_id}",
            channel=ch,
        ),
    )
    if ch == "sbp":
        from aiogram.types import BufferedInputFile

        from bot.services.wg_qr_util import pay_sbp_qr_filename, pay_url_qr_png_bytes

        cap = (
            f"<b>📱 QR — страница оплаты СБП</b>\n"
            f"Заказ <code>{esc(order_id)}</code> · <b>{esc(f'{float(due):.2f}')} ₽</b>\n\n"
            "1) Отсканируйте камерой или в банке.\n"
            "2) Откроется страница LAVA — там будет <b>QR НСПК</b> для СБП.\n"
            "3) Или нажмите кнопку «📱 Открыть СБП» в сообщении выше."
        )
        try:
            if qr_url:
                await cb.message.answer_photo(qr_url, caption=cap)
            else:
                png = pay_url_qr_png_bytes(pay_url)
                photo = BufferedInputFile(png, filename=pay_sbp_qr_filename(order_id))
                await cb.message.answer_photo(photo, caption=cap)
        except Exception:
            _log.warning("sbp_qr_photo_failed order_id=%s", order_id, exc_info=True)
    await cb.answer()


async def _pay_inv_ckassa(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    *,
    order_id: int,
) -> None:
    from bot.services.vpn_payment_copy import vpn_invoice_card_checkout_html

    row = await _require_pending_vpn_order(cb, conn, order_id, cb.from_user.id)
    if not row:
        return
    if not ckassa_checkout_configured(settings):
        await cb.answer("Ckassa сейчас недоступна", show_alert=True)
        return
    ok_cd, wait_s = await allow_checkout_invoice_attempt(
        conn, order_id, settings.payment_checkout_invoice_cooldown_seconds
    )
    if not ok_cd:
        await cb.answer(
            f"Повторный счёт можно запросить примерно через {int(wait_s) + 1} с.",
            show_alert=True,
        )
        return
    due = orders_repo.amount_due_external(row)
    product_title = str(row["product_title"])
    un = (cb.from_user.username or "").strip()
    fn = (cb.from_user.first_name or "").strip()
    ln = (cb.from_user.last_name or "").strip()
    fio = (f"{fn} {ln}".strip() or (f"@{un}" if un else f"Telegram user {cb.from_user.id}"))[:200]
    payer_email = f"tg{cb.from_user.id}@telegram.invalid"
    payer_phone = (settings.ckassa_default_phone or "").strip() or "+79990000000"
    ck_url, ck_ext = await create_ckassa_payment_meta(
        settings,
        order_id=order_id,
        rub_due=due,
        product_title=product_title,
        payer_email=payer_email,
        payer_phone=payer_phone,
        payer_fio=fio,
    )
    if not ck_url:
        await cb.answer("Ссылка Ckassa не открылась", show_alert=True)
        return
    await orders_repo.set_invoice_provider_metadata(
        conn, order_id=order_id, provider="ckassa", external_id=ck_ext
    )
    html = vpn_invoice_card_checkout_html(order_id=order_id, rub_due=due)
    await cb.message.edit_text(
        html,
        reply_markup=vpn_invoice_pay_url_kb(
            ck_url,
            back_callback=f"pay:inv:view:{order_id}",
            channel="card",
        ),
    )
    await cb.answer()


async def _pay_inv_bc_universal(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    *,
    order_id: int,
) -> None:
    row = await _require_pending_vpn_order(cb, conn, order_id, cb.from_user.id)
    if not row:
        return
    univers = (getattr(settings, "ckassa_bc_universal_payment_url", "") or "").strip()
    if not univers:
        await cb.answer("Ссылка оплаты не настроена", show_alert=True)
        return
    due = orders_repo.amount_due_external(row)
    rub_s = esc(f"{float(due):.2f}")
    oid_s = esc(str(order_id))
    order_memo = esc(f"ORDER{order_id}")
    sup_u = support_order_question_url(settings, order_id)
    text = (
        f"<b>Заказ <code>{oid_s}</code></b> · <b>{rub_s} ₽</b>\n\n"
        "<b>Оплата по ссылке</b>\n"
        f"• Сумма на странице: <b>{rub_s} ₽</b>\n"
        f"• В комментарии (если есть поле): <code>{order_memo}</code>\n"
        "• После оплаты нажмите <b>«Я оплатил»</b>.\n"
    )
    await cb.message.edit_text(
        text,
        reply_markup=fiat_checkout_options_kb(
            universal_url=univers,
            ckassa_shop_url=None,
            lava_url=None,
            bc_claim_order_id=order_id,
            support_order_url=sup_u,
        ),
    )
    await cb.answer()


@router.callback_query(F.data.startswith("pay:inv:"))
async def pay_inv_router(
    cb: CallbackQuery,
    settings: Settings,
    conn,
    products: list[Product],
    state: FSMContext,
) -> None:
    parsed = _parse_pay_inv(cb.data or "")
    if not parsed:
        await cb.answer()
        return
    action, order_id = parsed
    if action == "view":
        await _present_vpn_order_invoice(cb, settings, conn, products, order_id=order_id)
        await cb.answer()
        return
    if action == "cancel":
        await state.clear()
        await cb.answer("Счёт закрыт. Заказ остаётся в «Мои заказы».")
        from bot.handlers.vpn import _vpn_present_main_screen

        await _vpn_present_main_screen(
            cb.message, cb.bot, settings, conn, products, cb.from_user.id
        )
        return
    if action == "sbp":
        await _pay_inv_lava_channel(
            cb, settings, conn, order_id=order_id, lava_service="sbp", channel="sbp"
        )
        return
    if action == "card":
        await _pay_inv_lava_channel(
            cb, settings, conn, order_id=order_id, lava_service="card", channel="card"
        )
        return
    if action == "ckassa":
        await _pay_inv_ckassa(cb, settings, conn, order_id=order_id)
        return
    if action == "bc":
        await _pay_inv_bc_universal(cb, settings, conn, order_id=order_id)
        return
    if action == "crypto":
        row = await _require_pending_vpn_order(cb, conn, order_id, cb.from_user.id)
        if not row:
            return
        due = orders_repo.amount_due_external(row)
        q_usd = float(row["usd_base"] or 0)
        rub_total = float(row["rub_after_discounts"] or due)
        usd_part = q_usd * (due / rub_total) if rub_total > 1e-6 else q_usd
        from bot.services.vpn_invoice_screen import vpn_invoice_screen_html

        pmap = products_by_id(products)
        p = pmap.get(str(row["product_id"] or ""))
        if not p:
            await cb.answer("Товар не найден", show_alert=True)
            return
        try:
            bap = float(row["balance_applied_rub"] or 0)
        except (KeyError, TypeError):
            bap = 0.0
        pm = _order_row_str(row, "payment_method", "crypto").lower()
        intro = await vpn_invoice_screen_html(
            settings,
            conn,
            order_id=order_id,
            rub_due=due,
            product=p,
            telegram_user_id=cb.from_user.id,
            payment_method=pm,
            balance_applied=bap,
        )
        intro = intro + "\n\n"
        await _present_crypto_checkout(
            cb,
            settings,
            conn,
            order_id=order_id,
            due_rub=due,
            intro_html=intro,
            usd_for_fx=usd_part,
        )
        await cb.answer()
        return
    await cb.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("<b>Оформление сброшено.</b>", reply_markup=hub_menu_kb())


@router.callback_query(F.data.startswith("buy:"))
async def open_product(cb: CallbackQuery, products: list[Product], settings: Settings, conn, state: FSMContext) -> None:
    await state.clear()
    pid = cb.data.split(":", 1)[1]
    pmap = products_by_id(products)
    p = pmap.get(pid)
    if not p:
        await cb.answer("Товар не найден", show_alert=True)
        return
    if (p.kind or "").strip().lower() == "vpn":
        from bot.services.vpn_legal_gate import ensure_vpn_legal_accepted

        if not await ensure_vpn_legal_accepted(
            conn=conn,
            user_id=cb.from_user.id,
            settings=settings,
            message=cb.message,
            products=products,
        ):
            await cb.answer(
                "Сначала отметьте обе галочки: политика и соглашение AiMonkeyVPN.",
                show_alert=True,
            )
            return
    await cb.answer()
    is_first = await _is_first_purchase(conn, cb.from_user.id)
    q = quote_product(p, settings, is_first_order=is_first)
    if p.kind == "premium":
        text = (
            _fmt_quote_html(p, q, settings)
            + "\n\nКому оформляем <b>Telegram Premium</b>?"
        )
        await cb.message.edit_text(text, reply_markup=premium_dest_kb(p.id))
    else:
        hint = ""
        if p.kind == "stars":
            r100 = rub_per_100_stars_display(products, settings, is_first_order=is_first)
            if r100 is not None:
                hint = f"\n\n<i>Ориентир: от {esc(f'{r100:.2f}')} ₽ за 100 ⭐.</i>"
            hint += "\n<i>Подарок уйдёт на @username, который укажете после выбора оплаты.</i>"
        if p.kind == "gift":
            hint = "\n\n<i>Укажите @username получателя после выбора способа оплаты.</i>"
        if p.kind == "vpn":
            hint = (
                "\n\n<i>Подписка на этот Telegram. После оплаты (~2 мин) — "
                "«📥 Файл» или «📷 QR» в разделе AiMonkeyVPN.</i>"
            )
            if is_first and q.rub_referral_discount <= 0:
                rb = esc(settings.ref_buyer_discount_percent)
                hint = (
                    f"\n\n<i>Первая покупка в магазине: обычно −{rb}% по вашей пригласительной ссылке "
                    f"(если вы пришли по ref_ и ещё не было выданных заказов).</i>"
                ) + hint
        bal = await balance_repo.get_balance(conn, cb.from_user.id)
        text = _fmt_quote_html(p, q, settings) + hint + "\n\n<b>Способ оплаты</b>"
        await cb.message.edit_text(
            text,
            reply_markup=_payment_kb(p, bal, q.rub_final),
        )
    try:
        await analytics_repo.log_event(
            conn, user_id=cb.from_user.id, event_type="product_view", meta={"product_id": pid}
        )
        await analytics_repo.log_event(
            conn, user_id=cb.from_user.id, event_type="offer_click", meta={"product_id": pid}
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("prem:"))
async def premium_pick_dest(cb: CallbackQuery, products: list[Product], settings: Settings, conn, state: FSMContext) -> None:
    _, who, pid = cb.data.split(":", 2)
    pmap = products_by_id(products)
    p = pmap.get(pid)
    if not p or p.kind != "premium":
        await cb.answer("Товар не найден", show_alert=True)
        return
    await state.update_data(product_id=pid, premium_self=(who == "slf"))
    is_first = await _is_first_purchase(conn, cb.from_user.id)
    q = quote_product(p, settings, is_first_order=is_first)
    bal = await balance_repo.get_balance(conn, cb.from_user.id)
    text = _fmt_quote_html(p, q, settings) + "\n\n<b>Способ оплаты</b>"
    await cb.answer()
    await cb.message.edit_text(
        text,
        reply_markup=_payment_kb(p, bal, q.rub_final),
    )
    try:
        await analytics_repo.log_event(
            conn, user_id=cb.from_user.id, event_type="product_view", meta={"product_id": pid}
        )
        await analytics_repo.log_event(
            conn, user_id=cb.from_user.id, event_type="offer_click", meta={"product_id": pid}
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("pay:bcc:"))
async def bc_universal_payment_claim(cb: CallbackQuery, settings: Settings, conn, bot: Bot) -> None:
    """Покупатель сообщил, что оплатил на универсальной bc-странице Ckassa - пинг админам для ручной сверки."""
    raw = (cb.data or "").strip()
    parts = raw.split(":")
    if len(parts) != 3:
        await cb.answer()
        return
    try:
        oid = int(parts[2])
    except ValueError:
        await cb.answer()
        return
    cool = max(0, int(getattr(settings, "bc_payment_claim_cooldown_seconds", 900) or 0))
    code, wait_s = await orders_repo.touch_bc_payment_claim_if_allowed(
        conn,
        order_id=oid,
        user_id=cb.from_user.id,
        cooldown_seconds=cool,
    )
    if code == "not_found":
        await cb.answer("Заказ не найден", show_alert=True)
        return
    if code == "wrong_user":
        await cb.answer("Это не ваш заказ", show_alert=True)
        return
    if code == "wrong_status":
        await cb.answer("Статус заказа уже другой - откройте «Мои заказы».", show_alert=True)
        return
    if code == "cooldown":
        m = max(1, int(wait_s) // 60) if int(wait_s) >= 60 else 1
        await cb.answer(f"Сигнал уже отправляли. Повторите примерно через {m} мин или напишите в поддержку.", show_alert=True)
        return
    await _notify_admins_bc_payment_claim(bot, settings, conn, order_id=oid, from_user=cb.from_user)
    await cb.answer("Отправили операторам. Ждите проверки в «Мои заказы».")


@router.callback_query(F.data.startswith("pay:"))
async def choose_payment(cb: CallbackQuery, state: FSMContext, products: list[Product], settings: Settings, conn) -> None:
    parts = cb.data.split(":", 2)
    if len(parts) < 3:
        await cb.answer()
        return
    _, method, pid = parts
    if method not in ("fiat", "crypto", "bal", "mixfi", "mixcr"):
        await cb.answer()
        return
    pmap = products_by_id(products)
    if pid not in pmap:
        await cb.answer("Товар не найден", show_alert=True)
        return
    p = pmap[pid]
    try:
        await analytics_repo.log_event(
            conn,
            user_id=cb.from_user.id,
            event_type="checkout_start",
            meta={"product_id": pid, "payment_method": method},
        )
    except Exception:
        pass
    data = await state.get_data()
    premium_self = bool(data.get("premium_self"))

    if p.kind == "vpn":
        from bot.services.vpn_nav import VPN_FLOW_MAIN_CALLBACK

        un = (cb.from_user.username or "").strip()
        recipient = f"@{un}" if un else f"Telegram ID {cb.from_user.id}"
        await state.update_data(product_id=pid, payment=method, recipient=recipient)
        await state.set_state(CheckoutStates.waiting_confirm)
        is_first = await _is_first_purchase(conn, cb.from_user.id)
        q = quote_product(p, settings, is_first_order=is_first)
        await cb.answer()
        await cb.message.edit_text(
            _fmt_quote_html(p, q, settings)
            + f"\n\n<b>Подключение:</b> на ваш аккаунт Telegram "
            f"<code>{esc(recipient)}</code>.\n"
            "Нажмите «Создать заказ».",
            reply_markup=confirm_order_kb(cancel_callback=VPN_FLOW_MAIN_CALLBACK),
        )
        return

    if p.kind == "premium" and premium_self:
        un = cb.from_user.username
        if not un:
            await cb.answer("Нужен @username в Telegram или выберите «Подарок другому»", show_alert=True)
            return
        recipient = f"@{un}"
        await state.update_data(product_id=pid, payment=method, recipient=recipient)
        await state.set_state(CheckoutStates.waiting_confirm)
        is_first = await _is_first_purchase(conn, cb.from_user.id)
        q = quote_product(p, settings, is_first_order=is_first)
        await cb.message.edit_text(
            _fmt_quote_html(p, q, settings)
            + f"\n\n<b>Получатель:</b> <code>{esc(recipient)}</code> (ваш аккаунт)",
            reply_markup=confirm_order_kb(),
        )
        await cb.answer()
        return

    await state.update_data(product_id=pid, payment=method)
    await state.set_state(CheckoutStates.waiting_recipient)
    await cb.message.edit_text(
        "✍️ Укажите <b>@username</b> получателя в Telegram.\nПример: <code>@nickname</code>",
    )
    await cb.answer()


@router.message(CheckoutStates.waiting_recipient, F.text)
async def read_recipient(message: Message, state: FSMContext, products: list[Product], settings: Settings, conn) -> None:
    handle = (message.text or "").strip()
    if not _USERNAME_RE.match(handle):
        await message.answer("Похоже, это не username. Пример: <code>@nickname</code>")
        return
    if not handle.startswith("@"):
        handle = "@" + handle

    data = await state.get_data()
    pid = data.get("product_id")
    pmap = products_by_id(products)
    p = pmap.get(pid or "")
    if not p:
        await state.clear()
        await message.answer("Сессия устарела.", reply_markup=hub_menu_kb())
        return

    await state.update_data(recipient=handle)
    await state.set_state(CheckoutStates.waiting_verify_username)
    await message.answer(
        f"<b>Проверьте получателя</b>\n<code>{esc(handle)}</code>\n\n"
        "Если ошиблись - нажмите «Исправить» и введите снова.",
        reply_markup=verify_username_kb(),
    )


@router.callback_query(F.data == "usr:ok", CheckoutStates.waiting_verify_username)
async def verify_username_ok(cb: CallbackQuery, state: FSMContext, products: list[Product], settings: Settings, conn) -> None:
    data = await state.get_data()
    pid = data.get("product_id")
    recipient = data.get("recipient")
    pmap = products_by_id(products)
    p = pmap.get(pid or "")
    if not p or not recipient:
        await state.clear()
        await cb.message.edit_text("Сессия устарела.", reply_markup=hub_menu_kb())
        await cb.answer()
        return
    is_first = await _is_first_purchase(conn, cb.from_user.id)
    q = quote_product(p, settings, is_first_order=is_first)
    await state.set_state(CheckoutStates.waiting_confirm)
    await cb.message.edit_text(
        _fmt_quote_html(p, q, settings)
        + f"\n\n<b>Получатель:</b> <code>{esc(recipient)}</code>\n"
        "Нажмите «Создать заказ».",
        reply_markup=confirm_order_kb(),
    )
    await cb.answer()


@router.callback_query(F.data == "usr:ed", CheckoutStates.waiting_verify_username)
async def verify_username_edit(cb: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CheckoutStates.waiting_recipient)
    await cb.message.edit_text(
        "✍️ Введите <b>@username</b> получателя снова.\nПример: <code>@nickname</code>",
    )
    await cb.answer()


@router.callback_query(F.data == "order:cancel")
async def order_cancel(cb: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    await state.clear()
    await cb.message.edit_text("<b>Оформление отменено.</b>", reply_markup=hub_menu_kb(settings))
    await cb.answer()


@router.callback_query(F.data == "order:submit", CheckoutStates.waiting_confirm)
async def order_submit(
    cb: CallbackQuery,
    state: FSMContext,
    products: list[Product],
    settings: Settings,
    conn,
    bot: Bot,
) -> None:
    data = await state.get_data()
    pid = data.get("product_id")
    payment = data.get("payment")
    recipient = data.get("recipient")
    pmap = products_by_id(products)
    p = pmap.get(pid or "")
    pk, sq, pm = product_order_columns(p) if p else ("", None, None)
    if not p or payment not in ("fiat", "crypto", "bal", "mixfi", "mixcr") or not recipient:
        await cb.answer("Сессия устарела", show_alert=True)
        await state.clear()
        return

    if not await users_repo.is_onboarding_completed(conn, cb.from_user.id):
        await cb.answer("Сначала завершите вход в бота: отправьте /start", show_alert=True)
        return
    if not await users_repo.checkout_captcha_valid(conn, cb.from_user.id):
        await emoji_captcha.prompt_checkout_captcha(cb, conn, settings)
        await cb.answer()
        return
    if not await orders_repo.allow_order_create_interval(
        conn, cb.from_user.id, float(settings.order_create_min_interval_seconds)
    ):
        await cb.answer("Слишком частые заказы. Подождите несколько секунд.", show_alert=True)
        return

    is_first = await _is_first_purchase(conn, cb.from_user.id)
    q = quote_product(p, settings, is_first_order=is_first)
    row = await users_repo.get_user(conn, cb.from_user.id)
    referrer_id = int(row["referrer_id"]) if row and row["referrer_id"] is not None else None
    rub = q.rub_final
    ref_pct = referral_discount_percent_snapshot(rub_list=q.rub_list, rub_referral_discount=q.rub_referral_discount)
    rate_snap = float(settings.usd_rub_rate)

    if payment == "bal":
        try:
            order_id = await orders_repo.create_paid_order_from_balance(
                conn,
                user_id=cb.from_user.id,
                product_id=p.id,
                product_title=f"{p.emoji} {p.title}",
                usd_base=q.usd,
                rub_before=q.rub_list,
                rub_after=rub,
                referral_discount_rub=q.rub_referral_discount,
                wholesale_discount_rub=q.rub_wholesale_discount,
                referrer_id=referrer_id,
                user_note=str(recipient),
                product_kind=pk,
                stars_qty=sq,
                premium_months=pm,
                referral_discount_percent=ref_pct,
                usd_rub_rate_snapshot=rate_snap,
            )
        except ValueError:
            await cb.answer("Недостаточно средств на балансе", show_alert=True)
            return
        try:
            await analytics_repo.log_event(
                conn,
                user_id=cb.from_user.id,
                event_type="order_created",
                meta={"order_id": order_id, "product_id": p.id},
            )
            await analytics_repo.log_event(
                conn,
                user_id=cb.from_user.id,
                event_type="checkout_paid",
                meta={"order_id": order_id, "product_id": p.id, "payment_method": "bal"},
            )
        except Exception:
            pass
        from bot.services.vpn_payment_hook import schedule_vpn_provision_after_paid

        schedule_vpn_provision_after_paid(settings, order_id)
        await state.clear()
        if pk == "vpn":
            from bot.services.vpn_post_purchase_delivery import (
                vpn_paid_summary_html,
                vpn_paid_summary_kb,
            )

            days = int(p.vpn_subscription_days or 30)
            body = await vpn_paid_summary_html(
                settings,
                order_id=order_id,
                rub=rub,
                telegram_user_id=cb.from_user.id,
                vpn_days=days,
            )
            await cb.message.edit_text(body, reply_markup=vpn_paid_summary_kb())
            await cb.answer()
            await _notify_admins(bot, settings, conn, order_id)
            return
        else:
            body = (
                f"<b>Заказ оплачен с баланса</b>\n"
                f"ID: <code>{esc(order_id)}</code>\n"
                f"Сумма: <b>{esc(f'{rub:.2f}')} ₽</b>\n"
                f"Получатель: <code>{esc(recipient)}</code>\n\n"
                "Дальше оператор обработает заказ и обновит статус после выдачи."
            )
        await cb.message.edit_text(body, reply_markup=hub_menu_kb())
        await cb.answer()
        await _notify_admins(bot, settings, conn, order_id)
        return

    if payment in ("mixfi", "mixcr"):
        bal_now = await balance_repo.get_balance(conn, cb.from_user.id)
        apply = round(min(bal_now, rub), 2)
        if apply <= 0:
            await cb.answer("Недостаточно средств на балансе", show_alert=True)
            return
        pm = "mix_fiat" if payment == "mixfi" else "mix_crypto"
        try:
            order_id = await orders_repo.create_order_with_balance_partial(
                conn,
                user_id=cb.from_user.id,
                product_id=p.id,
                product_title=f"{p.emoji} {p.title}",
                payment_method=pm,
                usd_base=q.usd,
                rub_before=q.rub_list,
                rub_invoice_total=rub,
                referral_discount_rub=q.rub_referral_discount,
                wholesale_discount_rub=q.rub_wholesale_discount,
                referrer_id=referrer_id,
                user_note=str(recipient),
                balance_apply=apply,
                settings=settings,
                product_kind=pk,
                stars_qty=sq,
                premium_months=pm,
                referral_discount_percent=ref_pct,
                usd_rub_rate_snapshot=rate_snap,
            )
        except ValueError as e:
            if str(e) == "order_pending_cap":
                await cb.answer(
                    "Слишком много заказов в ожидании оплаты. Оплатите или отмените старые.",
                    show_alert=True,
                )
                return
            await cb.answer("Не удалось списать баланс", show_alert=True)
            return
        try:
            await analytics_repo.log_event(
                conn,
                user_id=cb.from_user.id,
                event_type="order_created",
                meta={"order_id": order_id, "product_id": p.id},
            )
        except Exception:
            pass
        await state.clear()
        row = await orders_repo.get_order(conn, order_id)
        due = orders_repo.amount_due_external(row)
        if due <= 0.01:
            from bot.services.vpn_payment_hook import schedule_vpn_provision_after_paid

            schedule_vpn_provision_after_paid(settings, order_id)
            try:
                await analytics_repo.log_event(
                    conn,
                    user_id=cb.from_user.id,
                    event_type="checkout_paid",
                    meta={"order_id": order_id, "product_id": p.id, "payment_method": pm},
                )
            except Exception:
                pass
            if pk == "vpn":
                from bot.services.vpn_post_purchase_delivery import (
                    vpn_paid_summary_html,
                    vpn_paid_summary_kb,
                )

                days = int(p.vpn_subscription_days or 30)
                body = await vpn_paid_summary_html(
                    settings,
                    order_id=order_id,
                    rub=rub,
                    telegram_user_id=cb.from_user.id,
                    vpn_days=days,
                )
                await cb.message.edit_text(body, reply_markup=vpn_paid_summary_kb())
            else:
                body = (
                    f"<b>Заказ оплачен</b> (часть с баланса)\n"
                    f"ID: <code>{esc(order_id)}</code>\n"
                    f"С баланса: <b>{esc(f'{apply:.2f}')} ₽</b>\n"
                    f"Всего: <b>{esc(f'{rub:.2f}')} ₽</b>\n"
                    f"Получатель: <code>{esc(recipient)}</code>"
                )
                await cb.message.edit_text(body, reply_markup=hub_menu_kb())
            await cb.answer()
            await _notify_admins(bot, settings, conn, order_id)
            return
        if pk == "vpn":
            await _present_vpn_order_invoice(cb, settings, conn, products, order_id=order_id)
        elif payment == "mixfi":
            intro = (
                f"<b>Заказ #{esc(order_id)}</b>\n"
                f"С баланса: <b>{esc(f'{apply:.2f}')} ₽</b> · "
                f"<b>доплатить: {esc(f'{due:.2f}')} ₽</b>\n"
            )
            await _present_fiat_checkout(
                cb,
                settings,
                conn,
                order_id=order_id,
                rub_due=due,
                intro_html=intro,
                usd_base=q.usd,
                buyer_user_id=cb.from_user.id,
            )
        else:
            usd_part = q.usd * (due / rub) if rub > 1e-6 else q.usd
            intro_mix_cr = (
                f"<b>Заказ #{esc(order_id)}</b>\n"
                f"С баланса: <b>{esc(f'{apply:.2f}')} ₽</b>\n"
                f"<b>К доплате криптой:</b> <b>{esc(f'{due:.2f}')} ₽</b>\n"
            )
            await _present_crypto_checkout(
                cb,
                settings,
                conn,
                order_id=order_id,
                due_rub=due,
                intro_html=intro_mix_cr,
                usd_for_fx=usd_part,
            )
        await cb.answer()
        await _notify_admins(bot, settings, conn, order_id)
        return

    try:
        await orders_repo.require_pending_order_cap(conn, cb.from_user.id, settings)
    except ValueError:
        await cb.answer(
            "Слишком много заказов в ожидании оплаты. Оплатите или отмените старые.",
            show_alert=True,
        )
        return

    order_id = await orders_repo.create_order(
        conn,
        user_id=cb.from_user.id,
        product_id=p.id,
        product_title=f"{p.emoji} {p.title}",
        payment_method=str(payment),
        usd_base=q.usd,
        rub_before=q.rub_list,
        rub_after=rub,
        referral_discount_rub=q.rub_referral_discount,
        wholesale_discount_rub=q.rub_wholesale_discount,
        referrer_id=referrer_id,
        commission_rub=0.0,
        user_note=str(recipient),
        status="pending_payment",
        product_kind=pk,
        stars_qty=sq,
        premium_months=pm,
        referral_discount_percent=ref_pct,
        usd_rub_rate_snapshot=rate_snap,
    )
    try:
        await analytics_repo.log_event(
            conn,
            user_id=cb.from_user.id,
            event_type="order_created",
            meta={"order_id": order_id, "product_id": p.id},
        )
    except Exception:
        pass

    await state.clear()

    if pk == "vpn":
        await _present_vpn_order_invoice(cb, settings, conn, products, order_id=order_id)
    elif payment == "crypto":
        intro_cr = f"<b>Заказ создан</b>\nID: <code>{esc(order_id)}</code>\n"
        await _present_crypto_checkout(
            cb,
            settings,
            conn,
            order_id=order_id,
            due_rub=rub,
            intro_html=intro_cr,
            usd_for_fx=q.usd,
        )
    else:
        intro = (
            f"<b>Заказ #{esc(order_id)}</b>\n"
            f"К оплате: <b>{esc(f'{rub:.2f}')} ₽</b>\n"
        )
        await _present_fiat_checkout(
            cb,
            settings,
            conn,
            order_id=order_id,
            rub_due=rub,
            intro_html=intro,
            usd_base=q.usd,
            buyer_user_id=cb.from_user.id,
        )
    await cb.answer()

    await _notify_admins(bot, settings, conn, order_id)


async def _notify_admins_bc_payment_claim(
    bot: Bot,
    settings: Settings,
    conn,
    *,
    order_id: int,
    from_user,
) -> None:
    """Пинг админам: покупатель нажал «Я оплатил» после универсальной bc-страницы (ручная сверка в ЛК Ckassa)."""
    order = await orders_repo.get_order(conn, order_id)
    if not order:
        return
    u = await users_repo.get_user(conn, int(order["user_id"]))
    uname = u["username"] if u else None
    user_line = f"@{uname}" if uname else f"id {order['user_id']}"
    amt = float(order["rub_after_discounts"])
    due = orders_repo.amount_due_external(order)
    try:
        bap = float(order["balance_applied_rub"] or 0)
    except (KeyError, TypeError):
        bap = 0.0
    extra = ""
    if bap > 0.01:
        extra = f"\nС баланса: <b>{esc(f'{bap:.2f}')} ₽</b>\nК доплате внешней оплатой: <b>{esc(f'{due:.2f}')} ₽</b>"
    claim_un = (from_user.username or "").strip()
    claim_line = f"@{claim_un}" if claim_un else f"id {from_user.id}"
    text = (
        "<b>Админам магазина</b> <i>(служебное)</i>\n"
        "<b>Покупатель: оплатил на универсальной странице Ckassa (bc)</b>\n"
        "Кнопка «Я оплатил» - только сигнал. Сверьте поступление в <b>личном кабинете Ckassa</b> по сумме и времени; "
        "в назначении ищите код как в боте. Если совпадает с заказом - нажмите <b>«Оплачен»</b>.\n\n"
        f"Заказ: <code>{esc(str(order_id))}</code> · в выписке: <code>{esc(f'ORDER{order_id}')}</code>\n"
        f"Покупатель (заказ): {esc(user_line)}\n"
        f"Нажал кнопку: {esc(claim_line)}\n"
        f"Товар: {esc(order['product_title'])}\n"
        f"Сумма заказа: <b>{esc(f'{amt:.2f}')} ₽</b>{extra}\n"
        f"Получатель Stars/Premium: <code>{esc(order['user_note'] or '')}</code>\n"
        f"Статус: <code>{esc(order['status'])}</code>"
    )
    from bot.keyboards.shop_kb import admin_order_kb
    from bot.services.admin_order_ff import ff_context_from_order_row, format_fulfillment_admin_block

    text = text + format_fulfillment_admin_block(order)
    text += await operator_bc_manual_checklist_html(conn, settings, order)
    oid = int(order["id"])
    buyer_id = int(order["user_id"])
    admin_ids = settings.parsed_admin_ids()
    for admin_id in admin_ids:
        if admin_id == buyer_id and len(admin_ids) > 1:
            continue
        try:
            await bot.send_message(
                admin_id,
                text,
                reply_markup=admin_order_kb(
                    oid,
                    settings=settings,
                    actor_id=admin_id,
                    order_ff=ff_context_from_order_row(order),
                ),
            )
        except Exception:
            continue


async def _notify_admins(bot: Bot, settings: Settings, conn, order_id: int) -> None:
    order = await orders_repo.get_order(conn, order_id)
    if not order:
        return
    u = await users_repo.get_user(conn, int(order["user_id"]))
    uname = u["username"] if u else None
    user_line = f"@{uname}" if uname else f"id {order['user_id']}"
    amt = float(order["rub_after_discounts"])
    due = orders_repo.amount_due_external(order)
    try:
        bap = float(order["balance_applied_rub"] or 0)
    except (KeyError, TypeError):
        bap = 0.0
    extra = ""
    if bap > 0.01:
        extra = f"\nС баланса: <b>{esc(f'{bap:.2f}')} ₽</b>\nК доплате: <b>{esc(f'{due:.2f}')} ₽</b>"
    text = (
        "<b>Админам магазина</b> <i>(служебное сообщение, не страница оплаты)</i>\n"
        "Кнопки «Оплачен / В работе / Выдан» - для операторов после проверки оплаты.\n\n"
        "<b>Новый заказ</b>\n\n"
        f"ID: <code>{esc(order['id'])}</code>\n"
        f"Пользователь: {esc(user_line)}\n"
        f"Товар: {esc(order['product_title'])}\n"
        f"Оплата: <code>{esc(order['payment_method'])}</code>\n"
        f"Сумма заказа: <b>{esc(f'{amt:.2f}')} ₽</b>{extra}\n"
        f"Получатель: <code>{esc(order['user_note'] or '')}</code>\n"
        f"Статус: <code>{esc(order['status'])}</code>"
    )
    from bot.keyboards.shop_kb import admin_order_kb
    from bot.services.admin_order_ff import ff_context_from_order_row, format_fulfillment_admin_block

    text = text + format_fulfillment_admin_block(order)
    pm = _order_row_str(order, "payment_method").lower()
    if pm in ("fiat", "mix_fiat"):
        text += await operator_bc_manual_checklist_html(conn, settings, order)
    oid = int(order["id"])
    buyer_id = int(order["user_id"])
    admin_ids = settings.parsed_admin_ids()
    for admin_id in admin_ids:
        if admin_id == buyer_id and len(admin_ids) > 1:
            # Покупатель сам в ADMIN_IDS: не дублировать ему панель оператора, если есть другие админы.
            continue
        try:
            await bot.send_message(
                admin_id,
                text,
                reply_markup=admin_order_kb(
                    oid,
                    settings=settings,
                    actor_id=admin_id,
                    order_ff=ff_context_from_order_row(order),
                ),
            )
        except Exception:
            continue
