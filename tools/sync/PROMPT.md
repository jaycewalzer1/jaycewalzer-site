# Site sync run (jaycewalzer.com)

You are running unattended, started by a weekly schedule. Nobody is watching and nobody can answer questions, so never wait for input: decide, do the work, and write down what you decided. Your working directory is the site repo, `~/Desktop/jaycewalzer-site`, which is live at https://jaycewalzer.com (GitHub Pages builds from `main`).

A detector found changes to Jayce's resume or GitHub projects since the site was last synced. The list is under "This run" at the end. Your job is to bring the site up to date with those changes and nothing else: text, the resume PDF, and the demo and explainer videos where a change makes them wrong or missing.

## How the site is built

- `site.json` holds the project list, jobs, proof points, skills and honors. `assets/content/<slug>.md` is each entry's write-up. `python3 tools/build.py` renders `index.html` from those plus `tools/template.html`, and picks up `assets/video/<slug>-demo.mp4` (+ `.jpg`) and `<slug>-explainer.mp4` (+ `.jpg`) when they exist.
- Never edit `index.html` by hand; the build overwrites it. Don't change `tools/template.html`, the design, the photos or the layout in this run.
- `explainers/BRIEF.md` is the rulebook for write-ups, demo recordings and explainer videos. Read it before making or changing any of them, and follow it, including its "Style update" section.

## What to do with each kind of change

Read the repo before deciding. Clone or update a read-only copy under `tools/sync/local/repos/<name>` (`gh repo clone jaycewalzer1/<name> tools/sync/local/repos/<name> -- --filter=blob:none`, or `git fetch` if it is there). Use what is pushed to GitHub, not the working copies elsewhere on this Mac, which may hold unpushed work. For a changed repo, `since_sha` is the commit the site last matched: read `git log since_sha..HEAD` and the diff of the README, docs and results files.

- **Changed repo that is on the site.** Update the write-up, hook, tag, links and stack only where a fact the site states is now wrong or a real new result landed. Most commits change nothing the site says; then leave it alone and say so in the report. Re-record the demo only if what it shows no longer matches the project. Re-render the explainer only if a number or mechanism it shows is now wrong; change the scene file in `explainers/` and render it again rather than starting over.
- **Changed repo that is not on the site.** Decide whether it has become a project worth showing (see next item). Usually not.
- **New repo.** Add it only if it is public, not a fork, and a real project: a README, working code, something to show. Skip scratch repos, coursework, config, and empty or near-empty repos, and say why in the report. When you add one: an entry at the end of `projects` in `site.json` with `"featured": false`, its write-up, a demo and an explainer, all per `explainers/BRIEF.md`. Jayce chooses what is featured; don't reorder or promote.
- **Private repos** are never added and never linked. Name them in the report so Jayce can decide.
- **Repo removed, renamed or made private.** Fix or drop links that now 404. Leave the project's entry on the site and flag it in the report.
- **Description or homepage changed.** Check the site's links and one-liners against it.
- **Resume changed.** `resume.path` is a clone of the Overleaf project. If `since_sha` is set, `git diff since_sha HEAD` there is exactly what changed; apply those changes to the matching places in `site.json` and `assets/content/job-*.md`. If `first_sync` is true there is no earlier version: the site was built from `tools/sync/local/resume-baseline.pdf`, so compare the LaTeX against that PDF's text and apply only the differences. Either way, the site deliberately differs from the resume in places (see the holds below, and entries that exist only on the site), so never rebuild site text wholesale from the resume. Then rebuild the PDF: copy the `.tex` to a scratch dir, apply the holds, compile with `latexmk -pdf`, check it is still one page and reads correctly, and replace `assets/Jayce_Walzer_Resume.pdf`. The phone number stays in the PDF and stays off the page.
- **Owed.** Items an earlier run could not finish. Try them again.

## Rules

- Every fact on the site comes from a repo (README, docs, code, results files) or the resume. Never invent numbers, users, outcomes or personal details. If you are unsure whether something is true or wanted, leave the site as it is and put the question in the report.
- The standing holds below are Jayce's decisions. They win over the resume and the repos.
- Videos use real material: real recordings, real output, real figures. No code-drawn stick figures, clip art or filler visuals.
- This Mac also runs kokopelli GPU jobs and a memory guard. Never kill or disturb those processes. Before a Manim render, a browser recording, Docker or anything heavy, check `memory_pressure` and `ps` for running kokopelli jobs; if memory is tight, don't start it. One heavy process at a time.
- Never enter real credentials anywhere. Don't commit or push to any repo except this one. Don't modify the clones under `tools/sync/local/repos`.
- If something can't be finished this run (memory too tight to render, a project that won't run), do the parts you can and record the rest in `tools/sync/local/owed.json`: a JSON list of `{"what": "...", "since": "YYYY-MM-DD", "attempts": n}`. Raise `attempts` on items you retried and failed again; drop an item after 3 attempts and say so in the report. Remove items you finished. Write `[]` when nothing is owed.

## Publish

If you changed anything on the site:

1. `python3 tools/build.py`, then check the result: `index.html` contains the new or changed entries, every video it references exists and plays (`ffprobe`), and for a new or re-rendered video, look at a contact sheet of its frames as BRIEF.md describes.
2. `git pull --rebase origin main`, commit only the files this run changed with a plain message saying what changed and why, and `git push origin main`.
3. Open each new or re-rendered video with `open` so Jayce sees it.

If nothing needed changing, don't commit.

## Report

Write the report to the path given under "This run", in plain language, short:

- what changed on the site, per project or resume section, and the commit hash (so one `git revert` undoes it);
- what you looked at and deliberately left alone, one line each;
- what was skipped, failed or is now owed, stated as plainly as what worked;
- questions for Jayce, if any;
- which Claude model ran this, and any other model or weights used in a demo or render.

End the report with a line that is exactly `STATUS: done` when every listed change was either handled, deliberately left alone, or recorded in `owed.json`. If the run broke in a way that means these same changes should be handed to the next run again, end with `STATUS: failed` and the reason.
