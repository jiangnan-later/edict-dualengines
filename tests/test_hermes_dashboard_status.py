"""Tests for Hermes runtime dashboard status behavior."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'dashboard'))
sys.path.insert(0, str(ROOT / 'scripts'))


def test_hermes_live_status_reports_connected_without_openclaw_sync(monkeypatch, tmp_path):
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    (data_dir / 'tasks_source.json').write_text(json.dumps([
        {
            'id': 'JJC-HERMES-001',
            'title': 'Hermes 状态验证',
            'state': 'Taizi',
            'org': '太子',
            'now': '等待太子接旨分拣',
            'heartbeat': {'status': 'idle', 'label': '待命'},
            'flow_log': [],
            'todos': [],
            'archived': False,
        }
    ], ensure_ascii=False), encoding='utf-8')
    (data_dir / 'live_status.json').write_text(json.dumps({
        'tasks': [],
        'syncStatus': {},
        'health': {'syncOk': False, 'syncLatencyMs': None, 'missingFieldCount': 0},
    }, ensure_ascii=False), encoding='utf-8')

    monkeypatch.setenv('EDICT_AGENT_RUNTIME', 'hermes')
    monkeypatch.setenv('HERMES_BIN', 'hermes')
    monkeypatch.setattr(srv, 'DATA', data_dir)
    monkeypatch.setattr(srv, '_ACTIVE_TASK_DATA_DIR', data_dir)
    monkeypatch.setattr(srv, 'resolve_runtime_binary', lambda cfg: '/usr/local/bin/hermes')

    status = srv.get_live_status_payload()

    assert status['health']['syncOk'] is True
    assert status['health']['runtime'] == 'hermes'
    assert status['health']['statusLabel'] == 'Hermes 模式在线'
    assert len(status['tasks']) == 1


def test_hermes_agents_status_uses_runtime_binary_not_openclaw_gateway(monkeypatch, tmp_path):
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    (data_dir / 'tasks_source.json').write_text('[]', encoding='utf-8')

    monkeypatch.setenv('EDICT_AGENT_RUNTIME', 'hermes')
    monkeypatch.setenv('HERMES_BIN', 'hermes')
    monkeypatch.setattr(srv, 'DATA', data_dir)
    monkeypatch.setattr(srv, '_ACTIVE_TASK_DATA_DIR', data_dir)
    monkeypatch.setattr(srv, 'resolve_runtime_binary', lambda cfg: '/usr/local/bin/hermes')

    status = srv.get_agents_status()

    assert status['gateway']['alive'] is True
    assert status['gateway']['runtime'] == 'hermes'
    assert status['gateway']['status'] == '🟢 Hermes 可用'
    assert status['agents']
    assert all(a['status'] in {'idle', 'running'} for a in status['agents'])
    assert all(a['statusLabel'] != '🔴 Gateway 离线' for a in status['agents'])
