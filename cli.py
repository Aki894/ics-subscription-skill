#!/usr/bin/env python3
"""
ICS Calendar Subscription CLI
命令行工具
"""

import click
import sys
import os
from rich.console import Console
from rich.table import Table
from rich import box

# 添加模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ics_calendar import CalendarManager

console = Console(stderr=True)


@click.group()
def cli():
    """ICS 日历订阅工具"""
    pass


@cli.command()
@click.argument('name')
@click.argument('url')
@click.option('--timezone', '-tz', default='Asia/Shanghai', help='时区')
def add(name, url, timezone):
    """添加日历订阅
    
    NAME: 日历名称
    URL: ICS 文件 URL
    """
    manager = CalendarManager()
    manager.add_calendar(name, url, timezone)
    console.print(f"[green]✅ 已添加日历：[/green] [bold]{name}[/bold]")
    console.print(f"   [dim]URL: {url}[/dim]")
    console.print(f"   [dim]时区：{timezone}[/dim]")


@cli.command()
@click.argument('name')
@click.confirmation_option(prompt='确定要删除这个日历吗？')
def remove(name):
    """删除日历订阅"""
    manager = CalendarManager()
    manager.remove_calendar(name)
    console.print(f"[green]✅ 已删除日历：[/green] [bold]{name}[/bold]")


@cli.command('list')
def list_calendars():
    """列出所有日历订阅"""
    manager = CalendarManager()
    
    if not manager.calendars:
        console.print("[yellow]暂无日历订阅[/yellow]")
        return
    
    table = Table(title=f"📅 已订阅的日历 ({len(manager.calendars)}个)", box=box.ROUNDED)
    table.add_column("状态", width=4, justify="center")
    table.add_column("名称", style="cyan", no_wrap=True)
    table.add_column("时区", style="dim")
    table.add_column("上次检查", style="dim")
    table.add_column("URL", style="blue")

    for cal in manager.calendars:
        status = "[green]✓[/green]" if cal.last_check else "[white] [/white]"
        last_check = cal.last_check.strftime("%Y-%m-%d %H:%M") if cal.last_check else "-"
        table.add_row(status, cal.name, cal.timezone, last_check, cal.url)

    console.print(table)


@cli.command()
@click.option('--days', '-d', default=7, help='查看未来多少天的事件')
@click.option('--calendar', '-c', help='指定日历名称')
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text')
@click.option('--page', '-p', 'page', type=int, default=1, help='页码 (默认1)')
@click.option('--columns', '-col', help='指定显示的列，用逗号分隔 (可选: time, summary, calendar, location)')
def view(days, calendar, format, page, columns):
    """查看日历事件"""
    manager = CalendarManager()
    
    events = manager.get_all_events(days=days)
    
    if calendar:
        events = [e for e in events if e.get('calendar') == calendar]
    
    total_count = len(events)
    
    if total_count == 0:
        console.print(f"[yellow]未来 {days} 天内没有事件[/yellow]")
        return
    
    # 分页逻辑
    page_size = 5
    total_pages = (total_count + page_size - 1) // page_size
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    displayed_events = events[start_idx:end_idx]
    has_more = page < total_pages
    
    if format == 'json':
        import json
        # 转换为 JSON 友好格式
        json_events = []
        for e in events:
            json_events.append({
                'summary': e['summary'],
                'start': e['start'].isoformat(),
                'end': e['end'].isoformat() if e['end'] else None,
                'calendar': e.get('calendar'),
                'location': e.get('location'),
                'description': e.get('description', '')[:200]
            })
        click.echo(json.dumps(json_events, indent=2, ensure_ascii=False))
        return

    # 解析列配置
    if not columns:
        columns = manager.get_setting("columns", "time,summary,calendar,location")
    
    col_list = [c.strip().lower() for c in columns.split(',')]
    
    # 映射表
    col_map = {
        "time": {"header": "时间", "style": "cyan", "width": 16},
        "summary": {"header": "标题", "style": "bold white", "max_width": 40},
        "calendar": {"header": "日历", "style": "dim green", "width": 12},
        "location": {"header": "地点", "style": "dim italic", "max_width": 20}
    }

    # 表格化显示
    table = Table(
        title=f"🕒 未来 {days} 天内的事件 (共{total_count}个，第 {page}/{total_pages} 页)",
        box=box.SIMPLE,
        header_style="bold magenta"
    )
    
    for col in col_list:
        if col in col_map:
            table.add_column(**col_map[col])

    for event in displayed_events:
        row_data = []
        for col in col_list:
            if col == "time":
                start = event['start']
                end = event['end']
                if event['all_day']:
                    time_str = start.strftime('%m-%d [blue]全天[/]')
                else:
                    time_str = start.strftime('%m-%d %H:%M')
                    if end and end.date() == start.date():
                        time_str += "-" + end.strftime('%H:%M')
                row_data.append(time_str)
            elif col == "summary":
                row_data.append(event['summary'])
            elif col == "calendar":
                row_data.append(event.get('calendar', '-'))
            elif col == "location":
                row_data.append(event.get('location') or '-')
        
        if row_data:
            table.add_row(*row_data)
    
    console.print(table)
    
    if total_pages > 1:
        status_msg = f"[dim]页码: {page}/{total_pages} | 每页显示 {page_size} 条[/dim]"
        if has_more:
            status_msg += f" [yellow](下一页: ics view -p {page + 1})[/yellow]"
        console.print(status_msg)


@cli.command()
def check():
    """检查日历更新"""
    manager = CalendarManager()
    updates = manager.check_updates()
    
    if not updates:
        console.print("[yellow]没有订阅任何日历[/yellow]")
        return
    
    table = Table(title="🔄 日历更新检查", box=box.HORIZONTALS)
    table.add_column("日历", style="cyan")
    table.add_column("状态", justify="center")
    table.add_column("最近事件", style="dim")

    for name, events in updates.items():
        if name.endswith('_error'):
            table.add_row(name[:-6], "[red]❌ 失败[/red]", str(events[0]))
        else:
            latest = events[0]['summary'] if events else "[dim]无事件[/dim]"
            table.add_row(name, f"[green]✅ {len(events)} 个事件[/green]", latest)
    
    console.print(table)


@cli.command()
def demo():
    """添加示例日历（中国节假日）"""
    manager = CalendarManager()
    manager.add_calendar(
        name="中国节假日",
        url="https://www.office-holiday.com/china/public-holidays.ics",
        timezone="Asia/Shanghai"
    )
    console.print("[green]✅ 已添加示例日历：[/green] [bold]中国节假日[/bold]")
    console.print("   使用 'ics view' 命令查看未来事件")


@cli.group()
def blacklist():
    """管理屏蔽词列表"""
    pass


@blacklist.command('add')
@click.argument('word')
def blacklist_add(word):
    """添加屏蔽词
    
    WORD: 要屏蔽的关键词（不区分大小写）
    """
    manager = CalendarManager()
    if manager.add_blacklist(word):
        console.print(f"[green]✅ 已添加屏蔽词：[/green] [bold]{word}[/bold]")
        console.print("   [dim]包含该词的事件将被自动过滤[/dim]")
    else:
        console.print(f"[blue]ℹ️  屏蔽词 '{word}' 已存在[/blue]")


@blacklist.command('remove')
@click.argument('word')
def blacklist_remove(word):
    """删除屏蔽词"""
    manager = CalendarManager()
    if manager.remove_blacklist(word):
        console.print(f"[green]✅ 已删除屏蔽词：[/green] [bold]{word}[/bold]")
    else:
        console.print(f"[red]❌ 未找到屏蔽词：[/red] {word}")


@blacklist.command('list')
def blacklist_list():
    """列出所有屏蔽词"""
    manager = CalendarManager()
    if not manager.blacklist:
        console.print("[yellow]当前没有屏蔽词[/yellow]")
        return
    
    table = Table(title=f"🚫 当前屏蔽词列表 ({len(manager.blacklist)}个)", box=box.SIMPLE)
    table.add_column("屏蔽词", style="red")
    for word in manager.blacklist:
        table.add_row(word)
    console.print(table)


@blacklist.command('clear')
@click.confirmation_option(prompt='确定要清空所有屏蔽词吗？')
def blacklist_clear():
    """清空所有屏蔽词"""
    manager = CalendarManager()
    manager.blacklist = []
    manager.save_config()
    console.print("[green]✅ 已清空所有屏蔽词[/green]")


@cli.group()
def config():
    """管理全局配置"""
    pass


@config.command('set-columns')
@click.argument('columns')
def config_set_columns(columns):
    """设置默认显示的列
    
    COLUMNS: 以逗号分隔的列名 (例如: time,summary,calendar)
    可选列: time, summary, calendar, location
    """
    manager = CalendarManager()
    valid_cols = ["time", "summary", "calendar", "location"]
    input_cols = [c.strip().lower() for c in columns.split(',')]
    filtered_cols = [c for c in input_cols if c in valid_cols]
    
    if not filtered_cols:
        console.print("[red]❌ 无效的列名。[/red] 可选: time, summary, calendar, location")
        return
        
    new_val = ",".join(filtered_cols)
    manager.set_setting("columns", new_val)
    console.print(f"[green]✅ 默认列已更新为：[/green] [bold]{new_val}[/bold]")


@config.command('show')
def config_show():
    """显示当前配置"""
    manager = CalendarManager()
    table = Table(title="⚙️ 当前全局配置", box=box.SIMPLE)
    table.add_column("配置项", style="cyan")
    table.add_column("当前值", style="green")
    
    for k, v in manager.settings.items():
        table.add_row(k, str(v))
        
    console.print(table)


# 确保可以作为模块入口
if __name__ == '__main__':
    cli()
