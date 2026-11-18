Reels Edits is a local dashboard I built for making short, beat-synced image edits with Claude Code. Claude pulls candidate images only from a whitelist of sites, I keep or reject every one in the dashboard, and the order I keep them in becomes the edit order. Claude never finalizes an edit with an image I haven't kept.

The renderer does the timing. It fits the track's tempo and first-beat offset with librosa, sizes the edit to a whole number of bars between 7 and 12 seconds so the music keeps its rhythm when the video loops, and cuts on a repeating pattern of sixteenth notes. Every image gets the same grade, and the last shot is the kept image closest in colour to the first, so the loop seam is hard to see. A checker then measures the finished video against the rules.

In the demo, with 12 public-domain paintings and a generated 124 BPM beat, it found 123.96 BPM and made 12 cuts in 6 bars over 11.63 seconds. The worst cut was 16 ms off the beat, and every check passed.

stack: Python, librosa, NumPy, Pillow, ffmpeg, Claude Code
links: https://github.com/jaycewalzer1/reels-edits
