import os, sys, importlib.util, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_script_has_8_scenes_with_cta():
    sc = load("knee_script", os.path.join(HERE, "script.py"))
    assert len(sc.SCENES) == 8
    cta = sc.SCENES[-1]
    assert "PRAKTEK FISIOTERAPI KAJHU" in cta["title"]
    assert cta["instagram"] == "@ftr.sayed" and cta["tiktok"] == "@ftr.sayed"
    assert "0853-7084-1555" in cta["subtitle"]


def test_assets_exist():
    sc = load("knee_script2", os.path.join(HERE, "script.py"))
    for s in sc.SCENES:
        assert os.path.exists(os.path.join(HERE, "audio", f"{s['id']}.mp3")), s["id"]
        assert os.path.exists(os.path.join(HERE, "slides", f"{s['id']}_bg.png")), s["id"]
        assert os.path.exists(os.path.join(HERE, "slides", f"{s['id']}_overlay.png")), s["id"]


def test_anatomy_frames_present():
    anim = os.path.join(HERE, "anim")
    frames = [f for f in os.listdir(anim) if f.endswith(".png")]
    assert len(frames) >= 150


def test_final_video_specs():
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_name,codec_type,width,height",
         "-of", "json", os.path.join(HERE, "video_nyeri_lutut.mp4")],
        capture_output=True, text=True)
    import json
    info = json.loads(out.stdout)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in info["streams"] if s["codec_type"] == "audio"][0]
    assert (v["width"], v["height"]) == (2160, 3840)
    assert v["codec_name"] == "h264" and a["codec_name"] == "aac"
    assert 55 <= float(info["format"]["duration"]) <= 65
