#!/bin/zsh
# Kokopelli explainer = KokoCity (Manim 3D) + four real-footage segments + KokoStudy (Manim 2D), 0.5 s crossfades.
# Footage is the owner's existing artifacts (read only, no model was run for this):
#   out/filter_test/test_clip/rgb.mp4                         Unreal render of the footbridge walk (0-5 s)
#   out/city_wm/bridge/controls/832x480/{depth,seg,edge,blur_v2_high}.mp4   control videos, 2x2 grid
#   out/city_wm/bridge/final/bridge_unreal_vs_simtransfer.mp4  Unreal vs Cosmos3-Nano-Sim-Transfer (bf16, MLX, blur control)
#   site/assets/demo.mp4 (8-14 s)                              four agents' painted views
# Caption/label overlays: kokopelli_parts/overlays.json rendered with talisman_3d/ovl.py; segment helpers in talisman_3d/seg.sh.
M=~/Desktop/lecture-viz/.venv/bin/manim
$M -qh --fps 30 kokopelli.py KokoCity --media_dir build
$M -qh --fps 30 kokopelli.py KokoStudy --media_dir build
# then: python3 talisman_3d/xcat.py ../assets/video/kokopelli-explainer.mp4 KokoCity.mp4 kseg1.mp4 kseg2.mp4 kseg3.mp4 kseg4.mp4 KokoStudy.mp4
