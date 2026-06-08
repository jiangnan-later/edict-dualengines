"""Tests for dashboard config fallbacks in Hermes mode."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'dashboard'))
sys.path.insert(0, str(ROOT / 'scripts'))


def test_hermes_agent_config_fallback_when_config_file_empty(monkeypatch, tmp_path):
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    (data_dir / 'agent_config.json').write_text('{}', encoding='utf-8')

    monkeypatch.setenv('EDICT_AGENT_RUNTIME', 'hermes')
    monkeypatch.setenv('HERMES_BIN', 'hermes')
    monkeypatch.setattr(srv, 'DATA', data_dir)

    payload = srv.get_agent_config_payload()

    assert payload['runtime'] == 'hermes'
    assert payload['defaultModel']
    assert payload['knownModels']
    assert len(payload['agents']) == 11
    assert all(agent['model'] == payload['defaultModel'] for agent in payload['agents'])
    assert all(agent['skills'] for agent in payload['agents'])
    first_skill = payload['agents'][0]['skills'][0]
    assert {'name', 'description', 'path', 'source'} <= set(first_skill)
    assert first_skill['source'] == 'hermes'


def test_hermes_officials_stats_fallback_when_stats_file_empty(monkeypatch, tmp_path):
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    (data_dir / 'officials_stats.json').write_text('{}', encoding='utf-8')
    (data_dir / 'tasks_source.json').write_text(json.dumps([
        {'id': 'JJC-1', 'title': '测试任务', 'state': 'Taizi', 'org': '太子'}
    ], ensure_ascii=False), encoding='utf-8')

    monkeypatch.setenv('EDICT_AGENT_RUNTIME', 'hermes')
    monkeypatch.setattr(srv, 'DATA', data_dir)
    monkeypatch.setattr(srv, '_ACTIVE_TASK_DATA_DIR', data_dir)

    payload = srv.get_officials_stats_payload()

    assert payload['officials']
    assert len(payload['officials']) == 11
    assert payload['totals']['tasks_done'] == 0
    taizi = next(o for o in payload['officials'] if o['id'] == 'taizi')
    assert taizi['tasks_active'] == 1
    assert taizi['heartbeat']['status'] == 'active'
