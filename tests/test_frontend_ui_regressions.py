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


def test_settings_panels_have_loading_and_retry_instead_of_false_server_errors():
    model = read("edict/frontend/src/components/ModelConfig.tsx")
    skills = read("edict/frontend/src/components/SkillsConfig.tsx")
    store = read("edict/frontend/src/store.ts")
    assert "agentConfigLoading" in store
    assert "agentConfigError" in store
    assert "agentConfigInFlight" in store
    assert "fetchAgentConfigWithRetry" in store
    assert "loadModelChangeLogSafely" in store
    assert "正在加载模型配置" in model
    assert "模型配置加载失败" in model
    assert "正在加载技能配置" in skills
    assert "技能配置加载失败" in skills
    assert "请先启动本地服务器" not in model
    assert "return <div className=\"empty\">无法加载</div>;" not in skills
