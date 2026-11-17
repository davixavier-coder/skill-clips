#!/usr/bin/env python3
"""Clipper do GTA 6: transforma lives longas em cortes verticais prontos pra postar.

Comandos:
  clip.py instalar                       confere e instala tudo que falta
  clip.py buscar [--quantas 7]           acha as maiores lives de GTA 6 de hoje no YouTube
  clip.py preparar LINK [LINK…]          baixa o áudio, escuta tudo e separa em blocos de 12 min
  clip.py escolher LIVE [--manter 3]     junta as notas e fica com os melhores momentos
  clip.py fazer LIVE                     monta os cortes (câmera em cima, jogo embaixo, legenda)
  clip.py status                         mostra em que passo cada live está
"""
import argparse
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from comum import CASA, CORTES, MODELOS, TRABALHO, YUNET, YUNET_URL, ffmpeg_embutido, hms, ler_json, pasta_da_live, tem  # noqa: E402

VENV = CASA / "ambiente"
VENV_PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PACOTES = ["faster-whisper", "opencv-python-headless", "numpy", "yt-dlp[default]", "certifi", "static-ffmpeg"]


def no_ambiente():
    """Roda sempre com o Python do próprio clipper, que o instalar cria."""
    if VENV_PY.exists() and Path(sys.prefix).resolve() != VENV.resolve() and sys.argv[1:2] != ["instalar"]:
        os.execv(str(VENV_PY), [str(VENV_PY), __file__, *sys.argv[1:]])


def instalar(_):
    print("Conferindo o que o computador precisa…\n")
    falta = []
    if sys.version_info < (3, 10):
        falta.append("python")
        print(f"  ✗ Python {sys.version.split()[0]} é antigo. Precisa do 3.10 ou mais novo.")
        if os.name == "nt":
            print("      Instale com:  winget install -e --id Python.Python.3.12 --scope user"
                  "   (depois feche e abra o terminal)")
        else:
            print("      Baixe o instalador oficial em https://www.python.org/downloads/ e abra o arquivo.")
    else:
        print(f"  ✓ Python {sys.version.split()[0]}")
    if "python" not in falta:
        if not VENV_PY.exists():
            print("  … criando o ambiente do clipper em", VENV)
            subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
        print("  … instalando pacotes:", ", ".join(PACOTES))
        subprocess.run([str(VENV_PY), "-m", "pip", "install", "-q", "--upgrade", "pip"], check=True)
        subprocess.run([str(VENV_PY), "-m", "pip", "install", "-q", "--upgrade", *PACOTES], check=True)
        print("  ✓ pacotes do Python")
        if tem("ffmpeg") and tem("ffprobe"):
            print("  ✓ ffmpeg")
        else:
            print("  … baixando o ffmpeg (programa que monta os vídeos, uma vez só)")
            r = subprocess.run([str(VENV_PY), "-c", "import sys,static_ffmpeg,shutil;static_ffmpeg.add_paths();"
                                "sys.exit(0 if shutil.which('ffmpeg') and shutil.which('ffprobe') else 1)"])
            if r.returncode == 0:
                print("  ✓ ffmpeg")
            else:
                falta.append("ffmpeg")
                print("  ✗ não consegui baixar o ffmpeg. Confira a internet e rode 'clip.py instalar' de novo.")
    if not YUNET.exists():
        print("  … baixando o detector de rosto (OpenCV YuNet, 0,2 MB)")
        MODELOS.mkdir(parents=True, exist_ok=True)
        if tem("curl"):  # Mac e Windows 10+ já vêm com curl (o Python do python.org às vezes não acha os certificados)
            subprocess.run(["curl", "-fsSL", "-o", str(YUNET), YUNET_URL], check=True)
        else:
            subprocess.run([str(VENV_PY), "-c", "import sys,ssl,certifi,urllib.request as u;"
                            "c=ssl.create_default_context(cafile=certifi.where());"
                            "open(sys.argv[2],'wb').write(u.urlopen(sys.argv[1],context=c).read())",
                            YUNET_URL, str(YUNET)], check=True)
    print("  ✓ detector de rosto")
    if "python" not in falta:
        print("  … baixando os modelos de escuta (base e small, uma vez só)")
        subprocess.run([str(VENV_PY), "-c", "from faster_whisper import WhisperModel as W; W('base'); W('small')"],
                       check=True)
        print("  ✓ modelos de escuta")
    for p in (TRABALHO, CORTES):
        p.mkdir(parents=True, exist_ok=True)
    if falta:
        print("\nFALTA:", ", ".join(falta), "— instale e rode 'clip.py instalar' de novo.")
        sys.exit(1)
    print(f"\nTUDO PRONTO. Os cortes vão sair em {CORTES}")


GTA6 = __import__("re").compile(r"gta\s*-?\s*(6|vi)(?![0-9a-z])", 2)
GTA5 = __import__("re").compile(r"gta\s*-?\s*(5|v|iv|4|rp)(?![0-9a-z])", 2)


def buscar(a):
    import json
    from comum import ytdlp
    # filtros oficiais da busca do YouTube: "Hoje" + "Mais de 20 minutos"
    filtro = "EgQIAhgC"
    vistos = {}
    for termo in a.termos:
        url = f"https://www.youtube.com/results?search_query={termo.replace(' ', '+')}&sp={filtro}"
        r = subprocess.run(ytdlp() + ["--flat-playlist", "-J", "--playlist-end", "40", "--no-warnings", url],
                           capture_output=True, text=True)
        try:
            itens = json.loads(r.stdout).get("entries", [])
        except json.JSONDecodeError:
            itens = []
        for v in itens:
            titulo = v.get("title") or ""
            if (v.get("id") and (v.get("duration") or 0) >= 30 * 60 and GTA6.search(titulo)
                    and not GTA5.search(titulo)):
                vistos[v["id"]] = v
    lista = sorted(vistos.values(), key=lambda v: -(v.get("view_count") or 0))[: a.quantas]
    if not lista:
        print("Não achei lives longas de GTA 6 publicadas hoje. Tente com um link direto.")
        return
    print(f"As {len(lista)} maiores lives de GTA 6 de hoje:\n")
    for i, v in enumerate(lista, 1):
        print(f"  {i}. {v.get('title')}\n     {v.get('channel') or v.get('uploader')} | "
              f"{hms(v.get('duration') or 0)} | {v.get('view_count') or 0:,} views\n"
              f"     https://www.youtube.com/watch?v={v['id']}\n".replace(",", "."))


def preparar(a):
    from ouvir import preparar as prep
    for link in a.links:
        prep(link, a.modelo, a.idioma)


def escolher(a):
    from cortar import escolher as esc
    esc(pasta_da_live(a.live), a.manter)


def fazer(a):
    from cortar import fazer as faz
    faz(pasta_da_live(a.live), a.modelo)


def status(_):
    if not TRABALHO.exists() or not any(TRABALHO.iterdir()):
        print("Nenhuma live ainda.")
        return
    for p in sorted(TRABALHO.iterdir()):
        if not p.is_dir():
            continue
        info = ler_json(p / "info.json", {})
        nb = len(list((p / "blocos").glob("bloco_*.txt")))
        nm = len(list((p / "momentos").glob("bloco_*.json")))
        esc = ler_json(p / "escolhidos.json", {}).get("cortes")
        prontos = len(list((CORTES / p.name).glob("corte_*.mp4")))
        print(f"{p.name}\n  {info.get('title', '')}\n  blocos lidos: {nm}/{nb} | escolhidos: "
              f"{len(esc) if esc else 0} | cortes prontos: {prontos}")


def certificados():
    """o Python do python.org (Mac) não acha os certificados sozinho: usa os do certifi"""
    try:
        import certifi
        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
        os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
    except ImportError:
        pass


def main():
    no_ambiente()
    certificados()
    ap = argparse.ArgumentParser(description="Clipper do GTA 6")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("instalar").set_defaults(f=instalar)
    b = sub.add_parser("buscar")
    b.add_argument("--quantas", type=int, default=7)
    b.add_argument("--termos", nargs="+", default=["GTA 6 live", "GTA 6 ao vivo", "GTA VI stream"])
    b.set_defaults(f=buscar)
    p = sub.add_parser("preparar")
    p.add_argument("links", nargs="+")
    p.add_argument("--modelo", default="base", help="modelo de escuta da live inteira (tiny é mais rápido)")
    p.add_argument("--idioma", default=None, help="pt, en… (vazio = detecta sozinho)")
    p.set_defaults(f=preparar)
    e = sub.add_parser("escolher")
    e.add_argument("live")
    e.add_argument("--manter", type=int, default=3)
    e.set_defaults(f=escolher)
    f = sub.add_parser("fazer")
    f.add_argument("live")
    f.add_argument("--modelo", default="small", help="modelo da legenda dos cortes")
    f.set_defaults(f=fazer)
    sub.add_parser("status").set_defaults(f=status)
    a = ap.parse_args()
    if a.f is not instalar:
        ffmpeg_embutido()
    a.f(a)


if __name__ == "__main__":
    main()
