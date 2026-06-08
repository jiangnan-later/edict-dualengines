"""Agent runtime adapter helpers for Edict.

This module keeps Edict's scheduling and dashboard code independent from the
concrete agent CLI.  OpenClaw remains the default runtime; Hermes can be enabled
with ``EDICT_AGENT_RUNTIME=hermes``.
"""
from __future__ import annotations

from dataclasses import dataclass
from os import environ
from shutil import which
from typing import Mapping


_TRUE_VALUES = {"1", "true", "yes", "on", "y"}
_SUPPORTED_RUNTIMES = {"openclaw", "hermes"}


@dataclass(frozen=True)
class AgentRuntimeConfig:
    """Configuration for dispatching work to an agent runtime."""

    runtime: str = "openclaw"
    openclaw_bin: str = "openclaw"
    hermes_bin: str = "hermes"
    hermes_profile_mode: bool = False
    hermes_toolsets: str = ""
    hermes_max_turns: int = 90
    project_dir: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AgentRuntimeConfig":
        """Build runtime configuration from environment variables."""
        source = env if env is not None else environ
        return cls(
            runtime=source.get("EDICT_AGENT_RUNTIME", source.get("AGENT_RUNTIME", "openclaw")),
            openclaw_bin=source.get("OPENCLAW_BIN", "openclaw"),
            hermes_bin=source.get("HERMES_BIN", "hermes"),
            hermes_profile_mode=_parse_bool(source.get("HERMES_PROFILE_MODE", "0")),
            hermes_toolsets=source.get("HERMES_TOOLSETS", ""),
            hermes_max_turns=_parse_int(source.get("HERMES_MAX_TURNS"), default=90),
            project_dir=source.get("OPENCLAW_PROJECT_DIR") or source.get("EDICT_PROJECT_DIR"),
        ).normalized()

    def normalized(self) -> "AgentRuntimeConfig":
        runtime = (self.runtime or "openclaw").strip().lower()
        if runtime not in _SUPPORTED_RUNTIMES:
            raise ValueError(
                f"Unsupported agent runtime '{self.runtime}'. "
                f"Expected one of: {', '.join(sorted(_SUPPORTED_RUNTIMES))}"
            )
        return AgentRuntimeConfig(
            runtime=runtime,
            openclaw_bin=self.openclaw_bin or "openclaw",
            hermes_bin=self.hermes_bin or "hermes",
            hermes_profile_mode=bool(self.hermes_profile_mode),
            hermes_toolsets=(self.hermes_toolsets or "").strip(),
            hermes_max_turns=int(self.hermes_max_turns or 90),
            project_dir=self.project_dir,
        )

    @property
    def binary(self) -> str:
        return self.hermes_bin if self.runtime == "hermes" else self.openclaw_bin

    @property
    def missing_status(self) -> str:
        return f"{self.runtime}-missing"

    @property
    def display_name(self) -> str:
        return "Hermes" if self.runtime == "hermes" else "OpenClaw"


def _parse_bool(value: str | None) -> bool:
    return str(value or "").strip().lower() in _TRUE_VALUES


def _parse_int(value: str | None, default: int) -> int:
    try:
        return int(str(value).strip()) if value not in (None, "") else default
    except (TypeError, ValueError):
        return default


def resolve_runtime_binary(config: AgentRuntimeConfig | None = None) -> str | None:
    """Return the configured runtime executable if it can be found."""
    cfg = (config or AgentRuntimeConfig.from_env()).normalized()
    configured = cfg.binary.strip()
    if not configured:
        return None
    if "/" in configured or "\\" in configured:
        return configured if which(configured) or _path_exists(configured) else None
    return which(configured)


def _path_exists(path: str) -> bool:
    try:
        from pathlib import Path

        return Path(path).exists()
    except OSError:
        return False


def missing_binary_error(config: AgentRuntimeConfig) -> str:
    """Human-readable missing binary error for scheduler status."""
    cfg = config.normalized()
    if cfg.runtime == "hermes":
        return "Hermes CLI 未找到：请确认已安装 hermes 并加入 PATH；可设置 HERMES_BIN 指向 hermes 可执行文件"
    return "OpenClaw CLI 未找到：请确认已安装 openclaw 并加入 PATH；Windows 可设置 OPENCLAW_BIN 指向 openclaw.cmd"


def build_dispatch_command(
    config: AgentRuntimeConfig,
    agent_id: str,
    message: str,
    timeout: int = 300,
    channel: str = "",
) -> list[str]:
    """Build the CLI command for dispatching a message to an agent."""
    cfg = config.normalized()
    if cfg.runtime == "hermes":
        cmd = [cfg.hermes_bin]
        if cfg.hermes_profile_mode:
            cmd.extend(["--profile", agent_id])
        cmd.extend(["chat", "-q", message, "--source", "edict"])
        if cfg.hermes_toolsets:
            cmd.extend(["--toolsets", cfg.hermes_toolsets])
        if cfg.hermes_max_turns:
            cmd.extend(["--max-turns", str(cfg.hermes_max_turns)])
        cmd.append("--quiet")
        return cmd

    cmd = [
        cfg.openclaw_bin,
        "agent",
        "--agent",
        agent_id,
        "-m",
        message,
        "--timeout",
        str(timeout),
    ]
    if channel:
        cmd.extend(["--deliver", "--channel", channel])
    return cmd
