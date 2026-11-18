At the Georgia Tech Research Institute I asked a narrow question: at a fixed search budget, does exploring candidate moves with different chess features help a small AlphaZero-style agent find correct moves that its own policy ranks low?

I trained a 5.6-million-parameter network in TensorFlow with supervised tactics, Monte Carlo tree search and self-play, then froze it and compared four ways of spending the same search budget: standard PUCT, quality-only, random, and feature-diverse allocation. The benchmark is 200 held-out forced-mate positions from 175 source families, graded by a forced-mate verifier I wrote that checks every legal defence. No chess engine or language model is used.

Feature-diverse search came out ahead at every budget: 32.5% against 29.0% at 1,024 simulations, and 41.5% against 35.0% at 3,072. But the 95% interval at the main budget, -1.5 to +8.8 points, includes zero, so the pre-registered verdict is inconclusive. The one interval that excludes zero is on positions the policy ranks outside its top three: +7.6 points over quality-only.

stack: Python, TensorFlow, MCTS, python-chess, bootstrap statistics
links: https://github.com/jaycewalzer1/ChessConceptDiscovery
