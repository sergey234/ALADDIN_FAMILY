(function () {
  var DICT_KEY = "aladdin.speech.words";
  var LARGE_KEY = "aladdin.speech.large";
  var fillers = ["э-э-э", "э-э", "эээ", "ээ", "эм", "ну вот", "типа"];

  var card = document.querySelector(".speech-card");
  var tabText = document.getElementById("tab-text");
  var tabRead = document.getElementById("tab-read");
  var panelText = document.getElementById("panel-text");
  var panelRead = document.getElementById("panel-read");
  var largeBtn = document.getElementById("speech-large");
  var source = document.getElementById("speech-source");
  var readBox = document.getElementById("speech-read-text");
  var result = document.getElementById("speech-result");
  var fileInput = document.getElementById("speech-file");
  var fileStatus = document.getElementById("speech-file-status");
  var wordInput = document.getElementById("speech-word");
  var wordList = document.getElementById("speech-words");
  var presetNote = document.getElementById("speech-preset-note");
  var placeholder = document.getElementById("speech-placeholder");
  var lastPreset = "";
  var lastFileName = "";
  var statusKey = "";

  function tr(key) {
    if (window.ALADDIN_I18N && window.ALADDIN_I18N.t) return window.ALADDIN_I18N.t(key);
    return key;
  }

  function setStatus(key) {
    statusKey = key;
    fileStatus.textContent = tr(key);
  }

  var output = document.createElement("p");
  output.id = "speech-output";
  output.hidden = true;
  result.appendChild(output);

  function showResult(text) {
    if (text) {
      placeholder.hidden = true;
      output.hidden = false;
      output.textContent = text;
      return;
    }
    output.hidden = true;
    output.textContent = "";
    placeholder.hidden = false;
  }

  function words() {
    try {
      var parsed = JSON.parse(localStorage.getItem(DICT_KEY) || "[]");
      return Array.isArray(parsed) ? parsed.slice(0, 100) : [];
    } catch (e) {
      return [];
    }
  }

  function saveWords(list) {
    localStorage.setItem(DICT_KEY, JSON.stringify(list.slice(0, 100)));
    drawWords();
  }

  function drawWords() {
    wordList.innerHTML = "";
    words().forEach(function (word, index) {
      var li = document.createElement("li");
      li.appendChild(document.createTextNode(word));
      var remove = document.createElement("button");
      remove.type = "button";
      remove.textContent = "×";
      remove.setAttribute("aria-label", tr("speech.remove") + " " + word);
      remove.addEventListener("click", function () {
        var next = words();
        next.splice(index, 1);
        saveWords(next);
      });
      li.appendChild(remove);
      wordList.appendChild(li);
    });
  }

  function showTextMode(on) {
    tabText.setAttribute("aria-selected", on ? "true" : "false");
    tabRead.setAttribute("aria-selected", on ? "false" : "true");
    panelText.hidden = !on;
    panelRead.hidden = on;
    if (!on && source.value && !readBox.value) readBox.value = source.value;
  }

  function setLarge(on) {
    card.classList.toggle("is-large", on);
    largeBtn.setAttribute("aria-pressed", on ? "true" : "false");
    localStorage.setItem(LARGE_KEY, on ? "1" : "0");
  }

  function cleanFillers(text) {
    var out = text;
    fillers.forEach(function (word) {
      var pattern = new RegExp("(^|\\s)" + word.replace("-", "\\-") + "(?=\\s|$|[,.!?])", "gi");
      out = out.replace(pattern, "$1");
    });
    return out.replace(/[ \t]{2,}/g, " ").replace(/ +\n/g, "\n").trim();
  }

  function splitSentences(text) {
    var parts = [];
    var buf = "";
    for (var i = 0; i < text.length; i++) {
      buf += text[i];
      if (".!?".indexOf(text[i]) !== -1) {
        if (buf.trim()) parts.push(buf.trim());
        buf = "";
      }
    }
    if (buf.trim()) parts.push(buf.trim());
    return parts;
  }
  function makeClear(text) {
    var chunks = splitSentences(text.replace(/\s+/g, " "));
    var lines = [];
    chunks.forEach(function (sentence) {
      var bits = sentence.split(",").map(function (bit) { return bit.trim(); }).filter(Boolean);
      if (sentence.split(" ").length > 12 && bits.length > 1) {
        bits.forEach(function (bit) { lines.push(bit.replace(/[.!?]$/, "") + "."); });
      } else {
        lines.push(sentence);
      }
    });
    return lines.join("\n");
  }

  function applyPreset(name) {
    var text = source.value.trim();
    document.querySelectorAll(".speech-chip").forEach(function (chip) {
      chip.setAttribute("aria-pressed", chip.getAttribute("data-preset") === name ? "true" : "false");
    });
    if (!text) {
      showResult("");
      presetNote.textContent = tr("speech.need.text");
      return;
    }
    if (name === "clean") {
      showResult(cleanFillers(text));
      presetNote.textContent = tr("speech.note.clean");
      return;
    }
    if (name === "clear") {
      showResult(makeClear(cleanFillers(text)));
      presetNote.textContent = tr("speech.note.clear");
      return;
    }
    if (name === "family") {
      showResult(makeClear(cleanFillers(text)));
      presetNote.textContent = tr("speech.note.family");
      return;
    }
    if (name === "protocol") {
      showResult(makeProtocol(text));
      presetNote.textContent = tr("speech.note.protocol");
      return;
    }
    showResult(text);
    presetNote.textContent = tr("speech.note.back");
  }

  function makeProtocol(text) {
    var clean = makeClear(cleanFillers(text));
    var lines = clean.split("\n").map(function (line) { return line.trim(); }).filter(Boolean);
    var voices = [];
    var decided = [];
    var todo = [];
    lines.forEach(function (line) {
      var found = line.match(/Голос\s+\d+/g) || [];
      found.forEach(function (name) {
        if (voices.indexOf(name) === -1) voices.push(name);
      });
      var low = line.toLowerCase();
      if (low.indexOf("решил") !== -1 || low.indexOf("договор") !== -1 || low.indexOf("decided") !== -1 || low.indexOf("agreed") !== -1) decided.push(line);
      if (low.indexOf("надо") !== -1 || low.indexOf("нужно") !== -1 || low.indexOf("сдела") !== -1 || low.indexOf("need to") !== -1 || low.indexOf("to do") !== -1) todo.push(line);
    });
    var parts = [];
    if (voices.length) parts.push(tr("speech.protocol.who") + ": " + voices.join(", "));
    if (decided.length) parts.push(tr("speech.protocol.decided") + ":\n" + decided.join("\n"));
    if (todo.length) parts.push(tr("speech.protocol.todo") + ":\n" + todo.join("\n"));
    return parts.length ? parts.join("\n\n") : clean;
  }

  tabText.addEventListener("click", function () { showTextMode(true); });
  tabRead.addEventListener("click", function () { showTextMode(false); });
  largeBtn.addEventListener("click", function () {
    setLarge(largeBtn.getAttribute("aria-pressed") !== "true");
  });

  var peopleBox = document.getElementById("speech-people");
  var makeBtn = document.getElementById("speech-make");
  var listenBtn = document.getElementById("speech-listen");
  var listenPhrase = document.getElementById("speech-listen-phrase");
  var recorder = null;
  var recordStream = null;
  var recordChunks = [];
  var sendOnStop = false;
  var hourTimer = null;

  function clock(sec) {
    var s = Math.max(0, Math.floor(Number(sec) || 0));
    var h = Math.floor(s / 3600);
    var m = Math.floor((s % 3600) / 60);
    var r = s % 60;
    function pad(n) { return (n < 10 ? "0" : "") + n; }
    return pad(h) + ":" + pad(m) + ":" + pad(r);
  }

  function showVoices(lines, whole) {
    result.querySelectorAll(".speech-voice").forEach(function (node) { node.remove(); });
    showResult(whole);
    (lines || []).forEach(function (line) {
      var row = document.createElement("p");
      row.className = "speech-voice";
      row.textContent = "[" + clock(line.start) + "] " + (line.voice || "") + "  " + (line.text || "");
      result.appendChild(row);
    });
  }

  function siteToken() {
    try { return localStorage.getItem("aladdin_web_access_token") || ""; }
    catch (e) { return ""; }
  }

  function hasAccess() {
    var token = siteToken();
    if (!token) return Promise.resolve(false);
    return fetch("/api/antifake/web/access", {
      headers: { "Authorization": "Bearer " + token, "X-Aladdin-Client": "web" }
    }).then(function (res) {
      if (!res.ok) return false;
      return res.json().then(function (data) { return !!data.access; });
    }).catch(function () { return false; });
  }

  function sendFile(file) {
    if (!peopleBox.checked) {
      setStatus("speech.need.consent");
      return;
    }
    hasAccess().then(function (allowed) {
      if (!allowed) {
        setStatus("speech.need.access");
        return;
      }
      setStatus("speech.working");
      makeBtn.disabled = true;
      listenBtn.disabled = true;
      fetch("/api/speech/transcribe", {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + siteToken(),
          "X-Aladdin-Client": "web",
          "X-Speech-People": "yes",
          "Content-Type": "application/octet-stream"
        },
        body: file
      }).then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (data) {
          return { ok: res.ok, status: res.status, data: data };
        });
      }).then(function (pack) {
        makeBtn.disabled = false;
        listenBtn.disabled = false;
        if (!pack.ok) {
          fileStatus.textContent = (pack.data && pack.data.detail) || (pack.status === 429 ? tr("speech.busy") : tr("speech.fail"));
          return;
        }
        if (pack.data.text) source.value = pack.data.text;
        showVoices(pack.data.voices, pack.data.text || "");
        fileStatus.textContent = pack.data.deleted ? tr("speech.deleted") : tr("speech.fail");
        if (pack.data.note) presetNote.textContent = pack.data.note;
      }).catch(function () {
        makeBtn.disabled = false;
        listenBtn.disabled = false;
        setStatus("speech.fail");
      });
    });
  }

  fileInput.addEventListener("change", function () {
    var file = fileInput.files && fileInput.files[0];
    if (!file) {
      statusKey = "";
      fileStatus.textContent = "";
      return;
    }
    lastFileName = file.name;
    statusKey = "";
    fileStatus.textContent = file.name + ". " + tr("speech.file.wait");
  });

  makeBtn.addEventListener("click", function () {
    var file = fileInput.files && fileInput.files[0];
    if (!file) {
      setStatus("speech.need.file");
      return;
    }
    sendFile(file);
  });

  function showListenPhrase() {
    var phrase = tr("speech.listen.phrase");
    if (listenPhrase) listenPhrase.textContent = phrase;
    statusKey = "speech.listen.phrase";
    fileStatus.textContent = phrase;
  }

  function recorderFor(stream) {
    var types = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/aac"];
    var options = null;
    if (window.MediaRecorder && MediaRecorder.isTypeSupported) {
      for (var i = 0; i < types.length; i++) {
        if (MediaRecorder.isTypeSupported(types[i])) {
          options = { mimeType: types[i] };
          break;
        }
      }
    }
    return options ? new MediaRecorder(stream, options) : new MediaRecorder(stream);
  }

  function releaseMic() {
    if (hourTimer) {
      clearTimeout(hourTimer);
      hourTimer = null;
    }
    if (recordStream) {
      recordStream.getTracks().forEach(function (track) { track.stop(); });
      recordStream = null;
    }
    listenBtn.textContent = tr("speech.listen");
  }

  function finishRecording() {
    var shouldSend = sendOnStop;
    var chunks = recordChunks.slice();
    var kind = (recorder && recorder.mimeType) || "audio/webm";
    recorder = null;
    recordChunks = [];
    releaseMic();
    if (!shouldSend || !chunks.length) return;
    sendFile(new Blob(chunks, { type: kind }));
  }

  function beginRecording(stream) {
    var rec;
    try {
      rec = recorderFor(stream);
    } catch (e) {
      stream.getTracks().forEach(function (track) { track.stop(); });
      setStatus("speech.mic.fail");
      return;
    }
    recordStream = stream;
    recordChunks = [];
    sendOnStop = true;
    recorder = rec;
    rec.ondataavailable = function (event) {
      if (event.data && event.data.size) recordChunks.push(event.data);
    };
    rec.onstop = finishRecording;
    rec.start();
    listenBtn.textContent = tr("speech.stop");
    showListenPhrase();
    hourTimer = setTimeout(function () {
      sendOnStop = true;
      if (recorder && recorder.state === "recording") recorder.stop();
    }, 60 * 60 * 1000);
  }

  function stopWithoutSending() {
    sendOnStop = false;
    if (recorder && recorder.state === "recording") {
      recorder.stop();
      return;
    }
    releaseMic();
  }

  listenBtn.addEventListener("click", function () {
    if (listenBtn.disabled) return;
    if (recorder && recorder.state === "recording") {
      sendOnStop = true;
      recorder.stop();
      return;
    }
    if (!peopleBox.checked) {
      setStatus("speech.need.consent");
      return;
    }
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !window.MediaRecorder) {
      setStatus("speech.mic.fail");
      return;
    }
    hasAccess().then(function (allowed) {
      if (!allowed) {
        setStatus("speech.need.access");
        return;
      }
      showListenPhrase();
      return navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
        if (document.visibilityState === "hidden") {
          stream.getTracks().forEach(function (track) { track.stop(); });
          return;
        }
        beginRecording(stream);
      });
    }).catch(function () {
      setStatus("speech.mic.fail");
    });
  });

  window.addEventListener("pagehide", stopWithoutSending);
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") stopWithoutSending();
  });

  document.getElementById("speech-add-word").addEventListener("click", function () {
    var value = wordInput.value.trim();
    if (!value) return;
    var list = words();
    if (list.indexOf(value) === -1) list.push(value);
    saveWords(list);
    wordInput.value = "";
  });

  document.getElementById("speech-clear-words").addEventListener("click", function () {
    saveWords([]);
  });

  document.querySelectorAll(".speech-chip").forEach(function (chip) {
    chip.addEventListener("click", function () {
      lastPreset = chip.getAttribute("data-preset");
      applyPreset(lastPreset);
    });
  });

  document.getElementById("speech-restore").addEventListener("click", function () {
    showResult(source.value.trim());
    presetNote.textContent = tr("speech.note.back");
    document.querySelectorAll(".speech-chip").forEach(function (chip) {
      chip.setAttribute("aria-pressed", "false");
    });
  });

  document.getElementById("speech-copy").addEventListener("click", function () {
    var text = (output.hidden ? "" : output.textContent).trim() || source.value.trim();
    if (!text || !navigator.clipboard) return;
    navigator.clipboard.writeText(text);
  });

  document.getElementById("speech-download").addEventListener("click", function () {
    var text = (output.hidden ? "" : output.textContent).trim() || source.value.trim();
    if (!text) return;
    var blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    var link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "aladdin-rech.txt";
    link.click();
    URL.revokeObjectURL(link.href);
  });

  document.getElementById("speech-check").addEventListener("click", function () {
    var text = (output.hidden ? "" : output.textContent).trim() || source.value.trim();
    if (!text) return;
    try { sessionStorage.setItem("aladdin.speech.check", text); } catch (e) {}
  });

  document.getElementById("speech-speak").addEventListener("click", function () {
    var text = readBox.value.trim();
    if (!text || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    text.split(/[.!?]+/).forEach(function (part) {
      if (!part.trim()) return;
      var utter = new SpeechSynthesisUtterance(part.trim());
      utter.lang = "ru-RU";
      window.speechSynthesis.speak(utter);
    });
  });

  document.getElementById("speech-stop").addEventListener("click", function () {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  });

  document.addEventListener("aladdin:langchange", function () {
    drawWords();
    if (lastFileName) fileStatus.textContent = lastFileName + ". " + tr("speech.file.wait");
    else if (statusKey) fileStatus.textContent = tr(statusKey);
    if (lastPreset) applyPreset(lastPreset);
  });

  setLarge(localStorage.getItem(LARGE_KEY) === "1");
  drawWords();
  showTextMode(true);
})();
