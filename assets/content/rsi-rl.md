RSI-RL is a self-improving factory for RL coding environments. It reads what developers complain about on X, keeps a failure mode only when a published paper backs it up, and stacks at least three independent modes into one Harbor task: a ticket, a starting repo and hidden tests.

Every task passes a seven-stage gate before it counts: shape, the reference solution scoring 1 in three runs, the untouched repo scoring 0, every mutation patch caught by a failing test, a red-team shortcut attempt, K cold attempts by a frontier agent, and a fairness check that each failed test maps to a ticket sentence. Calibration then holds the pass rate near 25%. A task everyone solves, or no one solves, teaches nothing; one that is solved some of the time gives a learning signal. Too easy adds a criterion from a fresh failure mode, too hard drops the case family most attempts miss.

The self-improving part: each calibrated task records which modes made solvers slip, and the next design samples modes from that history. It started from the six tasks I built at the Frist RL hackathon, where cold Opus 5.5 solved between 1 of 4 and 3 of 3.

stack: Python, Harbor, Docker, pytest, Claude (author, judge and solver models)
links: https://github.com/jaycewalzer1/rsi-rl-dev
