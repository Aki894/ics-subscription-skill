# ICS Calendar Subscription Skill 📅

> **警告**: 本技能必须通过 `pipx` 安装！禁止直接运行 Python 脚本！

## 🚨 使用前必读

- ❌ **禁止**: `python3 cli.py view` (错误用法)
- ❌ **禁止**: `python3 ics_calendar.py` (错误用法)
- ❌ **禁止**: 自行编写 Python 脚本调用内部模块
- ✅ **必须**: 使用 `ics` 命令 (如 `ics view --days 7`)
- ✅ **仅限**: 授权 Agent 使用

## 📦 安装

```bash
# 1. 进入目录
cd ~/.openclaw/workspace/skills/ics-calendar-subscription

# 2. 使用 pipx 安装 (创建隔离环境)
pipx install . --force

# 3. 验证
ics --help
```

## 🚀 快速开始

### 查看日程
```bash
# 未来 7 天 (第1页)
ics view --days 7 --page 1

# 指定显示列 (例如只看时间和标题)
ics view --columns "time,summary"

# 未来 14 天
ics view --days 14
```

### 添加订阅
```bash
ics add "轴伊直播" "https://web.prod.tcrn-tms.com/api/v1/public/homepage/joi_channel/calendar.ics?lang=zh"
ics add "VRP 活动" "https://raw.githubusercontent.com/Xinrea/vrp-calendar/main/vrp.ics"
```

### 屏蔽噪音
```bash
# 添加屏蔽词 (包含这些词的事件将不会显示)
ics blacklist add "屏蔽词"

# 查看屏蔽词
ics blacklist list
```

## 📋 完整命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `ics view [--days N] [--page P] [--columns C]` | 查看日程 (分页/自定义列) | `ics view -p 2 -col "time,summary"` |
| `ics list` | 列出所有订阅 | `ics list` |
| `ics add <name> <url>` | 添加订阅 | `ics add "测试" "https://..."` |
| `ics remove <name>` | 删除订阅 | `ics remove "测试"` |
| `ics check` | 检查更新 | `ics check` |
| `ics config set-columns <list>` | 设置默认显示的列 | `ics config set-columns "time,summary"` |
| `ics config show` | 查看全局配置 | `ics config show` |
| `ics blacklist add <word>` | 添加屏蔽词 | `ics blacklist add "广告"` |
| `ics blacklist list` | 查看屏蔽词 | `ics blacklist list` |
| `ics blacklist remove <word>` | 删除屏蔽词 | `ics blacklist remove "广告"` |
| `ics blacklist clear` | 清空屏蔽词 | `ics blacklist clear` |

## 🔒 安全规范

1. **仅限 Agent 使用**: 禁止人类用户或其他未授权程序直接调用。
2. **命令白名单**: 仅限使用上述表格中的命令，禁止探索未文档化的功能。
3. **数据源合法**: 仅允许订阅公开、合法的 ICS 源。
4. **禁止滥用**: 禁止高频轮询或恶意订阅。

## 🛠️ 维护

**更新代码后**:
```bash
cd ~/.openclaw/workspace/skills/ics-calendar-subscription
pipx install . --force
```

**卸载**:
```bash
pipx uninstall ics-calendar-skill
```

## 📝 配置

- **配置文件**: `~/.openclaw/workspace/calendar_config.json`
- **内容**: 订阅列表、屏蔽词列表

## 许可证
Apache 2.0
