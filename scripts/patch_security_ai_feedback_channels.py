# Apply on server: paths under /opt/aladdin-backend/security/api/routers/ai_assistant_router.py
from pathlib import Path

p = Path("/opt/aladdin-backend/security/api/routers/ai_assistant_router.py")
text = p.read_text(encoding="utf-8")

if "security router patched marker" in text:
    print("already patched")
    raise SystemExit(0)

if "import requests" not in text:
    text = text.replace(
        "import json\n",
        "import json\nimport smtplib\nfrom email.message import EmailMessage\nimport requests\n",
        1,
    )

helpers = """

def _send_feedback_email(payload: Dict[str, Any]) -> bool:
    \"\"\"SMTP уведомление (опционально). Env: ALADDIN_FEEDBACK_SMTP_*\"\"\"
    smtp_host = os.getenv("ALADDIN_FEEDBACK_SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("ALADDIN_FEEDBACK_SMTP_PORT", "587"))
    smtp_user = os.getenv("ALADDIN_FEEDBACK_SMTP_USER", "").strip()
    smtp_password = os.getenv("ALADDIN_FEEDBACK_SMTP_PASSWORD", "")
    from_email = os.getenv("ALADDIN_FEEDBACK_FROM_EMAIL", "").strip() or smtp_user
    to_email = os.getenv("ALADDIN_FEEDBACK_TO_EMAIL", "").strip()
    use_tls = os.getenv("ALADDIN_FEEDBACK_SMTP_TLS", "true").lower() in ("1", "true", "yes")

    if not smtp_host or not from_email or not to_email:
        logger.info("Feedback email skipped: SMTP env is not configured")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[ALADDIN][AI Feedback] rating={payload.get('rating')} source={payload.get('resolved_by', 'unknown')}"
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(
            "\\n".join(
                [
                    "ALADDIN AI Feedback",
                    f"time: {datetime.utcnow().isoformat()}Z",
                    f"rating: {payload.get('rating')}",
                    f"resolved_by: {payload.get('resolved_by')}",
                    f"faq_id: {payload.get('faq_id')}",
                    f"confidence: {payload.get('confidence')}",
                    f"session_id: {payload.get('session_id')}",
                    f"message_id: {payload.get('message_id')}",
                    "",
                    f"query_text: {payload.get('query_text')}",
                    "",
                    f"comment: {payload.get('comment')}",
                ]
            )
        )
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if use_tls:
                server.starttls()
            if smtp_user:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Feedback email sent successfully")
        return True
    except Exception as email_error:
        logger.error(f"Feedback email send failed: {email_error}")
        return False


def _send_feedback_telegram(payload: Dict[str, Any]) -> bool:
    \"\"\"Telegram. Env: ALADDIN_FEEDBACK_TELEGRAM_BOT_TOKEN, ALADDIN_FEEDBACK_TELEGRAM_CHAT_ID\"\"\"
    bot_token = os.getenv("ALADDIN_FEEDBACK_TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("ALADDIN_FEEDBACK_TELEGRAM_CHAT_ID", "").strip()
    proxy_url = os.getenv("ALADDIN_FEEDBACK_TELEGRAM_PROXY", "").strip()

    if not bot_token or not chat_id:
        logger.info("Feedback telegram skipped: bot token or chat id is not configured")
        return False

    body_text = "\\n".join(
        [
            "ALADDIN AI Feedback",
            f"time: {datetime.utcnow().isoformat()}Z",
            f"rating: {payload.get('rating')}",
            f"resolved_by: {payload.get('resolved_by')}",
            f"faq_id: {payload.get('faq_id')}",
            f"confidence: {payload.get('confidence')}",
            f"session_id: {payload.get('session_id')}",
            f"message_id: {payload.get('message_id')}",
            "",
            f"query_text: {payload.get('query_text')}",
            "",
            f"comment: {payload.get('comment')}",
        ]
    )
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
    try:
        resp = requests.post(
            url,
            json={"chat_id": chat_id, "text": body_text, "disable_web_page_preview": True},
            timeout=12,
            proxies=proxies,
        )
        if resp.status_code == 200:
            logger.info("Feedback telegram sent successfully")
            return True
        logger.error(f"Feedback telegram send failed: status={resp.status_code} body={resp.text[:400]}")
        return False
    except Exception as tg_error:
        logger.error(f"Feedback telegram send failed: {tg_error}")
        return False

"""

marker = "logger = logging.getLogger(__name__)"
text = text.replace(marker, marker + helpers + "\n# security router patched marker\n", 1)

old_fb_class = """class FeedbackRequest(BaseModel):
    \"\"\"Запрос на отправку обратной связи\"\"\"
    rating: int = Field(..., description=\"Оценка (1-5)\", ge=1, le=5)
    comment: Optional[str] = Field(None, description=\"Комментарий\", max_length=1000)
    message_id: Optional[str] = Field(None, description=\"ID сообщения\")"""

new_fb_class = """class FeedbackRequest(BaseModel):
    \"\"\"Запрос на отправку обратной связи\"\"\"
    rating: int = Field(..., description=\"Оценка (1-5)\", ge=1, le=5)
    comment: Optional[str] = Field(None, description=\"Комментарий\", max_length=1000)
    message_id: Optional[str] = Field(None, description=\"ID сообщения\")
    query_text: Optional[str] = Field(None, description=\"Текст запроса\")
    resolved_by: Optional[str] = Field(None, description=\"Источник отзыва\")
    faq_id: Optional[str] = None
    confidence: Optional[float] = None
    session_id: Optional[str] = None"""

if old_fb_class not in text:
    raise SystemExit("FeedbackRequest block not found")
text = text.replace(old_fb_class, new_fb_class, 1)

old_fn = """@router.post(\"/feedback\", response_model=FeedbackResponse)
async def ai_assistant_feedback(request: FeedbackRequest) -> FeedbackResponse:
    \"\"\"
    Обратная связь по работе AI помощника
    
    Args:
        request: Запрос с оценкой и комментарием
    
    Returns:
        Результат сохранения обратной связи
    \"\"\"
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                \"rating\": request.rating,
                \"comment\": request.comment,
                \"message_id\": request.message_id
            }
            success, result, message = sfm_adapter.execute_function(\"ai_assistant_feedback\", data)
            
            if success:
                return FeedbackResponse(
                    feedback_recorded=True,
                    average_rating=result.get(\"average_rating\", 4.8),
                    total_feedbacks=result.get(\"total_feedbacks\", 1250)
                )
            else:
                logger.warning(f\"SFM adapter error: {message}, using fallback\")
        
        # Fallback mock response
        return FeedbackResponse(
            feedback_recorded=True,
            average_rating=4.8,
            total_feedbacks=1250
        )
    except Exception as e:
        logger.error(f\"Ошибка при сохранении обратной связи: {e}\")
        return FeedbackResponse(feedback_recorded=False, average_rating=0.0, total_feedbacks=0)"""

new_fn = """@router.post(\"/feedback\", response_model=FeedbackResponse)
async def ai_assistant_feedback(request: FeedbackRequest) -> FeedbackResponse:
    \"\"\"
    Обратная связь по работе AI помощника
    
    Args:
        request: Запрос с оценкой и комментарием
    
    Returns:
        Результат сохранения обратной связи
    \"\"\"
    try:
        payload = {
            \"rating\": request.rating,
            \"comment\": request.comment,
            \"message_id\": request.message_id,
            \"query_text\": request.query_text,
            \"resolved_by\": request.resolved_by or \"unknown\",
            \"faq_id\": request.faq_id,
            \"confidence\": request.confidence,
            \"session_id\": request.session_id,
        }
        _send_feedback_email(payload)
        _send_feedback_telegram(payload)

        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = dict(payload)
            success, result, message = sfm_adapter.execute_function(\"ai_assistant_feedback\", data)

            if success:
                return FeedbackResponse(
                    feedback_recorded=True,
                    average_rating=result.get(\"average_rating\", 4.8),
                    total_feedbacks=result.get(\"total_feedbacks\", 1250)
                )
            logger.warning(f\"SFM adapter error: {message}, using fallback\")

        return FeedbackResponse(
            feedback_recorded=True,
            average_rating=4.8,
            total_feedbacks=1250
        )
    except Exception as e:
        logger.error(f\"Ошибка при сохранении обратной связи: {e}\")
        return FeedbackResponse(feedback_recorded=False, average_rating=0.0, total_feedbacks=0)"""

if old_fn not in text:
    raise SystemExit("ai_assistant_feedback block not found")
text = text.replace(old_fn, new_fn, 1)

p.write_text(text, encoding="utf-8")
print("security_router_patch_ok")
