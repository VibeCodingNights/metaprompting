#!/usr/bin/env bash
# local.sh — install Ollama, pull Gemma 4, set up Python venv.
#
# 15–30 minutes. ~17GB download. Needs 16GB+ RAM.
# You own the model when this finishes. No rate limits, no data leaving the box.

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

cat <<'BANNER'

  ╭──────────────────────────────────────────────╮
  │  metaprompting · local setup                 │
  │  Gemma 4, your laptop, no rate limits.       │
  ╰──────────────────────────────────────────────╯

This installs Ollama if it's missing, pulls gemma4 (~17GB),
creates a Python venv, and runs verify.sh.

If your local setup is taking longer than 15 minutes, switch to
./setup/cloud.sh — both paths converge at verify.sh.

BANNER

# 1. Ollama
if ! command -v ollama >/dev/null 2>&1; then
  echo "Installing Ollama ..."
  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        brew install --cask ollama
      else
        echo "Homebrew not found. Download Ollama from https://ollama.com and rerun this script."
        exit 1
      fi
      ;;
    Linux)
      curl -fsSL https://ollama.com/install.sh | sh
      ;;
    *)
      echo "Unsupported OS. Install Ollama manually from https://ollama.com then rerun."
      exit 1
      ;;
  esac
else
  echo "Ollama already installed: $(ollama --version 2>/dev/null || true)"
fi

# 2. Make sure the daemon is up. Ollama starts on demand on macOS, but on
#    Linux you may need to launch the server in another shell.
if ! curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo
  echo "Ollama daemon doesn't appear to be running."
  echo "On macOS: open the Ollama app once."
  echo "On Linux: run 'ollama serve' in another terminal, then rerun this script."
  echo
  read -r -p "Press enter once it's running, or ctrl-C to bail. " _
fi

# 3. Pull Gemma 4
MODEL="${GEMMA_MODEL:-gemma4}"
echo
echo "Pulling $MODEL ..."
ollama pull "$MODEL"

# 4. Memory check + quantization fallback hint
TOTAL_GB=0
case "$(uname -s)" in
  Darwin)
    TOTAL_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
    TOTAL_GB=$(( TOTAL_BYTES / 1024 / 1024 / 1024 ))
    ;;
  Linux)
    TOTAL_KB=$(awk '/MemTotal/ {print $2}' /proc/meminfo 2>/dev/null || echo 0)
    TOTAL_GB=$(( TOTAL_KB / 1024 / 1024 ))
    ;;
esac

if [ "$TOTAL_GB" -gt 0 ] && [ "$TOTAL_GB" -lt 18 ]; then
  echo
  echo "⚠  Detected ~${TOTAL_GB}GB RAM. The full gemma4 may swap badly."
  echo "   Consider pulling a smaller quantization:"
  echo "       ollama pull gemma4:q4_K_M"
  echo "   Then re-run with:  GEMMA_MODEL=gemma4:q4_K_M ./setup/verify.sh"
fi

# 5. Python venv
if [ ! -d "$REPO_ROOT/.venv" ]; then
  echo "Creating Python venv at .venv"
  python3 -m venv "$REPO_ROOT/.venv"
fi

# shellcheck disable=SC1091
source "$REPO_ROOT/.venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$REPO_ROOT/setup/requirements.txt"

# Make sure local mode is selected (no GEMMA_API_BASE set).
unset GEMMA_API_BASE
unset GEMMA_API_KEY

echo
echo "Running verify.sh ..."
bash "$REPO_ROOT/setup/verify.sh"
