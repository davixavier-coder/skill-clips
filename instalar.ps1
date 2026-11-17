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
  Write-Host "Instalando o Python 3.12 (oficial, pelo winget)..."
  winget install -e --id Python.Python.3.12 --scope user --accept-source-agreements --accept-package-agreements
  Write-Host "FECHE e abra o PowerShell (ou o app do Claude) e rode este mesmo comando de novo."
  exit 1
}
$pre = $py.pre
& $py.exe @pre (Join-Path $dest "scripts\clip.py") instalar
