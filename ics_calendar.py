#!/usr/bin/env python3
"""
ICS Calendar Subscription Module
"""

import requests
import json
import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import zoneinfo

class ICSCalendar:
    """ICS 日历类"""
    
    def __init__(self, name: str, url: str, timezone: str = "Asia/Shanghai"):
        self.name = name
        self.url = url
        self.timezone = timezone
        self.last_check = None
        self.events = []
        self.last_hash = None
        self.last_count = 0
    
    def fetch(self) -> List[Dict[str, Any]]:
        """获取并解析 ICS 文件 - 使用最原始的字符串解析"""
        try:
            # 1. 下载原始内容
            response = requests.get(self.url, timeout=30)
            response.raise_for_status()
            content = response.content.decode('utf-8')
            
            # 2. 检查内容是否变化
            import hashlib
            current_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            if current_hash == self.last_hash and self.events:
                return self.events
            self.last_hash = current_hash
            
            # 3. 手动解析 ICS (不依赖 icalendar 库的复杂逻辑，直接正则提取)
            self.events = self._parse_ics_raw(content)
            self.last_check = datetime.now()
            
            # 4. 记录变化
            if len(self.events) != self.last_count:
                print(f"[{self.name}] 事件数量更新：{self.last_count} -> {len(self.events)}")
                self.last_count = len(self.events)
            
            return self.events
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch calendar '{self.name}': {e}") from e
    
    def _parse_ics_raw(self, content: str) -> List[Dict[str, Any]]:
        """
        原始 ICS 解析器
        直接按行读取，提取 VEVENT 块中的 DTSTART, DTEND, SUMMARY, DESCRIPTION
        """
        events = []
        lines = content.split('\n')
        
        # 状态机
        in_vevent = False
        current_event = {}
        
        # 处理续行 (ICS 规范：以空格开头的行是上一行的延续)
        processed_lines = []
        buffer = ""
        for line in lines:
            if line.startswith(' ') or line.startswith('\t'):
                buffer += line[1:]  # 去掉第一个空格接上去
            else:
                if buffer:
                    processed_lines.append(buffer)
                buffer = line
        if buffer:
            processed_lines.append(buffer)
        
        # 解析
        for line in processed_lines:
            line = line.strip()
            if not line:
                continue
            
            # 开始一个事件
            if line == 'BEGIN:VEVENT':
                in_vevent = True
                current_event = {}
                continue
            
            # 结束一个事件
            if line == 'END:VEVENT':
                if in_vevent and current_event:
                    # 标准化当前事件
                    event = self._normalize_event(current_event)
                    if event:
                        events.append(event)
                in_vevent = False
                current_event = {}
                continue
            
            # 在事件中
            if in_vevent:
                if ':' in line:
                    key, value = line.split(':', 1)
                    
                    # 处理属性参数 (如 DTSTART;TZID=Asia/Shanghai:20260312T210000)
                    param_sep = key.find(';')
                    if param_sep != -1:
                        params = key[param_sep+1:]
                        key = key[:param_sep]
                        # 保存时区信息
                        if 'TZID=' in params:
                            tz_match = re.search(r'TZID=([^;,:]+)', params)
                            if tz_match:
                                current_event[f'{key}_tz'] = tz_match.group(1)
                    
                    # 存储原始值
                    if key in ['DTSTART', 'DTEND', 'SUMMARY', 'DESCRIPTION', 'UID', 'LOCATION']:
                        # 处理描述中的转义符
                        if key == 'DESCRIPTION':
                            value = value.replace('\\n', '\n').replace('\\,', ',').replace('\\;', ';').replace('\\\\', '\\')
                        current_event[key] = value
        
        # 按开始时间排序
        events.sort(key=lambda x: x.get('sort_key', 0))
        return events
    
    def _normalize_event(self, raw: Dict[str, str]) -> Dict[str, Any]:
        """将原始字符串转换为标准事件对象"""
        dtstart_str = raw.get('DTSTART')
        dtend_str = raw.get('DTEND')
        summary = raw.get('SUMMARY', '无标题')
        description = raw.get('DESCRIPTION', '')
        location = raw.get('LOCATION', '')
        uid = raw.get('UID', '')
        
        if not dtstart_str:
            return None
        
        # 解析开始时间
        start, is_all_day = self._parse_datetime(dtstart_str)
        end = self._parse_datetime(dtend_str)[0] if dtend_str else None
        
        if not start:
            return None
        
        # 如果没有结束时间，默认 1 小时
        if not end:
            if is_all_day:
                end = start + timedelta(days=1)
            else:
                end = start + timedelta(hours=1)
        
        return {
            'summary': summary,
            'description': description,
            'location': location,
            'start': start,
            'end': end,
            'uid': uid,
            'all_day': is_all_day,
            'sort_key': start.timestamp()
        }
    
    def _parse_datetime(self, dt_str: str):
        """解析时间字符串 (YYYYMMDDTHHMMSS 或 YYYYMMDD)"""
        if not dt_str:
            return None, False
        
        dt_str = dt_str.strip()
        is_all_day = len(dt_str) == 8  # YYYYMMDD
        
        try:
            if is_all_day:
                dt = datetime.strptime(dt_str, '%Y%m%d')
            else:
                dt = datetime.strptime(dt_str, '%Y%m%dT%H%M%S')
            return dt, is_all_day
        except ValueError:
            return None, False
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取未来事件"""
        if not self.events:
            self.fetch()
        
        if not self.events:
            return []
        
        now = datetime.now()
        future = now + timedelta(days=days)
        
        upcoming = []
        for event in self.events:
            start = event['start']
            if start >= now and start <= future:
                upcoming.append(event)
        
        return upcoming
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'url': self.url,
            'timezone': self.timezone,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'event_count': len(self.events)
        }


class CalendarManager:
    """日历管理器 - 带屏蔽词功能"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            home = os.getenv("HOME", "/home/nanao")
            config_path = os.getenv("ICS_CALENDAR_CONFIG", f"{home}/.openclaw/workspace/calendar_config.json")
        self.config_path = os.path.abspath(config_path)
        self.calendars: List[ICSCalendar] = []
        self.blacklist: List[str] = []
        self.settings: Dict[str, Any] = {
            "columns": "time,summary,calendar,location"
        }
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 加载日历
                for cal_config in config.get('calendars', []):
                    calendar = ICSCalendar(
                        name=cal_config['name'],
                        url=cal_config['url'],
                        timezone=cal_config.get('timezone', 'Asia/Shanghai')
                    )
                    self.calendars.append(calendar)
                # 加载屏蔽词
                self.blacklist = config.get('blacklist', [])
                # 加载设置
                if 'settings' in config:
                    self.settings.update(config['settings'])
    
    def save_config(self):
        config = {
            'calendars': [cal.to_dict() for cal in self.calendars],
            'blacklist': self.blacklist,
            'settings': self.settings
        }
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)
        
    def set_setting(self, key: str, value: Any):
        self.settings[key] = value
        self.save_config()
    
    def add_calendar(self, name: str, url: str, timezone: str = "Asia/Shanghai"):
        calendar = ICSCalendar(name, url, timezone)
        self.calendars.append(calendar)
        self.save_config()
    
    def remove_calendar(self, name: str):
        self.calendars = [cal for cal in self.calendars if cal.name != name]
        self.save_config()
    
    def is_blacklisted(self, event: Dict[str, Any]) -> bool:
        """检查事件是否命中屏蔽词"""
        text = f"{event.get('summary', '')} {event.get('description', '')}".lower()
        for word in self.blacklist:
            if word.lower() in text:
                return True
        return False

    def get_all_events(self, days: int = 7, skip_blacklist: bool = True) -> List[Dict[str, Any]]:
        all_events = []
        skipped_count = 0
        
        for calendar in self.calendars:
            events = calendar.get_upcoming_events(days)
            for event in events:
                event['calendar'] = calendar.name
                # 检查屏蔽
                if skip_blacklist and self.is_blacklisted(event):
                    skipped_count += 1
                    continue
                all_events.append(event)
        
        all_events.sort(key=lambda x: x['start'])
        return all_events
    
    def check_updates(self, skip_blacklist: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        updates = {}
        for calendar in self.calendars:
            try:
                events = calendar.fetch()
                if events:
                    # 应用屏蔽
                    if skip_blacklist:
                        filtered = [e for e in events if not self.is_blacklisted(e)]
                        updates[calendar.name] = filtered[:5]
                    else:
                        updates[calendar.name] = events[:5]
            except Exception as e:
                updates[f"{calendar.name}_error"] = [str(e)]
        return updates

    def add_blacklist(self, word: str):
        """添加屏蔽词"""
        if word not in self.blacklist:
            self.blacklist.append(word)
            self.save_config()
            return True
        return False

    def remove_blacklist(self, word: str):
        """删除屏蔽词"""
        if word in self.blacklist:
            self.blacklist.remove(word)
            self.save_config()
            return True
        return False




if __name__ == "__main__":
    print("="*10)
    print("ICS Calendar")
    print("="*10)
    
    manager = CalendarManager()
    
    if len(manager.calendars) == 0:
        print("没有配置的日历")
    else:
        events = manager.get_all_events(days=14)
        print(f"\n未来 14 天内的事件总数：{len(events)}")
        
        if events:
            print("\n事件列表:")
            for event in events:
                print(format_event(event))
                print("-" * 10)
        else:
            print("未来 14 天内没有事件")
