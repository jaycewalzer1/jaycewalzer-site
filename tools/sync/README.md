# Site sync

A daily job (06:00, or on wake if the Mac was asleep) that checks whether the resume on Overleaf or any of my GitHub repos changed, and if so starts a headless Claude Code run that updates the site, the write-ups and the videos, then pushes to `main`.

- `sync.py` is the detector and runner. Its docstring lists what counts as a change.
- `PROMPT.md` is what the agent is told to do.
- `local/` stays on this Mac: `state.json` (what the site was last synced against), `holds.md` (my standing decisions the agent must respect), `owed.json`, `reports/`.
- Log: `~/Library/Logs/jaycewalzer-site-sync.log`.

```
python3 tools/sync/sync.py --dry-run    # what would it act on right now
python3 tools/sync/sync.py              # run it now
python3 tools/sync/sync.py --selftest   # can it reach GitHub, Overleaf and claude
```

## Schedule

```
cp tools/sync/com.jaycewalzer.site-sync.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.jaycewalzer.site-sync.plist
launchctl bootout gui/$(id -u)/com.jaycewalzer.site-sync      # turn it off
```

## Overleaf access (one time)

The resume is read over Overleaf's git access, which needs a token only I can make:

1. Overleaf, Account settings, Git integration, "Generate token". Copy it.
2. In a terminal: `git -c credential.helper=osxkeychain ls-remote https://git.overleaf.com/64ecc81c0101605112ebff00`
   Username `git`, password the token. The keychain remembers it.

Until then the job still checks GitHub and says the resume was not checked.
