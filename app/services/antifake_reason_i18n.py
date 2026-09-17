"""TI-UX-01 — human-readable antifake reasons (RU/EN). SSOT for client UI."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

# Machine reason code → user-facing copy
REASON_I18N: Dict[str, Dict[str, str]] = {
    # --- Threat intel / URL ---
    "feed_known_phishing_domain": {
        "ru": "Ссылка есть в базе угроз (известные мошеннические сайты).",
        "en": "This link matches a known scam site in our threat databases.",
    },
    "fuzzy_typosquat": {
        "ru": "Адрес похож на известный бренд, но это другой сайт (подделка).",
        "en": "The address looks like a known brand, but it is a different site (likely fake).",
    },
    "url_redirect_chain": {
        "ru": "Ссылка ведёт через переадресацию — проверьте конечный адрес.",
        "en": "The link redirects — check the final address.",
    },
    "url_redirect_host_mismatch": {
        "ru": "После переадресации открывается другой сайт.",
        "en": "After the redirect, a different site opens.",
    },
    "url_redirect_blocked_hop": {
        "ru": "Подозрительный шаг переадресации заблокирован.",
        "en": "A suspicious redirect hop was blocked.",
    },
    "brand_lookalike_redirect": {
        "ru": "Переадресация ведёт на сайт, похожий на бренд банка или сервиса.",
        "en": "The redirect lands on a site that looks like a bank or service brand.",
    },
    "fuzzy_brand_in_host": {
        "ru": "В адресе есть имя банка или сервиса, но домен чужой.",
        "en": "The address contains a bank/service name, but the domain is not official.",
    },
    "fuzzy_suspicious_tld": {
        "ru": "Подозрительная зона домена (.ru.com, .xyz и т.п.) рядом с брендом.",
        "en": "Suspicious domain zone (.ru.com, .xyz, etc.) next to a brand name.",
    },
    "fuzzy_phish_label": {
        "ru": "В ссылке слова вроде login/secure/verify — типичный фишинг.",
        "en": "The link uses words like login/secure/verify — typical phishing.",
    },
    "phishing_agent_hit": {
        "ru": "Проверка ссылки нашла признаки фишинга (подозрительный адрес или шаблон).",
        "en": "Link check found phishing signs (suspicious address or pattern).",
    },
    "fuzzy_punycode": {
        "ru": "В адресе есть необычные символы (возможна подмена букв).",
        "en": "The address uses unusual characters (possible letter lookalikes).",
    },
    "url_typosquat_tld": {
        "ru": "Подозрительная зона домена (.ru.com).",
        "en": "Suspicious domain zone (.ru.com).",
    },
    "rkn_blocked_signal": {
        "ru": "Домен встречается в реестре заблокированных сайтов — это дополнительный сигнал, не приговор.",
        "en": "Domain appears in a block registry — an extra signal, not a final verdict.",
    },
    "url_credential_trap": {
        "ru": "В ссылке есть признаки сбора паролей или карт.",
        "en": "The link shows signs of a password or card harvesting trap.",
    },
    "url_phishing_path": {
        "ru": "Путь в ссылке типичен для фишинга (login, verify, secure).",
        "en": "The URL path looks like common phishing (login, verify, secure).",
    },
    "url_ip_address": {
        "ru": "Ссылка ведёт на IP-адрес вместо обычного сайта.",
        "en": "The link points to an IP address instead of a normal website.",
    },
    "url_shortener": {
        "ru": "Короткая ссылка скрывает конечный адрес — откройте с осторожностью.",
        "en": "A short link hides the final address — open with caution.",
    },
    "insecure_http": {
        "ru": "Соединение без защиты HTTPS.",
        "en": "Connection without HTTPS protection.",
    },
    "url_looks_neutral": {
        "ru": "Явных признаков фишинга в ссылке не найдено.",
        "en": "No obvious phishing signs found in the link.",
    },
    "blocked_url": {
        "ru": "Ссылка заблокирована правилами безопасности.",
        "en": "The link was blocked by security rules.",
    },
    "empty_url": {
        "ru": "Ссылка пустая — нечего проверять.",
        "en": "The link is empty — nothing to check.",
    },
    "sfm_verdict": {
        "ru": "Дополнительная проверка содержимого.",
        "en": "Extra content check.",
    },
    "sfm_agent": {
        "ru": "Дополнительная проверка содержимого.",
        "en": "Extra content check.",
    },
    "heuristic_fallback": {
        "ru": "Сработали простые правила безопасности.",
        "en": "Simple safety rules were applied.",
    },
    # --- Text heuristics ---
    "empty_text": {
        "ru": "Текст пустой — пришлите сообщение или ссылку.",
        "en": "Text is empty — send a message or a link.",
    },
    "text_too_short": {
        "ru": "Слишком мало текста для уверенного ответа.",
        "en": "Too little text for a confident answer.",
    },
    "too_short": {
        "ru": "Слишком мало текста для уверенного ответа.",
        "en": "Too little text for a confident answer.",
    },
    "multiple_links": {
        "ru": "В сообщении сразу несколько ссылок — так часто делают мошенники.",
        "en": "Several links in one message — a common scam pattern.",
    },
    "email_header_suspicious": {
        "ru": "Подозрительные заголовки письма.",
        "en": "Suspicious email headers.",
    },
    "sensationalism": {
        "ru": "Сенсационные формулировки («шок», «скрывают правду»).",
        "en": "Sensational wording (“shock”, “they hide the truth”).",
    },
    "urgency": {
        "ru": "Давление срочностью — типичный приём мошенников.",
        "en": "Urgency pressure — a common scam tactic.",
    },
    "no_source": {
        "ru": "Нет понятного источника информации.",
        "en": "No clear source of information.",
    },
    "scam": {
        "ru": "Признаки просьбы перевести деньги или «разблокировать счёт».",
        "en": "Signs of a request to send money or “unlock an account”.",
    },
    # afhub-p1-01 intent tags
    "intent_money_transfer": {
        "ru": "Просьба перевести деньги.",
        "en": "Request to transfer money.",
    },
    "intent_card": {
        "ru": "Просят данные карты или перевод на карту.",
        "en": "Asks for card details or a card transfer.",
    },
    "intent_otp": {
        "ru": "Просят код из SMS / одноразовый код.",
        "en": "Asks for an SMS / one-time code.",
    },
    "intent_sbp": {
        "ru": "Давление на перевод через СБП.",
        "en": "Pressure to pay via instant transfer (SBP).",
    },
    "intent_authority": {
        "ru": "Притворяются банком или госорганом.",
        "en": "Impersonates a bank or government agency.",
    },
    "intent_prize": {
        "ru": "Приманка «приз / выигрыш» с оплатой комиссии.",
        "en": "Prize / win lure that asks for a fee.",
    },
    "no_suspicious_patterns": {
        "ru": "Подозрительных шаблонов в тексте не найдено.",
        "en": "No suspicious patterns found in the text.",
    },
    "no_signals": {
        "ru": "Недостаточно сигналов для уверенного вывода.",
        "en": "Not enough signals for a confident conclusion.",
    },
    "insufficient_data": {
        "ru": "Недостаточно данных для проверки.",
        "en": "Not enough data for a check.",
    },
    "local_ml_analysis": {
        "ru": "Сервер дополнительно прослушал запись.",
        "en": "The server also listened to the recording.",
    },
    # --- Calls / numbers ---
    "scam_directory_hit": {
        "ru": "Номер есть в нашей базе мошеннических звонков.",
        "en": "This number is in our scam-call database.",
    },
    "ktozvonil_reputation": {
        "ru": "Номер имеет плохую репутацию в открытых базах жалоб.",
        "en": "This number has a poor reputation in open complaint databases.",
    },
    "display_number_mismatch": {
        "ru": "Имя на экране не совпадает с реальным номером — возможна подмена.",
        "en": "The on-screen name does not match the real number — possible spoofing.",
    },
    "authority_label_no_caller_id": {
        "ru": "На экране «банк/госорган», но номер скрыт — будьте осторожны.",
        "en": "Screen says “bank/government”, but the number is hidden — be careful.",
    },
    "authority_label_personal_number": {
        "ru": "Подпись как у банка/службы, но номер похож на обычный мобильный.",
        "en": "Label looks like a bank/service, but the number looks like a personal mobile.",
    },
    "authority_label_short_code": {
        "ru": "Короткий номер (например 900) с именем банка на экране — проверьте, не подделка ли это.",
        "en": "A short code (e.g. 900) with a bank name on screen — verify it is not spoofed.",
    },
    "authority_name_non_service_number": {
        "ru": "Название организации не совпадает с типом номера.",
        "en": "Organization name does not match the number type.",
    },
    # --- Media / deepfake ---
    "empty_file": {
        "ru": "Файл пустой или не удалось прочитать.",
        "en": "The file is empty or could not be read.",
    },
    "video_too_small": {
        "ru": "Видео слишком короткое или маленькое для уверенной проверки.",
        "en": "Video is too short or small for a confident check.",
    },
    "probe_blocked_likely_fake": {
        "ru": "Сильные признаки синтеза или монтажа в записи.",
        "en": "Strong signs of synthesis or editing in the recording.",
    },
    "video_confidence_capped_no_nn": {
        "ru": "Это предварительная оценка — полной «военной» нейросети deepfake у нас нет.",
        "en": "This is a preliminary estimate — we do not run a full deepfake neural net.",
    },
    "video_confidence_capped": {
        "ru": "Оценка осторожная: даже при хорошем результате мы не обещаем 100%.",
        "en": "Cautious estimate: even a good result is never a 100% guarantee.",
    },
    "video_onnx_model_missing": {
        "ru": "Проверка упрощена — полная модель на сервере временно недоступна.",
        "en": "Simplified check — the full on-server model is temporarily unavailable.",
    },
    "video_onnx_fallback_heuristic": {
        "ru": "Проверили базовые признаки ролика без глубокой нейросети.",
        "en": "Checked basic clip signals without a deep neural net.",
    },
    "video_onnx_active": {
        "ru": "Сервер дополнительно просмотрел кадры на признаки подмены лица.",
        "en": "The server also scanned frames for face-swap signs.",
    },
    "video_no_face_swap_signs": {
        "ru": "Явных признаков подмены лица не нашли. Это не гарантия 100% — смотрите, кто прислал ролик.",
        "en": "No clear face-swap signs found. Not a 100% guarantee — check who sent the clip.",
    },
    "video_onnx_timeout": {
        "ru": "Видео слишком долго разбиралось — попробуйте более короткий ролик.",
        "en": "Video analysis took too long — try a shorter clip.",
    },
    "video_onnx_busy": {
        "ru": "Сейчас много проверок видео. Подождите минуту и загрузите снова.",
        "en": "Video checks are busy. Wait a minute and upload again.",
    },
    "video_frames_low_texture": {
        "ru": "Картинка слишком «мыльная» — так бывает при сжатии в мессенджере или у синтетики.",
        "en": "The picture looks too soft — common with messenger compression or synthesis.",
    },
    "video_temporal_jump": {
        "ru": "Между кадрами резкие скачки — возможны склейка или монтаж.",
        "en": "Sharp jumps between frames — possible cuts or editing.",
    },
    "jpeg_as_video_name": {
        "ru": "Вам прислали картинку под видом видео — это подозрительно.",
        "en": "An image was sent as if it were a video — that is suspicious.",
    },
    "claimed_authority_source": {
        "ru": "В ролике упоминают «официальную» организацию — лучше перепроверить отдельно.",
        "en": "The clip mentions an “official” organization — verify separately.",
    },
    "video_metadata_neutral": {
        "ru": "По файлу нет явных тревожных сигналов.",
        "en": "No obvious red flags in the file itself.",
    },
    "extension_container_mismatch": {
        "ru": "Тип файла не совпадает с содержимым — лучше не открывать с незнакомых.",
        "en": "File type does not match contents — avoid opening from strangers.",
    },
    "moov_after_mdat": {
        "ru": "Файл перекодировали (часто так делают в WhatsApp/Telegram).",
        "en": "The file was re-encoded (common in WhatsApp/Telegram).",
    },
    "jpeg_not_video_container": {
        "ru": "Это фото, а не видео.",
        "en": "This is a photo, not a video.",
    },
    "riff_container": {
        "ru": "Старый формат записи — проверьте, от кого файл.",
        "en": "Legacy recording format — check who sent the file.",
    },
    "unknown_video_container": {
        "ru": "Необычный формат видео — проверка ограничена.",
        "en": "Unusual video format — check is limited.",
    },
    "ftyp_present": {
        "ru": "Файл выглядит как обычное видео.",
        "en": "The file looks like a normal video.",
    },
    "ftyp_isom": {
        "ru": "Файл выглядит как обычное видео.",
        "en": "The file looks like a normal video.",
    },
    "ftyp_mp41": {
        "ru": "Файл выглядит как обычное видео.",
        "en": "The file looks like a normal video.",
    },
    "ftyp_qt": {
        "ru": "Файл выглядит как обычное видео.",
        "en": "The file looks like a normal video.",
    },
    "ftyp_mp42": {
        "ru": "Файл выглядит как обычное видео.",
        "en": "The file looks like a normal video.",
    },
    "ftyp_container": {
        "ru": "Файл выглядит как обычное видео.",
        "en": "The file looks like a normal video.",
    },
    "video_bytes_received": {
        "ru": "Ролик принят на проверку.",
        "en": "Clip accepted for checking.",
    },
    "video_codec_av1_unsupported": {
        "ru": "Этот формат (AV1) сервер сейчас не читает. Откройте ролик на телефоне/Mac → «Поделиться» / экспортируйте как MP4 (H.264) и загрузите снова.",
        "en": "This format (AV1) cannot be read on the server yet. Open the clip → Share/Export as MP4 (H.264) and upload again.",
    },
    "video_decode_failed": {
        "ru": "Не удалось разобрать видео. Сохраните как обычный MP4 (H.264) и попробуйте снова.",
        "en": "Could not decode the video. Save as a normal MP4 (H.264) and try again.",
    },
    "video_no_frames": {
        "ru": "Из файла не удалось взять кадры. Часто помогает пересохранение в MP4 (H.264).",
        "en": "Could not read frames from the file. Re-saving as MP4 (H.264) usually helps.",
    },
    "face_quality_blurry": {
        "ru": "Кадры слишком размытые — нельзя уверенно сказать про подмену лица.",
        "en": "Frames are too blurry — we cannot confidently judge face-swap.",
    },
    "face_not_detected": {
        "ru": "Лицо на кадрах не видно — вердикт «подмена» не ставим.",
        "en": "No face visible in the frames — we will not claim a face-swap.",
    },
    "face_quality_insufficient": {
        "ru": "Качество кадра недостаточное для жёсткого вердикта.",
        "en": "Frame quality is too low for a hard verdict.",
    },
    "face_quality_no_frames": {
        "ru": "Нет кадров для проверки лица.",
        "en": "No frames available for a face check.",
    },
    "face_quality_gate_blocked": {
        "ru": "Жёсткий вердикт «фейк» не ставим: лицо не видно или картинка мутная.",
        "en": "Hard «fake» verdict withheld: face not visible or picture is muddy.",
    },
    "deepfake_signal": {
        "ru": "Голос или лицо могут быть синтезированы — будьте осторожны.",
        "en": "Voice or face may be synthetic — be careful.",
    },
    "synthetic_voice": {
        "ru": "Голос звучит неестественно — похоже на компьютерную речь.",
        "en": "The voice sounds unnatural — like computer speech.",
    },
    "stt_unavailable": {
        "ru": "Не удалось распознать речь в записи. Проверьте текст сообщения отдельно или загрузите более чёткий файл.",
        "en": "Could not transcribe speech from this recording. Check the text separately or upload a clearer file.",
    },
    "stt_transcript_scam_check": {
        "ru": "Распознанный текст проверен как SMS/скам-сообщение.",
        "en": "Recognized speech was checked like an SMS/scam message.",
    },
    "stt_transcript_too_short": {
        "ru": "Распознанный текст слишком короткий для уверенного вывода.",
        "en": "Recognized speech is too short for a confident result.",
    },
    "clipping_artifacts": {
        "ru": "В записи сильные искажения громкости (клиппинг) — частый признак синтетики.",
        "en": "Loudness clipping in the recording — often seen with synthetic audio.",
    },
    "narrowband_synthetic_profile": {
        "ru": "Спектр узкий, как у телефонной/синтетической речи.",
        "en": "Narrow spectrum profile typical of phone/synthetic speech.",
    },
    "overly_steady_energy": {
        "ru": "Громкость слишком ровная — у живой речи обычно больше перепадов.",
        "en": "Energy is too steady — natural speech usually varies more.",
    },
    "natural_voice": {
        "ru": "Голос звучит как обычный человеческий.",
        "en": "The voice sounds like a normal human.",
    },
    "document_agent_unavailable": {
        "ru": "Проверка документа сейчас упрощена — повторите позже.",
        "en": "Document check is simplified right now — try again later.",
    },
    "pdf_scam_keywords": {
        "ru": "В тексте есть «штраф / оплатите / задолженность» — так часто пишут мошенники.",
        "en": "The text has words like “fine / pay now / debt” — a common scam pattern.",
    },
    "pdf_container": {
        "ru": "Это PDF-файл.",
        "en": "This is a PDF file.",
    },
    "pdf_encrypted": {
        "ru": "PDF защищён паролем — содержимое проверить нельзя.",
        "en": "PDF is password-protected — contents cannot be checked.",
    },
    "pdf_too_small": {
        "ru": "PDF слишком маленький — мало данных для проверки.",
        "en": "PDF is too small — not enough data to check.",
    },
    "provenance_tampered": {
        "ru": "У документа странные «служебные» данные — возможна подделка.",
        "en": "The document has odd internal data — possible forgery.",
    },
    "provenance_missing": {
        "ru": "Нет понятных сведений, откуда документ.",
        "en": "No clear info about where the document came from.",
    },
    "provenance_found": {
        "ru": "Есть сведения о происхождении документа.",
        "en": "There is info about the document’s origin.",
    },
    "jpeg_container": {
        "ru": "Это фото (JPEG).",
        "en": "This is a photo (JPEG).",
    },
    "png_container": {
        "ru": "Это изображение (PNG).",
        "en": "This is an image (PNG).",
    },
    "image_too_small": {
        "ru": "Фото слишком маленькое — проверка ограничена.",
        "en": "Photo is too small — check is limited.",
    },
    "unknown_document_container": {
        "ru": "Формат файла не знаком — проверка ограничена.",
        "en": "Unknown file format — check is limited.",
    },
    "document_cv_ok": {
        "ru": "На фото документа явных следов подделки не видно.",
        "en": "No obvious forgery traces on the document photo.",
    },
    "document_cv_weak": {
        "ru": "По фото документа вывод слабый — лучше перепроверить у взрослых.",
        "en": "Weak result from the document photo — better ask an adult.",
    },
    "document_local_ml": {
        "ru": "Документ просмотрен на сервере.",
        "en": "Document was reviewed on the server.",
    },
    "document_heuristic": {
        "ru": "Проверили документ по простым правилам.",
        "en": "Checked the document with simple rules.",
    },
    # --- Ensemble / rules / SFM tagged tails ---
    "urgency_manipulation": {
        "ru": "Давление срочностью — типичный приём мошенников.",
        "en": "Urgency pressure — a common scam tactic.",
    },
    "financial_scam": {
        "ru": "Признаки финансового мошенничества (просьба перевести деньги).",
        "en": "Signs of a financial scam (request to send money).",
    },
    "has_urls": {
        "ru": "В сообщении есть ссылка — проверьте её отдельно.",
        "en": "The message contains a link — check it separately.",
    },
    "audio_agent_unavailable": {
        "ru": "Полный разбор голоса сейчас недоступен — смотрим простые признаки.",
        "en": "Full voice analysis is unavailable — using simple signals.",
    },
    "video_agent_unavailable": {
        "ru": "Полный разбор видео сейчас недоступен — смотрим простые признаки.",
        "en": "Full video analysis is unavailable — using simple signals.",
    },
    "call_agent_unavailable": {
        "ru": "Полный разбор звонка ограничен — смотрим номер и простые признаки.",
        "en": "Full call analysis is limited — checking the number and simple signals.",
    },
    "high_spectral_flatness": {
        "ru": "Голос звучит слишком «ровно» — так бывает у компьютерной речи.",
        "en": "The voice sounds too flat — common with computer speech.",
    },
    "overly_steady_energy": {
        "ru": "Громкость почти не меняется — похоже на синтез.",
        "en": "Loudness barely changes — possible synthesis.",
    },
    "strong_periodic_pitch": {
        "ru": "Тон голоса слишком ровный — возможна подделка.",
        "en": "Pitch is too even — possible fake voice.",
    },
    "unnaturally_low_zcr": {
        "ru": "Запись звучит неестественно гладко.",
        "en": "The recording sounds unnaturally smooth.",
    },
    "noisy_or_artifacts": {
        "ru": "В записи много шума — качество плохое, вывод осторожный.",
        "en": "Lots of noise in the recording — cautious result.",
    },
    "natural_voice_features": {
        "ru": "Голос звучит естественно.",
        "en": "The voice sounds natural.",
    },
    "audio_too_short": {
        "ru": "Запись слишком короткая — мало данных.",
        "en": "Recording is too short — not enough data.",
    },
    "audio_decode_failed": {
        "ru": "Не удалось прослушать файл — попробуйте WAV или MP3.",
        "en": "Could not play the file — try WAV or MP3.",
    },
    "mp3_container_undecoded": {
        "ru": "Файл принят, но разбор ограничен — лучше загрузить WAV.",
        "en": "File accepted, but analysis is limited — WAV works better.",
    },
    "wav_container": {
        "ru": "Обычная аудиозапись.",
        "en": "A normal audio recording.",
    },
    "numpy_unavailable": {
        "ru": "Проверка голоса упрощена.",
        "en": "Voice check is simplified.",
    },
    "cv2_unavailable": {
        "ru": "Часть проверки недоступна — результат упрощён.",
        "en": "Part of the check is unavailable — simplified result.",
    },
}


# Machine codes that add noise for families — skip in reasons_human
_REASON_HIDE_FROM_UI = frozenset(
    {
        "video_bytes_received",
        "video_onnx_scored",
        "video_onnx_active",
        "video_onnx_fallback_heuristic",
        "ftyp_isom",
        "ftyp_mp41",
        "ftyp_mp42",
        "ftyp_qt",
        "ftyp_present",
        "ftyp_container",
        "cv2_no_frame",
        "frame_detail_ok",
        "pdf_container",
        "jpeg_container",
        "png_container",
        "wav_container",
        "local_ml_analysis",
        "document_local_ml",
        "document_heuristic",
        "sfm_agent",
        "sfm_verdict",
        "heuristic_fallback",
        "numpy_unavailable",
    }
)


_GENERIC = {
    "ru": "Ещё один сигнал при проверке — смотрите основной вывод выше.",
    "en": "Another check signal — see the main conclusion above.",
}


def normalize_ui_lang(raw: Optional[str]) -> str:
    text = (raw or "").strip().lower()
    if text.startswith("en"):
        return "en"
    return "ru"


def resolve_ui_lang_from_headers(
    *,
    accept_language: Optional[str] = None,
    x_aladdin_lang: Optional[str] = None,
    query_lang: Optional[str] = None,
) -> str:
    """Pick ru/en from query, X-Aladdin-Lang, or Accept-Language (q-weighted)."""
    for candidate in (query_lang, x_aladdin_lang):
        if candidate:
            c = candidate.strip().lower()
            if c.startswith("en"):
                return "en"
            if c.startswith("ru"):
                return "ru"

    al = accept_language or ""
    best_lang = "ru"
    best_q = -1.0
    for part in al.split(","):
        part = part.strip()
        if not part:
            continue
        if ";q=" in part:
            tag, _, qstr = part.partition(";q=")
            try:
                qv = float(qstr.strip())
            except ValueError:
                qv = 0.0
        else:
            tag, qv = part, 1.0
        tag = tag.strip().lower()
        lang = "en" if tag.startswith("en") else ("ru" if tag.startswith("ru") else None)
        if lang and qv > best_q:
            best_lang, best_q = lang, qv
    return best_lang if best_q >= 0 else "ru"


def _lookup_entry(code: str, lang_key: str) -> Optional[str]:
    entry = REASON_I18N.get(code)
    if entry:
        return entry.get(lang_key) or entry.get("ru")
    if ":" in code:
        tail = code.split(":", 1)[1].strip()
        entry = REASON_I18N.get(tail)
        if entry:
            return entry.get(lang_key) or entry.get("ru")
        underscored = code.replace(":", "_")
        entry = REASON_I18N.get(underscored)
        if entry:
            return entry.get(lang_key) or entry.get("ru")
    return None


def _looks_already_human(code: str) -> bool:
    if " " in code:
        return True
    lower = code.lower()
    return any("а" <= ch <= "я" or "ё" == ch for ch in lower)


def humanize_reasons(reasons: List[str], *, lang: str = "ru") -> List[str]:
    lang_key = normalize_ui_lang(lang)
    out: List[str] = []
    seen = set()
    for code in reasons or []:
        raw = str(code or "").strip()
        if not raw:
            continue
        tail = raw.split(":", 1)[-1].strip() if ":" in raw else raw
        if tail in _REASON_HIDE_FROM_UI or raw in _REASON_HIDE_FROM_UI:
            continue
        if tail.startswith("frames_sampled_") or tail.startswith("video_onnx_frames_"):
            continue
        if tail.startswith("faces_detected_"):
            continue
        if tail.startswith("frame_decoded_") or tail.startswith("transcript_len=") or tail.startswith("doc_level_"):
            continue
        text = _lookup_entry(raw, lang_key)
        if not text:
            if _looks_already_human(raw):
                text = raw
            else:
                # Prefer skip unknown machine codes over "Дополнительный признак…"
                continue
        if text in seen:
            continue
        seen.add(text)
        out.append(text)
        if len(out) >= 5:
            break
    return out


def _infer_check_kind(payload: Dict[str, Any]) -> str:
    blob = " ".join(
        [
            str(payload.get("source") or ""),
            str(payload.get("agent") or ""),
            str(payload.get("job_type") or ""),
            " ".join(str(r) for r in (payload.get("reasons") or [])),
        ]
    ).lower()
    if any(k in blob for k in ("video", "onnx", "ftyp", "face_swap", "frames_sampled")):
        return "video"
    if any(k in blob for k in ("audio", "voice", "synthetic_voice", "natural_voice", "spectral", "wav", "mp3")):
        return "audio"
    if any(k in blob for k in ("document", "pdf", "provenance", "jpeg_container", "png_container", "doc_level")):
        return "document"
    if any(k in blob for k in ("call", "caller", "scam_directory", "ktozvonil", "display_number")):
        return "call"
    if any(k in blob for k in ("url", "phishing", "feed_known", "fuzzy_", "typosquat", "shortener")):
        return "url"
    if any(k in blob for k in ("text", "sms", "urgency", "scam", "sensational", "no_suspicious")):
        return "text"
    return "generic"


def build_summary_human(payload: Dict[str, Any], *, lang: str = "ru") -> str:
    """One plain-language paragraph for the result card (all check kinds)."""
    lang_key = normalize_ui_lang(lang)
    verdict = str(payload.get("verdict") or "uncertain")
    kind = _infer_check_kind(payload)
    reasons = [str(r) for r in (payload.get("reasons") or [])]
    joined = " ".join(reasons)

    if "video_codec_av1_unsupported" in joined or (
        kind == "video" and "video_codec_av1" in joined
    ):
        return (
            "Сервер не смог прочитать этот ролик (часто так бывает с AV1 из Telegram). "
            "Откройте файл → экспортируйте как MP4 (H.264) → загрузите снова. "
            "Это не поломка Antifake — нужен другой формат."
            if lang_key == "ru"
            else "The server could not read this clip (common with AV1 from Telegram). "
            "Open the file → export as MP4 (H.264) → upload again. "
            "Antifake is fine — the format needs changing."
        )

    if kind == "video" and (
        "video_decode_failed" in joined or "video_no_frames" in joined
    ):
        return (
            "Не удалось разобрать это видео. Сохраните как обычный MP4 (H.264) "
            "и загрузите снова — так бывает с редкими кодеками из мессенджеров. "
            "Мы не ставим «всё ок», пока файл не читается."
            if lang_key == "ru"
            else "Could not decode this video. Save as a normal MP4 (H.264) and upload again — "
            "common with rare messenger codecs. We will not show «all clear» until the file is readable."
        )

    if "face_quality_gate_blocked" in joined or (
        kind == "video"
        and verdict == "uncertain"
        and ("face_quality_blurry" in joined or "face_not_detected" in joined)
    ):
        return (
            "Кадры мутные или лицо не видно — жёсткий вердикт «подмена» не ставим. "
            "Попробуйте более чёткий ролик или уточните у взрослых, кто прислал файл."
            if lang_key == "ru"
            else "Frames are muddy or no face is visible — we will not claim a hard face-swap. "
            "Try a clearer clip or ask an adult who sent the file."
        )

    if "video_no_face_swap_signs" in joined or (
        kind == "video" and verdict == "likely_real" and "video_onnx_scored" in joined
    ):
        return (
            "Похоже на обычное видео: явных признаков подмены лица не нашли. "
            "Это помощник, а не доказательство — если ролик прислал незнакомец, уточните у взрослых."
            if lang_key == "ru"
            else "Looks like a normal video: no clear face-swap signs. "
            "This is a helper, not proof — if a stranger sent it, ask an adult."
        )

    # kind × verdict → family-friendly summary
    table: Dict[str, Dict[str, Dict[str, str]]] = {
        "text": {
            "likely_fake": {
                "ru": "В тексте есть признаки обмана (срочность, деньги, подозрительные формулировки). Не переводите деньги и не сообщайте коды.",
                "en": "The text shows scam signs (urgency, money, suspicious wording). Do not send money or share codes.",
            },
            "likely_real": {
                "ru": "Явных признаков мошенничества в тексте не видно. Всё равно не переводите деньги по просьбе из сообщения.",
                "en": "No clear scam signs in the text. Still do not send money because a message asks you to.",
            },
            "uncertain": {
                "ru": "По тексту однозначно сказать нельзя. Лучше уточнить у взрослых, прежде чем что-то делать.",
                "en": "We cannot judge this text for sure. Ask an adult before you act.",
            },
            "insufficient_data": {
                "ru": "Слишком мало текста. Вставьте полное сообщение или ссылку.",
                "en": "Too little text. Paste the full message or link.",
            },
        },
        "url": {
            "likely_fake": {
                "ru": "Ссылка похожа на опасную или поддельную. Не открывайте её и не вводите пароли.",
                "en": "This link looks dangerous or fake. Do not open it or enter passwords.",
            },
            "likely_real": {
                "ru": "Явных признаков фишинга в ссылке не нашли. Если сомневаетесь — откройте сайт банка вручную, не по этой ссылке.",
                "en": "No clear phishing signs in the link. If unsure — open the bank site yourself, not via this link.",
            },
            "uncertain": {
                "ru": "По ссылке вывод неясный. Не спешите открывать — спросите взрослых.",
                "en": "The link is unclear. Do not rush to open it — ask an adult.",
            },
            "insufficient_data": {
                "ru": "Ссылка пустая или слишком короткая для проверки.",
                "en": "The link is empty or too short to check.",
            },
        },
        "audio": {
            "likely_fake": {
                "ru": "Голос звучит подозрительно (похоже на синтез). Не выполняйте просьбы о деньгах из этой записи.",
                "en": "The voice sounds suspicious (possibly synthetic). Do not follow money requests from this recording.",
            },
            "likely_real": {
                "ru": "Голос звучит обычно. Это не гарантия 100% — если просят деньги, уточните у взрослых.",
                "en": "The voice sounds ordinary. Not a 100% guarantee — if they ask for money, ask an adult.",
            },
            "uncertain": {
                "ru": "По голосу однозначно сказать нельзя. Не торопитесь и покажите запись взрослым.",
                "en": "We cannot judge this voice for sure. Do not rush — show the recording to an adult.",
            },
            "insufficient_data": {
                "ru": "Запись слишком короткая или плохого качества. Загрузите более длинный фрагмент.",
                "en": "Recording is too short or poor quality. Upload a longer clip.",
            },
        },
        "video": {
            "likely_fake": {
                "ru": "Есть признаки подделки видео. Не переводите деньги и не открывайте ссылки из ролика.",
                "en": "There are signs the video may be fake. Do not send money or open links from the clip.",
            },
            "likely_real": {
                "ru": "Похоже на обычное видео, без явных признаков подмены. Всё равно будьте внимательны к просьбам о деньгах.",
                "en": "Looks like an ordinary video without clear face-swap signs. Still be careful with money requests.",
            },
            "uncertain": {
                "ru": "По видео однозначно сказать нельзя. Не спешите — уточните у взрослых, кто прислал ролик.",
                "en": "We cannot judge this video for sure. Do not rush — ask an adult who sent the clip.",
            },
            "insufficient_data": {
                "ru": "Мало данных по видео или файл не прочитался. Сохраните как MP4 (H.264) и загрузите снова.",
                "en": "Not enough video data or the file could not be read. Save as MP4 (H.264) and upload again.",
            },
        },
        "document": {
            "likely_fake": {
                "ru": "Документ выглядит подозрительно (типичные слова мошенников или следы подделки). Не оплачивайте по нему.",
                "en": "The document looks suspicious (scam wording or forgery signs). Do not pay from it.",
            },
            "likely_real": {
                "ru": "Явных признаков подделки документа не видно. Важные оплаты лучше сверять с официальным источником.",
                "en": "No clear forgery signs. For important payments, still verify with an official source.",
            },
            "uncertain": {
                "ru": "По документу вывод неясный. Покажите его взрослым, прежде чем что-то оплачивать.",
                "en": "The document is unclear. Show it to an adult before paying anything.",
            },
            "insufficient_data": {
                "ru": "Файл слишком маленький или формат не подходит. Загрузите PDF или чёткое фото.",
                "en": "File is too small or the format is wrong. Upload a PDF or a clear photo.",
            },
        },
        "call": {
            "likely_fake": {
                "ru": "Звонок или номер выглядят как мошенничество. Положите трубку и не называйте коды из SMS.",
                "en": "The call or number looks like a scam. Hang up and do not share SMS codes.",
            },
            "likely_real": {
                "ru": "Явных признаков мошеннического звонка не нашли. Банк сами перезвоните по номеру с официального сайта.",
                "en": "No clear scam-call signs. If needed, call the bank using the number from the official site.",
            },
            "uncertain": {
                "ru": "По звонку однозначно сказать нельзя. Не сообщайте пароли и коды — уточните у взрослых.",
                "en": "We cannot judge this call for sure. Do not share passwords or codes — ask an adult.",
            },
            "insufficient_data": {
                "ru": "Мало данных о звонке. Добавьте запись разговора или номер.",
                "en": "Not enough call data. Add a recording or the phone number.",
            },
        },
        "generic": {
            "likely_fake": {
                "ru": "Есть признаки обмана. Не переводите деньги и не сообщайте пароли.",
                "en": "There are signs of a scam. Do not send money or share passwords.",
            },
            "likely_real": {
                "ru": "Явных признаков подделки не видно. Оставайтесь внимательны к просьбам о деньгах.",
                "en": "No clear fake signs. Stay careful with money requests.",
            },
            "uncertain": {
                "ru": "Однозначно сказать нельзя. Уточните у взрослых, прежде чем действовать.",
                "en": "We cannot say for sure. Ask an adult before you act.",
            },
            "insufficient_data": {
                "ru": "Мало данных для вывода. Добавьте больше текста или другой файл.",
                "en": "Not enough data. Add more text or another file.",
            },
        },
    }
    kind_table = table.get(kind) or table["generic"]
    entry = kind_table.get(verdict) or kind_table["uncertain"]
    return entry[lang_key]


def attach_human_reasons(payload: Dict[str, Any], *, lang: str = "ru") -> Dict[str, Any]:
    """Return a shallow copy with reasons_human refreshed from machine codes."""
    result = dict(payload)
    result["reasons_human"] = humanize_reasons(list(result.get("reasons") or []), lang=lang)
    result["summary_human"] = build_summary_human(result, lang=lang)
    return result
