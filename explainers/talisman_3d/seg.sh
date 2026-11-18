# kb <src (image or video)> <dur> <z0> <z1> <cx> <cy> (in 1920x1080 coords of src scaled to 1920 width) <out> [cap start end]...
kb() {
  src=$1; dur=$2; z0=$3; z1=$4; cx=$5; cy=$6; out=$7; shift 7
  N=$(python3 -c "print(round($dur*30))")
  inputs=(); fc=""; i=1; last="base"
  if [[ $src == *.png || $src == *.jpg ]]; then inputs+=(-loop 1 -framerate 30 -t $dur -i $src); else inputs+=(-ss ${SS:-0} -t $dur -i $src); fi
  # smooth zoom: scale up large then crop with float expressions via zoompan on an 4x upscaled frame
  fc="[0:v]fps=30,scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,scale=7680:4320:flags=bicubic,zoompan=z='$z0+($z1-$z0)*on/$N':x='$cx*4-iw/zoom/2':y='$cy*4-ih/zoom/2':d=1:s=1920x1080:fps=30,setsar=1,drawbox=y=ih-175:w=iw:h=175:color=0x1F3240@0.55:t=fill[base];"
  while [[ $# -gt 0 ]]; do
    c=$1; a=$2; b=$3; shift 3
    inputs+=(-loop 1 -framerate 30 -t $dur -i $c)
    fc+="[$i:v]format=rgba,fade=t=in:st=$a:d=0.5:alpha=1,fade=t=out:st=$(python3 -c "print($b-0.4)"):d=0.4:alpha=1[c$i];[$last][c$i]overlay=0:0[o$i];"
    last="o$i"; i=$((i+1))
  done
  fc+="[$last]null[v]"
  ffmpeg -v error -y "${inputs[@]}" -filter_complex "$fc" -map "[v]" -frames:v $N -an -c:v libx264 -crf 16 -pix_fmt yuv420p $out
}
