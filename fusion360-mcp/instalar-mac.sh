#!/usr/bin/env bash
# Instalador do Fusion 360 MCP Bridge (macOS)
# Instala o servidor MCP + add-in do Fusion 360 e registra no Claude Code / Claude Desktop.
set -euo pipefail

REPO_URL="https://github.com/ndoo/fusion360-mcp-bridge.git"
INSTALL_DIR="$HOME/fusion360-mcp-bridge"
ADDIN_DIR="$HOME/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns"
SECRET_FILE="$HOME/.fusion-mcp-secret"

echo "==> Instalando Fusion 360 MCP Bridge..."

command -v git >/dev/null || { echo "ERRO: git não encontrado. Rode: xcode-select --install"; exit 1; }
command -v python3 >/dev/null || { echo "ERRO: python3 não encontrado (necessário Python 3.9+)."; exit 1; }

# 1. Clonar ou atualizar o repositório do bridge
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "==> Atualizando instalação existente..."
  git -C "$INSTALL_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

# 2. Ambiente virtual Python + dependências
python3 -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/pip" install --quiet --upgrade pip
"$INSTALL_DIR/.venv/bin/pip" install --quiet -r "$INSTALL_DIR/mcp-server/requirements.txt"

# 3. Segredo compartilhado entre o add-in e o servidor MCP
if [ ! -f "$SECRET_FILE" ]; then
  python3 -c "import secrets; print(secrets.token_hex(32))" > "$SECRET_FILE"
  chmod 600 "$SECRET_FILE"
  echo "==> Segredo gerado em $SECRET_FILE"
fi

# 4. Instalar o add-in no Fusion 360
mkdir -p "$ADDIN_DIR"
cp -R "$INSTALL_DIR/fusion-addin/FusionMCPBridge" "$ADDIN_DIR/"
echo "==> Add-in copiado para: $ADDIN_DIR/FusionMCPBridge"

# 5. Registrar o servidor MCP no Claude
PYTHON_BIN="$INSTALL_DIR/.venv/bin/python"
SERVER="$INSTALL_DIR/mcp-server/server.py"

if command -v claude >/dev/null; then
  claude mcp remove fusion360 --scope user >/dev/null 2>&1 || true
  claude mcp add --scope user fusion360 -- "$PYTHON_BIN" "$SERVER"
  echo "==> Registrado no Claude Code."
fi

CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -d "$(dirname "$CONFIG")" ]; then
  python3 - "$CONFIG" "$PYTHON_BIN" "$SERVER" <<'EOF'
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
EOF
fi

echo ""
echo "✅ Instalação concluída! Próximos passos:"
echo "  1. Abra o Fusion 360 → aba Utilities → Add-Ins → Scripts and Add-Ins"
echo "  2. Na aba Add-Ins, selecione 'FusionMCPBridge' → Run (marque 'Run on Startup')"
echo "  3. Reinicie o Claude Desktop (ou abra o Claude Code no terminal)"
echo "  4. Teste pedindo ao Claude: 'tire um screenshot do viewport do Fusion 360'"
