Kusama Studio is the second version of Kusama. Instead of a hand-built medium, a frozen vision-language model directs a frozen image model. Qwen3-VL-8B-Instruct reads a reference packet and the current image, then proposes one concrete change and its expected effect. FLUX.2-klein-base-4B generates or edits the image. Nothing is trained, and both run locally on a 36 GB M4 Max, one after the other to fit in memory.

Every proposal, mask, image, hash and cost is saved with its parent, so each work carries a lineage tree. Model choices and human judgments are stored apart, and only a person advances a work.

The clearest result is a scale experiment. Qwen directed shrinking a hiker to one-third size. FLUX repaired a patch of 1.65% of the image, none of the 1,031,297 protected pixels changed, and the measured height ratio was 0.3365. Asked whether the smaller figure changed the feeling of vastness, the human reviewer said yes. Qwen's first unguided edit was less clear: the reviewer wasn't sure it felt any more vast.

stack: Python, PyTorch (MPS), Diffusers, Transformers, FastAPI, SQLite
links: https://github.com/jaycewalzer1/Kusama_v2
