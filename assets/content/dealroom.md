DealRoom is a synthetic deal environment for testing and training tool-using language models. An agent has to close a fictional transaction: gather evidence, get authority, draft the right amendment, collect signatures on that exact revision before the deadline, commit to proceed or cancel, and report what happened. It works through seven typed tools, and a plausible explanation, an informal agreement or an unsigned draft does not count.

A deterministic Python verifier scores the final state: authority, signatures, deadlines, buyer constraints and the structured final claims, with no LLM judge. Inspect AI runs the agent loop, and a local React research console shows model results, trajectories step by step, and grading.

On 48 generated scenarios, Qwen3 8B passed 13 of 32 scored tasks and Llama 3.1 8B passed 1 of 46. Budget limits stay unscored, so the two cover different subsets. I then trained Llama with supervised fine-tuning and with SFT followed by RL; each passed the same 2 of 64 held-out tasks, so RL added no measured gain.

stack: Python, Inspect AI, Ollama, MLX LoRA, React, TypeScript
links: https://github.com/jaycewalzer1/DealRoom
