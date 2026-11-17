#!/bin/bash
# Instala (ou atualiza) o Clipper do GTA 6 no Mac/Linux com um comando só:
#   curl -fsSL https://raw.githubusercontent.com/davixavier-coder/skill-clips/main/instalar.sh | bash
set -e
DEST="$HOME/.claude/skills/clipper-gta6"
echo "Baixando a skill pra $DEST…"
mkdir -p "$DEST"
curl -fsSL https://github.com/davixavier-coder/skill-clips/archive/refs/heads/main.tar.gz \
  | tar -xz --strip-components=1 -C "$DEST"
echo "✓ skill no lugar"

PY=""
for c in /Library/Frameworks/Python.framework/Versions/3.1[0-9]/bin/python3 python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo ""
  echo "✗ FALTA O PYTHON (3.10 ou mais novo). Abrindo o site oficial…"
  echo "  Clica em 'Download Python', abre o arquivo e vai em Continuar, Concordar e Instalar."
  echo "  Depois rode este mesmo comando de novo."
  command -v open >/dev/null && open https://www.python.org/downloads/
  exit 1
fi
"$PY" "$DEST/scripts/clip.py" instalar
