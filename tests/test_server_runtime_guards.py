from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "dashboard" / "server.py"


def test_dashboard_uses_threading_http_server_for_concurrent_api_requests():
    src = SERVER.read_text(encoding="utf-8")
    assert "ThreadingHTTPServer" in src
    assert "server = ThreadingHTTPServer" in src


def test_dashboard_static_responses_disable_browser_cache():
    src = SERVER.read_text(encoding="utf-8")
    assert "Cache-Control" in src
    assert "no-store" in src
