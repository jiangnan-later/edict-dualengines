# Hermes / OpenClaw 双运行时适配

Edict 默认保持 OpenClaw 运行时不变，同时支持通过环境变量切换到 Hermes Agent。

## 运行时选择

```bash
# 默认：OpenClaw
export EDICT_AGENT_RUNTIME=openclaw

# 切换：Hermes
export EDICT_AGENT_RUNTIME=hermes
```

## OpenClaw 配置

```bash
export OPENCLAW_BIN=openclaw
export OPENCLAW_PROJECT_DIR=/path/to/edict
```

Dashboard / DispatchWorker 会继续生成如下命令：

```bash
openclaw agent --agent <agent_id> -m "<message>" --timeout 300
```

如果配置了 `dispatchChannel`，Dashboard 派发会继续追加：

```bash
--deliver --channel <channel>
```

## Hermes 配置

```bash
export EDICT_AGENT_RUNTIME=hermes
export HERMES_BIN=hermes
export HERMES_TOOLSETS=terminal,file,web
export HERMES_MAX_TURNS=90
```

默认 Hermes 派发命令形态：

```bash
hermes chat -q "<message>" --source edict --toolsets terminal,file,web --max-turns 90 --quiet
```

## Hermes Profile 模式

如果希望每个三省六部 Agent 使用独立 Hermes profile：

```bash
export EDICT_AGENT_RUNTIME=hermes
export HERMES_PROFILE_MODE=1
```

此时 `agent_id=bingbu` 会映射为：

```bash
hermes --profile bingbu chat -q "<message>" --source edict --quiet
```

建议提前创建对应 profile：

```bash
hermes profile create taizi
hermes profile create zhongshu
hermes profile create menxia
hermes profile create shangshu
hermes profile create hubu
hermes profile create libu
hermes profile create bingbu
hermes profile create xingbu
hermes profile create gongbu
hermes profile create libu_hr
hermes profile create zaochao
```

## 后端配置字段

`edict/backend/app/config.py` 支持以下字段：

| 环境变量 | 默认值 | 说明 |
|---|---:|---|
| `EDICT_AGENT_RUNTIME` / `AGENT_RUNTIME` | `openclaw` | `openclaw` 或 `hermes` |
| `OPENCLAW_BIN` | `openclaw` | OpenClaw CLI 路径 |
| `OPENCLAW_PROJECT_DIR` | 空 | OpenClaw 工作目录 |
| `HERMES_BIN` | `hermes` | Hermes CLI 路径 |
| `HERMES_PROFILE_MODE` | `false` | 是否按 agent_id 选择 Hermes profile |
| `HERMES_TOOLSETS` | 空 | 传给 `hermes chat --toolsets` 的工具集 |
| `HERMES_MAX_TURNS` | `90` | 传给 `hermes chat --max-turns` 的最大轮数 |

## 测试

```bash
python3 -m pytest tests/test_agent_runtime.py tests/test_dashboard_dispatch.py -q
```

覆盖内容：

- OpenClaw 命令保持原有形态
- OpenClaw dispatch channel 兼容
- Hermes `chat -q` 命令构造
- Hermes profile-per-agent 模式
- 环境变量配置读取
- Dashboard 对 OpenClaw/Hermes CLI 缺失的状态上报
