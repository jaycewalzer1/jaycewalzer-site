Kusama is a painting medium I built as the ground floor of an RL environment for artistic judgment. An agent never outputs pixels. It writes a JSON program, a tree of typed nodes with no free code, and changes it only through eight kinds of bounded edits. p5 and p5.brush draw the program inside a pinned headless Chromium on software WebGL.

The point is determinism: under one pinned configuration, the same program renders to a byte-identical canonical.png. That makes runs replayable and rewards checkable. Every step goes into a hash-chained log, and a finished run replays byte for byte with the model unplugged, so scores can be rebuilt from the record alone. To get there, the renderer warms up until two frames agree and returns only once two consecutive renders hash the same.

For novelty, I embedded about 20,000 public-domain works from the Cleveland Museum of Art, the Met and the Art Institute of Chicago with CLIP. A painting's novelty is one minus its cosine to the nearest one.

In the demo, a second render in a fresh browser gave the same sha256, and 11 committed goldens check this on every test run.

stack: TypeScript, Node, p5.js, p5.brush, Playwright, headless Chromium, JSON Schema, CLIP (ONNX), Claude Sonnet (agent policy), Claude Opus (judge)
links: https://github.com/jaycewalzer1/kusama
