#!/usr/bin/env bash
# Publish the Expository *application only* to a dedicated GitHub Pages repository.
# Usage: bash tools/expository/publish-pages.sh [owner/repo]
set -euo pipefail

TARGET="${1:-gamesbyian/Expository}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$SCRIPT_DIR/index.html"
MARKER=".expository-managed"
MARKER_TEXT="Expository static app-only deployment. Do not add private repository contents."

die(){ printf 'Expository publish: %s\n' "$*" >&2; exit 1; }
command -v gh >/dev/null || die 'GitHub CLI (gh) is required; run gh auth login first.'
command -v git >/dev/null || die 'git is required.'
[[ -f "$SOURCE" ]] || die 'index.html is missing.'
[[ "$TARGET" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]] || die 'Expected owner/repo.'
[[ "${2:-}" == "" ]] || die 'Expected zero or one argument.'

gh auth status >/dev/null 2>&1 || die 'Authenticate with gh auth login.'
OWNER="${TARGET%%/*}"
NAME="${TARGET#*/}"
printf '\nEXPOSITORY PUBLIC DEPLOYMENT\n'
printf '  Source: %s\n' "$SOURCE"
printf '  Destination: https://github.com/%s (PUBLIC)\n' "$TARGET"
printf '  Website: https://%s.github.io/%s/\n' "$OWNER" "$NAME"
printf '  Published app files: index.html, .nojekyll, %s\n' "$MARKER"
printf '  Never published: other general-purpose files, private manifests, secrets or tokens.\n\n'

# Explicit public-export confirmation. Do not permit unattended automation to
# publish a private repository's source tree by accident.
[[ -t 0 ]] || die 'Run interactively to confirm the public export.'
read -r -p "Type PUBLISH to continue: " ANSWER
[[ "$ANSWER" == "PUBLISH" ]] || die 'Cancelled; no GitHub changes made.'

TMP="$(mktemp -d)"
trap 'rm -rf -- "$TMP"' EXIT
if gh repo view "$TARGET" >/dev/null 2>&1; then
  VISIBILITY="$(gh repo view "$TARGET" --json visibility --jq '.visibility')"
  [[ "$VISIBILITY" == "PUBLIC" ]] || die 'Existing target is not public; refusing an implicit visibility change.'
  gh repo clone "$TARGET" "$TMP/repo" -- --quiet >/dev/null
  [[ -f "$TMP/repo/$MARKER" ]] || die 'Existing repository is not marked as Expository-managed; refusing to modify it.'
  [[ "$(cat "$TMP/repo/$MARKER")" == "$MARKER_TEXT" ]] || die 'Unexpected management marker; refusing to modify it.'
  [[ -z "$(git -C "$TMP/repo" status --porcelain)" ]] || die 'Deployment checkout has uncommitted changes.'
  cp -- "$SOURCE" "$TMP/repo/index.html"
  git -C "$TMP/repo" add -- index.html
  if git -C "$TMP/repo" diff --cached --quiet; then
    echo 'App unchanged; no commit required.'
  else
    git -C "$TMP/repo" -c user.name='Expository Publisher' -c user.email='expository-publisher@users.noreply.github.com' commit -m 'Update Expository app-only deployment' >/dev/null
    git -C "$TMP/repo" push origin HEAD >/dev/null
  fi
else
  mkdir -p "$TMP/repo"
  cp -- "$SOURCE" "$TMP/repo/index.html"
  printf '%s\n' "$MARKER_TEXT" > "$TMP/repo/$MARKER"
  touch "$TMP/repo/.nojekyll"
  git -C "$TMP/repo" init -b main >/dev/null
  git -C "$TMP/repo" add -- index.html "$MARKER" .nojekyll
  git -C "$TMP/repo" -c user.name='Expository Publisher' -c user.email='expository-publisher@users.noreply.github.com' commit -m 'Publish standalone Expository app' >/dev/null
  gh repo create "$TARGET" --public --source "$TMP/repo" --remote origin --push
fi

# Enable Pages for the dedicated deployment repository, never the private source.
if ! gh api "repos/$TARGET/pages" --silent >/dev/null 2>&1; then
  gh api -X POST "repos/$TARGET/pages" \
    -f 'source[branch]=main' -f 'source[path]=/' >/dev/null \
    || die "App pushed, but Pages setup failed. Enable Pages manually in $TARGET Settings → Pages."
fi
printf '\nExpository published from a static-only repository.\n'
printf 'Check Pages deployment status at https://github.com/%s/deployments\n' "$TARGET"
