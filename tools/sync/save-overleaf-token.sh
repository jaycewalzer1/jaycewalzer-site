#!/bin/sh
# Save an Overleaf Git token in the macOS keychain so sync.py can read the resume.
# Asks for the token in a macOS dialog (hidden), so it never passes through the clipboard
# history of a terminal command or a log. Make a token in Overleaf: Account settings, Git integration.
set -e
URL=https://git.overleaf.com/64ecc81c0101605112ebff00

token=$(osascript -e 'with timeout of 900 seconds' \
  -e 'text returned of (display dialog "Paste your Overleaf Git token (starts with olp_):" default answer "" with hidden answer with title "jaycewalzer.com sync" giving up after 840)' \
  -e 'end timeout')
token=$(printf %s "$token" | tr -d '[:space:]')
case "$token" in
  olp_*) ;;
  *) echo "That doesn't look like an Overleaf token (they start with olp_). Nothing saved." >&2; exit 1 ;;
esac

printf 'protocol=https\nhost=git.overleaf.com\nusername=git\n\n' | git credential-osxkeychain erase
printf 'protocol=https\nhost=git.overleaf.com\nusername=git\npassword=%s\n\n' "$token" | git credential-osxkeychain store

if GIT_TERMINAL_PROMPT=0 git -c credential.helper=osxkeychain ls-remote "$URL" HEAD >/dev/null 2>&1; then
  echo "Saved. Overleaf accepted the token."
else
  printf 'protocol=https\nhost=git.overleaf.com\nusername=git\n\n' | git credential-osxkeychain erase
  echo "Overleaf rejected that token, so it was not kept. Check you copied the newest one." >&2
  exit 1
fi
