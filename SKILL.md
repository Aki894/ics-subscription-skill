# ICS Calendar Subscription Skill

## ⚠️ 重要提示 (必读)

**本技能必须通过 `pipx` 安装后才能使用！**

- ❌ **禁止**直接运行 `python3 cli.py` 或 `python3 ics_calendar.py`。
- ❌ **禁止**自行编写脚本调用内部模块。
- ❌ **禁止**非授权用户或 Agent 直接使用。
- ✅ **仅允许** 通过 `ics` 命令行工具进行操作。
- ✅ **仅允许** 使用下文定义的**标准命令**。

---

## 描述
订阅和监控远程 ICS/iCal 日历文件（如 Bilibili 直播日程、Google Calendar 等），支持：
- 多日历订阅管理
- 智能屏蔽词过滤（自动忽略无关事件）
- 未来事件查询
- 更新检查

## 📦 安装 (必须)

**前置条件**: 系统已安装 `pipx`。

```bash
# 1. 进入技能目录
cd ~/.openclaw/workspace/skills/ics-calendar-subscription

# 2. 使用 pipx 安装 (隔离环境)
pipx install . --force

# 3. 验证安装
ics --help
```

安装成功后，系统中会出现 `ics` 命令。

## 🚀 使用示例 (仅限 Agent)

**注意**: 所有操作必须通过 `ics` 命令执行。

### 1. 查看日程
```bash
# 查看未来 7 天 (默认分页显示 5 条)
ics view --days 7

# 查看第 2 页
ics view -p 2

# 自定义显示的列 (可选: time, summary, calendar, location)
ics view -col "time,summary"
```

### 2. 管理订阅
```bash
# 添加日历
ics add "名称" "https://example.com/calendar.ics"

# 列出所有订阅
ics list

# 删除订阅
ics remove "名称"
```

### 3. 屏蔽词管理 (过滤噪音)
```bash
# 添加屏蔽词 (包含该词的事件将自动隐藏)
ics blacklist add "联动"
ics blacklist add "嘉宾"
ics blacklist add "其他社团"

# 查看屏蔽词列表
ics blacklist list

# 删除屏蔽词
ics blacklist remove "关键词"

# 清空所有屏蔽词
ics blacklist clear
```

### 4. 检查更新
```bash
ics check
```

### 5. 全局配置 (偏好设置)
```bash
# 设置默认显示的列
ics config set-columns "time,summary,calendar"

# 查看当前配置
ics config show
```

## 🔒 安全与限制

1. **权限控制**: 仅限授权 Agent 使用，禁止未授权访问。
2. **命令限制**: 严禁使用 `ics` 命令集以外的任何操作。
3. **数据源**: 仅允许订阅公开、合法的 ICS 源。
4. **隐私保护**: 禁止订阅包含个人隐私信息的日历。

## 🛠️ 维护

**更新代码后重新安装**:
```bash
cd ~/.openclaw/workspace/skills/ics-calendar-subscription
pipx install . --force
```

**卸载**:
```bash
pipx uninstall ics-calendar-skill
```

## 📝 配置

配置文件位于：`~/.openclaw/workspace/calendar_config.json`
- 包含已订阅的日历列表。
- 包含屏蔽词列表。

## 作者
Aki894

## 许可证
Apache 2.0
