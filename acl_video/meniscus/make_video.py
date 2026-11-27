import os, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = "id-ID-ArdiNeural"
W, H, FPS = 1920, 1080, 30

spec = importlib.util.spec_from_file_location("mscript", os.path.join(HERE, "script.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SCENES = mod.SCENES

for s in SCENES:
    audio = os.path.join(HERE, "audio", s["id"] + ".mp3")
    subprocess.run(["edge-tts", "--voice", VOICE, "--text", s["narration"],
                    "--write-media", audio], check=True)

    slide = os.path.join(HERE, "slides", s["id"] + ".png")
    clip = os.path.join(HERE, "clips", s["id"] + ".mp4")
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", audio], capture_output=True, text=True, check=True).stdout.strip())
    dur = max(dur + 0.6, 6.0)
    frames = int(dur * FPS)
    vf = (f"zoompan=z='1+0.0008*on':x='iw/2-(iw/zoom/2)':y='ih/4-(ih/zoom/4)':"
          f"d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", slide, "-i", audio,
           "-vf", vf, "-t", f"{dur:.2f}",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-c:a", "aac", "-b:a", "160k", "-shortest", clip]
    subprocess.run(cmd, check=True, capture_output=True)
    print("clip", clip, f"{dur:.1f}s")

concat = os.path.join(HERE, "clips", "concat.txt")
with open(concat, "w") as f:
    for s in SCENES:
        f.write(f"file '{os.path.join(HERE, 'clips', s['id'] + '.mp4')}'\n")

out = os.path.join(HERE, "video_cedera_meniskus.mp4")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat,
                "-c", "copy", out], check=True, capture_output=True)
print("video", out)
