Talisman explainer (three.js clay scene + real footage/docs), built 2026-11-17.
- index.html: the 3D table scene, posed by setTime(t) (0-58 s). Needs `npm i three@0.160.0` beside it and the EB Garamond ttf files; serve the folder over http.
- render3d.py <url> frames <t0> <t1> <outdir>: Playwright frame render, 1920x1080 at 30 fps.
- kb.html + d1.url/d2.url: ken-burns over screenshots of notes.html / sched.html (verbatim excerpts of NOTES.md and docs/phase1_scheduler.md).
- seg.sh `kb`: ffmpeg push-in over the real viewer recording (talisman-demo source webm, 27-34 s) with caption PNGs from capimg.py.
- Cut: 3D 0-30 | viewer footage 7 s | 3D 30-52 | NOTES.md 8 s | scheduler doc 6.5 s | 3D 52-58, joined with xcat.py (0.5 s crossfades).
