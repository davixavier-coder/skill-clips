# Instala (ou atualiza) o Clipper do GTA 6 no Windows com um comando só (PowerShell):
#   irm https://raw.githubusercontent.com/davixavier-coder/skill-clips/main/instalar.ps1 | iex
$ErrorActionPreference = "Stop"
$dest = Join-Path $HOME ".claude\skills\clipper-gta6"
Write-Host "Baixando a skill pra $dest..."
New-Item -ItemType Directory -Force -Path $dest | Out-Null
$tgz = Join-Path $env:TEMP "skill-clips.tar.gz"
curl.exe -fsSL "https://github.com/davixavier-coder/skill-clips/archive/refs/heads/main.tar.gz" -o $tgz
tar.exe -xzf $tgz --strip-components=1 -C $dest
Write-Host "OK: skill no lugar"

$py = $null
$candidatos = @(@{exe = "py"; pre = @("-3")}, @{exe = "python"; pre = @()})
foreach ($c in $candidatos) {
  if (Get-Command $c.exe -ErrorAction SilentlyContinue) {
    $pre = $c.pre
    & $c.exe @pre -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $py = $c; break }
  }
}
if (-not $py) {
  # sem Python bom no computador: baixa um Python só pro clipper (uv, oficial da Astral), sem reiniciar o terminal
  Write-Host "... o computador nao tem Python 3.10+: baixando um Python so pro clipper (uma vez so)"
  $uvdir = Join-Path $HOME "clipper-gta6\uv"
  New-Item -ItemType Directory -Force -Path $uvdir | Out-Null
  $env:UV_INSTALL_DIR = $uvdir; $env:UV_NO_MODIFY_PATH = "1"; $env:INSTALLER_NO_MODIFY_PATH = "1"
  try {
    powershell -ExecutionPolicy Bypass -NoProfile -Command "irm https://astral.sh/uv/install.ps1 | iex" | Out-Null
    $uv = Join-Path $uvdir "uv.exe"
    if (Test-Path $uv) {
      & $uv python install 3.12 | Out-Null
      $achado = "$(& $uv python find 3.12)".Trim()
      if ($achado) { $py = @{exe = $achado; pre = @()} }
    }
  } catch { }
}
if (-not $py) {
  Write-Host "Instalando o Python 3.12 (oficial, pelo winget)..."
  winget install -e --id Python.Python.3.12 --scope user --accept-source-agreements --accept-package-agreements
  Write-Host "FECHE e abra o PowerShell (ou o app do Claude) e rode este mesmo comando de novo."
  exit 1
}
Write-Host "OK: Python encontrado"
$pre = $py.pre
& $py.exe @pre (Join-Path $dest "scripts\clip.py") instalar
