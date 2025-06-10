import pytest
import cobrapinger
import sys
import json


def test_get_transcript_fallback_invoked(monkeypatch):
    def mock_fetch(video_id, retries=5, delay=2):
        raise Exception("boom")

    called = {}

    def mock_whisper(url):
        called['url'] = url
        return "hi"

    monkeypatch.setattr(cobrapinger, "fetch_via_api", mock_fetch)
    monkeypatch.setattr(cobrapinger, "transcribe_with_whisper", mock_whisper)

    result = cobrapinger.get_transcript("v1", "http://youtube.com/watch?v=v1")
    assert called['url'] == "http://youtube.com/watch?v=v1"
    assert result == "hi"


def test_transcribe_with_whisper_uses_model_path(monkeypatch, tmp_path):
    called = {}

    class DummyStream:
        def download(self, output_path):
            p = tmp_path / "a.webm"
            p.write_bytes(b"0")
            return str(p)

    class DummyYT:
        def __init__(self, url):
            pass

        @property
        def streams(self):
            return type("S", (), {"filter": lambda self, only_audio: [DummyStream()]})()

    class DummyModel:
        def __init__(self, name):
            called["model"] = name

        def transcribe(self, path):
            called["file"] = path
            return {"text": "ok"}

    def fake_run(cmd, check):
        assert cmd[0] == "ffmpeg"
        mp3_path = cmd[3]
        from pathlib import Path
        Path(mp3_path).write_bytes(b"1")
        return 0

    import types
    monkeypatch.setitem(sys.modules, "pytube", types.SimpleNamespace(YouTube=DummyYT))
    monkeypatch.setitem(sys.modules, "whisper", types.SimpleNamespace(load_model=lambda name: DummyModel(name)))
    monkeypatch.setattr(cobrapinger.os.path, "exists", lambda p: True)
    monkeypatch.setattr(cobrapinger.subprocess, "run", fake_run)
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"whisper_model_path": "/models/foo.pt"}))
    monkeypatch.setattr(cobrapinger, "CONFIG_FILE", str(cfg))
    cobrapinger.WHISPER_MODEL = None
    res = cobrapinger.transcribe_with_whisper("http://x")
    assert called["model"] == "/models/foo.pt"
    assert called["file"].endswith(".mp3")
    assert res == "ok"


def test_get_whisper_model_cached(monkeypatch, tmp_path):
    called = []

    class DummyModel:
        pass

    def load_model(name):
        called.append(name)
        return DummyModel()

    import types
    monkeypatch.setitem(sys.modules, "whisper", types.SimpleNamespace(load_model=load_model))
    monkeypatch.setattr(cobrapinger.os.path, "exists", lambda p: True)
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"whisper_model_path": "/cache/model.pt"}))
    monkeypatch.setattr(cobrapinger, "CONFIG_FILE", str(cfg))
    cobrapinger.WHISPER_MODEL = None

    m1 = cobrapinger.get_whisper_model()
    m2 = cobrapinger.get_whisper_model()

    assert m1 is m2
    assert called == ["/cache/model.pt"]


@pytest.mark.skip(reason="Requires network access to YouTube and Whisper model")
def test_whisper_fallback_integration():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # video with no captions
    result = cobrapinger.get_transcript("dQw4w9WgXcQ", url)
    assert result
