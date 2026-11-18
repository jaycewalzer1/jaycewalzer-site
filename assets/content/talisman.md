Talisman is my research code for one question: how should AI bughouse teammates share time and computation between thinking, talking and moving?

Bughouse is chess for two teams of two on two boards. When you capture a piece it goes to your partner, who can drop it onto their own board as a move. Everyone is on a clock, and a checkmate or a flag on either board ends the game for both. So each turn is a choice: think longer, ask for a piece, or sit and wait for one while the clock runs.

I build on Hivemind, an AlphaZero-style bughouse engine. Before adding anything I fixed its baseline on macOS: a `-Ofast` finite-math flag was making search selection return nothing (24 nodes in 3 s); after the fix the C++ suite passes 296/296. On top, an arena runs four players on a shared simulated clock with partner messages (need, have, sit, go), and a small scheduler policy, trained with REINFORCE on team wins, decides around the frozen engine: move or wait, what to say, and how long to think. A 3D viewer replays every game.

stack: C++, Python, PyTorch, ONNX Runtime, Fairy-Stockfish, React, three.js, Vite
links: https://github.com/jaycewalzer1/talisman-bughouse-engine, https://github.com/jaycewalzer1/hivemind
