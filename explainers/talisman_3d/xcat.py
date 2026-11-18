import sys, subprocess, json
out, files = sys.argv[1], sys.argv[2:]
X = 0.5
durs = [float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode()) for f in files]
args = []; [args.extend(["-i", f]) for f in files]
fc = ""; prev = "[0:v]"; off = 0
for i in range(1, len(files)):
    off += durs[i-1] - X
    lab = f"[x{i}]"
    fc += f"{prev}[{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}{lab};"
    prev = lab
fc = fc.rstrip(";")
subprocess.check_call(["ffmpeg","-v","error","-y",*args,"-filter_complex",fc,"-map",prev,"-r","30","-c:v","libx264","-crf","27","-preset","slow","-pix_fmt","yuv420p","-movflags","+faststart",out])
