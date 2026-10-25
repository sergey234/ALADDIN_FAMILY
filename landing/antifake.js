(function () {
  'use strict';

  const API = 'https://aladdin-ai.ru';
  const MAX_BYTES = 25 * 1024 * 1024;
  const POLL_INTERVAL_MS = 2000;
  // AG07: video ONNX on CPU may need up to ~120s (60 * 2s)
  const POLL_MAX_ATTEMPTS = 60;
  const DEVICE_KEY = 'aladdin_web_device_id';
  const TOKEN_KEY = 'aladdin_web_access_token';
  const CASE_KEY = 'aladdin_antifake_case_id';

  const DEMO = {
    scam: 'СРОЧНО! Ваш счёт заблокирован банком. Переведите 15 000 ₽ по ссылке до 18:00, иначе арест счёта: https://pay-safe-bank.ru/confirm',
    url: 'https://secure-client-verify.example-bank.ru/login?session=expired',
    card: 'Ваша карта *4532 будет заблокирована через 15 мин. Продлите доступ: https://bank-card-renew.ru/extend?id=4532 Введите CVV и код из SMS.'
  };

  const tabs = document.querySelectorAll('.af-tab');
  const panels = document.querySelectorAll('.af-panel');
  const gate = document.getElementById('af-premium-gate');
  const gateForm = document.getElementById('af-premium-form');
  const gateInput = document.getElementById('af-activation-code');
  const gateMsg = document.getElementById('af-premium-msg');
  const mainContent = document.getElementById('af-main-content');
  const caseBar = document.getElementById('af-case-bar');
  const caseSummary = document.getElementById('af-case-summary');
  const caseStartBtn = document.getElementById('af-case-start');
  const caseRefreshBtn = document.getElementById('af-case-refresh');
  const caseClearBtn = document.getElementById('af-case-clear');

  let hasPremium = false;

  function t(key, fallback) {
    var out = key;
    if (window.ALADDIN_I18N && window.ALADDIN_I18N.t) {
      out = window.ALADDIN_I18N.t(key);
    }
    if (!out || out === key) {
      return fallback != null ? fallback : key;
    }
    return out;
  }

  function sleep(ms) {
    return new Promise(function (resolve) { setTimeout(resolve, ms); });
  }

  /** Sync SHA-256 (hex) — PoW via SubtleCrypto is too slow in the browser. */
  function sha256HexSync(str) {
    function rotr(n, x) { return (x >>> n) | (x << (32 - n)); }
    var K = [
      0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
      0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
      0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
      0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
      0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
      0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
      0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
      0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
    ];
    var bytes = unescape(encodeURIComponent(str));
    var len = bytes.length;
    var bitLen = len * 8;
    var withOne = bytes + String.fromCharCode(0x80);
    while ((withOne.length % 64) !== 56) withOne += String.fromCharCode(0);
    for (var i = 7; i >= 0; i--) withOne += String.fromCharCode((Math.floor(bitLen / Math.pow(2, 8 * i))) & 0xff);
    var H = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    for (var off = 0; off < withOne.length; off += 64) {
      var w = new Array(64);
      for (var j = 0; j < 16; j++) {
        var o = off + j * 4;
        w[j] = (withOne.charCodeAt(o) << 24) | (withOne.charCodeAt(o + 1) << 16) |
          (withOne.charCodeAt(o + 2) << 8) | withOne.charCodeAt(o + 3);
      }
      for (j = 16; j < 64; j++) {
        var s0 = rotr(7, w[j - 15]) ^ rotr(18, w[j - 15]) ^ (w[j - 15] >>> 3);
        var s1 = rotr(17, w[j - 2]) ^ rotr(19, w[j - 2]) ^ (w[j - 2] >>> 10);
        w[j] = (w[j - 16] + s0 + w[j - 7] + s1) | 0;
      }
      var a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
      for (j = 0; j < 64; j++) {
        var S1 = rotr(6, e) ^ rotr(11, e) ^ rotr(25, e);
        var ch = (e & f) ^ (~e & g);
        var t1 = (h + S1 + ch + K[j] + w[j]) | 0;
        var S0 = rotr(2, a) ^ rotr(13, a) ^ rotr(22, a);
        var maj = (a & b) ^ (a & c) ^ (b & c);
        var t2 = (S0 + maj) | 0;
        h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
      }
      H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0;
      H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
    }
    return H.map(function (x) { return (x >>> 0).toString(16).padStart(8, '0'); }).join('');
  }

  function solvePow(challenge, difficulty) {
    var target = '0'.repeat(difficulty || 3);
    var nonce = 0;
    // Sync loop is OK for difficulty 3 (~4k hashes); keep chunked for Safari UI.
    while (true) {
      if (sha256HexSync(challenge + ':' + String(nonce)).indexOf(target) === 0) {
        return String(nonce);
      }
      nonce += 1;
      if (nonce > 2000000) throw new Error('pow_too_hard');
    }
  }

  async function solvePowAsync(challenge, difficulty) {
    var target = '0'.repeat(difficulty || 3);
    var nonce = 0;
    while (true) {
      for (var i = 0; i < 200; i++) {
        if (sha256HexSync(challenge + ':' + String(nonce)).indexOf(target) === 0) {
          return String(nonce);
        }
        nonce += 1;
        if (nonce > 2000000) throw new Error('pow_too_hard');
      }
      await sleep(0);
    }
  }

  async function prepareCaptchaPayload(onProgress) {
    // Prefer completed Turnstile token when widget worked.
    var token = window.__aladdinTurnstileToken || '';
    if (token) {
      return { turnstileToken: token };
    }
    // Fallback PoW: Cloudflare widget missing/blocked (Safari / RU / adblock).
    var wantTurnstileOnly =
      window.__aladdinCaptchaMode === 'turnstile' && window.__aladdinCaptchaFallback === false;
    if (wantTurnstileOnly) {
      throw new Error('turnstile_pending');
    }
    if (onProgress) onProgress(t('af.trial.checking') || 'Проверяем браузер…');
    var chRes = await apiFetch('/api/antifake/web/pow-challenge', { method: 'POST' });
    var ch = await chRes.json().catch(function () { return {}; });
    if (!chRes.ok || !ch.challenge) {
      throw new Error('pow_issue_failed');
    }
    var nonce = await solvePowAsync(ch.challenge, ch.difficulty || 3);
    return { powChallenge: ch.challenge, powNonce: nonce };
  }

  async function browserFpHash() {
    var parts = [
      navigator.userAgent || '',
      navigator.language || '',
      (Intl.DateTimeFormat().resolvedOptions().timeZone || ''),
      String(screen.width) + 'x' + String(screen.height),
      String(window.devicePixelRatio || 1),
      navigator.platform || '',
      String(navigator.hardwareConcurrency || 0)
    ].join('|');
    if (!window.crypto || !window.crypto.subtle) {
      var h = 0;
      for (var i = 0; i < parts.length; i++) h = ((h << 5) - h + parts.charCodeAt(i)) | 0;
      var hex = (h >>> 0).toString(16).padStart(8, '0');
      return (hex + hex + hex + hex + hex + hex + hex + hex).slice(0, 64);
    }
    var buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(parts));
    return Array.from(new Uint8Array(buf)).map(function (b) {
      return b.toString(16).padStart(2, '0');
    }).join('');
  }

  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      if (!hasPremium) return;
      const id = tab.getAttribute('data-tab');
      tabs.forEach(function (tb) { tb.classList.toggle('af-tab--active', tb === tab); });
      panels.forEach(function (p) {
        p.classList.toggle('af-panel--active', p.id === 'panel-' + id);
      });
    });
  });

  function showResult(el, kind, title, body) {
    el.style.display = 'block';
    el.className = 'af-result af-result--' + kind;
    el.innerHTML = '<strong>' + title + '</strong><p style="margin:8px 0 0">' + body + '</p>';
  }

  function verdictLabel(v) {
    const map = {
      likely_fake: ['fake', '⚠️ ' + (t('af.verdict.fake') || 'Похоже на подделку'), t('af.verdict.fake_hint') || 'Будьте осторожны. Не переводите деньги и не сообщайте пароли.'],
      uncertain: ['warn', '❓ ' + (t('af.verdict.uncertain') || 'Пока неясно'), t('af.verdict.uncertain_hint') || 'Однозначно сказать нельзя. Уточните у взрослых и проверьте, кто прислал.'],
      likely_real: ['ok', '✓ ' + (t('af.verdict.ok') || 'Похоже на обычное'), t('af.verdict.ok_hint') || 'Явных признаков подделки не видно. Это не гарантия 100%.'],
      insufficient_data: ['warn', t('af.verdict.nodata') || 'Мало данных', t('af.verdict.nodata_hint') || 'Попробуйте другой файл или более длинный ролик.']
    };
    return map[v] || map.uncertain;
  }

  function confidenceLabel(conf) {
    if (conf == null || isNaN(conf)) return '';
    const pct = Math.round(Number(conf) * 100);
    let words = t('af.conf.low') || 'уверенность осторожная';
    if (pct >= 70) words = t('af.conf.high') || 'уверенность высокая';
    else if (pct >= 45) words = t('af.conf.mid') || 'уверенность средняя';
    return pct + '% · ' + words;
  }

  function postVerdictHtml(verdict, kindHint) {
    const k = kindHint || 'text';
    const byKind = {
      text: {
        likely_fake: [t('af.step.tfake1') || 'Не переводите деньги и не сообщайте коды из SMS.', t('af.step.tfake2') || 'Спросите родителей или перезвоните в организацию по номеру с официального сайта.', t('af.step.tfake3') || 'Удалите сообщение и заблокируйте отправителя.'],
        uncertain: [t('af.step.tunc1') || 'Не спешите отвечать.', t('af.step.tunc2') || 'Покажите текст взрослым.', t('af.step.tunc3') || 'Не переходите по ссылкам из сообщения.'],
        likely_real: [t('af.step.tok1') || 'Текст выглядит обычным, но просьбы о деньгах всё равно опасны.', t('af.step.tok2') || 'При сомнении — спросите взрослых.'],
        insufficient_data: [t('af.step.nd1') || 'Вставьте полное сообщение.', t('af.step.nd2') || 'Или проверьте ссылку отдельно.']
      },
      url: {
        likely_fake: [t('af.step.ufake1') || 'Не открывайте эту ссылку.', t('af.step.ufake2') || 'Не вводите пароли и данные карты.', t('af.step.ufake3') || 'Зайдите на сайт банка вручную через закладку или поиск.'],
        uncertain: [t('af.step.uunc1') || 'Не открывайте ссылку, пока не уточните у взрослых.', t('af.step.uunc2') || 'Сравните адрес с официальным сайтом.'],
        likely_real: [t('af.step.uok1') || 'Явных признаков фишинга нет, но лучше открывать сайт вручную.', t('af.step.uok2') || 'Не вводите пароли по чужой ссылке.'],
        insufficient_data: [t('af.step.und1') || 'Вставьте полную ссылку, начиная с https://.']
      },
      audio: {
        likely_fake: [t('af.step.afake1') || 'Не выполняйте просьбы о деньгах из этой записи.', t('af.step.afake2') || 'Перезвоните человеку сами на известный номер.', t('af.step.afake3') || 'Покажите запись родителям.'],
        uncertain: [t('af.step.aunc1') || 'Не торопитесь.', t('af.step.aunc2') || 'Спросите, можно ли созвониться «вживую».', t('af.step.aunc3') || 'Покажите запись взрослым.'],
        likely_real: [t('af.step.aok1') || 'Голос звучит обычно, но просьбы «срочно перевести» опасны.', t('af.step.aok2') || 'При сомнении — уточните у взрослых.'],
        insufficient_data: [t('af.step.and1') || 'Загрузите более длинную запись (лучше WAV/MP3).']
      },
      video: {
        likely_fake: [t('af.step.fake1') || 'Не переводите деньги и не сообщайте пароли.', t('af.step.fake2') || 'Спросите родителей.', t('af.step.fake3') || 'Не открывайте ссылки из ролика.'],
        uncertain: [t('af.step.vunc1') || 'Не отвечайте на просьбы о деньгах из ролика.', t('af.step.vunc2') || 'Спросите, откуда видео.', t('af.step.vunc3') || 'Покажите ролик взрослым.'],
        likely_real: [t('af.step.vok1') || 'Ролик выглядит обычным, но просьбы о деньгах опасны.', t('af.step.vok2') || 'Если прислал незнакомец — уточните у взрослых.'],
        insufficient_data: [t('af.step.vnd1') || 'Загрузите другое или более длинное видео.']
      },
      document: {
        likely_fake: [t('af.step.dfake1') || 'Не оплачивайте по этому документу.', t('af.step.dfake2') || 'Проверьте организацию по официальному сайту.', t('af.step.dfake3') || 'Покажите документ взрослым.'],
        uncertain: [t('af.step.dunc1') || 'Не спешите платить.', t('af.step.dunc2') || 'Покажите документ родителям.', t('af.step.dunc3') || 'Сверьте реквизиты с официальным источником.'],
        likely_real: [t('af.step.dok1') || 'Явных следов подделки нет, но крупные оплаты лучше сверять официально.', t('af.step.dok2') || 'При сомнении — спросите взрослых.'],
        insufficient_data: [t('af.step.dnd1') || 'Загрузите PDF или более чёткое фото.']
      },
      call: {
        likely_fake: [t('af.step.cfake1') || 'Положите трубку. Не называйте коды из SMS.', t('af.step.cfake2') || 'Перезвоните в банк по номеру с официального сайта.', t('af.step.cfake3') || 'Расскажите родителям о звонке.'],
        uncertain: [t('af.step.cunc1') || 'Не сообщайте пароли и коды.', t('af.step.cunc2') || 'Уточните у взрослых.', t('af.step.cunc3') || 'Не переводите деньги по телефону.'],
        likely_real: [t('af.step.cok1') || 'Явных признаков мошенничества нет, но банк сами наберите с сайта.', t('af.step.cok2') || 'Не диктуйте коды из SMS.'],
        insufficient_data: [t('af.step.cnd1') || 'Добавьте запись разговора или номер звонящего.']
      }
    };
    const pack = byKind[k] || byKind.text;
    const list = pack[verdict] || pack.uncertain;
    const childTip = childTipForVerdict(verdict);
    return '<div class="af-next-steps"><strong>' + (t('af.next_steps') || 'Что делать дальше') + '</strong><ul>' +
      list.map(function (s) { return '<li>' + s + '</li>'; }).join('') +
      '</ul></div>' +
      '<div class="af-child-tip" style="margin-top:14px;padding:12px 14px;border-radius:10px;background:rgba(255,255,255,0.06);border:1px solid rgba(245,200,110,0.25)">' +
      '<strong>' + (t('af.child.title') || 'Что сказать ребёнку') + '</strong>' +
      '<p style="margin:8px 0 0;font-size:14px;line-height:1.45">' + childTip + '</p>' +
      '<p style="margin:8px 0 0;font-size:13px"><a href="help/decode-deepfake.html" style="color:var(--gold-light)">' +
      (t('af.child.more') || 'Ещё карточки Decode →') + '</a></p></div>';
  }

  function childTipForVerdict(verdict) {
    if (verdict === 'likely_fake') {
      return t('af.child.fake') ||
        '«Это похоже на развод. Ты правильно остановился. Деньги и коды из SMS мы никогда не диктуем незнакомцам. Давай разберём вместе.»';
    }
    if (verdict === 'likely_real') {
      return t('af.child.ok') ||
        '«Похоже на обычное сообщение, но если просят деньги или секрет — всё равно скажи мне. Лучше лишний раз спросить.»';
    }
    if (verdict === 'insufficient_data') {
      return t('af.child.nodata') ||
        '«Пока мало данных. Не отвечай и не переходи по ссылкам — покажем взрослому полный текст или файл.»';
    }
    return t('af.child.unc') ||
      '«Пока неясно. Не отвечай и не переводи ничего. Покажи мне сообщение — проверим вместе в ALADDIN.»';
  }

  function shareVerdictUrl(data) {
    const params = new URLSearchParams();
    params.set('verdict', data.verdict || 'uncertain');
    if (data.confidence != null) params.set('confidence', String(data.confidence));
    return API + '/antifake.html?' + params.toString();
  }

  function shareVerdictHtml(data) {
    const url = shareVerdictUrl(data);
    const label = t('af.share.link') || 'Поделиться результатом';
    return '<p style="margin-top:12px"><button type="button" class="help-btn help-btn--ghost af-share-verdict" data-share-url="' +
      encodeURIComponent(url) + '">🔗 ' + label + '</button></p>';
  }

  function reasonsForDisplay(data) {
    const human = (data && data.reasons_human) || [];
    if (human.length) {
      return human.slice(0, 3);
    }
    const raw = (data && data.reasons) || [];
    // Never show snake_case codes in the UI when human list is empty
    return raw.filter(function (r) {
      return typeof r === 'string' && (r.indexOf(' ') >= 0 || /[а-яё]/i.test(r));
    }).slice(0, 3);
  }

  function renderVerdict(out, data, mediaKind) {
    const [kind, title, hint] = verdictLabel(data.verdict);
    const confWords = confidenceLabel(data.confidence);
    const summary = (data && data.summary_human) || hint;
    const why = reasonsForDisplay(data).filter(function (r) {
      return r && r !== summary && String(r).indexOf('ONNX') < 0 && String(r).indexOf('MP4') < 0;
    }).slice(0, 2);
    const whyHtml = why.length
      ? '<p style="margin:10px 0 0;font-size:14px"><strong>' + (t('af.why') || 'Коротко почему') + '</strong></p><ul style="margin:6px 0 0;padding-left:18px">' + why.map(function (r) {
          return '<li>' + String(r).replace(/</g, '&lt;') + '</li>';
        }).join('') + '</ul>'
      : '';
    showResult(
      out,
      kind,
      title + (confWords ? ' · ' + confWords : ''),
      '<p style="margin:0;font-size:15px;line-height:1.45">' + String(summary).replace(/</g, '&lt;') + '</p>' +
        whyHtml +
        postVerdictHtml(data.verdict, mediaKind) +
        shareVerdictHtml(data)
    );
  }

  function parseApiError(res, data) {
    const detail = data && data.detail;
    if (res.status === 403) {
      if (detail && detail.premium_required) {
        return {
          title: t('af.err.premium_title') || 'Нужен Antifake Premium',
          body: t('af.err.premium_body') || 'Введите код активации Family/Premium выше или оформите тариф на <a href="/index.html#pay" style="color:var(--gold-light)">странице оплаты</a>.',
          premium: true
        };
      }
      return {
        title: t('af.err.forbidden') || 'Доступ запрещён',
        body: t('af.err.forbidden_body') || 'Проверьте код активации или войдите снова.'
      };
    }
    if (res.status === 429) {
      const d = (typeof detail === 'object' && detail) ? detail : {};
      if (d.error === 'trial_media_limit') {
        return {
          title: t('af.err.trial_media_title') || 'Лимит пробных проверок',
          body: t('af.err.trial_media_body') ||
            'В пробном периоде можно проверить голос/видео ограниченное число раз. Оформите Family/Premium — или подождите, если лимит только что расширили для теста.'
        };
      }
      const mins = d.window_sec ? Math.max(1, Math.ceil(d.window_sec / 60)) : 1;
      const body = (t('af.err.rate_body') || 'Слишком много запросов. Подождите {min} мин и попробуйте снова.').replace('{min}', String(mins));
      return { title: t('af.err.rate_title') || 'Слишком много запросов', body: body };
    }
    if (res.status === 413) {
      return {
        title: t('af.err.large_title') || 'Файл слишком большой',
        body: t('af.err.large_body') || 'Максимум 25 МБ — как в приложении ALADDIN.'
      };
    }
    if (res.status === 400) {
      const code = (typeof detail === 'string' ? detail : (detail && detail.error)) || '';
      if (String(code).indexOf('invalid_filename') >= 0) {
        return {
          title: t('af.err.filename_title') || 'Не удалось принять файл',
          body: t('af.err.filename_body') || 'Обновите страницу и попробуйте снова. Имена с кириллицей и пробелами теперь поддерживаются.'
        };
      }
    }
    if (res.status === 401) {
      return {
        title: t('af.err.auth_title') || 'Сессия истекла',
        body: t('af.err.auth_body') || 'Обновите страницу и нажмите проверку ещё раз.'
      };
    }
    return {
      title: t('af.err.generic') || 'Не удалось выполнить запрос',
      body: (typeof detail === 'string' ? detail : '') || ('HTTP ' + res.status)
    };
  }

  function deviceId() {
    let id = localStorage.getItem(DEVICE_KEY);
    if (!id) {
      id = 'web-' + (crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + '-' + Math.random().toString(36).slice(2));
      localStorage.setItem(DEVICE_KEY, id);
    }
    return id;
  }

  async function ensureToken(forceRefresh) {
    if (!forceRefresh) {
      const cached = localStorage.getItem(TOKEN_KEY);
      if (cached) {
        // Drop obviously expired JWTs before the request fails
        try {
          const parts = cached.split('.');
          if (parts.length === 3) {
            var payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
            if (payload && payload.exp && payload.exp * 1000 < Date.now() + 5000) {
              localStorage.removeItem(TOKEN_KEY);
            } else {
              return cached;
            }
          } else {
            return cached;
          }
        } catch (e) {
          return cached;
        }
      }
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
    const res = await fetch(API + '/api/auth/register-device', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deviceId: deviceId(), deviceType: 'web' })
    });
    if (!res.ok) {
      const errData = await res.json().catch(function () { return {}; });
      const parsed = parseApiError(res, errData);
      throw new Error(parsed.title);
    }
    const data = await res.json();
    const token = data.access_token || data.token;
    if (!token) throw new Error('no token');
    localStorage.setItem(TOKEN_KEY, token);
    return token;
  }

  async function apiFetch(path, options) {
    options = options || {};
    const lang = (typeof localStorage !== 'undefined' && localStorage.getItem('aladdin_lang'))
      || (document.documentElement && document.documentElement.lang)
      || 'ru';
    async function once(forceRefresh) {
      const token = await ensureToken(forceRefresh);
      const headers = Object.assign(
        {
          'Authorization': 'Bearer ' + token,
          'X-Aladdin-Client': 'web',
          'X-Aladdin-Lang': String(lang).toLowerCase().startsWith('en') ? 'en' : 'ru',
          'Accept-Language': String(lang).toLowerCase().startsWith('en') ? 'en' : 'ru'
        },
        options.headers || {}
      );
      return fetch(API + path, Object.assign({}, options, { headers: headers }));
    }
    var res = await once(false);
    if (res.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      res = await once(true);
    }
    return res;
  }

  async function pollJob(jobId, out, mediaKind) {
    for (let attempt = 0; attempt < POLL_MAX_ATTEMPTS; attempt++) {
      await sleep(POLL_INTERVAL_MS);
      const res = await apiFetch('/api/antifake/jobs/' + encodeURIComponent(jobId), { method: 'GET' });
      if (res.status === 401) {
        localStorage.removeItem(TOKEN_KEY);
        throw new Error('auth expired');
      }
      if (!res.ok) {
        const errData = await res.json().catch(function () { return {}; });
        const parsed = parseApiError(res, errData);
        showResult(out, 'warn', parsed.title, parsed.body);
        return;
      }
      const data = await res.json();
      if (data.status === 'queued' || data.status === 'processing') {
        showResult(out, 'warn', t('af.poll.analyzing') || 'Анализ…', (t('af.poll.wait') || 'Ждём результат…') + ' (' + data.status + ')');
        continue;
      }
      if (data.status === 'failed') {
        showResult(out, 'warn', t('af.poll.failed') || 'Анализ не удался', data.error || '');
        return;
      }
      if (data.verdict) {
        renderVerdict(out, data, mediaKind);
        return;
      }
    }
    showResult(out, 'warn', t('af.poll.timeout') || 'Долгий анализ', t('af.poll.timeout_hint') || 'Попробуйте короче файл.');
  }

  function getCaseId() {
    try {
      return sessionStorage.getItem(CASE_KEY) || '';
    } catch (e) {
      return '';
    }
  }

  function setCaseId(id) {
    try {
      if (id) sessionStorage.setItem(CASE_KEY, id);
      else sessionStorage.removeItem(CASE_KEY);
    } catch (e) { /* ignore */ }
    updateCaseUI();
  }

  function caseVerdictLabel(v) {
    const map = {
      likely_fake: t('af.verdict.fake') || 'Похоже на подделку',
      uncertain: t('af.verdict.uncertain') || 'Неясно',
      likely_real: t('af.verdict.ok') || 'Похоже на подлинное',
      insufficient_data: t('af.verdict.nodata') || 'Недостаточно данных'
    };
    return map[v] || v || '—';
  }

  function updateCaseUI(meta) {
    if (!caseBar) return;
    const caseId = getCaseId();
    caseBar.style.display = hasPremium ? 'block' : 'none';
    if (!hasPremium) return;
    if (caseStartBtn) caseStartBtn.style.display = caseId ? 'none' : '';
    if (caseRefreshBtn) caseRefreshBtn.style.display = caseId ? '' : 'none';
    if (caseClearBtn) caseClearBtn.style.display = caseId ? '' : 'none';
    if (!caseSummary) return;
    if (!caseId) {
      caseSummary.textContent = t('af.case.hint') || 'Один кейс — текст, ссылка и файлы.';
      return;
    }
    if (!meta) {
      const tpl = t('af.case.active') || 'Кейс активен · проверок: {n}';
      caseSummary.textContent = tpl.replace('{n}', '…');
      return;
    }
    const items = meta.items || [];
    const pending = items.some(function (i) { return i.status === 'queued' || i.status === 'processing'; });
    if (pending) {
      caseSummary.textContent = t('af.case.pending') || 'Кейс активен · ждём завершения проверок…';
      return;
    }
    if (meta.aggregate_verdict) {
      const tpl = t('af.case.aggregate') || 'Итог кейса: {verdict}';
      caseSummary.textContent = tpl.replace('{verdict}', caseVerdictLabel(meta.aggregate_verdict)) +
        ' · ' + items.length;
      return;
    }
    const tpl = t('af.case.active') || 'Кейс активен · проверок: {n}';
    caseSummary.textContent = tpl.replace('{n}', String(items.length));
  }

  async function refreshCaseSummary() {
    const caseId = getCaseId();
    if (!caseId || !hasPremium) return null;
    try {
      const res = await apiFetch('/api/antifake/cases/' + encodeURIComponent(caseId), { method: 'GET' });
      if (res.status === 404) {
        setCaseId('');
        return null;
      }
      if (!res.ok) return null;
      const data = await res.json();
      updateCaseUI(data);
      return data;
    } catch (e) {
      if (caseSummary) caseSummary.textContent = t('af.case.err') || 'Не удалось обновить кейс';
      return null;
    }
  }

  async function ensureCase() {
    if (getCaseId()) return getCaseId();
    const res = await apiFetch('/api/antifake/cases', { method: 'POST' });
    const data = await res.json().catch(function () { return {}; });
    if (!res.ok || !data.case_id) throw new Error('case_create_failed');
    setCaseId(data.case_id);
    return data.case_id;
  }

  function setPremiumUI(access, meta) {
    hasPremium = !!access;
    if (gate) gate.style.display = access ? 'none' : 'block';
    if (mainContent) mainContent.style.display = access ? 'block' : 'none';
    tabs.forEach(function (tb) { tb.disabled = !access; });
    updateTrialBanner(meta || {});
    updateCaseUI();
    if (access && getCaseId()) refreshCaseSummary();
  }

  function updateTrialBanner(meta) {
    const gateEl = document.getElementById('af-trial-status');
    const mainEl = document.getElementById('af-trial-banner');
    const startBtn = document.getElementById('af-start-trial');
    const el = hasPremium ? mainEl : gateEl;
    if (gateEl && el !== gateEl) gateEl.style.display = 'none';
    if (mainEl && el !== mainEl) mainEl.style.display = 'none';
    if (!el) return;
    if (hasPremium && meta.trial_active && !meta.paid) {
      const left = meta.trial_days_left != null ? meta.trial_days_left : '';
      const tpl = t('af.trial.active') || 'Пробный период: осталось {days} дн.';
      el.textContent = tpl.replace('{days}', String(left));
      el.className = 'af-premium-msg af-premium-msg--ok';
      el.style.display = 'block';
      if (startBtn) startBtn.style.display = 'none';
      return;
    }
    if (hasPremium && meta.paid) {
      el.style.display = 'none';
      return;
    }
    if (meta.trial && !meta.trial_active) {
      el.textContent = t('af.trial.expired') || 'Пробный период закончился. Введите код или оформите тариф.';
      el.className = 'af-premium-msg af-premium-msg--warn';
      el.style.display = 'block';
      if (startBtn) startBtn.style.display = 'none';
      return;
    }
    el.style.display = 'none';
    if (startBtn) startBtn.style.display = '';
  }

  function showGateMsg(text, kind) {
    if (!gateMsg) return;
    gateMsg.style.display = 'block';
    gateMsg.className = 'af-premium-msg af-premium-msg--' + (kind || 'warn');
    gateMsg.textContent = text;
  }

  async function refreshAccess() {
    try {
      const res = await apiFetch('/api/antifake/web/access', { method: 'GET' });
      if (res.status === 401) {
        localStorage.removeItem(TOKEN_KEY);
        return refreshAccess();
      }
      if (!res.ok) {
        setPremiumUI(false);
        return;
      }
      const data = await res.json();
      setPremiumUI(!!data.access, data);
    } catch (e) {
      setPremiumUI(false);
      showGateMsg(t('af.err.network') || 'Не удалось подключиться. Обновите страницу.', 'warn');
    }
  }

  function prefillFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    if (code && gateInput) gateInput.value = code.trim();

    const text = params.get('text');
    const urlParam = params.get('url');
    const field = document.getElementById('af-text');
    if (field) {
      if (text) field.value = text;
      else if (urlParam) field.value = urlParam;
      else {
        try {
          const saved = sessionStorage.getItem("aladdin.speech.check");
          if (saved) {
            field.value = saved;
            sessionStorage.removeItem("aladdin.speech.check");
          }
        } catch (e) { /* keep the empty field */ }
      }
    }

    const verdict = params.get('verdict');
    if (verdict) {
      const out = document.getElementById('af-result-text');
      const conf = params.get('confidence');
      renderVerdict(out, {
        verdict: verdict,
        confidence: conf ? parseFloat(conf) : null,
        reasons: [t('af.share.shared') || 'Результат проверки, которым поделились (без исходного текста).']
      });
      if (mainContent) mainContent.style.display = 'block';
    }
  }

  async function loadTransparency() {
    const el = document.getElementById('af-transparency');
    if (!el) return;
    try {
      const res = await fetch(API + '/api/antifake/public/transparency?days=30');
      if (!res.ok) return;
      const data = await res.json();
      const fake = data.likely_fake_detected || 0;
      const checks = data.checks_completed || 0;
      if (checks <= 0) return;
      el.style.display = 'block';
      el.innerHTML = '<strong>' + (t('af.transparency.title') || 'За месяц на платформе') + '</strong><p style="margin:8px 0 0">' +
        (t('af.transparency.body') || 'Завершено проверок: {checks}. Подозрительных: {fake}.')
          .replace('{checks}', String(checks)).replace('{fake}', String(fake)) + '</p>';
    } catch (e) { /* optional */ }
  }

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.af-share-verdict');
    if (!btn) return;
    const url = decodeURIComponent(btn.getAttribute('data-share-url') || '');
    if (navigator.share) {
      navigator.share({ title: 'ALADDIN Antifake', url: url }).catch(function () {});
    } else if (navigator.clipboard) {
      navigator.clipboard.writeText(url);
      btn.textContent = '✓ ' + (t('af.share.copied') || 'Ссылка скопирована');
    }
  });

  const trialBtn = document.getElementById('af-start-trial');
  async function startTrialFlow() {
    if (!trialBtn) return;
    showGateMsg(t('af.trial.starting') || 'Запускаем пробный период…', 'warn');
    trialBtn.disabled = true;
    var fb = document.getElementById('af-start-trial-fallback');
    if (fb) fb.disabled = true;
    try {
      // Force PoW path if Turnstile never gave a token (Safari / blocked CF)
      if (!window.__aladdinTurnstileToken) {
        window.__aladdinCaptchaFallback = true;
        window.__aladdinCaptchaMode = 'pow';
      }
      const fp = await browserFpHash();
      var captcha;
      try {
        captcha = await prepareCaptchaPayload(function (msg) { showGateMsg(msg, 'warn'); });
      } catch (ce) {
        var cem = String(ce && ce.message || ce);
        if (cem === 'turnstile_pending') {
          showGateMsg(t('af.trial.turnstile') || 'Подтвердите, что вы не робот, и нажмите ещё раз.', 'warn');
          return;
        }
        showGateMsg(t('af.trial.err') || 'Не удалось начать пробный период. Обновите страницу и попробуйте ещё раз.', 'warn');
        return;
      }
      const res = await apiFetch('/api/antifake/web/start-trial', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(Object.assign({ browserFp: fp }, captcha))
      });
      const data = await res.json().catch(function () { return {}; });
      if (!res.ok) {
        const detail = data.detail;
        const errCode = (detail && detail.error) || detail;
        if (errCode === 'trial_ip_limit') {
          showGateMsg(t('af.trial.ip_limit') || 'С этой сети пробный период уже использовали. Введите код Family/Premium.', 'warn');
          return;
        }
        if (errCode === 'trial_fp_limit') {
          showGateMsg(t('af.trial.fp_limit') || 'Пробный период в этом браузере уже был. Введите код Family/Premium.', 'warn');
          return;
        }
        if (errCode === 'turnstile_failed' || errCode === 'pow_required' ||
            errCode === 'pow_challenge_failed' || errCode === 'pow_challenge_expired' ||
            errCode === 'pow_challenge_invalid' || errCode === 'pow_challenge_ip_mismatch') {
          showGateMsg(t('af.trial.turnstile') || 'Проверка не прошла. Нажмите ещё раз.', 'warn');
          return;
        }
        if (errCode === 'trial_already_used') {
          showGateMsg(t('af.trial.used') || 'Пробный период на этом устройстве уже был. Введите код.', 'warn');
          return;
        }
        // already active trial on same account
        if (data && (data.trial_active || data.reason === 'trial_already_active')) {
          showGateMsg(t('af.trial.ok') || '14 дней бесплатно активированы.', 'ok');
          setPremiumUI(true, data);
          return;
        }
        showGateMsg(t('af.trial.err') || 'Не удалось начать пробный период. Обновите страницу и попробуйте ещё раз.', 'warn');
        return;
      }
      showGateMsg(t('af.trial.ok') || '14 дней бесплатно активированы.', 'ok');
      setPremiumUI(true, data);
    } catch (e) {
      showGateMsg(t('af.err.network') || 'Ошибка сети. Проверьте интернет и обновите страницу.', 'warn');
    } finally {
      trialBtn.disabled = false;
      trialBtn.style.pointerEvents = 'auto';
      if (fb) fb.disabled = false;
    }
  }

  window.__aladdinStartTrial = startTrialFlow;

  if (trialBtn) {
    trialBtn.disabled = false;
    trialBtn.style.pointerEvents = 'auto';
    trialBtn.addEventListener('click', function (e) {
      e.preventDefault();
      startTrialFlow();
    });
  }

  if (gateForm) {
    gateForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      const code = (gateInput && gateInput.value || '').trim();
      if (!code) {
        showGateMsg(t('af.gate.code_required') || 'Введите код активации Family или Premium.', 'warn');
        return;
      }
      showGateMsg(t('af.gate.checking') || 'Проверяем код…', 'warn');
      try {
        const res = await apiFetch('/api/antifake/web/activate-code', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: code })
        });
        if (res.status === 401) {
          localStorage.removeItem(TOKEN_KEY);
          throw new Error('auth expired');
        }
        const data = await res.json().catch(function () { return {}; });
        if (!res.ok) {
          const detail = data.detail;
          const codeKey = typeof detail === 'string' ? detail : (detail && detail.error) || 'error';
          const messages = {
            activation_code_not_found: t('af.gate.err_not_found') || 'Код не найден.',
            activation_code_expired: t('af.gate.err_expired') || 'Срок действия кода истёк.',
            activation_code_inactive: t('af.gate.err_inactive') || 'Код неактивен.',
            tariff_not_eligible_for_antifake: t('af.gate.err_tariff') || 'Тариф не включает Antifake.',
            code_required: t('af.gate.code_required') || 'Введите код.'
          };
          showGateMsg(messages[codeKey] || t('af.gate.err_generic') || 'Не удалось активировать код.', 'warn');
          return;
        }
        showGateMsg(t('af.gate.ok') || 'Premium активирован. Можно проверять.', 'ok');
        setPremiumUI(true, { paid: true });
      } catch (err) {
        showGateMsg(t('af.err.network') || 'Ошибка сети. Попробуйте позже.', 'warn');
      }
    });
  }

  if (caseStartBtn) {
    caseStartBtn.addEventListener('click', async function () {
      if (!hasPremium) return;
      caseStartBtn.disabled = true;
      try {
        await ensureCase();
      } catch (e) {
        if (caseSummary) caseSummary.textContent = t('af.case.err') || 'Не удалось создать кейс';
      } finally {
        caseStartBtn.disabled = false;
      }
    });
  }
  if (caseRefreshBtn) {
    caseRefreshBtn.addEventListener('click', function () {
      if (!hasPremium) return;
      refreshCaseSummary();
    });
  }
  if (caseClearBtn) {
    caseClearBtn.addEventListener('click', function () {
      setCaseId('');
    });
  }

  document.getElementById('af-check-text').addEventListener('click', async function () {
    if (!hasPremium) {
      showGateMsg(t('af.gate.need_code') || 'Сначала введите код активации.', 'warn');
      return;
    }
    const raw = document.getElementById('af-text').value.trim();
    const out = document.getElementById('af-result-text');
    if (!raw) {
      showResult(out, 'warn', t('af.empty.title') || 'Пусто', t('af.empty.body') || 'Вставьте текст или ссылку.');
      return;
    }
    showResult(out, 'warn', t('af.poll.analyzing') || 'Анализ…', t('af.text.wait') || 'Обычно до 15 секунд.');
    const isUrl = /^https?:\/\//i.test(raw);
    const endpoint = isUrl ? '/api/antifake/check/url' : '/api/antifake/check/text';
    const body = isUrl ? { url: raw } : { text: raw, mode: 'news' };
    const caseId = getCaseId();
    if (caseId) body.case_id = caseId;
    try {
      const res = await apiFetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (res.status === 401) {
        localStorage.removeItem(TOKEN_KEY);
        throw new Error('auth expired');
      }
      const errData = await res.json().catch(function () { return {}; });
      if (!res.ok) {
        const parsed = parseApiError(res, errData);
        if (parsed.premium) setPremiumUI(false);
        showResult(out, 'warn', parsed.title, parsed.body);
        return;
      }
      renderVerdict(out, errData, isUrl ? 'url' : 'text');
      if (getCaseId()) refreshCaseSummary();
    } catch (e) {
      showResult(
        out,
        'warn',
        t('af.err.generic') || 'Не удалось проверить',
        t('af.err.network') || 'Проверьте интернет и нажмите «Проверить» ещё раз. Текст обычно быстрый; при слабой сети подождите 10–15 секунд.'
      );
    }
  });

  document.querySelectorAll('[data-af-example]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (!hasPremium) {
        showGateMsg(t('af.gate.need_code') || 'Сначала введите код активации.', 'warn');
        return;
      }
      const kind = btn.getAttribute('data-af-example');
      const field = document.getElementById('af-text');
      if (field && DEMO[kind]) field.value = DEMO[kind];
    });
  });

  function setupUpload(dropId, inputId, resultId, kind, fileAccept) {
    const drop = document.getElementById(dropId);
    const input = document.getElementById(inputId);
    const out = document.getElementById(resultId);
    if (!drop || !input || !out) return;
    drop.addEventListener('click', function () {
      if (!hasPremium) {
        showGateMsg(t('af.gate.need_code') || 'Сначала введите код активации.', 'warn');
        return;
      }
      input.click();
    });
    drop.addEventListener('dragover', function (e) { e.preventDefault(); });
    drop.addEventListener('drop', function (e) {
      e.preventDefault();
      if (!hasPremium) {
        showGateMsg(t('af.gate.need_code') || 'Сначала введите код активации.', 'warn');
        return;
      }
      if (e.dataTransfer.files[0]) upload(e.dataTransfer.files[0]);
    });
    input.addEventListener('change', function () {
      if (input.files[0]) upload(input.files[0]);
    });

    async function upload(file) {
      if (!hasPremium) return;
      if (file.size > MAX_BYTES) {
        const parsed = parseApiError({ status: 413 }, {});
        showResult(out, 'warn', parsed.title, parsed.body);
        return;
      }
      showResult(out, 'warn', t('af.uploading') || 'Загрузка…', file.name);
      const fd = new FormData();
      fd.append('file', file);
      const uploadCaseId = getCaseId();
      if (uploadCaseId) fd.append('case_id', uploadCaseId);
      try {
        const res = await apiFetch('/api/antifake/check/' + kind, { method: 'POST', body: fd });
        const data = await res.json().catch(function () { return {}; });
        if (!res.ok) {
          const parsed = parseApiError(res, data);
          if (parsed.premium) setPremiumUI(false);
          showResult(out, 'warn', parsed.title, parsed.body);
          return;
        }
        const jobId = data.job_id || data.jobId;
        if (jobId) {
          showResult(out, 'warn', t('af.poll.analyzing') || 'Анализ…', t('af.poll.wait') || 'Ждём результат на сайте…');
          await pollJob(jobId, out, kind);
          if (getCaseId()) refreshCaseSummary();
          return;
        }
        if (data.verdict) {
          renderVerdict(out, data, kind);
          if (getCaseId()) refreshCaseSummary();
          return;
        }
        showResult(out, 'warn', t('af.poll.analyzing') || 'Анализ…', t('af.poll.wait') || 'Ждём результат…');
      } catch (e) {
        showResult(out, 'warn', t('af.err.generic') || 'Не удалось загрузить', t('af.err.network') || 'Сеть оборвалась или файл не принят. Уменьшите файл (до 25 МБ), проверьте Wi‑Fi и повторите. Голос/видео могут идти 1–3 минуты.');
      }
    }
  }

  setupUpload('af-drop-voice', 'af-file-voice', 'af-result-voice', 'audio', 'audio/*');
  setupUpload('af-drop-video', 'af-file-video', 'af-result-video', 'video', 'video/*');
  setupUpload('af-drop-document', 'af-file-document', 'af-result-document', 'document', 'application/pdf,image/*');

  function setupCallUpload() {
    const drop = document.getElementById('af-drop-call');
    const input = document.getElementById('af-file-call');
    const out = document.getElementById('af-result-call');
    const callerInput = document.getElementById('af-call-caller-id');
    const nameInput = document.getElementById('af-call-display-name');
    if (!drop || !input || !out) return;

    function normalizeCallerId(raw) {
      const digits = String(raw || '').replace(/\D/g, '');
      if (!digits) return '';
      if (digits.length === 11 && digits.charAt(0) === '8') return '7' + digits.slice(1);
      if (digits.length === 10) return '7' + digits;
      return digits;
    }

    drop.addEventListener('click', function () {
      if (!hasPremium) {
        showGateMsg(t('af.gate.need_code') || 'Сначала введите код активации.', 'warn');
        return;
      }
      input.click();
    });
    drop.addEventListener('dragover', function (e) { e.preventDefault(); });
    drop.addEventListener('drop', function (e) {
      e.preventDefault();
      if (!hasPremium) {
        showGateMsg(t('af.gate.need_code') || 'Сначала введите код активации.', 'warn');
        return;
      }
      if (e.dataTransfer.files[0]) upload(e.dataTransfer.files[0]);
    });
    input.addEventListener('change', function () {
      if (input.files[0]) upload(input.files[0]);
    });

    async function upload(file) {
      if (!hasPremium) return;
      if (file.size > MAX_BYTES) {
        const parsed = parseApiError({ status: 413 }, {});
        showResult(out, 'warn', parsed.title, parsed.body);
        return;
      }
      showResult(out, 'warn', t('af.uploading') || 'Загрузка…', file.name);
      const fd = new FormData();
      fd.append('file', file);
      const callerId = normalizeCallerId(callerInput && callerInput.value);
      const displayName = (nameInput && nameInput.value || '').trim();
      if (callerId) fd.append('caller_id', callerId);
      if (displayName) fd.append('display_name', displayName);
      const caseId = getCaseId();
      if (caseId) fd.append('case_id', caseId);
      try {
        const res = await apiFetch('/api/antifake/call/analyze', { method: 'POST', body: fd });
        const data = await res.json().catch(function () { return {}; });
        if (!res.ok) {
          const parsed = parseApiError(res, data);
          if (parsed.premium) setPremiumUI(false);
          showResult(out, 'warn', parsed.title, parsed.body);
          return;
        }
        const jobId = data.job_id || data.jobId;
        if (jobId) {
          showResult(out, 'warn', t('af.poll.analyzing') || 'Анализ…', t('af.call.analyzing') || 'Проверяем запись звонка…');
          await pollJob(jobId, out, 'call');
          if (getCaseId()) refreshCaseSummary();
          return;
        }
        if (data.verdict) {
          renderVerdict(out, data, 'call');
          if (getCaseId()) refreshCaseSummary();
          return;
        }
        showResult(out, 'warn', t('af.poll.analyzing') || 'Анализ…', t('af.poll.wait') || 'Ждём результат…');
      } catch (e) {
        showResult(out, 'warn', t('af.err.generic') || 'Не удалось загрузить', t('af.err.network') || 'Сеть оборвалась или файл не принят. Уменьшите файл (до 25 МБ), проверьте Wi‑Fi и повторите. Голос/видео могут идти 1–3 минуты.');
      }
    }
  }

  setupCallUpload();

  prefillFromUrl();
  loadTransparency();
  refreshAccess();
})();
