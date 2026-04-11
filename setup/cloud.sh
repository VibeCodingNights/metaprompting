#!/usr/bin/env bash
# cloud.sh — fast lane to Gemma 4 via a free hosted endpoint.
#
# Pick a provider, paste your API key, run verify.sh. ~2 minutes.
# No GPU. No 17GB download. Rate-limited but enough for one event.

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

cat <<'BANNER'

  ╭──────────────────────────────────────────────╮
  │  metaprompting · cloud setup                 │
  │  Gemma 4, hosted, free.                      │
  ╰──────────────────────────────────────────────╯

Pick a provider. All three serve Gemma 4 on a free tier as of the
event date. If one is rate-limited or down, try another.

  1) Google AI Studio    (recommended — generous limits)
  2) OpenRouter          (simple, free credits on signup)
  3) Groq                (fast, smaller free tier)

BANNER

read -r -p "Choose 1, 2, or 3: " choice

case "$choice" in
  1)
    PROVIDER="google-ai-studio"
    GEMMA_API_BASE="https://generativelanguage.googleapis.com/v1beta/openai/"
    SIGNUP_URL="https://aistudio.google.com/apikey"
    DEFAULT_MODEL="gemma-4-27b-it"
    ;;
  2)
    PROVIDER="openrouter"
    GEMMA_API_BASE="https://openrouter.ai/api/v1"
    SIGNUP_URL="https://openrouter.ai/keys"
    DEFAULT_MODEL="google/gemma-4-27b-it"
    ;;
  3)
    PROVIDER="groq"
    GEMMA_API_BASE="https://api.groq.com/openai/v1"
    SIGNUP_URL="https://console.groq.com/keys"
    DEFAULT_MODEL="gemma-4-27b-it"
    ;;
  *)
    echo "Unknown choice. Pick 1, 2, or 3 next time."
    exit 1
    ;;
esac

echo
echo "Provider: $PROVIDER"
echo "Get an API key here: $SIGNUP_URL"
echo
read -r -p "Paste your API key (input hidden): " -s GEMMA_API_KEY
echo

if [ -z "$GEMMA_API_KEY" ]; then
  echo "No key entered. Exiting."
  exit 1
fi

# Persist for the current shell + future shells via a dotfile fragment.
ENV_FILE="$REPO_ROOT/.env"
cat > "$ENV_FILE" <<EOF
# metaprompting cloud config — sourced by setup/verify.sh and the challenges
export GEMMA_API_BASE="$GEMMA_API_BASE"
export GEMMA_API_KEY="$GEMMA_API_KEY"
export GEMMA_MODEL="$DEFAULT_MODEL"
EOF

echo "Wrote $ENV_FILE"
echo "Source it with:  source $ENV_FILE"
echo

# Make the values available to the verify step in this shell.
export GEMMA_API_BASE
export GEMMA_API_KEY
export GEMMA_MODEL="$DEFAULT_MODEL"

# Python venv + deps.
if [ ! -d "$REPO_ROOT/.venv" ]; then
  echo "Creating Python venv at .venv"
  python3 -m venv "$REPO_ROOT/.venv"
fi

# shellcheck disable=SC1091
source "$REPO_ROOT/.venv/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$REPO_ROOT/setup/requirements.txt"

echo
echo "Running verify.sh ..."
bash "$REPO_ROOT/setup/verify.sh"
