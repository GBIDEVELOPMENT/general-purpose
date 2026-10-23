#!/usr/bin/env bash
set -euo pipefail
# Local, opt-in environment setup. No hidden model fetch, media fetch, or credential use.
cd "$(dirname "$0")/.."
tier="${1:-acoustics}"
case "$tier" in
  acoustics|asr|diarization|emotion) ;;
  *) echo "Choose: acoustics | asr | diarization | emotion" >&2; exit 2 ;;
esac
python3 -m venv ".venv-vocal-$tier"
".venv-vocal-$tier/bin/python" -m pip install --upgrade pip
".venv-vocal-$tier/bin/python" -m pip install -r "tools/vocal-requirements-$tier.txt"
".venv-vocal-$tier/bin/python" -m pip freeze > ".venv-vocal-$tier/resolved-dependencies.txt"
echo "Installed $tier dependencies under the local ignored venv. No model weights downloaded."
echo "Evaluate the openSMILE license before use, especially outside noncommercial research."
