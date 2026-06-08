"""Tests for Chinese morning news mode."""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))


def test_chinese_display_language_prefers_chinese_feeds():
    import fetch_morning_news as news

    feeds = news.get_feeds_for_language('zh-CN')

    assert feeds['政治'][0][0].startswith('BBC中文')
    assert any('chinanews' in url for _, url in feeds['经济'])
    assert any(name == '量子位' for name, _ in feeds['AI大模型'])


def test_default_morning_config_uses_chinese_display(monkeypatch, tmp_path):
    sys.path.insert(0, str(ROOT / 'dashboard'))
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    monkeypatch.setattr(srv, 'DATA', data_dir)

    cfg = srv.get_morning_config_payload()

    assert cfg['display_language'] == 'zh-CN'
    assert any(c['name'] == '政治' and c['enabled'] for c in cfg['categories'])
