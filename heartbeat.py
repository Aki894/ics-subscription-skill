#!/usr/bin/env python3
"""
ICS Calendar Heartbeat Check
定期检查日历更新并通知（用于 OpenClaw 心跳）
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ics_calendar import CalendarManager, format_event
from datetime import datetime
import hashlib

def check_calendar_updates():
    """检查日历更新并返回新事件"""
    manager = CalendarManager()
    
    if not manager.calendars:
        return "没有日历订阅"
    
    updates = []
    for calendar in manager.calendars:
        try:
            # 获取未来 7 天的事件
            events = calendar.get_upcoming_events(days=7)
            
            if events:
                updates.append(f"\n📅 {calendar.name} ({len(events)}个事件):")
                for event in events[:5]:  # 只显示前 5 个
                    start = event['start']
                    if event['all_day']:
                        time_str = start.strftime('%m-%d') + ' (全天)'
                    else:
                        time_str = start.strftime('%m-%d %H:%M')
                    
                    updates.append(f"  • {time_str} - {event['summary']}")
                    
        except Exception as e:
            updates.append(f"❌ {calendar.name}: {e}")
    
    if updates:
        return "\n".join(updates)
    else:
        return "未来 7 天内没有新事件"

if __name__ == "__main__":
    result = check_calendar_updates()
    print(result)
    
    # 如果有更新，可以集成到 OpenClaw 通知系统
    # 例如：发送 Telegram 消息
    if "新事件" not in result and "没有" not in result:
        print("\n✅ 检查完成，有新事件！")
