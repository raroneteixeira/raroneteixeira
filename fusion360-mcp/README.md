# Conectar o Claude ao Fusion 360 via MCP

Este guia instala o **[Fusion 360 MCP Bridge](https://github.com/ndoo/fusion360-mcp-bridge)** (projeto open-source, licença MIT), que permite ao Claude controlar o Autodesk Fusion 360 por linguagem natural: criar sketches, extrusões, montagens, exportar arquivos e capturar screenshots do viewport.

## Como funciona

```
Claude (Code/Desktop) ⇄ Servidor MCP (Python, stdio) ⇄ Add-in do Fusion (HTTP local, porta 7654) ⇄ API do Fusion 360
```

O servidor MCP roda no seu computador e conversa com um add-in instalado dentro do Fusion 360. A comunicação é local e protegida por um segredo compartilhado gerado automaticamente (`~/.fusion-mcp-secret`).

Ferramentas expostas ao Claude:

- **`fusion_execute`** — executa qualquer script Python dentro do Fusion com acesso completo à API `adsk.*` (criar geometria, modificar, exportar etc.)
- **`fusion_screenshot`** — captura o viewport ativo como imagem PNG

## Pré-requisitos

- Autodesk Fusion 360 instalado (licença pessoal gratuita serve)
- Python 3.9 ou superior
- Git
- Claude Desktop e/ou Claude Code (CLI)

## Instalação

### Windows

Abra o **PowerShell** e rode:

```powershell
git clone -b claude/fusion-360-mcp-connection-gjr5k3 https://github.com/raroneteixeira/raroneteixeira.git
cd raroneteixeira\fusion360-mcp
powershell -ExecutionPolicy Bypass -File .\instalar-windows.ps1
```

### macOS

Abra o **Terminal** e rode:

```bash
git clone -b claude/fusion-360-mcp-connection-gjr5k3 https://github.com/raroneteixeira/raroneteixeira.git
cd raroneteixeira/fusion360-mcp
bash instalar-mac.sh
```

O script faz tudo: baixa o bridge, cria o ambiente Python, gera o segredo, instala o add-in no Fusion e registra o servidor MCP no Claude Code (`claude mcp add`) e no Claude Desktop (`claude_desktop_config.json`).

## Depois de instalar (obrigatório)

1. Abra o **Fusion 360** → aba **Utilities** → **Add-Ins** → **Scripts and Add-Ins**
2. Na aba **Add-Ins**, selecione **FusionMCPBridge** → clique em **Run** (marque **Run on Startup** para ativar sempre)
3. Reinicie o **Claude Desktop** (feche completamente e abra de novo) ou abra o **Claude Code** no terminal
4. Teste pedindo ao Claude: *"tire um screenshot do viewport do Fusion 360"*

## Solução de problemas

| Problema | Solução |
|---|---|
| Claude não lista as ferramentas `fusion_*` | Reinicie o Claude Desktop por completo (bandeja do sistema → Quit). No Claude Code, rode `claude mcp list` para conferir se `fusion360` aparece. |
| Erro de conexão ao usar as ferramentas | Confira se o add-in **FusionMCPBridge** está rodando dentro do Fusion (passo 1 acima) e se o Fusion está aberto. |
| Porta 7654 ocupada | Defina outra porta com a variável de ambiente `FUSION_MCP_PORT` (no add-in e no servidor). |
| `python` não encontrado (Windows) | Reinstale o Python marcando **"Add python.exe to PATH"**. |

## Observação de segurança

O `fusion_execute` roda scripts Python arbitrários dentro do Fusion 360. Use apenas com o add-in oficial deste bridge e mantenha o arquivo `~/.fusion-mcp-secret` privado — é ele que impede que outros processos locais enviem comandos ao Fusion.
