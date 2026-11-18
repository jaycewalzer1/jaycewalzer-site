# Brief for project workers (jaycewalzer.com)

You are producing, for each project you were assigned, three things for Jayce Walzer's portfolio site:

1. **Explanation** — `assets/content/<slug>.md`. 120–200 words, plain language, first person ("I built…") is fine since it's Jayce's site. What it is, why it matters, how it works, the one real result. Then a line `stack: …` and a line `links: <repo url>[, <live url>]`. Every fact must come from the repo (README, docs, code, results files) or from `~/Downloads/Jayce_Walzer_Resume.pdf`. Never invent numbers, users, outcomes or personal details. If something is unknown, leave it out.

2. **Demo video** — `assets/video/<slug>-demo.mp4`. A real recording of the real project running: 20–60 s, 1920x1080 or 1280x720, H.264, no audio needed, under ~12 MB (`ffmpeg -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -movflags +faststart`).
   - Web apps: run locally and record with Playwright video (`record_video_dir`), driving a short realistic path. Python: `uv run --with playwright python script.py` (Chromium is already installed under `~/Library/Caches/ms-playwright`; if a version mismatch, `uv run --with playwright==1.49.0`).
   - CLI / research code: run a small real command, then show its real outputs (figures, tables, logs). Recording a terminal: render the actual captured output into a video (e.g. a Playwright page that types out the real log, or ffmpeg drawtext over real output). Never fake output.
   - Also save a poster frame `assets/video/<slug>-demo.jpg`.
   - If a project truly cannot run (needs paid cloud, private keys, a GPU cluster), say so in your report and make the demo from the project's real artifacts (screenshots/figures/results in the repo, panned in order). Say plainly which you did.

3. **Explainer video** — 3Blue1Brown-style Manim animation, `assets/video/<slug>-explainer.mp4`, 40–90 s.
   - Write `explainers/<slug>.py`, `from style import *`, subclass `Explainer` (see `explainers/style.py` and the finished example `explainers/concept_discovery.py` — copy its structure: `title_card()`, animated diagram of the core mechanism, captions via `self.say()`, real numbers, `closing()`).
   - Colors only from style.py (BG, INK, MUTED, SEA, DRIFT, GOLD, CORAL); text only via `T()` / `I()`; font sizes ≥ 24.
   - Render from `explainers/`: `~/Desktop/lecture-viz/.venv/bin/manim -qh --fps 30 <slug>.py <Scene> --media_dir build`, then copy the mp4 to `assets/video/<slug>-explainer.mp4`.
   - The scene prints `LAYOUT PROBLEMS` if text overlaps / goes off frame — fix until none. Then check frames yourself: `ffmpeg -i X.mp4 -vf "fps=1/5,scale=480:-1,tile=4x3" -frames:v 1 sheet.jpg` and Read the sheet. Fix anything unreadable, overlapping or empty.
   - Explain the actual mechanism with shapes/graphs, not slides of bullet text.

## Style update (from Jayce, overrides the 3b1b-only direction above)
Don't lean hard on the 3Blue1Brown look: it's played out. Mix it up, and don't make every explainer the same. Take cues from **Fern** (YouTube documentary channel: slow camera moves through 3D scenes and models, real footage and documents intercut, calm editorial pacing, few words on screen at once), and use 3D where it helps:
- **3D**: Manim `ThreeDScene` with real camera moves (orbit, dolly, push-in), or a three.js scene rendered frame by frame with Playwright. A working three.js render pipeline lives in `~/Desktop/stonehenge-reel` (`index.html` poses everything from `setTime(t)`; `render.mjs` renders frames; read it, copy the approach into your scratch dir, don't modify it). Matte, clay-like materials in the palette colours, soft light, fog — no glossy default materials, no rainbow colours.
- **Real material intercut**: actual screenshots, terminal output, figures, code, the project's own UI — panned or pushed in on slowly, ken-burns style, between animated sections.
- **2D diagrams** still fine where they're the clearest way to show the mechanism, but vary layouts; avoid bullet-text slides and avoid the "black background + yellow equation" default look.
- Keep it coherent with the site: palette from `explainers/style.py` (less washed than the site), EB Garamond for type (`explainers/fonts/`), captions sparse and short. Final output still `assets/video/<slug>-explainer.mp4`, 1080p, 30 fps, 40–90 s.
- Pick per project the style that explains it best (e.g. a world-model city or a chess board suits 3D; a data pipeline may suit footage + diagram). Say in your report which style you used.

## Rules
- Paths: site is `~/Desktop/jaycewalzer-site`. Clone repos with `gh repo clone jaycewalzer1/<repo> <your scratch dir>/<repo>` (use the scratch dir in your prompt), never inside the site folder. Some repos are already cloned under `~/code/archive/` — copy, don't modify those.
- Do not commit, push, open PRs, or modify any repo on GitHub. Do not edit files outside your scratch dir except your own outputs in the site folder listed above.
- Python: `uv` with a `.venv`. Node: pnpm if the project uses it.
- Memory: this machine also runs kokopelli jobs and a memory guard. Never kill or touch kokopelli processes. Keep at most one heavy process (docker, Manim render, model) at a time per worker. Before Docker or anything over ~4 GB, check `vm_stat`/`memory_pressure`; skip if pressure is high.
- Never enter real credentials. Use test/mock modes, seed data, `.env.example` values, or local-only fakes. If a service needs real keys (AWS, Stripe live, Plaid, DocuSign), don't attempt it; use mocks or the artifact fallback.
- Ports: avoid 8787, 8790, 8798, 8811, 9001, 9005 (in use).
- Report back: for each project — what the demo shows and whether it is a live recording or an artifact fallback; explainer duration; any model/weights used; anything that failed or was skipped. Plainly.
