import os, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SLIDES = os.path.join(HERE, "slides")
ANIM = os.path.join(HERE, "anim")
CLIPS = os.path.join(HERE, "clips")
os.makedirs(CLIPS, exist_ok=True)

W, H, FPS = 2160, 3840, 30
spec = importlib.util.spec_from_file_location("sc", os.path.join(HERE, "script.py"))
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


def dur_of(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return float(out)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-2000:])


def render_scene(scene, scene_index):
    audio = os.path.join(HERE, "audio", f"{scene['id']}.mp3")
    adur = dur_of(audio)
    dur = adur + 0.7
    frames = int(dur * FPS)
    ov = os.path.join(SLIDES, f"{scene['id']}_overlay.png")
    out = os.path.join(CLIPS, f"{scene['id']}.mp4")
    fade = f"fade=t=in:st=0:d=0.6:alpha=1"
    slide = f"overlay=0:y='260*(1-min(1,t/0.6))':format=auto"
    if scene.get("image"):
        bg = os.path.join(SLIDES, f"{scene['id']}_bg.png")
        direction = ["in", "out", "right", "in", "left", "out", "in", "out"][scene_index % 8]
        if direction == "in":
            z = f"z='1+0.08*min(1,on/{frames})':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
        elif direction == "out":
            z = f"z='1.08-0.08*min(1,on/{frames})':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
        elif direction == "right":
            z = f"z='1.12':x='(iw-iw/zoom)*min(1,on/{frames})':y='(ih-ih/zoom)/2'"
        else:
            z = f"z='1.12':x='(iw-iw/zoom)*(1-min(1,on/{frames}))':y='(ih-ih/zoom)/2'"
        cam = (f"zoompan={z}:d=1:s={W}x{H}:fps={FPS}")
        fc = (f"[0:v]{cam}[bg];[1:v]{fade}[ov];"
              f"[bg][ov]{slide}[v]")
        cmd = ["ffmpeg", "-y", "-loop", "1", "-t", f"{dur}", "-i", bg,
               "-loop", "1", "-t", f"{dur}", "-i", ov, "-i", audio,
               "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
               "-t", f"{dur}", "-r", str(FPS),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out]
    else:
        # animated anatomy frames (1080x1920) upscaled, gentle zoom, overlay on top
        cam = (f"zoompan=z='1+0.05*min(1,on/{frames})':x='(iw-iw/zoom)/2':"
               f"y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={FPS}")
        fc = (f"[0:v]{cam}[bg];[1:v]{fade}[ov];[bg][ov]{slide}[v]")
        cmd = ["ffmpeg", "-y", "-framerate", "25", "-i", os.path.join(ANIM, "f%04d.png"),
               "-loop", "1", "-t", f"{dur}", "-i", ov, "-i", audio,
               "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
               "-t", f"{dur}", "-r", str(FPS),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", out]
    run(cmd)
    return out


def main():
    parts = []
    for i, s in enumerate(sc.SCENES):
        clip = render_scene(s, i)
        parts.append(clip)
        print("clip", s["id"], round(dur_of(clip), 2), flush=True)
    lst = os.path.join(CLIPS, "concat.txt")
    with open(lst, "w") as f:
        for p in parts:
            f.write(f"file '{os.path.abspath(p)}'\n")
    silent = os.path.join(CLIPS, "video_silent.mp4")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", silent])
    total = dur_of(silent)
    # narration already embedded per clip; just add soft music bed
    music = os.path.join(HERE, "audio", "music.wav")
    run(["ffmpeg", "-y", "-f", "lavfi", "-i",
         "aevalsrc=0.10*sin(2*PI*220*t)+0.08*sin(2*PI*330*t)+0.06*sin(2*PI*440*t+0.7)"
         ":s=44100:d=120", "-ac", "1", music])
    final = os.path.join(HERE, "video_nyeri_lutut.mp4")
    run(["ffmpeg", "-y", "-i", silent, "-i", music,
         "-filter_complex",
         f"[1:a]volume=0.05,afade=t=in:d=2,afade=t=out:st={total-2:.2f}:d=2[m];"
         "[0:a][m]amix=inputs=2:normalize=0[aout]",
         "-map", "0:v", "-map", "[aout]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final])
    print("final", final, round(dur_of(final), 2), flush=True)


if __name__ == "__main__":
    main()
