from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def test_court_ceremony_does_not_block_tab_clicks():
    src = read("edict/frontend/src/components/CourtCeremony.tsx")
    assert "pointerEvents: 'none'" in src or 'pointerEvents: "none"' in src
    assert "onClick={skip}" not in src


def test_edict_board_has_quick_decree_form():
    src = read("edict/frontend/src/components/EdictBoard.tsx")
    assert "quick-edict" in src
    assert "handleCreateEdict" in src
    assert "api.createTask" in src
    assert "快速下旨" in src


def test_create_task_payload_starts_at_taizi_for_quick_decree():
    src = read("edict/frontend/src/components/EdictBoard.tsx")
    assert "org: '太子'" in src
    assert "targetDept: quickDept" in src
    assert "templateId: 'quick-decree'" in src
