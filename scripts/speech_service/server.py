"""Neighbor speech service on MAIN. Localhost only. One file at a time.

The upload is deleted before the answer is returned. Nothing here is the
public site button, and nothing here restarts the app on port 8002.
"""

from __future__ import annotations

import gc
import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

HOST = "127.0.0.1"
PORT = 8016
ROOT = Path("/opt/aladdin-speech")
WORK = ROOT / "work"
JOURNAL = ROOT / "journal" / "deletions.log"
TOKEN_PATH = ROOT / "secret" / "internal_token"
GIGAAM_DIR = ROOT / "weights" / "gigaam-v3-e2e_rnnt"
DIAR_CONFIG = ROOT / "app" / "diarization-local.yaml"
MAX_BYTES = 700 * 1024 * 1024
MAX_SECONDS = 60 * 60
CHUNK_SECONDS = 22.0

_lock = threading.Lock()
_busy = False
_gigaam = None
_diar = None


def _token() -> str:
    return TOKEN_PATH.read_text(encoding="utf-8").strip()


def _authorized(request: Request) -> bool:
    header = request.headers.get("authorization", "")
    return header == f"Bearer {_token()}"


def _web_access(request: Request) -> bool:
    header = request.headers.get("authorization", "")
    if not header.startswith("Bearer "):
        return False
    probe = urllib.request.Request(
        "http://127.0.0.1:8002/api/antifake/web/access",
        headers={"Authorization": header, "X-Aladdin-Client": "web"},
    )
    try:
        with urllib.request.urlopen(probe, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return False
    return bool(payload.get("access"))


def _journal(job_id: str, nbytes: int, deleted: bool) -> None:
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = f"{stamp} {job_id} bytes={nbytes} deleted={'yes' if deleted else 'no'}\n"
    with JOURNAL.open("a", encoding="utf-8") as handle:
        handle.write(line)


def _wipe(paths: list[Path], job_id: str, nbytes: int) -> bool:
    deleted = True
    for path in paths:
        try:
            if path.exists():
                path.unlink()
        except OSError:
            deleted = False
    _journal(job_id, nbytes, deleted)
    return deleted


def _run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(cmd, check=True, capture_output=True, timeout=timeout)


def _duration_seconds(path: Path) -> float:
    result = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        timeout=30,
    )
    text = result.stdout.decode("utf-8", errors="replace").strip()
    if not text or text == "N/A":
        return 0.0
    return float(text)


def _to_wav(src: Path, dst: Path) -> None:
    _run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(dst),
        ],
        timeout=180,
    )


def _slice_wav(src: Path, dst: Path, start: float, end: float) -> None:
    _run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-to",
            f"{end:.3f}",
            "-i",
            str(src),
            "-ac",
            "1",
            "-ar",
            "16000",
            str(dst),
        ],
        timeout=60,
    )


def _free() -> None:
    gc.collect()


def _waveform(path: Path) -> dict:
    import numpy as np
    import torch
    import wave

    with wave.open(str(path), "rb") as handle:
        rate = handle.getframerate()
        channels = handle.getnchannels()
        frames = handle.readframes(handle.getnframes())
    audio = np.frombuffer(frames, dtype=np.int16).astype("float32") / 32768.0
    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    tensor = torch.from_numpy(np.ascontiguousarray(audio)).unsqueeze(0)
    return {"waveform": tensor, "sample_rate": rate}


def _turns(wav_path: Path) -> list[tuple[float, float, str]]:
    import torch
    from pyannote.audio import Pipeline

    torch.set_num_threads(2)
    pipe = Pipeline.from_pretrained(str(DIAR_CONFIG))
    pipe.to(torch.device("cpu"))
    try:
        output = pipe(_waveform(wav_path))
        annotation = getattr(output, "speaker_diarization", output)
        turns: list[tuple[float, float, str]] = []
        if hasattr(annotation, "itertracks"):
            for turn, _, speaker in annotation.itertracks(yield_label=True):
                turns.append((float(turn.start), float(turn.end), str(speaker)))
        else:
            for turn, speaker in annotation:
                turns.append((float(turn.start), float(turn.end), str(speaker)))
        return turns
    finally:
        pipe = None
        _free()


def _model():
    import torch
    from transformers import AutoModel

    torch.set_num_threads(2)
    model = AutoModel.from_pretrained(str(GIGAAM_DIR), trust_remote_code=True)
    model.eval()
    return model


def _transcribe_piece(model: object, wav_path: Path, start: float, end: float, piece: Path) -> str:
    if end - start < 0.3:
        return ""
    _slice_wav(wav_path, piece, start, end)
    try:
        text = model.transcribe(str(piece))
    finally:
        piece.unlink(missing_ok=True)
    return str(text or "").strip()


def _transcribe_span(model: object, wav_path: Path, start: float, end: float, piece: Path) -> str:
    parts: list[str] = []
    cursor = start
    while cursor < end - 0.05:
        stop = min(end, cursor + CHUNK_SECONDS)
        text = _transcribe_piece(model, wav_path, cursor, stop, piece)
        if text:
            parts.append(text)
        cursor = stop
    return " ".join(parts).strip()


def _voice_names(turns: list[tuple[float, float, str]]) -> dict[str, str]:
    order: list[str] = []
    for _start, _end, speaker in sorted(turns, key=lambda item: item[0]):
        if speaker not in order:
            order.append(speaker)
    return {speaker: f"Голос {index + 1}" for index, speaker in enumerate(order)}


def _count(wav_path: Path, job_dir: Path) -> dict:
    turns: list[tuple[float, float, str]] = []
    try:
        turns = [(s, e, sp) for s, e, sp in _turns(wav_path) if e - s >= 0.3]
    except Exception:
        turns = []
    if not turns:
        length = _duration_seconds(wav_path)
        turns = [(0.0, length, "only")]
    names = _voice_names(turns)
    model = _model()
    piece = job_dir / "piece.wav"
    lines: list[dict] = []
    try:
        for start, end, speaker in turns:
            text = _transcribe_span(model, wav_path, start, end, piece)
            if not text:
                continue
            lines.append(
                {
                    "voice": names[speaker],
                    "start": round(start, 1),
                    "end": round(end, 1),
                    "text": text,
                }
            )
    finally:
        model = None
        _free()
    whole = " ".join(line["text"] for line in lines).strip()
    return {
        "text": whole,
        "voices": lines,
        "note": "Если шумно или люди говорят вместе, метки могут перепутать.",
    }


def _sweep_old_work() -> None:
    cutoff = time.time() - 2 * 60 * 60
    if not WORK.exists():
        return
    for path in WORK.iterdir():
        try:
            if path.stat().st_mtime < cutoff:
                if path.is_file():
                    path.unlink()
        except OSError:
            continue


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.on_event("startup")
def _startup() -> None:
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("PYANNOTE_METRICS_ENABLED", "false")
    WORK.mkdir(parents=True, exist_ok=True)
    _sweep_old_work()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "busy": _busy}


@app.post("/v1/transcribe")
async def transcribe(request: Request) -> dict:
    global _busy
    internal = _authorized(request)
    if not internal and not _web_access(request):
        raise HTTPException(status_code=401, detail="Сначала откройте 14 дней или введите семейный код.")
    if not internal and request.headers.get("x-speech-people") != "yes":
        raise HTTPException(status_code=400, detail="Сначала подтвердите, что люди в записи об этом знают.")
    if not _lock.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Сейчас считается другая запись. Подождите.")
    _busy = True
    job_id = uuid.uuid4().hex
    raw = WORK / f"{job_id}.bin"
    wav = WORK / f"{job_id}.wav"
    nbytes = 0
    try:
        with raw.open("wb") as handle:
            async for chunk in request.stream():
                nbytes += len(chunk)
                if nbytes > MAX_BYTES:
                    handle.close()
                    raw.unlink(missing_ok=True)
                    _journal(job_id, nbytes, not raw.exists())
                    raise HTTPException(status_code=413, detail="Файл слишком большой.")
                handle.write(chunk)
        if nbytes == 0:
            raise HTTPException(status_code=400, detail="Файл пустой.")
        try:
            incoming = _duration_seconds(raw)
        except Exception:
            incoming = 0.0
        if incoming > MAX_SECONDS + 1:
            raise HTTPException(status_code=413, detail="Файл длиннее часа.")
        try:
            _to_wav(raw, wav)
        except Exception:
            raise HTTPException(status_code=400, detail="Не получилось прочитать запись.")
        heard = _duration_seconds(wav)
        if heard < 0.3:
            raise HTTPException(status_code=400, detail="В записи нет звука.")
        if heard > MAX_SECONDS + 1:
            raise HTTPException(status_code=413, detail="Файл длиннее часа.")
        raw.unlink(missing_ok=True)
        result = _count(wav, WORK)
        gone = _wipe([raw, wav], job_id, nbytes)
        result["deleted"] = gone
        return result
    except HTTPException:
        _wipe([raw, wav, WORK / "piece.wav"], job_id, nbytes)
        raise
    except Exception:
        _wipe([raw, wav, WORK / "piece.wav"], job_id, nbytes)
        raise HTTPException(status_code=500, detail="Не получилось прочитать запись.")
    finally:
        _busy = False
        _lock.release()
