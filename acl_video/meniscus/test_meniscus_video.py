import os
import subprocess
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))


def load_module():
    spec = importlib.util.spec_from_file_location(
        "meniscus_script", os.path.join(HERE, "script.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_script_has_six_scenes_with_narration():
    m = load_module()
    assert len(m.SCENES) == 6
    for s in m.SCENES:
        assert s["id"] and s["title"]
        assert len(s["narration"]) > 100, s["id"]
        assert os.path.exists(os.path.join(HERE, "img", s["image"])), s["id"]


def test_cta_contact_details_present():
    m = load_module()
    assert "0853-7084-1555" in m.FOOTER
    for s in m.SCENES:
        if s["id"] == "06_cta":
            text = " ".join(s["bullets"])
            assert "Ftr. Sayed" in text
            assert "0853-7084-1555" in text
            assert "Fisioterapi Kajhu" in text


def test_slides_and_narration_files_exist():
    m = load_module()
    for s in m.SCENES:
        assert os.path.exists(os.path.join(HERE, "audio", s["id"] + ".mp3")), s["id"]
        slide = os.path.join(HERE, "slides", s["id"] + ".png")
        assert os.path.exists(slide), s["id"]


def test_final_video_exists_and_is_full_hd():
    m = load_module()
    ids = "+".join(s["id"] for s in m.SCENES)
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,codec_type,width,height:format=duration",
         "-of", "default=noprint_wrappers=1",
         os.path.join(HERE, "video_cedera_meniskus.mp4")],
        capture_output=True, text=True, check=True).stdout
    assert "width=1920" in out and "height=1080" in out, ids
    assert "codec_name=h264" in out and "codec_name=aac" in out
    assert float(out.split("duration=")[1].split()[0]) > 120
