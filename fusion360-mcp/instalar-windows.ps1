# Instalador do Fusion 360 MCP Bridge (Windows)
# Instala o servidor MCP + add-in do Fusion 360 e registra no Claude Code / Claude Desktop.
$ErrorActionPreference = "Stop"

$RepoUrl = "https://github.com/ndoo/fusion360-mcp-bridge.git"
$InstallDir = Join-Path $HOME "fusion360-mcp-bridge"
$AddinDir = Join-Path $env:APPDATA "Autodesk\Autodesk Fusion 360\API\AddIns"
$SecretFile = Join-Path $HOME ".fusion-mcp-secret"

Write-Host "==> Instalando Fusion 360 MCP Bridge..."

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git não encontrado. Instale em https://git-scm.com/download/win e rode este script de novo."
}
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python não encontrado (necessário 3.9+). Instale em https://www.python.org/downloads/ marcando 'Add python.exe to PATH'."
}

# 1. Clonar ou atualizar o repositório do bridge
if (Test-Path (Join-Path $InstallDir ".git")) {
    Write-Host "==> Atualizando instalação existente..."
    git -C $InstallDir pull --ff-only
} else {
    git clone $RepoUrl $InstallDir
}

# 2. Ambiente virtual Python + dependências
python -m venv (Join-Path $InstallDir ".venv")
$VenvPython = Join-Path $InstallDir ".venv\Scripts\python.exe"
& $VenvPython -m pip install --quiet --upgrade pip
& $VenvPython -m pip install --quiet -r (Join-Path $InstallDir "mcp-server\requirements.txt")

# 3. Segredo compartilhado entre o add-in e o servidor MCP
if (-not (Test-Path $SecretFile)) {
    $secret = python -c "import secrets; print(secrets.token_hex(32))"
    Set-Content -Path $SecretFile -Value $secret -Encoding ascii
    Write-Host "==> Segredo gerado em $SecretFile"
}

# 4. Instalar o add-in no Fusion 360
New-Item -ItemType Directory -Force -Path $AddinDir | Out-Null
Copy-Item -Recurse -Force (Join-Path $InstallDir "fusion-addin\FusionMCPBridge") $AddinDir
Write-Host "==> Add-in copiado para: $AddinDir\FusionMCPBridge"

# 5. Registrar o servidor MCP no Claude
$Server = Join-Path $InstallDir "mcp-server\server.py"

if (Get-Command claude -ErrorAction SilentlyContinue) {
    claude mcp remove fusion360 --scope user 2>$null | Out-Null
    claude mcp add --scope user fusion360 -- $VenvPython $Server
    Write-Host "==> Registrado no Claude Code."
}

$ConfigDir = Join-Path $env:APPDATA "Claude"
if (Test-Path $ConfigDir) {
    $ConfigPath = Join-Path $ConfigDir "claude_desktop_config.json"
    $pyMerge = @'
import json, os, sys
cfg_path, py, server = sys.argv[1], sys.argv[2], sys.argv[3]
cfg = {}
if os.path.exists(cfg_path):
    try:
        with open(cfg_path) as f:
            cfg = json.load(f)
    except ValueError:
        cfg = {}
cfg.setdefault("mcpServers", {})["fusion360"] = {"command": py, "args": [server]}
with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)
print("==> Registrado no Claude Desktop:", cfg_path)
'@
    $pyMerge | & $VenvPython - $ConfigPath $VenvPython $Server
}

Write-Host ""
Write-Host "✅ Instalação concluída! Próximos passos:"
Write-Host "  1. Abra o Fusion 360 → aba Utilities → Add-Ins → Scripts and Add-Ins"
Write-Host "  2. Na aba Add-Ins, selecione 'FusionMCPBridge' → Run (marque 'Run on Startup')"
Write-Host "  3. Reinicie o Claude Desktop (ou abra o Claude Code no terminal)"
Write-Host "  4. Teste pedindo ao Claude: 'tire um screenshot do viewport do Fusion 360'"
