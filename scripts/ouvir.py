"""Passos 1 e 2: baixa só o áudio da live, escuta tudo no computador e separa em blocos de 12 minutos.

Cada bloco vira um .txt com a fala e duas marcas:
  [ALTO +11dB]   o streamer ficou bem mais alto que o normal daquele trecho (grito, surto)
  [CHAT 3.4x]    no replay do YouTube, o chat andou 3,4 vezes mais rápido que o normal
"""
import json
import sys
import time
import wave
from pathlib import Path

import numpy as np

from comum import (BLOCO_MIN, TRABALHO, gravar_json, hms, ler_json, motivo_trancada, rodar, slug, ytdlp)


# ---------------------------------------------------------------- download
def baixar(url):
    print(f"\n[1/4] Lendo a live: {url}")
    import subprocess
    r = subprocess.run(ytdlp() + ["-J", "--no-playlist", "--no-warnings", url], capture_output=True, text=True)
    if r.returncode != 0:
        motivo = motivo_trancada(r.stderr)
        if motivo:
            sys.exit(f"\n  ✗ NÃO DÁ PRA BAIXAR: {motivo}.\n    Isso é trava do site, não erro do clipper. "
                     "Escolha outra live (rode 'clip.py buscar', que já pula as trancadas).")
        print(r.stderr[-1500:])
        sys.exit("\n  ✗ Não consegui ler essa live. Rode 'clip.py instalar' (atualiza o baixador) e tente de novo.")
    meta = json.loads(r.stdout)
    nome = slug(f"{meta.get('uploader') or meta.get('channel') or 'live'}-{meta.get('title', '')}")
    pasta = TRABALHO / nome
    pasta.mkdir(parents=True, exist_ok=True)
    info = {k: meta.get(k) for k in ("id", "title", "uploader", "channel", "duration", "view_count",
                                     "webpage_url", "extractor_key", "was_live", "live_status")}
    info["url"] = url
    gravar_json(pasta / "info.json", info)
    print(f"      {info['title']}  |  {info.get('uploader')}  |  {hms(info.get('duration') or 0)}")

    if not list(pasta.glob("audio.*")):
        print("      baixando só o áudio (uma live de 4h fica com algumas centenas de MB)…")
        rodar(ytdlp() + ["-f", "ba/b", "-x", "--no-playlist", "--no-warnings",
                         "-o", str(pasta / "audio.%(ext)s"), url])
    if (info.get("extractor_key") or "").lower().startswith("youtube") and not (pasta / "chat.feito").exists():
        print("      tentando o replay do chat (só existe em live que passou no YouTube)…")
        try:
            rodar(ytdlp() + ["--skip-download", "--write-subs", "--sub-langs", "live_chat", "--no-warnings",
                             "-o", str(pasta / "chat"), url], timeout=1200)
        except Exception as e:  # sem chat não é erro: só não tem a marca [CHAT]
            print(f"      sem replay de chat ({type(e).__name__})")
        (pasta / "chat.feito").write_text("ok")
    return pasta


def wav16k(pasta):
    w = pasta / "audio16k.wav"
    if not w.exists():
        audio = next(p for p in pasta.glob("audio.*"))
        rodar(["ffmpeg", "-y", "-loglevel", "error", "-i", audio, "-ac", "1", "-ar", "16000", w])
    return w


# ---------------------------------------------------------------- transcrição
def transcrever(pasta, modelo="base", idioma=None):
    saida = pasta / "transcricao.json"
    if saida.exists():
        return ler_json(saida)
    from faster_whisper import WhisperModel
    w = wav16k(pasta)
    dur = (pasta / "info.json").exists() and (ler_json(pasta / "info.json", {}).get("duration") or 0)
    print(f"\n[2/4] Escutando a live inteira aqui no computador (modelo {modelo})…")
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, inf = m.transcribe(str(w), language=idioma, vad_filter=True, beam_size=1,
                             condition_on_previous_text=False)
    out, t0, aviso = [], time.time(), 0
    for s in segs:
        out.append([round(s.start, 2), round(s.end, 2), s.text.strip()])
        if s.end - aviso > 300:
            aviso = s.end
            pct = f" ({100 * s.end / dur:.0f}%)" if dur else ""
            print(f"      {hms(s.end)}{pct} escutado em {time.time() - t0:.0f}s", flush=True)
    dados = {"idioma": inf.language, "segmentos": out}
    gravar_json(saida, dados)
    return dados


# ---------------------------------------------------------------- picos de volume
def picos_de_volume(pasta):
    saida = pasta / "volume.json"
    if saida.exists():
        return ler_json(saida)
    with wave.open(str(wav16k(pasta))) as f:
        sr, n = f.getframerate(), f.getnframes()
        a = np.frombuffer(f.readframes(n), dtype=np.int16).astype(np.float32)
    seg = len(a) // sr
    rms = np.sqrt(np.mean(a[: seg * sr].reshape(seg, sr) ** 2, axis=1) + 1e-6)
    db = 20 * np.log10(rms / 32768 + 1e-9)
    fala = db > np.percentile(db, 20)                       # ignora silêncio no cálculo da base
    base = np.zeros_like(db)
    for i in range(0, seg, 60):                             # "normal" = mediana dos 5 min em volta
        j0, j1 = max(0, i - 150), min(seg, i + 150)
        janela = db[j0:j1][fala[j0:j1]]
        base[i:i + 60] = np.median(janela) if len(janela) else np.median(db)
    excesso = db - base
    corte = max(8.0, float(np.percentile(excesso, 98)))
    picos = [[int(i), round(float(excesso[i]), 1)] for i in np.where(excesso >= corte)[0]]
    gravar_json(saida, picos)
    return picos


# ---------------------------------------------------------------- velocidade do chat
def picos_do_chat(pasta):
    arq = next(iter(pasta.glob("chat*.live_chat.json")), None)
    if not arq:
        return []
    tempos = []
    for linha in arq.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            ms = json.loads(linha)["replayChatItemAction"]["videoOffsetTimeMsec"]
            tempos.append(int(ms) / 1000)
        except (KeyError, ValueError, json.JSONDecodeError):
            continue
    if len(tempos) < 50:
        return []
    caixas = np.bincount((np.array(tempos) // 10).astype(int))   # mensagens a cada 10 s
    picos = []
    for i, c in enumerate(caixas):
        viz = caixas[max(0, i - 30): i + 30]
        normal = max(1.0, float(np.median(viz)))
        if c >= 8 and c / normal >= 2.5:
            picos.append([i * 10, round(c / normal, 1)])
    return picos


# ---------------------------------------------------------------- blocos de 12 min
def blocos(pasta, trans, volume, chat):
    pb = pasta / "blocos"
    pb.mkdir(exist_ok=True)
    (pasta / "momentos").mkdir(exist_ok=True)
    vol = dict((s, e) for s, e in volume)
    segs = trans["segmentos"]
    fim = segs[-1][1] if segs else 0
    passo = BLOCO_MIN * 60
    n = 0
    for k, ini in enumerate(range(0, int(fim) + 1, passo), start=1):
        linhas = []
        for s, e, t in segs:
            if not (ini <= s < ini + passo):
                continue
            marca = ""
            alto = max((vol.get(x, 0) for x in range(int(s), int(e) + 1)), default=0)
            if alto:
                marca += f"  [ALTO +{alto:.0f}dB]"
            ch = max((r for c, r in chat if s - 10 <= c <= e), default=0)
            if ch:
                marca += f"  [CHAT {ch}x]"
            linhas.append(f"[{hms(s)}] {t}{marca}")
        if not linhas:
            continue
        n += 1
        cab = (f"# BLOCO {k:02d} — de {hms(ini)} a {hms(ini + passo)}\n"
               f"# Escreva os momentos deste bloco em: momentos/bloco_{k:02d}.json\n\n")
        (pb / f"bloco_{k:02d}.txt").write_text(cab + "\n".join(linhas) + "\n", encoding="utf-8")
    return n


def preparar(url, modelo="base", idioma=None):
    pasta = baixar(url)
    trans = transcrever(pasta, modelo, idioma)
    print("\n[2/4] Marcando onde o streamer ficou alto e onde o chat acelerou…")
    volume = picos_de_volume(pasta)
    chat = picos_do_chat(pasta)
    n = blocos(pasta, trans, volume, chat)
    print(f"      {len(volume)} segundos de grito/surto, {len(chat)} picos de chat")
    print(f"\nPRONTO PRA ESCOLHER: {n} blocos em {pasta / 'blocos'}")
    print(f"Próximo: ler cada bloco e escrever {pasta / 'momentos'}/bloco_NN.json")
    return pasta
