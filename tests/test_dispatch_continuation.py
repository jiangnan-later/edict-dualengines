"""Tests for automatic dispatch continuation after state updates."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'dashboard'))
sys.path.insert(0, str(ROOT / 'scripts'))


def test_scheduler_scan_dispatches_state_that_has_not_been_dispatched(monkeypatch, tmp_path):
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    task_id = 'JJC-AUTO-001'
    task = {
        'id': task_id,
        'title': '自动续派测试',
        'state': 'Zhongshu',
        'org': '中书省',
        'now': '太子已转中书',
        'updatedAt': '2026-06-07T18:00:00+08:00',
        '_scheduler': {
            'lastDispatchStatus': 'success',
            'lastDispatchAgent': 'taizi',
            'lastDispatchTrigger': 'imperial-edict',
        },
        'flow_log': [],
    }
    (data_dir / 'tasks_source.json').write_text(json.dumps([task], ensure_ascii=False), encoding='utf-8')

    monkeypatch.setattr(srv, 'DATA', data_dir)
    monkeypatch.setattr(srv, '_ACTIVE_TASK_DATA_DIR', data_dir)
    calls = []
    monkeypatch.setattr(srv, 'dispatch_for_state', lambda task_id, task, state, trigger='': calls.append((task_id, state, trigger)))

    result = srv.scan_and_recover_dispatch_gaps(threshold_sec=60)

    assert result['count'] == 1
    assert calls == [(task_id, 'Zhongshu', 'state-dispatch-gap')]


def test_scheduler_tick_includes_dispatch_gap_scan(monkeypatch, tmp_path):
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    task_id = 'JJC-AUTO-002'
    task = {
        'id': task_id,
        'title': '自动续派测试',
        'state': 'Zhongshu',
        'org': '中书省',
        'now': '太子已转中书',
        'updatedAt': '2026-06-07T18:00:00+08:00',
        '_scheduler': {
            'lastDispatchStatus': 'success',
            'lastDispatchAgent': 'taizi',
            'lastDispatchTrigger': 'imperial-edict',
            'lastProgressAt': '2026-06-07T18:00:00+08:00',
            'retryCount': 0,
            'maxRetry': 2,
        },
        'flow_log': [],
    }
    (data_dir / 'tasks_source.json').write_text(json.dumps([task], ensure_ascii=False), encoding='utf-8')

    monkeypatch.setattr(srv, 'DATA', data_dir)
    monkeypatch.setattr(srv, '_ACTIVE_TASK_DATA_DIR', data_dir)
    calls = []
    monkeypatch.setattr(srv, 'dispatch_for_state', lambda task_id, task, state, trigger='': calls.append((task_id, state, trigger)))
    monkeypatch.setattr(srv, 'wake_agent', lambda *args, **kwargs: None)

    result = srv.handle_scheduler_tick(threshold_sec=600)

    assert result['ok'] is True
    assert result['dispatchGap']['count'] == 1
    assert calls == [(task_id, 'Zhongshu', 'state-dispatch-gap')]


def test_dispatch_gap_scan_respects_failed_dispatch_cooldown(monkeypatch, tmp_path):
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    task_id = 'JJC-AUTO-003'
    task = {
        'id': task_id,
        'title': '失败冷却测试',
        'state': 'Taizi',
        'org': '太子',
        'now': '等待太子接旨分拣',
        'updatedAt': '2026-06-07T18:00:00+08:00',
        '_scheduler': {
            'lastDispatchStatus': 'gateway-offline',
            'lastDispatchAgent': 'taizi',
            'lastDispatchState': 'Taizi',
            'lastDispatchTrigger': 'state-dispatch-gap',
            'lastDispatchAt': srv.now_iso(),
        },
        'flow_log': [],
    }
    (data_dir / 'tasks_source.json').write_text(json.dumps([task], ensure_ascii=False), encoding='utf-8')

    monkeypatch.setattr(srv, 'DATA', data_dir)
    monkeypatch.setattr(srv, '_ACTIVE_TASK_DATA_DIR', data_dir)
    calls = []
    monkeypatch.setattr(srv, 'dispatch_for_state', lambda *args, **kwargs: calls.append(args))

    result = srv.scan_and_recover_dispatch_gaps(threshold_sec=60)

    assert result['count'] == 0
    assert calls == []


def test_dispatch_gap_scan_skips_inflight_state(monkeypatch, tmp_path):
    import server as srv

    data_dir = tmp_path / 'data'
    data_dir.mkdir()
    task_id = 'JJC-AUTO-004'
    task = {
        'id': task_id,
        'title': '派发中防重测试',
        'state': 'Zhongshu',
        'org': '中书省',
        'now': '中书省已接旨',
        'updatedAt': '2026-06-07T18:00:00+08:00',
        '_scheduler': {
            'lastDispatchStatus': 'queued',
            'lastDispatchAgent': 'zhongshu',
            'lastDispatchState': 'Zhongshu',
            'lastDispatchTrigger': 'state-dispatch-gap',
            'lastDispatchAt': srv.now_iso(),
        },
        'flow_log': [],
    }
    (data_dir / 'tasks_source.json').write_text(json.dumps([task], ensure_ascii=False), encoding='utf-8')

    monkeypatch.setattr(srv, 'DATA', data_dir)
    monkeypatch.setattr(srv, '_ACTIVE_TASK_DATA_DIR', data_dir)
    calls = []
    monkeypatch.setattr(srv, 'dispatch_for_state', lambda *args, **kwargs: calls.append(args))

    result = srv.scan_and_recover_dispatch_gaps(threshold_sec=0)

    assert result['count'] == 0
    assert calls == []


def test_dashboard_defaults_to_hermes_runtime(monkeypatch):
    import server as srv

    monkeypatch.delenv('EDICT_AGENT_RUNTIME', raising=False)
    monkeypatch.delenv('AGENT_RUNTIME', raising=False)

    assert srv._get_agent_runtime_config().runtime == 'hermes'
