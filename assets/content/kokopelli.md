Kokopelli is an agent that lives inside a world model. A SimWorld city in Unreal holds the physical truth. Cosmos3-Nano-Sim-Transfer paints that sim into realistic video from its control videos (depth, segmentation, edges, blur). A Qwen3-VL-8B agent sees only that painted video, plus words for what its body feels ("you feel shaky and empty inside", never a number), decides, and its action lands back in the sim. Everything runs locally on Apple silicon.

The question behind it: does living through experience, with a LoRA updating the weights each night while the agent sleeps, shift a model differently than simply telling it the same facts? I'm testing that as a 5-arm study: the adapter trained on its own lives, the untrained model, the same model told every effect in its prompt, and two controls trained with the same code (one rewarded for more of everything, one with shuffled rewards).

The first 25-day lived run finished end to end: 99 decisions, 25 trained nights, MMLU unchanged at 75.0. Its honest result is that the choices mostly matched the untrained model's prior, so the next runs raise the sampling temperature and add flipped and shuffled arms to tell learning from prior.

stack: Python, MLX, Qwen3-VL-8B, Cosmos3-Nano, Unreal Engine (SimWorld), LoRA
links: https://github.com/jaycewalzer1/kokopelli, https://kokopelli-labs.com
