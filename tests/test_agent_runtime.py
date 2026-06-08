"""Tests for Edict agent runtime adapters."""
from __future__ import annotations

import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def test_openclaw_dispatch_command_keeps_existing_cli_shape():
    from agent_runtime import AgentRuntimeConfig, build_dispatch_command

    cfg = AgentRuntimeConfig(runtime="openclaw", openclaw_bin="/usr/bin/openclaw")

    cmd = build_dispatch_command(cfg, agent_id="bingbu", message="处理任务", timeout=300)

    assert cmd == [
        "/usr/bin/openclaw",
        "agent",
        "--agent",
        "bingbu",
        "-m",
        "处理任务",
        "--timeout",
        "300",
    ]


def test_openclaw_dispatch_command_supports_delivery_channel():
    from agent_runtime import AgentRuntimeConfig, build_dispatch_command

    cfg = AgentRuntimeConfig(runtime="openclaw", openclaw_bin="openclaw")

    cmd = build_dispatch_command(
        cfg,
        agent_id="taizi",
        message="心跳",
        timeout=120,
        channel="feishu",
    )

    assert cmd[-3:] == ["--deliver", "--channel", "feishu"]


def test_hermes_dispatch_command_uses_chat_query_and_source():
    from agent_runtime import AgentRuntimeConfig, build_dispatch_command

    cfg = AgentRuntimeConfig(
        runtime="hermes",
        hermes_bin="/usr/local/bin/hermes",
        hermes_toolsets="terminal,file",
        hermes_max_turns=42,
    )

    cmd = build_dispatch_command(cfg, agent_id="gongbu", message="修复部署", timeout=300)

    assert cmd == [
        "/usr/local/bin/hermes",
        "chat",
        "-q",
        "修复部署",
        "--source",
        "edict",
        "--toolsets",
        "terminal,file",
        "--max-turns",
        "42",
        "--quiet",
    ]


def test_hermes_dispatch_command_can_select_profile_per_agent():
    from agent_runtime import AgentRuntimeConfig, build_dispatch_command

    cfg = AgentRuntimeConfig(
        runtime="hermes",
        hermes_bin="hermes",
        hermes_profile_mode=True,
    )

    cmd = build_dispatch_command(cfg, agent_id="menxia", message="审核", timeout=120)

    assert cmd[:3] == ["hermes", "--profile", "menxia"]
    assert cmd[3:6] == ["chat", "-q", "审核"]


def test_runtime_config_reads_environment(monkeypatch):
    from agent_runtime import AgentRuntimeConfig

    monkeypatch.setenv("EDICT_AGENT_RUNTIME", "hermes")
    monkeypatch.setenv("HERMES_BIN", "/opt/bin/hermes")
    monkeypatch.setenv("HERMES_PROFILE_MODE", "1")
    monkeypatch.setenv("HERMES_TOOLSETS", "terminal,file,web")
    monkeypatch.setenv("HERMES_MAX_TURNS", "77")

    cfg = AgentRuntimeConfig.from_env(os.environ)

    assert cfg.runtime == "hermes"
    assert cfg.hermes_bin == "/opt/bin/hermes"
    assert cfg.hermes_profile_mode is True
    assert cfg.hermes_toolsets == "terminal,file,web"
    assert cfg.hermes_max_turns == 77


def test_missing_runtime_binary_status_is_runtime_specific(monkeypatch):
    from agent_runtime import AgentRuntimeConfig, resolve_runtime_binary

    cfg = AgentRuntimeConfig(runtime="hermes", hermes_bin="definitely-not-hermes")

    assert resolve_runtime_binary(cfg) is None
