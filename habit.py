#!/usr/bin/env python3
"""
+------------------------------------------------------------------+
|           HabitFlow - Personal Offline Habit Tracker             |
|      No accounts. No internet. No cloud. 100% yours.             |
+------------------------------------------------------------------+
|  Requirements:  Python 3.8+  (tkinter is built-in)               |
|  Dependencies:  none - every chart is drawn with tkinter         |
|                                                                  |
|  Run:   python habit.py                                          |
|  Data:  ~/.habitflow/data.json  (fully local)                    |
+------------------------------------------------------------------+

v2.1 "Command Center" - a second, deeper design pass on the v2 UI.

Everything the app stores and calculates is unchanged: the same
~/.habitflow/data.json format, the same scheduling rules, the same
streak and XP maths.  This file changes only how the app looks and
how it is laid out.
"""

# ==================================================================
# IMPORTS
# ==================================================================
import calendar as cal_module
import json
import math
import os
import random
import shutil
import sys
import tempfile
import time
import tkinter as tk
import tkinter.font as tkfont
import uuid
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, ttk


# ==================================================================
# CONSTANTS
# ==================================================================
APP_NAME = "HabitFlow"
VERSION = "2.2.0"
DATA_DIR = os.path.join(os.path.expanduser("~"), ".habitflow")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# -- XP & levelling thresholds (unchanged from v1) -------------------
XP_PER_TASK = 10
XP_PERFECT_DAY = 50
LEVELS = [0, 100, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 99_999]
LEVEL_NAMES = [
    "Beginner",
    "Apprentice",
    "Practitioner",
    "Adept",
    "Expert",
    "Master",
    "Grandmaster",
    "Legend",
    "Mythic",
    "Ascended",
]

# -- Category -> accent colour (desaturated for dark surfaces) ------
CATEGORIES = {
    "Health": "#3ED598",
    "Study": "#5B9CFF",
    "Fitness": "#FF9A5B",
    "Personal": "#A78BFA",
    "Work": "#F5C451",
    "Social": "#F472B6",
    "Sleep": "#7C93F5",
    "Other": "#8394AB",
}
CAT_LIST = list(CATEGORIES.keys())

RECURRENCE_OPTIONS = ["Daily", "Weekdays", "Weekends", "Weekly", "Monthly", "Custom Days"]
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# -- Layout tokens: one spacing scale for the whole application -----
PAGE_PAD = 32          # page gutter
SECTION_GAP = 18       # vertical rhythm between sections
CARD_RADIUS = 18
CARD_PAD = (20, 18)


# -- Motivational quotes (unchanged) --------------------------------
QUOTES = [
    ("We are what we repeatedly do. Excellence is not an act, but a habit.", "Aristotle"),
    ("Discipline is the bridge between goals and accomplishment.", "Jim Rohn"),
    ("Small daily improvements are the key to staggering long-term results.", "Robin Sharma"),
    ("You don't rise to your goals; you fall to the level of your systems.", "James Clear"),
    ("Motivation is what gets you started. Habit is what keeps you going.", "Jim Ryun"),
    ("The secret of your future is hidden in your daily routine.", "Mike Murdock"),
    ("Success is the sum of small efforts repeated day in and day out.", "Robert Collier"),
    ("First forget inspiration. Habit is more dependable.", "Octavia Butler"),
    ("Habits are the compound interest of self-improvement.", "James Clear"),
    ("A year from now you may wish you had started today.", "Karen Lamb"),
    ("The only bad workout is the one that didn't happen.", "Unknown"),
    ("Don't count the days; make the days count.", "Muhammad Ali"),
    ("Push yourself, because no one else is going to do it for you.", "Unknown"),
    ("Wake up with determination. Go to bed with satisfaction.", "Unknown"),
    ("Your future self is watching you right now through memories.", "Unknown"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Do something today that your future self will thank you for.", "Sean Patrick Flanery"),
]

# -- Default starter habits (unchanged) -----------------------------
DEFAULT_TASKS = [
    {"name": "Drink 4L of water", "category": "Health", "daily_target": "4L", "notes": "Stay hydrated throughout the day"},
    {"name": "Revise notes", "category": "Study", "daily_target": "", "notes": "Review today's study material"},
    {"name": "Gym / Workout", "category": "Fitness", "daily_target": "45min", "notes": ""},
    {"name": "Social interaction", "category": "Social", "daily_target": "", "notes": "Connect meaningfully with someone"},
    {"name": "Learn something new", "category": "Study", "daily_target": "", "notes": "Read, watch, or explore"},
    {"name": "Sleep 7-8 hours", "category": "Sleep", "daily_target": "7-8h", "notes": "Consistent sleep schedule"},
    {"name": "Deep work (2 hours)", "category": "Work", "daily_target": "2h", "notes": "No distractions, fully focused"},
    {"name": "Daily reflection", "category": "Personal", "daily_target": "10min", "notes": "Journal or meditate before bed"},
]


# ==================================================================
# COLOUR THEMES
# ==================================================================
# Midnight-blue / deep charcoal surfaces, one electric blue accent,
# cyan used sparingly for "live" information, green for completion.
# The sidebar stays dark in both themes so the app keeps its identity.
THEMES = {
    "dark": {
        "name": "dark",
        "bg": "#05070B",
        "bg_alt": "#070A0F",
        "surface": "#0A0D13",
        "surface2": "#0E1219",
        "surface3": "#141A24",
        "card": "#0A0D13",
        "card2": "#0D1118",
        "border": "#191F2A",
        "border_hi": "#2A3444",
        "primary": "#2E8BFF",
        "primary_l": "#7FB4FF",
        "primary_d": "#1A4FA8",
        "primary_soft": "#0B1730",
        "cyan": "#22D3EE",
        "cyan_soft": "#0C2B36",
        "purple": "#8B5CF6",
        "purple_l": "#B79CFF",
        "purple_soft": "#191334",
        "accent": "#22D3A5",
        "success": "#34D399",
        "warning": "#F2B33D",
        "danger": "#F0616B",
        "text": "#F2F6FC",
        "text2": "#9AA8BA",
        "text3": "#687687",
        "sidebar": "#04060A",
        "sidebar2": "#090D14",
        "side_text": "#E8EEF9",
        "side_text2": "#93A5BD",
        "side_active": "#101823",
        "prog_bg": "#141A24",
        "ring_track": "#141A24",
        "highlight": "#121923",
        "shadow": "#000000",
        "on_accent": "#04121B",
        "scrim": "#05070B",
        "toast": "#11161F",
        "track": "#141A24",
    },
    "light": {
        "name": "light",
        "bg": "#EEF3FB",
        "bg_alt": "#E7EEF9",
        "surface": "#FFFFFF",
        "surface2": "#F4F8FF",
        "surface3": "#E6EEFA",
        "card": "#FFFFFF",
        "card2": "#F8FAFF",
        "border": "#DBE5F4",
        "border_hi": "#C2D2EA",
        "primary": "#2563EB",
        "primary_l": "#1D4ED8",
        "primary_d": "#1E40AF",
        "primary_soft": "#E7EFFE",
        "cyan": "#0E7490",
        "cyan_soft": "#E0F5FA",
        "purple": "#7C3AED",
        "purple_l": "#6D28D9",
        "purple_soft": "#F0E9FE",
        "accent": "#0E9F7E",
        "success": "#12915C",
        "warning": "#B87503",
        "danger": "#D93036",
        "text": "#0B1526",
        "text2": "#4A5B72",
        "text3": "#7C8CA3",
        "sidebar": "#0A1120",
        "sidebar2": "#0F1A2C",
        "side_text": "#E8EEF9",
        "side_text2": "#93A5BD",
        "side_active": "#16243A",
        "prog_bg": "#E3ECFA",
        "ring_track": "#E3ECFA",
        "highlight": "#EDF3FE",
        "shadow": "#D7E2F2",
        "on_accent": "#04121B",
        "scrim": "#EEF3FB",
        "toast": "#FFFFFF",
        "track": "#E3ECFA",
    },
}


# ==================================================================
# COLOUR HELPERS
# ==================================================================
def _clamp(value, low=0, high=255):
    return max(low, min(high, value))


def _hex_to_rgb(color: str):
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(_clamp(int(round(c))) for c in rgb)


def mix(color_a: str, color_b: str, t: float) -> str:
    """Blend two hex colours (t=0 -> a, t=1 -> b)."""
    t = max(0.0, min(1.0, t))
    a, b = _hex_to_rgb(color_a), _hex_to_rgb(color_b)
    return _rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def shade(color: str, factor: float) -> str:
    """Lighten (factor > 1) or darken (factor < 1) a hex colour."""
    rgb = _hex_to_rgb(color)
    if factor >= 1:
        return _rgb_to_hex(tuple(c + (255 - c) * (factor - 1) for c in rgb))
    return _rgb_to_hex(tuple(c * factor for c in rgb))


def readable_on(color: str) -> str:
    """Return near-black or white depending on the background luminance."""
    r, g, b = _hex_to_rgb(color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#08111E" if luminance > 0.62 else "#FFFFFF"


def cat_color(category: str, theme) -> str:
    """Category accent, darkened for legibility on the light theme."""
    base = CATEGORIES.get(category, CATEGORIES["Other"])
    if theme.get("name") == "light":
        return mix(base, "#0B1526", 0.34)
    return base


# ==================================================================
# TYPOGRAPHY
# ==================================================================
FONT_STACK = [
    "Segoe UI Variable Text",
    "Segoe UI",
    "Inter",
    "SF Pro Text",
    "Helvetica Neue",
    "Ubuntu",
    "Noto Sans",
    "DejaVu Sans",
    "Arial",
]
MONO_STACK = ["Cascadia Mono", "Consolas", "SF Mono", "JetBrains Mono",
              "DejaVu Sans Mono", "Courier New"]

FONT_FAMILY = "Segoe UI"
MONO_FAMILY = "Consolas"


def init_fonts(root):
    """Pick the best available UI font for this platform."""
    global FONT_FAMILY, MONO_FAMILY
    try:
        available = set(tkfont.families(root))
    except Exception:
        available = set()
    for family in FONT_STACK:
        if family in available:
            FONT_FAMILY = family
            break
    for family in MONO_STACK:
        if family in available:
            MONO_FAMILY = family
            break
    return FONT_FAMILY, MONO_FAMILY


def f(size=12, weight="normal", slant="roman"):
    """Shorthand for a UI font tuple."""
    return (FONT_FAMILY, size, weight, slant)


def mono(size=10, weight="normal"):
    return (MONO_FAMILY, size, weight)


# ==================================================================
# DATA MANAGER - all persistence and business logic
# ==================================================================
class DataManager:
    """Reads, writes and calculates everything HabitFlow knows.

    The on-disk format is unchanged from v1:
        {"tasks": [...], "completions": {"YYYY-MM-DD": [task_id, ...]}, "settings": {...}}
    New settings keys are additive, so older data files keep working.
    """

    def __init__(self, data_file=None, data_dir=None, backup_dir=None):
        self.data_file = data_file or DATA_FILE
        self.data_dir = data_dir or os.path.dirname(self.data_file)
        self.backup_dir = backup_dir or os.path.join(self.data_dir, "backups")
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        self.data = self._load()

    # -- Persistence -------------------------------------------------
    def _load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                if not isinstance(loaded, dict):
                    raise ValueError("Data file is not an object")
                return self._ensure_defaults(loaded)
            except Exception:
                # Never silently throw away a file we failed to parse.
                try:
                    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.copy2(self.data_file, f"{self.data_file}.corrupt-{stamp}")
                except Exception:
                    pass
        return self._fresh_data()

    @staticmethod
    def _ensure_defaults(data: dict) -> dict:
        """Fill in anything a v1 / imported file may be missing."""
        data.setdefault("tasks", [])
        data.setdefault("completions", {})
        settings = data.setdefault("settings", {})
        settings.setdefault("theme", "dark")
        settings.setdefault("xp", 0)
        settings.setdefault("level", 1)
        settings.setdefault("notifications", True)
        settings.setdefault("created_date", date.today().isoformat())
        settings.setdefault("daily_quote_date", "")
        settings.setdefault("daily_quote_idx", 0)
        settings.setdefault("perfect_day_awarded", "")
        settings.setdefault("window_alpha", 0.93)
        settings.setdefault("animations", True)

        for index, task in enumerate(data["tasks"]):
            task.setdefault("id", str(uuid.uuid4()))
            task.setdefault("name", "Untitled habit")
            task.setdefault("category", "Other")
            task.setdefault("notes", "")
            task.setdefault("daily_target", "")
            task.setdefault("recurrence", "Daily")
            task.setdefault("recurrence_days", [])
            task.setdefault("pinned", False)
            task.setdefault("order", index)
            task.setdefault("created_date", date.today().isoformat())

        if not isinstance(data["completions"], dict):
            data["completions"] = {}
        return data

    def _fresh_data(self):
        tasks = []
        for index, template in enumerate(DEFAULT_TASKS):
            tasks.append(
                {
                    "id": str(uuid.uuid4()),
                    "name": template["name"],
                    "category": template["category"],
                    "notes": template.get("notes", ""),
                    "daily_target": template.get("daily_target", ""),
                    "recurrence": "Daily",
                    "recurrence_days": [],
                    "pinned": False,
                    "order": index,
                    "created_date": date.today().isoformat(),
                }
            )
        return {
            "tasks": tasks,
            "completions": {},
            "settings": {
                "theme": "dark",
                "xp": 0,
                "level": 1,
                "notifications": True,
                "created_date": date.today().isoformat(),
                "daily_quote_date": "",
                "daily_quote_idx": 0,
                "perfect_day_awarded": "",
                "window_alpha": 0.93,
                "animations": True,
            },
        }

    def save(self):
        """Atomic write: a crash mid-save can no longer corrupt the file."""
        os.makedirs(self.data_dir, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(dir=self.data_dir, prefix=".data-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self.data, fh, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.data_file)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    # -- Task CRUD ---------------------------------------------------
    def add_task(self, name, category="Other", notes="", daily_target="",
                 recurrence="Daily", recurrence_days=None, pinned=False):
        task = {
            "id": str(uuid.uuid4()),
            "name": name.strip(),
            "category": category,
            "notes": notes.strip(),
            "daily_target": daily_target.strip(),
            "recurrence": recurrence,
            "recurrence_days": recurrence_days or [],
            "pinned": pinned,
            "order": len(self.data["tasks"]),
            "created_date": date.today().isoformat(),
        }
        self.data["tasks"].append(task)
        self.save()
        return task

    def update_task(self, task_id, **kwargs):
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                task.update(kwargs)
                break
        self.save()

    def delete_task(self, task_id):
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        for day in list(self.data["completions"].keys()):
            self.data["completions"][day] = [
                tid for tid in self.data["completions"][day] if tid != task_id
            ]
            if not self.data["completions"][day]:
                del self.data["completions"][day]
        self.save()

    def toggle_task(self, task_id, completed: bool):
        today_str = date.today().isoformat()
        completions = self.data["completions"].setdefault(today_str, [])
        if completed and task_id not in completions:
            completions.append(task_id)
            self._add_xp(XP_PER_TASK)
        elif not completed and task_id in completions:
            completions.remove(task_id)
            self._add_xp(-XP_PER_TASK)
        if not completions:
            self.data["completions"].pop(today_str, None)
        self.save()
        return completed

    # -- Scheduling: is a habit due on a given date? ------------------
    @staticmethod
    def _created_on(task) -> date:
        try:
            return date.fromisoformat(task.get("created_date", ""))
        except (ValueError, TypeError):
            return date.today()

    def is_scheduled(self, task, check_date: date) -> bool:
        recurrence = task.get("recurrence", "Daily")
        weekday = check_date.weekday()  # 0=Mon ... 6=Sun
        if recurrence == "Daily":
            return True
        if recurrence == "Weekdays":
            return weekday < 5
        if recurrence == "Weekends":
            return weekday >= 5
        if recurrence == "Weekly":
            return weekday == self._created_on(task).weekday()
        if recurrence == "Monthly":
            created = self._created_on(task)
            # Clamp to the last day of short months so a habit created on the
            # 31st still runs in February instead of silently disappearing.
            last_day = cal_module.monthrange(check_date.year, check_date.month)[1]
            return check_date.day == min(created.day, last_day)
        if recurrence == "Custom Days":
            return weekday in task.get("recurrence_days", [])
        return True

    def get_scheduled_today(self):
        """Habits due today, pinned first, then by manual order."""
        today = date.today()
        tasks = [t for t in self.data["tasks"] if self.is_scheduled(t, today)]
        tasks.sort(key=lambda t: (not t.get("pinned", False), t.get("order", 0)))
        return tasks

    def get_scheduled_for(self, check_date: date):
        return [t for t in self.data["tasks"] if self.is_scheduled(t, check_date)]

    # -- Completion helpers ------------------------------------------
    def get_completed_today(self) -> set:
        return set(self.data["completions"].get(date.today().isoformat(), []))

    def get_completed_on(self, check_date: date) -> set:
        return set(self.data["completions"].get(check_date.isoformat(), []))

    def completion_pct(self, check_date: date) -> float:
        scheduled = self.get_scheduled_for(check_date)
        if not scheduled:
            return 0.0
        completed = self.get_completed_on(check_date)
        done = sum(1 for t in scheduled if t["id"] in completed)
        return done / len(scheduled)

    def is_perfect_day(self, check_date: date) -> bool:
        scheduled = self.get_scheduled_for(check_date)
        if not scheduled:
            return False
        completed = self.get_completed_on(check_date)
        return all(t["id"] in completed for t in scheduled)

    # -- Streaks -----------------------------------------------------
    def calculate_streak(self) -> int:
        """Current perfect-day streak (v1 logic, unchanged)."""
        streak = 0
        check = date.today() - timedelta(days=1)
        for _ in range(366):
            if self.is_perfect_day(check):
                streak += 1
                check -= timedelta(days=1)
            else:
                break
        if self.is_perfect_day(date.today()):
            streak += 1
        return streak

    def best_streak(self) -> int:
        """Longest perfect-day run found in the stored history."""
        days = sorted(self.data.get("completions", {}).keys())
        if not days:
            return 0
        try:
            start = date.fromisoformat(days[0])
        except ValueError:
            return 0
        today = date.today()
        if start > today:
            return 0
        best = current = 0
        cursor = start
        while cursor <= today:
            if self.is_perfect_day(cursor):
                current += 1
                best = max(best, current)
            else:
                current = 0
            cursor += timedelta(days=1)
        return best

    def habit_stats(self, task, window: int = 30) -> dict:
        """Per-habit streak and consistency over the last `window` days."""
        task_id = task["id"]
        today = date.today()
        streak = 0
        cursor = today
        if self.is_scheduled(task, today) and task_id not in self.get_completed_on(today):
            cursor = today - timedelta(days=1)
        for _ in range(366):
            if self.is_scheduled(task, cursor):
                if task_id in self.get_completed_on(cursor):
                    streak += 1
                else:
                    break
            cursor -= timedelta(days=1)

        scheduled = done = 0
        for offset in range(window):
            day = today - timedelta(days=offset)
            if self.is_scheduled(task, day):
                scheduled += 1
                if task_id in self.get_completed_on(day):
                    done += 1
        rate = done / scheduled if scheduled else 0.0
        return {"streak": streak, "scheduled": scheduled, "done": done, "rate": rate}

    # -- XP & levels -------------------------------------------------
    @staticmethod
    def _level_from_xp(xp: int) -> int:
        level = 1
        for threshold in LEVELS[1:]:
            if xp >= threshold:
                level += 1
            else:
                break
        return min(level, len(LEVEL_NAMES))

    def _add_xp(self, amount: int):
        settings = self.data["settings"]
        settings["xp"] = max(0, int(settings.get("xp", 0)) + amount)
        settings["level"] = self._level_from_xp(settings["xp"])

    def give_perfect_day_xp(self):
        self._add_xp(XP_PERFECT_DAY)
        self.save()

    def award_perfect_day_if_due(self) -> bool:
        """Grant the +50 XP perfect-day bonus at most once per calendar day.

        v1 tracked this in memory only, so restarting the app re-awarded the
        bonus on an already-perfect day. The award date is now persisted.
        """
        today = date.today()
        settings = self.data["settings"]
        if settings.get("perfect_day_awarded") == today.isoformat():
            return False
        if not self.is_perfect_day(today):
            return False
        settings["perfect_day_awarded"] = today.isoformat()
        self._add_xp(XP_PERFECT_DAY)
        self.save()
        return True

    def get_xp_info(self):
        """Return (xp, level, level_name, xp_in_level, xp_for_level)."""
        settings = self.data["settings"]
        xp = int(settings.get("xp", 0))
        level = self._level_from_xp(xp)
        previous = LEVELS[level - 1]
        following = LEVELS[level] if level < len(LEVELS) else LEVELS[-1]
        xp_in_level = max(0, xp - previous)
        xp_for_level = max(1, following - previous)
        return xp, level, LEVEL_NAMES[level - 1], xp_in_level, xp_for_level

    # -- Statistics --------------------------------------------------
    def get_week_pcts(self):
        """Completion percentages Mon -> Sun for the current week."""
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        return [round(self.completion_pct(monday + timedelta(days=i)) * 100) for i in range(7)]

    def get_month_pcts(self):
        """Completion percentage for every day of the current month."""
        today = date.today()
        days = cal_module.monthrange(today.year, today.month)[1]
        base = date(today.year, today.month, 1)
        return [round(self.completion_pct(base + timedelta(days=i)) * 100) for i in range(days)]

    def get_week_dates(self):
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        return [monday + timedelta(days=i) for i in range(7)]

    def consistency(self, days: int = 30) -> float:
        """Average completion rate over the last `days` days that had habits due."""
        today = date.today()
        rates = []
        for offset in range(days):
            day = today - timedelta(days=offset)
            if self.get_scheduled_for(day):
                rates.append(self.completion_pct(day))
        return sum(rates) / len(rates) if rates else 0.0

    def total_checkins(self) -> int:
        return sum(len(ids) for ids in self.data.get("completions", {}).values())

    def perfect_days_in_month(self, year=None, month=None) -> int:
        today = date.today()
        year = year or today.year
        month = month or today.month
        days = cal_module.monthrange(year, month)[1]
        count = 0
        for day_number in range(1, days + 1):
            day = date(year, month, day_number)
            if day > today:
                break
            if self.is_perfect_day(day):
                count += 1
        return count

    def perfect_days_total(self) -> int:
        total = 0
        for day_str in self.data.get("completions", {}):
            try:
                day = date.fromisoformat(day_str)
            except ValueError:
                continue
            if self.is_perfect_day(day):
                total += 1
        return total

    def next_streak_milestone(self, streak=None):
        """Return (next milestone, days remaining) for the streak badge."""
        streak = self.calculate_streak() if streak is None else streak
        for milestone in (3, 7, 14, 30, 60, 100, 180, 365):
            if streak < milestone:
                return milestone, milestone - streak
        return None, 0

    def get_daily_quote(self):
        settings = self.data["settings"]
        today = date.today().isoformat()
        if settings.get("daily_quote_date") != today:
            settings["daily_quote_date"] = today
            settings["daily_quote_idx"] = random.randrange(len(QUOTES))
            self.save()
        index = settings.get("daily_quote_idx", 0)
        if not isinstance(index, int) or not 0 <= index < len(QUOTES):
            index = 0
        return QUOTES[index]

    # -- Backup / Export / Import ------------------------------------
    def backup(self):
        if not os.path.exists(self.data_file):
            self.save()
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination = os.path.join(self.backup_dir, f"backup_{stamp}.json")
        shutil.copy2(self.data_file, destination)
        return destination

    def export_json(self, path: str):
        self.save()
        shutil.copy2(self.data_file, path)

    def import_json(self, path: str):
        with open(path, "r", encoding="utf-8") as fh:
            new_data = json.load(fh)
        if not isinstance(new_data, dict) or "tasks" not in new_data or "completions" not in new_data:
            raise ValueError("Invalid HabitFlow data file.")
        self.backup()  # automatic safety copy before overwriting
        self.data = self._ensure_defaults(new_data)
        self.save()

    def reset(self):
        self.backup()
        self.data = self._fresh_data()
        self.save()


# ==================================================================
# DRAWING PRIMITIVES
# ==================================================================
def rrect(canvas, x1, y1, x2, y2, radius=12, fill=None, outline=None, width=1, tags=()):
    """Draw a rounded rectangle using exact geometry (no blobby polygons)."""
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)
    radius = max(0, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
    items = []
    if radius <= 0.5:
        if fill:
            items.append(canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="", tags=tags))
        if outline:
            items.append(canvas.create_rectangle(x1, y1, x2, y2, outline=outline, width=width, tags=tags))
        return items

    d = radius * 2
    if fill:
        items.append(canvas.create_rectangle(x1 + radius, y1, x2 - radius, y2,
                                             fill=fill, outline="", tags=tags))
        items.append(canvas.create_rectangle(x1, y1 + radius, x2, y2 - radius,
                                             fill=fill, outline="", tags=tags))
        for cx1, cy1 in ((x1, y1), (x2 - d, y1), (x1, y2 - d), (x2 - d, y2 - d)):
            items.append(canvas.create_oval(cx1, cy1, cx1 + d, cy1 + d,
                                            fill=fill, outline="", tags=tags))
    if outline:
        arcs = (
            (x1, y1, x1 + d, y1 + d, 90, 90),          # top-left
            (x2 - d, y1, x2, y1 + d, 0, 90),           # top-right
            (x2 - d, y2 - d, x2, y2, 270, 90),         # bottom-right
            (x1, y2 - d, x1 + d, y2, 180, 90),         # bottom-left
        )
        for ax1, ay1, ax2, ay2, start, extent in arcs:
            items.append(canvas.create_arc(ax1, ay1, ax2, ay2, start=start, extent=extent,
                                           style="arc", outline=outline, width=width, tags=tags))
        items.append(canvas.create_line(x1 + radius, y1, x2 - radius, y1,
                                        fill=outline, width=width, tags=tags))
        items.append(canvas.create_line(x1 + radius, y2, x2 - radius, y2,
                                        fill=outline, width=width, tags=tags))
        items.append(canvas.create_line(x1, y1 + radius, x1, y2 - radius,
                                        fill=outline, width=width, tags=tags))
        items.append(canvas.create_line(x2, y1 + radius, x2, y2 - radius,
                                        fill=outline, width=width, tags=tags))
    return items


# ==================================================================
# ICONS - clean vector glyphs drawn on a canvas (no emoji font needed)
# ==================================================================
def draw_icon(canvas, name, cx, cy, size=18, color="#FFFFFF", width=1.7, tags=("icon",)):
    """Draw a 24x24 glyph scaled into `size`, centred on (cx, cy)."""
    scale = size / 24.0

    def X(value):
        return cx + (value - 12) * scale

    def Y(value):
        return cy + (value - 12) * scale

    def line(points, w=width, cap="round", fill=None):
        coords = []
        for index, value in enumerate(points):
            coords.append(X(value) if index % 2 == 0 else Y(value))
        canvas.create_line(*coords, fill=fill or color, width=w, capstyle=cap,
                           joinstyle="round", smooth=False, tags=tags)

    def poly(points, fill=None, outline=""):
        coords = []
        for index, value in enumerate(points):
            coords.append(X(value) if index % 2 == 0 else Y(value))
        canvas.create_polygon(*coords, fill=fill or color, outline=outline,
                              width=width, smooth=True, tags=tags)

    def circle(x, y, r, filled=False, w=width):
        canvas.create_oval(X(x - r), Y(y - r), X(x + r), Y(y + r),
                           fill=(color if filled else ""), outline=color,
                           width=w, tags=tags)

    def rect(x, y, w, h, filled=False, radius=2):
        rrect(canvas, X(x), Y(y), X(x + w), Y(y + h), radius * scale,
              fill=(color if filled else None), outline=(None if filled else color),
              width=width, tags=tags)

    if name == "grid":
        rect(3, 3, 8, 8)
        rect(13, 3, 8, 8)
        rect(3, 13, 8, 8)
        rect(13, 13, 8, 8)
    elif name == "list":
        for offset in (5, 12, 19):
            circle(4.5, offset, 1.4, filled=True, w=1)
            line([9, offset, 21, offset])
    elif name == "chart":
        for x, top in ((5, 12), (11.5, 6), (18, 9.5)):
            rrect(canvas, X(x), Y(top), X(x + 3.4), Y(21), 1.6 * scale,
                  fill=color, tags=tags)
    elif name == "calendar":
        rect(3, 5, 18, 16, radius=3)
        line([3, 10, 21, 10])
        line([8, 2.5, 8, 7])
        line([16, 2.5, 16, 7])
        for x in (8, 12, 16):
            circle(x, 15.5, 1.1, filled=True, w=1)
    elif name == "settings":
        circle(12, 12, 4.2)
        circle(12, 12, 1.4, filled=True, w=1)
        for angle in range(0, 360, 60):
            import math as _math

            rad = _math.radians(angle)
            line([12 + 7.2 * _math.cos(rad), 12 + 7.2 * _math.sin(rad),
                  12 + 9.4 * _math.cos(rad), 12 + 9.4 * _math.sin(rad)], w=width + 0.3)
    elif name == "plus":
        line([12, 5, 12, 19], w=width + 0.5)
        line([5, 12, 19, 12], w=width + 0.5)
    elif name == "check":
        line([5, 12.5, 10, 17.5, 19, 6.5], w=width + 0.6)
    elif name == "pencil":
        poly([4, 20, 5.5, 15.5, 16, 5, 19, 8, 8.5, 18.5], fill=color)
        line([14, 7, 17, 10])
    elif name == "trash":
        line([4, 7, 20, 7])
        line([9.5, 4, 14.5, 4])
        line([9, 3.2, 9, 7])
        line([15, 3.2, 15, 7])
        line([6, 7, 7.5, 21, 16.5, 21, 18, 7])
        line([10, 10.5, 10, 17.5])
        line([14, 10.5, 14, 17.5])
    elif name == "search":
        circle(10.5, 10.5, 6.2)
        line([15.2, 15.2, 20, 20], w=width + 0.4)
    elif name == "flame":
        poly([12, 2.5, 16.5, 8.5, 18.5, 13, 17.5, 17.5, 12, 21.5, 6.5, 17.5, 6, 13,
              9.5, 15, 11.5, 10, 12, 6.5, 12, 2.5], fill=color)
    elif name == "bolt":
        poly([13, 2.5, 6.5, 13.5, 11.5, 13.5, 10, 21.5, 17.5, 10, 12.5, 10, 14.5, 2.5],
             fill=color)
    elif name == "spark":
        poly([12, 2, 13.6, 10.4, 22, 12, 13.6, 13.6, 12, 22, 10.4, 13.6, 2, 12,
              10.4, 10.4, 12, 2], fill=color)
    elif name == "target":
        circle(12, 12, 8.5)
        circle(12, 12, 4.6)
        circle(12, 12, 1.5, filled=True, w=1)
    elif name == "clock":
        circle(12, 12, 8.5)
        line([12, 6.8, 12, 12.4, 15.8, 14.4])
    elif name == "chevron-left":
        line([15, 5, 8.5, 12, 15, 19], w=width + 0.4)
    elif name == "chevron-right":
        line([9, 5, 15.5, 12, 9, 19], w=width + 0.4)
    elif name == "arrow-right":
        line([4, 12, 19, 12], w=width + 0.3)
        line([13.5, 6.5, 19.5, 12, 13.5, 17.5], w=width + 0.3)
    elif name == "trophy":
        line([8, 4, 16, 4, 16, 10])
        line([8, 4, 8, 10])
        line([8, 10, 10, 15.5, 14, 15.5, 16, 10])
        canvas.create_arc(X(3), Y(4), X(9), Y(11), start=270, extent=180,
                          style="arc", outline=color, width=width, tags=tags)
        canvas.create_arc(X(15), Y(4), X(21), Y(11), start=270, extent=180,
                          style="arc", outline=color, width=width, tags=tags)
        line([12, 15.5, 12, 18.5])
        line([8, 20.5, 16, 20.5])
        line([9.5, 20.5, 12, 18.5, 14.5, 20.5])
    elif name == "close":
        line([6, 6, 18, 18])
        line([18, 6, 6, 18])
    elif name == "sun":
        circle(12, 12, 3.7, filled=True, w=1)
        for angle in range(0, 360, 45):
            import math as _math

            rad = _math.radians(angle)
            line([12 + 6.1 * _math.cos(rad), 12 + 6.1 * _math.sin(rad),
                  12 + 8.6 * _math.cos(rad), 12 + 8.6 * _math.sin(rad)], w=1.6)
    elif name == "moon":
        # Filled crescent: a disc with an offset disc punched out in the canvas colour.
        bg = canvas.cget("bg")
        canvas.create_oval(X(5.5), Y(3), X(19.5), Y(21), fill=color, outline=color, tags=tags)
        canvas.create_oval(X(11.5), Y(0.5), X(24.5), Y(16.5), fill=bg, outline=bg, tags=tags)
    elif name == "download":
        line([12, 3.5, 12, 15])
        line([7, 10.5, 12, 15.5, 17, 10.5])
        line([4.5, 17.5, 4.5, 20.5, 19.5, 20.5, 19.5, 17.5])
    elif name == "upload":
        line([12, 16, 12, 4.5])
        line([7, 9, 12, 3.5, 17, 9])
        line([4.5, 17.5, 4.5, 20.5, 19.5, 20.5, 19.5, 17.5])
    elif name == "archive":
        rect(3.5, 4.5, 17, 4.5, radius=1.6)
        rect(5.5, 9, 13, 11, radius=2)
        line([10, 12.5, 14, 12.5])
    elif name == "reset":
        canvas.create_arc(X(4), Y(4), X(20), Y(20), start=40, extent=290,
                          style="arc", outline=color, width=width + 0.3, tags=tags)
        poly([16.5, 3.5, 20.5, 6.5, 16.5, 9.5, 16.5, 3.5], fill=color, outline=color)
    elif name == "pin":
        circle(12, 9, 4.4)
        line([12, 13.5, 12, 21])
    elif name == "dots":
        for x in (6.5, 12, 17.5):
            circle(x, 12, 1.5, filled=True, w=1)
    elif name == "layers":
        poly([12, 3, 21, 8, 12, 13, 3, 8, 12, 3], fill=color)
        line([3.5, 12.5, 12, 17.5, 20.5, 12.5])
        line([3.5, 16.5, 12, 21.5, 20.5, 16.5])
    elif name == "info":
        circle(12, 12, 8.5)
        circle(12, 8, 1.1, filled=True, w=1)
        line([12, 11.5, 12, 17])
    else:  # unknown icon -> dot
        circle(12, 12, 2.4, filled=True, w=1)


#!/usr/bin/env python3
"""
+------------------------------------------------------------------+
|           HabitFlow - Personal Offline Habit Tracker             |
|      No accounts. No internet. No cloud. 100% yours.             |
+------------------------------------------------------------------+
|  Requirements:  Python 3.8+  (tkinter is built-in)               |
|  Dependencies:  none - every chart is drawn with tkinter         |
|                                                                  |
|  Run:   python habit.py                                          |
|  Data:  ~/.habitflow/data.json  (fully local)                    |
+------------------------------------------------------------------+

v2.1 "Command Center" - a second, deeper design pass on the v2 UI.

Everything the app stores and calculates is unchanged: the same
~/.habitflow/data.json format, the same scheduling rules, the same
streak and XP maths.  This file changes only how the app looks and
how it is laid out.
"""

# ==================================================================
# IMPORTS
# ==================================================================
import calendar as cal_module
import json
import math
import os
import random
import shutil
import sys
import tempfile
import tkinter as tk
import tkinter.font as tkfont
import uuid
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox, ttk


# ==================================================================
# CONSTANTS
# ==================================================================
APP_NAME = "HabitFlow"
DATA_DIR = os.path.join(os.path.expanduser("~"), ".habitflow")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# -- XP & levelling thresholds (unchanged from v1) -------------------
XP_PER_TASK = 10
XP_PERFECT_DAY = 50
LEVELS = [0, 100, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 99_999]
LEVEL_NAMES = [
    "Beginner",
    "Apprentice",
    "Practitioner",
    "Adept",
    "Expert",
    "Master",
    "Grandmaster",
    "Legend",
    "Mythic",
    "Ascended",
]

# -- Category -> accent colour (desaturated for dark surfaces) ------
CATEGORIES = {
    "Health": "#3ED598",
    "Study": "#5B9CFF",
    "Fitness": "#FF9A5B",
    "Personal": "#A78BFA",
    "Work": "#F5C451",
    "Social": "#F472B6",
    "Sleep": "#7C93F5",
    "Other": "#8394AB",
}
CAT_LIST = list(CATEGORIES.keys())

RECURRENCE_OPTIONS = ["Daily", "Weekdays", "Weekends", "Weekly", "Monthly", "Custom Days"]
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# -- Layout tokens: one spacing scale for the whole application -----
PAGE_PAD = 32          # page gutter
SECTION_GAP = 18       # vertical rhythm between sections
CARD_RADIUS = 18
CARD_PAD = (20, 18)


# -- Motivational quotes (unchanged) --------------------------------
QUOTES = [
    ("We are what we repeatedly do. Excellence is not an act, but a habit.", "Aristotle"),
    ("Discipline is the bridge between goals and accomplishment.", "Jim Rohn"),
    ("Small daily improvements are the key to staggering long-term results.", "Robin Sharma"),
    ("You don't rise to your goals; you fall to the level of your systems.", "James Clear"),
    ("Motivation is what gets you started. Habit is what keeps you going.", "Jim Ryun"),
    ("The secret of your future is hidden in your daily routine.", "Mike Murdock"),
    ("Success is the sum of small efforts repeated day in and day out.", "Robert Collier"),
    ("First forget inspiration. Habit is more dependable.", "Octavia Butler"),
    ("Habits are the compound interest of self-improvement.", "James Clear"),
    ("A year from now you may wish you had started today.", "Karen Lamb"),
    ("The only bad workout is the one that didn't happen.", "Unknown"),
    ("Don't count the days; make the days count.", "Muhammad Ali"),
    ("Push yourself, because no one else is going to do it for you.", "Unknown"),
    ("Wake up with determination. Go to bed with satisfaction.", "Unknown"),
    ("Your future self is watching you right now through memories.", "Unknown"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Do something today that your future self will thank you for.", "Sean Patrick Flanery"),
]

# -- Default starter habits (unchanged) -----------------------------
DEFAULT_TASKS = [
    {"name": "Drink 4L of water", "category": "Health", "daily_target": "4L", "notes": "Stay hydrated throughout the day"},
    {"name": "Revise notes", "category": "Study", "daily_target": "", "notes": "Review today's study material"},
    {"name": "Gym / Workout", "category": "Fitness", "daily_target": "45min", "notes": ""},
    {"name": "Social interaction", "category": "Social", "daily_target": "", "notes": "Connect meaningfully with someone"},
    {"name": "Learn something new", "category": "Study", "daily_target": "", "notes": "Read, watch, or explore"},
    {"name": "Sleep 7-8 hours", "category": "Sleep", "daily_target": "7-8h", "notes": "Consistent sleep schedule"},
    {"name": "Deep work (2 hours)", "category": "Work", "daily_target": "2h", "notes": "No distractions, fully focused"},
    {"name": "Daily reflection", "category": "Personal", "daily_target": "10min", "notes": "Journal or meditate before bed"},
]


# ==================================================================
# COLOUR THEMES
# ==================================================================
# Midnight-blue / deep charcoal surfaces, one electric blue accent,
# cyan used sparingly for "live" information, green for completion.
# The sidebar stays dark in both themes so the app keeps its identity.
THEMES = {
    "dark": {
        "name": "dark",
        "bg": "#05070B",
        "bg_alt": "#070A0F",
        "surface": "#0A0D13",
        "surface2": "#0E1219",
        "surface3": "#141A24",
        "card": "#0A0D13",
        "card2": "#0D1118",
        "border": "#191F2A",
        "border_hi": "#2A3444",
        "primary": "#2E8BFF",
        "primary_l": "#7FB4FF",
        "primary_d": "#1A4FA8",
        "primary_soft": "#0B1730",
        "cyan": "#22D3EE",
        "cyan_soft": "#0C2B36",
        "purple": "#8B5CF6",
        "purple_l": "#B79CFF",
        "purple_soft": "#191334",
        "accent": "#22D3A5",
        "success": "#34D399",
        "warning": "#F2B33D",
        "danger": "#F0616B",
        "text": "#F2F6FC",
        "text2": "#9AA8BA",
        "text3": "#687687",
        "sidebar": "#04060A",
        "sidebar2": "#090D14",
        "side_text": "#E8EEF9",
        "side_text2": "#93A5BD",
        "side_active": "#101823",
        "prog_bg": "#141A24",
        "ring_track": "#141A24",
        "highlight": "#121923",
        "shadow": "#000000",
        "on_accent": "#04121B",
        "scrim": "#05070B",
        "toast": "#11161F",
        "track": "#141A24",
    },
    "light": {
        "name": "light",
        "bg": "#EEF3FB",
        "bg_alt": "#E7EEF9",
        "surface": "#FFFFFF",
        "surface2": "#F4F8FF",
        "surface3": "#E6EEFA",
        "card": "#FFFFFF",
        "card2": "#F8FAFF",
        "border": "#DBE5F4",
        "border_hi": "#C2D2EA",
        "primary": "#2563EB",
        "primary_l": "#1D4ED8",
        "primary_d": "#1E40AF",
        "primary_soft": "#E7EFFE",
        "cyan": "#0E7490",
        "cyan_soft": "#E0F5FA",
        "purple": "#7C3AED",
        "purple_l": "#6D28D9",
        "purple_soft": "#F0E9FE",
        "accent": "#0E9F7E",
        "success": "#12915C",
        "warning": "#B87503",
        "danger": "#D93036",
        "text": "#0B1526",
        "text2": "#4A5B72",
        "text3": "#7C8CA3",
        "sidebar": "#0A1120",
        "sidebar2": "#0F1A2C",
        "side_text": "#E8EEF9",
        "side_text2": "#93A5BD",
        "side_active": "#16243A",
        "prog_bg": "#E3ECFA",
        "ring_track": "#E3ECFA",
        "highlight": "#EDF3FE",
        "shadow": "#D7E2F2",
        "on_accent": "#04121B",
        "scrim": "#EEF3FB",
        "toast": "#FFFFFF",
        "track": "#E3ECFA",
    },
}


# ==================================================================
# COLOUR HELPERS
# ==================================================================
def _clamp(value, low=0, high=255):
    return max(low, min(high, value))


def _hex_to_rgb(color: str):
    color = color.lstrip("#")
    if len(color) == 3:
        color = "".join(ch * 2 for ch in color)
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(_clamp(int(round(c))) for c in rgb)


def mix(color_a: str, color_b: str, t: float) -> str:
    """Blend two hex colours (t=0 -> a, t=1 -> b)."""
    t = max(0.0, min(1.0, t))
    a, b = _hex_to_rgb(color_a), _hex_to_rgb(color_b)
    return _rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def shade(color: str, factor: float) -> str:
    """Lighten (factor > 1) or darken (factor < 1) a hex colour."""
    rgb = _hex_to_rgb(color)
    if factor >= 1:
        return _rgb_to_hex(tuple(c + (255 - c) * (factor - 1) for c in rgb))
    return _rgb_to_hex(tuple(c * factor for c in rgb))


def readable_on(color: str) -> str:
    """Return near-black or white depending on the background luminance."""
    r, g, b = _hex_to_rgb(color)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#08111E" if luminance > 0.62 else "#FFFFFF"


def cat_color(category: str, theme) -> str:
    """Category accent, darkened for legibility on the light theme."""
    base = CATEGORIES.get(category, CATEGORIES["Other"])
    if theme.get("name") == "light":
        return mix(base, "#0B1526", 0.34)
    return base


# ==================================================================
# TYPOGRAPHY
# ==================================================================
FONT_STACK = [
    "Segoe UI Variable Text",
    "Segoe UI",
    "Inter",
    "SF Pro Text",
    "Helvetica Neue",
    "Ubuntu",
    "Noto Sans",
    "DejaVu Sans",
    "Arial",
]
MONO_STACK = ["Cascadia Mono", "Consolas", "SF Mono", "JetBrains Mono",
              "DejaVu Sans Mono", "Courier New"]

FONT_FAMILY = "Segoe UI"
MONO_FAMILY = "Consolas"


def init_fonts(root):
    """Pick the best available UI font for this platform."""
    global FONT_FAMILY, MONO_FAMILY
    try:
        available = set(tkfont.families(root))
    except Exception:
        available = set()
    for family in FONT_STACK:
        if family in available:
            FONT_FAMILY = family
            break
    for family in MONO_STACK:
        if family in available:
            MONO_FAMILY = family
            break
    return FONT_FAMILY, MONO_FAMILY


def f(size=12, weight="normal", slant="roman"):
    """Shorthand for a UI font tuple."""
    return (FONT_FAMILY, size, weight, slant)


def mono(size=10, weight="normal"):
    return (MONO_FAMILY, size, weight)

# ==================================================================
# SMALL HELPERS
# ==================================================================
def bind_tree(widget, sequence, callback, skip=("Canvas",)):
    """Bind an event on a widget and all of its text descendants."""
    widget.bind(sequence, callback)
    for child in widget.winfo_children():
        try:
            if child.winfo_class() in skip:
                continue
        except tk.TclError:
            continue
        bind_tree(child, sequence, callback, skip)


def elide(text, font, max_width):
    """Trim a string with an ellipsis so it fits `max_width` pixels."""
    if not text:
        return ""
    try:
        width = font.measure(text)
    except tk.TclError:
        return text
    if width <= max_width:
        return text
    trimmed = text
    while trimmed and font.measure(trimmed + "…") > max_width:
        trimmed = trimmed[:-1]
    return (trimmed.rstrip() + "…") if trimmed else "…"


def hairline(parent, app, color=None, pady=(0, 0), padx=0):
    line = tk.Frame(parent, bg=color or app.c["border"], height=1)
    line.pack(fill="x", padx=padx, pady=pady)
    return line


# ==================================================================
# SCROLLING
# ==================================================================
class SlimScrollbar(tk.Canvas):
    """A slim rounded scrollbar that replaces the dated native one."""

    def __init__(self, parent, bg, track, thumb, command, width=8):
        super().__init__(parent, width=width, bg=bg, highlightthickness=0, bd=0,
                         cursor="arrow")
        self._track = track
        self._thumb = thumb
        self._command = command
        self._first = 0.0
        self._last = 1.0
        self._drag_offset = None
        self.bind("<Configure>", lambda _e=None: self._draw())
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", lambda _e=None: setattr(self, "_drag_offset", None))

    def set(self, first, last):
        self._first, self._last = float(first), float(last)
        self._draw()

    def _draw(self):
        self.delete("all")
        height = self.winfo_height()
        width = self.winfo_width()
        if height <= 1:
            return
        if self._last - self._first >= 0.999:
            return
        rrect(self, 0, 0, width, height, width / 2, fill=self._track)
        top = self._first * height
        bottom = max(self._last * height, top + 28)
        rrect(self, 1, top + 1, width - 1, min(bottom, height) - 1,
              (width - 2) / 2, fill=self._thumb)

    def _on_press(self, event):
        height = self.winfo_height() or 1
        unit = self._first + (event.y / height) * (self._last - self._first)
        self._drag_offset = (self._last - self._first) / 2
        self._command("moveto", max(0.0, min(1.0, unit - self._drag_offset)))

    def _on_drag(self, event):
        if self._drag_offset is None:
            return
        height = self.winfo_height() or 1
        unit = self._first + (event.y / height) * (self._last - self._first)
        self._command("moveto", max(0.0, min(1.0, unit - self._drag_offset)))


class ScrollableFrame(tk.Frame):
    """Vertically scrollable page container with mousewheel + slim bar."""

    def __init__(self, parent, bg, padding=0, track=None, thumb=None, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((padding, padding), window=self.inner,
                                              anchor="nw")
        self._padding = padding
        self.scrollbar = SlimScrollbar(self, bg, track or mix(bg, "#FFFFFF", 0.05),
                                       thumb or mix(bg, "#FFFFFF", 0.16),
                                       self._on_scroll_command)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y", padx=(2, 0))

        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", self._on_canvas)
        self.canvas.bind("<Enter>", self._bind_wheel)
        self.canvas.bind("<Leave>", self._unbind_wheel)
        self.inner.bind("<Enter>", self._bind_wheel)

    def _on_scroll_command(self, *args):
        self.canvas.yview(*args)

    def _on_inner(self, _event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas(self, event):
        self.canvas.itemconfigure(self._win, width=max(1, event.width - self._padding * 2))

    def _bind_wheel(self, _event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)
        self.canvas.bind_all("<Button-4>", self._on_wheel_up)
        self.canvas.bind_all("<Button-5>", self._on_wheel_down)

    def _unbind_wheel(self, _event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_wheel(self, event):
        delta = int(-event.delta / 120) if abs(event.delta) >= 120 else (-1 if event.delta > 0 else 1)
        self.canvas.yview_scroll(delta, "units")

    def _on_wheel_up(self, _event):
        self.canvas.yview_scroll(-1, "units")

    def _on_wheel_down(self, _event):
        self.canvas.yview_scroll(1, "units")

    def scroll_to_top(self):
        self.canvas.yview_moveto(0)


# ==================================================================
# CARD
# ==================================================================
class Card(tk.Frame):
    """Rounded surface that hugs its content.

    The background (fill, hairline border, optional accent stripe) is a
    canvas *placed* behind a normally packed content frame.  Because the
    canvas never takes part in geometry negotiation, a card's requested
    height is exactly its content height - no measurement races, so
    nested cards can never be clipped.
    """

    def __init__(self, parent, app, radius=CARD_RADIUS, pad=CARD_PAD, fill=None,
                 border=None, accent=None, bg=None, hoverable=False):
        self.app = app
        self.c = app.c
        self._radius = radius
        self._fill = fill or self.c["card"]
        self._base_border = border or self.c["border"]
        self._border = self._base_border
        self._accent = accent
        self._hoverable = hoverable
        self._hover = False
        self._outer_bg = bg or parent.cget("bg")

        super().__init__(parent, bg=self._outer_bg, highlightthickness=0, bd=0)
        self.canvas = tk.Canvas(self, bg=self._outer_bg, highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.body = tk.Frame(self, bg=self._fill)
        self.body.pack(fill="both", expand=True, padx=pad[0], pady=pad[1])
        # keep the painted background behind the content frame
        self.tk.call("lower", self.canvas._w)
        self.canvas.bind("<Configure>", lambda _e=None: self._paint())
        if hoverable:
            bind_tree(self, "<Enter>", self._on_enter, skip=("Canvas",))
            bind_tree(self, "<Leave>", self._on_leave, skip=("Canvas",))

    # -- painting ----------------------------------------------------
    def _paint(self):
        canvas = self.canvas
        canvas.delete("bg")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 4 or height < 4:
            return
        rrect(canvas, 0.5, 0.5, width - 0.5, height - 0.5, self._radius,
              fill=self._fill, tags=("bg",))
        rrect(canvas, 0.5, 0.5, width - 0.5, height - 0.5, self._radius,
              outline=self._border, width=1, tags=("bg",))
        # single light hairline across the top: reads as a glass edge
        canvas.create_line(max(self._radius, 6), 1.0, width - max(self._radius, 6), 1.0,
                           fill=mix(self._fill, "#FFFFFF", 0.07), tags=("bg",))
        if self._accent:
            inset = self._radius * 0.85
            rrect(canvas, 0.5, inset, 3.5, height - inset, 1.5,
                  fill=self._accent, tags=("bg",))

    def set_accent(self, color):
        if color == self._accent:
            return
        self._accent = color
        self._paint()

    def set_border(self, color):
        if color == self._border:
            return
        self._border = color
        self._paint()

    # -- hover -------------------------------------------------------
    def _on_enter(self, _event=None):
        if self._hover or not self._hoverable:
            return
        self._hover = True
        self.set_border(mix(self._base_border, self.c["primary"], 0.45))

    def _on_leave(self, _event=None):
        if not self._hoverable:
            return
        self.after(60, self._check_leave)

    def _check_leave(self):
        try:
            under = self.app.root.winfo_containing(*self.app.root.winfo_pointerxy())
        except (tk.TclError, KeyError):
            under = None
        widget = under
        while widget is not None:
            if widget is self:
                return
            widget = getattr(widget, "master", None)
        self._hover = False
        self.set_border(self._base_border)


# ==================================================================
# PILL - small rounded label for metadata
# ==================================================================
class Pill(tk.Canvas):
    """Small rounded label used for metadata; text can change in place."""

    def __init__(self, parent, app, text, color=None, bg=None, dot=False, icon=None,
                 filled=False, size=9, height=22, padx=9):
        self.c = app.c
        self._color = color or self.c["text2"]
        self._host = bg or parent.cget("bg")
        self._dot = dot
        self._icon = icon
        self._filled = filled
        self._size = size
        self._height = height
        self._padx = padx
        self._text = text
        super().__init__(parent, width=self._measure(text), height=height,
                         bg=self._host, highlightthickness=0, bd=0)
        self._paint()

    def _measure(self, text):
        width = tkfont.Font(font=(FONT_FAMILY, self._size, "bold")).measure(text)
        leading = (11 if self._dot else 0) + (17 if self._icon else 0)
        return int(width + self._padx * 2 + leading)

    def _paint(self):
        self.delete("all")
        color, host = self._color, self._host
        height, padx = self._height, self._padx
        font = (FONT_FAMILY, self._size, "bold")
        width = self._measure(self._text)
        self.configure(width=width)
        fill = color if self._filled else mix(color, host, 0.86)
        fg = readable_on(color) if self._filled else color
        rrect(self, 0, 0, width, height, height / 2, fill=fill)
        x = padx
        if self._dot:
            cy = height / 2
            self.create_oval(x - 1, cy - 3.5, x + 6, cy + 3.5, fill=fg, outline="")
            x += 11
        if self._icon:
            draw_icon(self, self._icon, x + 6, height / 2, size=13, color=fg, width=1.7)
            x += 17
        self.create_text(x, height / 2 + 0.5, text=self._text, anchor="w",
                         font=font, fill=fg)

    def set_text(self, text):
        if text == self._text:
            return
        self._text = text
        self._paint()


# ==================================================================
# BUTTONS
# ==================================================================
BUTTON_KINDS = {
    "primary": {"fill": "primary", "fg": None, "border": None},
    "soft": {"fill": "surface2", "fg": "text", "border": "border"},
    "ghost": {"fill": None, "fg": "text2", "border": None},
    "outline": {"fill": None, "fg": "primary_l", "border": "primary_d"},
    "success": {"fill": "success", "fg": None, "border": None},
    "danger": {"fill": None, "fg": "danger", "border": None},
}


class HoverButton(tk.Canvas):
    """Rounded button with a short hover transition."""

    def __init__(self, parent, app, text, command=None, icon=None, kind="primary",
                 height=38, radius=11, font_size=10, bg=None, padx=16, min_width=0,
                 tooltip=None, bold=True):
        self.app = app
        self.c = app.c
        self._kind = kind if kind in BUTTON_KINDS else "primary"
        self._spec = BUTTON_KINDS[self._kind]
        self._command = command
        self._font = (FONT_FAMILY, font_size, "bold" if bold else "normal")
        self._icon = icon
        self._padx = padx
        self._radius = radius
        self._height = height
        self._host = bg or parent.cget("bg")
        self._enabled = True
        self._hover = False
        self._animation = None
        self._tooltip_text = tooltip
        self._text = text
        self._min_width = min_width
        self._width = self._measure(text)
        super().__init__(parent, width=self._width, height=height, bg=self._host,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._paint(0.0)

    # -- geometry ----------------------------------------------------
    def _measure(self, text):
        width = tkfont.Font(font=self._font).measure(text)
        icon = 18 if self._icon else 0
        return int(max(self._min_width, width + icon + self._padx * 2))

    def set_text(self, text):
        self._text = text
        self._width = self._measure(text)
        self.configure(width=self._width)
        self._paint(0.0)

    def set_enabled(self, enabled):
        self._enabled = bool(enabled)
        self.configure(cursor="hand2" if enabled else "arrow")
        self._paint(0.0)

    # -- palette -----------------------------------------------------
    def _resolve(self, key):
        return self.c.get(key, key) if isinstance(key, str) else key

    def _colors(self):
        c = self.c
        spec = self._spec
        if not self._enabled:
            return None, c["text3"], None, c["text3"]
        fill = self._resolve(spec["fill"]) if spec["fill"] else None
        border = self._resolve(spec["border"]) if spec["border"] else None
        fg = spec["fg"]
        fg = self._resolve(fg) if fg else readable_on(fill or c["primary"])
        if self._kind == "danger":
            border = mix(c["danger"], self._host, 0.55)
        return fill, fg, border, fg

    # -- drawing -----------------------------------------------------
    def _paint(self, hover_t=0.0, pressed=False):
        self.delete("all")
        c = self.c
        fill, fg, border, _ = self._colors()
        if not self._enabled:
            rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5, self._radius,
                  outline=border or c["border"], width=1)
        elif fill:
            base = shade(fill, 0.9) if pressed else shade(fill, 1 + 0.12 * hover_t)
            rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5, self._radius,
                  fill=base)
            if self._kind in ("primary", "success"):
                rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5,
                      self._radius, outline=mix(base, "#FFFFFF", 0.18), width=1)
        else:
            if hover_t > 0:
                hover_fill = mix(self._host, c["primary"] if self._kind != "danger"
                                 else c["danger"], 0.14 * hover_t)
                rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5,
                      self._radius, fill=hover_fill)
            if border:
                rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5,
                      self._radius, outline=border, width=1)
            if self._kind == "ghost" and hover_t > 0:
                fg = mix(fg, c["text"], hover_t)

        if self._icon:
            text_width = tkfont.Font(font=self._font).measure(self._text)
            total = 18 + text_width
            start = (self._width - total) / 2
            draw_icon(self, self._icon, start + 7, self._height / 2, size=15,
                      color=fg, width=1.8)
            self.create_text(start + 18 + text_width / 2, self._height / 2 + 0.5,
                             text=self._text, font=self._font, fill=fg)
        else:
            self.create_text(self._width / 2, self._height / 2 + 0.5, text=self._text,
                             font=self._font, fill=fg)

    # -- interaction -------------------------------------------------
    def _animate(self, target):
        if self._animation is not None:
            try:
                self.after_cancel(self._animation)
            except tk.TclError:
                pass
            self._animation = None

        def step(index, start):
            if not self.winfo_exists():
                return
            t = start + (target - start) * (index / 4)
            self._paint(t)
            if index < 4:
                self._animation = self.after(22, lambda: step(index + 1, start))

        step(1, 0.0 if target else 1.0)

    def _on_enter(self, _event):
        if not self._enabled:
            return
        self._hover = True
        self._animate(1.0)

    def _on_leave(self, _event):
        self._hover = False
        self._paint(0.0)

    def _on_press(self, _event):
        if not self._enabled:
            return
        self._paint(1.0, pressed=True)

    def _on_release(self, event):
        if not self._enabled:
            return
        inside = 0 <= event.x <= self._width and 0 <= event.y <= self._height
        self._paint(1.0 if inside else 0.0)
        if inside and self._command:
            self._command()


class IconButton(tk.Canvas):
    """Compact square icon button (edit / delete / theme toggle)."""

    def __init__(self, parent, app, icon, command=None, size=32, icon_size=16,
                 color=None, hover_color=None, bg=None, tooltip=None, radius=9):
        self.app = app
        self.c = app.c
        self._icon = icon
        self._command = command
        self._icon_size = icon_size
        self._color = color or self.c["text2"]
        self._hover_color = hover_color or self.c["text"]
        self._size = size
        self._radius = radius
        self._hover = False
        self._host = bg or parent.cget("bg")
        super().__init__(parent, width=size, height=size, bg=self._host,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Enter>", lambda _e=None: self._set_hover(True))
        self.bind("<Leave>", lambda _e=None: self._set_hover(False))
        self.bind("<Button-1>", lambda _e=None: self._command() if self._command else None)
        self._draw()

    def _set_hover(self, hover):
        self._hover = hover
        self._draw()

    def _draw(self):
        self.delete("all")
        if self._hover:
            rrect(self, 0, 0, self._size, self._size, self._radius,
                  fill=mix(self._host, self.c["primary"], 0.16))
        draw_icon(self, self._icon, self._size / 2, self._size / 2,
                  size=self._icon_size,
                  color=self._hover_color if self._hover else self._color, width=1.7)


class CheckCircle(tk.Canvas):
    """Habit completion control: a rounded square that fills and strokes its tick.

    The tick is a two-segment path revealed by its own arc length, so completion
    lands as a drawn check instead of an icon appearing in one frame.  A single
    expanding ripple carries the "logged" feeling without any sustained glow.
    """

    CHECK_MS = 165
    RIPPLE_MS = 280

    def __init__(self, parent, app, checked=False, color=None, command=None,
                 size=26, bg=None):
        self.app = app
        self.c = app.c
        self._checked = bool(checked)
        self._color = color or self.c["success"]
        self._command = command
        self._size = size
        self._hover = False
        self._progress = 1.0 if self._checked else 0.0
        self._job = None
        self._host = bg or parent.cget("bg")
        super().__init__(parent, width=size, height=size, bg=self._host,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Enter>", lambda _e=None: self._set_hover(True))
        self.bind("<Leave>", lambda _e=None: self._set_hover(False))
        self.bind("<Button-1>", self._on_click)
        self._draw()

    # -- geometry ------------------------------------------------------
    @staticmethod
    def _lerp(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    def _tick_points(self):
        size = self._size
        return ((0.29 * size, 0.53 * size), (0.44 * size, 0.68 * size),
                (0.72 * size, 0.36 * size))

    # -- painting ------------------------------------------------------
    def _draw(self, scale=1.0, progress=None, ripple=None):
        self.delete("all")
        size = self._size
        centre = size / 2
        inset = 1.5
        p = self._progress if progress is None else progress

        if ripple:
            spread = size * 0.55 * ripple
            tint = mix(self._host, self._color, max(0.0, 1.0 - ripple))
            self.create_oval(centre - spread, centre - spread, centre + spread,
                             centre + spread, outline=tint, width=1.4)

        filled = self._checked
        half = (centre - inset) * scale
        outline = None
        if not filled:
            outline = self.c["primary"] if self._hover else self.c["border_hi"]
        rrect(self, centre - half, centre - half, centre + half, centre + half,
              size * 0.30 * scale, fill=self._color if filled else None,
              outline=outline, width=1.6)

        if filled and p > 0.001:
            p0, p1, p2 = self._tick_points()
            l1 = math.dist(p0, p1)
            l2 = math.dist(p1, p2)
            target = p * (l1 + l2)
            if target <= l1:
                path = (p0, self._lerp(p0, p1, target / l1 if l1 else 0.0))
            else:
                path = (p0, p1, self._lerp(p1, p2, (target - l1) / l2 if l2 else 1.0))
            flat = []
            for point in path:
                flat.extend(point)
            self.create_line(*flat, fill=readable_on(self._color), width=2.4,
                             capstyle="round", joinstyle="round")

    # -- interaction ---------------------------------------------------
    def _set_hover(self, hover):
        self._hover = hover
        self._draw()

    def _on_click(self, _event=None):
        if self._command:
            self._command()

    def _cancel(self):
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except tk.TclError:
                pass
            self._job = None

    def _animate_in(self):
        self._cancel()
        started = time.perf_counter()
        span = self.RIPPLE_MS / 1000.0

        def step():
            self._job = None
            if not self.winfo_exists():
                return
            t = min(1.0, (time.perf_counter() - started) / span)
            tick = max(0.0, min(1.0, (t - 0.18) / 0.72))
            scale = 1.0 + 0.14 * math.sin(math.pi * min(1.0, t / 0.45))
            self._progress = tick
            if t < 1.0:
                self._draw(scale=scale, progress=tick, ripple=t)
                self._job = self.after(16, step)
            else:
                self._progress = 1.0
                self._draw()

        step()

    def _animate_out(self):
        self._cancel()
        started = time.perf_counter()
        span = 0.11

        def step():
            self._job = None
            if not self.winfo_exists():
                return
            t = min(1.0, (time.perf_counter() - started) / span)
            if t < 1.0:
                self._draw(scale=1.0 - 0.10 * t, progress=1.0 - t)
                self._job = self.after(16, step)
            else:
                self._checked = False
                self._progress = 0.0
                self._draw()

        step()

    def set_checked(self, checked, animate=False):
        checked = bool(checked)
        was = self._checked
        if checked == was and self._job is not None:
            # the dashboard refreshes rows right after a toggle; don't cut the tick off
            return
        if checked and not was:
            self._checked = True
            self._progress = 0.0
            self._animate_in()
            return
        if animate and was and not checked:
            self._animate_out()
            return
        self._cancel()
        self._checked = checked
        self._progress = 1.0 if checked else 0.0
        self._draw()

    def _pop(self):
        """Compatibility shim: replay the fill-and-tick motion."""
        self._checked = True
        self._progress = 0.0
        self._animate_in()


# ==================================================================
# DATA VISUALS
# ==================================================================
class ProgressRing(tk.Canvas):
    """Arc completion ring with an eased fill and a cyan end cap."""

    def __init__(self, parent, app, size=152, thickness=11, pct=0.0, bg=None,
                 caption="complete", color=None):
        self.app = app
        self.c = app.c
        self._size = size
        self._thickness = thickness
        self._color = color or self.c["primary"]
        self._pct = 0.0
        self._target = max(0.0, min(1.0, pct))
        self._caption = caption
        self._animation = None
        super().__init__(parent, width=size, height=size, bg=bg or parent.cget("bg"),
                         highlightthickness=0, bd=0)
        self._draw(0.0)
        self.after(60, lambda: self.animate_to(self._target))

    def animate_to(self, pct, duration=520):
        pct = max(0.0, min(1.0, pct))
        self._target = pct
        if self._animation is not None:
            try:
                self.after_cancel(self._animation)
            except tk.TclError:
                pass
        start = self._pct
        started = time.perf_counter()
        span = max(0.05, duration / 1000.0)

        def step():
            if not self.winfo_exists():
                return
            t = min(1.0, (time.perf_counter() - started) / span)
            eased = 1 - (1 - t) ** 3
            self._pct = start + (pct - start) * eased
            self._draw(self._pct)
            if t < 1.0:
                self._animation = self.after(16, step)

        step()

    def _draw(self, pct):
        self.delete("all")
        c = self.c
        size = self._size
        thickness = self._thickness
        pad = thickness / 2 + 2
        box = (pad, pad, size - pad, size - pad)
        self.create_oval(*box, outline=c["ring_track"], width=thickness)
        if pct > 0.001:
            extent = -359.99 * pct
            self.create_arc(*box, start=90, extent=extent, style="arc",
                            outline=self._color, width=thickness)
            # cyan shoulder near the leading edge for a subtle "live" feel
            self.create_arc(*box, start=90, extent=max(extent, -10) if extent > -10 else -10,
                            style="arc", outline=c["cyan"], width=max(2, thickness - 5))
            angle = math.radians(90 + extent)
            radius = (size - pad * 2) / 2
            cx = size / 2 + radius * math.cos(angle)
            cy = size / 2 - radius * math.sin(angle)
            dot = max(2.6, thickness * 0.30)
            self.create_oval(cx - dot, cy - dot, cx + dot, cy + dot,
                             fill=c["cyan"], outline="")
        # "100%" is far wider than "7%": shrink the label until it clears the arc
        label = f"{int(round(pct * 100))}%"
        limit = max(40, size - 2 * thickness - 24)
        base = int(size * 0.21)
        if getattr(self, "_probe", None) is None:
            self._probe = tkfont.Font(font=(FONT_FAMILY, base, "bold"))
            self._cap_probe = tkfont.Font(font=(FONT_FAMILY, 9))
            self._probe.configure(size=base)
        self._probe.configure(size=base)
        width = max(1, self._probe.measure(label))
        font_size = base if width <= limit else max(9, int(base * limit / width))
        self.create_text(size / 2, size / 2 - 3, text=label,
                         font=(FONT_FAMILY, font_size, "bold"), fill=c["text"])
        cap_limit = max(34, limit - 10)
        cap_width = max(1, self._cap_probe.measure(self._caption))
        cap_size = 9 if cap_width <= cap_limit else max(6, int(9 * cap_limit / cap_width))
        self.create_text(size / 2, size / 2 + int(size * 0.16), text=self._caption,
                         font=(FONT_FAMILY, cap_size), fill=c["text2"])


class SegmentBar(tk.Canvas):
    """One segment per habit: a HUD-style progress readout."""

    def __init__(self, parent, app, total=0, done=0, height=7, bg=None, gap=5):
        self.app = app
        self.c = app.c
        self._total = max(0, total)
        self._done = max(0, done)
        self._gap = gap
        self._height = height
        super().__init__(parent, height=height, bg=bg or parent.cget("bg"),
                         highlightthickness=0, bd=0)
        self.bind("<Configure>", lambda _e=None: self._draw(animate=False))

    def set_values(self, done, total, animate=True):
        self._done, self._total = max(0, done), max(0, total)
        if animate:
            self._animate(0)
        else:
            self._draw(animate=False)

    def _animate(self, step):
        if not self.winfo_exists():
            return
        self._draw(progress=min(1.0, step / 4))
        if step < 4:
            self.after(30, lambda: self._animate(step + 1))

    def _draw(self, animate=False, progress=1.0):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height() or self._height
        if width < 10:
            return
        if self._total <= 0:
            rrect(self, 0, 0, width, height, height / 2, fill=self.c["track"])
            return
        gap = self._gap
        seg_w = max(3.0, (width - gap * (self._total - 1)) / self._total)
        for index in range(self._total):
            x1 = index * (seg_w + gap)
            filled = index < self._done
            color = self.c["success"] if filled else self.c["track"]
            if filled and progress < 1.0:
                color = mix(self.c["track"], self.c["success"], progress)
            rrect(self, x1, 0, x1 + seg_w, height, height / 2, fill=color)


class WeekBars(tk.Canvas):
    """Seven-day completion chart with an axis, gridlines and value labels."""

    def __init__(self, parent, app, height=168, values=None, labels=None,
                 dates=None, highlight=None, bg=None, show_values=True):
        self.app = app
        self.c = app.c
        self._values = list(values or [])
        self._labels = list(labels or [])
        self._dates = list(dates or [])
        self._highlight = highlight
        self._show_values = show_values
        self._progress = 0.0
        self._bg = bg or parent.cget("bg")
        super().__init__(parent, height=height, bg=self._bg, highlightthickness=0, bd=0)
        self.bind("<Configure>", lambda _e=None: self._draw(self._progress))
        self.after(70, self._animate)

    def set_values(self, values, labels=None, highlight=None, animate=True):
        self._values = list(values)
        if labels is not None:
            self._labels = list(labels)
        self._highlight = highlight
        if animate:
            self._progress = 0.0
            self._animate()
        else:
            self._progress = 1.0
            self._draw(1.0)

    def _animate(self):
        started = time.perf_counter()
        span = 0.55

        def step():
            if not self.winfo_exists():
                return
            t = min(1.0, (time.perf_counter() - started) / span)
            self._progress = t
            self._draw(1 - (1 - t) ** 2.4)
            if t < 1.0:
                self.after(22, step)

        step()

    def _draw(self, progress):
        self.delete("all")
        c = self.c
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 40 or height <= 40 or not self._values:
            return

        axis_w = 26
        top_pad = 20
        bottom_pad = 24
        plot_x0 = axis_w
        plot_x1 = width - 4
        plot_y0 = top_pad
        plot_y1 = height - bottom_pad
        plot_w = max(10, plot_x1 - plot_x0)
        plot_h = max(10, plot_y1 - plot_y0)
        count = len(self._values)
        slot = plot_w / count
        bar_w = min(30, max(9, slot * 0.44))

        # gridlines + axis labels (0 / 50 / 100 keeps it quiet)
        for level in (0, 50, 100):
            y = plot_y1 - (level / 100) * plot_h
            if level:
                self.create_line(plot_x0, y, plot_x1, y, fill=mix(c["border"], self._bg, 0.35),
                                 dash=(2, 6))
            else:
                self.create_line(plot_x0, y, plot_x1, y, fill=c["border"])
            self.create_text(axis_w - 7, y, text=f"{level}", anchor="e",
                             font=(FONT_FAMILY, 8), fill=c["text3"])

        for index, value in enumerate(self._values):
            centre = plot_x0 + slot * index + slot / 2
            is_today = self._highlight == index
            value = max(0, min(100, value))
            # an empty day shows only a quiet stub on the baseline
            if value <= 0:
                rrect(self, centre - bar_w / 2, plot_y1 - 5, centre + bar_w / 2, plot_y1,
                      min(3, bar_w / 2), fill=mix(c["text3"], self._bg, 0.55))
            else:
                bar_h = max(6.0, (value / 100.0) * plot_h * progress)
                top = plot_y1 - bar_h
                if is_today:
                    color = c["primary"]
                elif value >= 100:
                    color = mix(c["primary_d"], c["primary"], 0.72)
                else:
                    color = mix(c["primary_d"], c["primary"], 0.42)
                rrect(self, centre - bar_w / 2, top, centre + bar_w / 2, plot_y1,
                      min(7, bar_w / 2), fill=color)
                if is_today:
                    rrect(self, centre - bar_w / 2, top, centre + bar_w / 2,
                          top + 3, min(2, bar_w / 2), fill=c["cyan"])
            # Only partial days get a number: full bars would collide with the
            # axis and empty days read better without a "0" under every bar.
            if self._show_values and slot >= 30 and progress > 0.8 and 0 < value < 100:
                bar_top = plot_y1 - (value / 100.0) * plot_h * progress
                if bar_top - plot_y0 < 20:
                    self.create_text(centre, bar_top + 12, text=f"{int(round(value))}",
                                     font=(FONT_FAMILY, 8, "bold"), fill="#FFFFFF")
                else:
                    self.create_text(centre, bar_top - 11, text=f"{int(round(value))}",
                                     font=(FONT_FAMILY, 8, "bold"),
                                     fill=c["primary_l"] if is_today else c["text3"])
            label = self._labels[index] if index < len(self._labels) else ""
            self.create_text(centre, plot_y1 + 14, text=label,
                             font=(FONT_FAMILY, 9, "bold" if is_today else "normal"),
                             fill=c["primary_l"] if is_today else c["text2"])

        if not any(self._values):
            self.create_text(plot_x0 + plot_w / 2, plot_y0 + plot_h / 2 - 4,
                             text="No activity logged this week yet",
                             font=(FONT_FAMILY, 9), fill=c["text3"])


class TrendChart(tk.Canvas):
    """Completion trend line with a stippled area fill (no dependencies)."""

    def __init__(self, parent, app, values, labels=None, height=190, color=None, bg=None):
        self.c = app.c
        self._values = list(values)
        self._labels = list(labels or [])
        self._color = color or self.c["primary"]
        self._bg = bg or parent.cget("bg")
        self._progress = 0.0
        super().__init__(parent, height=height, bg=self._bg, highlightthickness=0, bd=0)
        self.bind("<Configure>", lambda _e=None: self._draw(self._progress))
        self.after(80, self._animate)

    def _animate(self):
        started = time.perf_counter()
        span = 0.65

        def step():
            if not self.winfo_exists():
                return
            t = min(1.0, (time.perf_counter() - started) / span)
            self._progress = t
            self._draw(1 - (1 - t) ** 2.5)
            if t < 1.0:
                self.after(24, step)

        step()

    def _draw(self, progress=1.0):
        self.delete("all")
        c = self.c
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 60 or height < 50 or not self._values:
            return
        left, right, top, bottom = 30, 12, 14, 22
        chart_w = width - left - right
        chart_h = height - top - bottom
        count = len(self._values)

        for level in (0, 50, 100):
            y = top + chart_h - (level / 100) * chart_h
            if level:
                self.create_line(left, y, width - right, y,
                                 fill=mix(c["border"], self._bg, 0.35), dash=(2, 6))
            else:
                self.create_line(left, y, width - right, y, fill=c["border"])
            self.create_text(left - 7, y, text=str(level), anchor="e",
                             font=(FONT_FAMILY, 8), fill=c["text3"])

        def point(index, value):
            x = left + (chart_w * index / max(1, count - 1))
            y = top + chart_h - (max(0.0, min(100.0, value)) / 100) * chart_h * progress
            return x, y

        points = [point(index, value) for index, value in enumerate(self._values)]
        if len(points) > 1:
            area = points + [(points[-1][0], top + chart_h), (points[0][0], top + chart_h)]
            self.create_polygon(*[coord for pair in area for coord in pair],
                                fill=mix(self._color, self._bg, 0.78), outline="")
            self.create_line(*[coord for pair in points for coord in pair],
                             fill=self._color, width=2, smooth=True, splinesteps=16,
                             capstyle="round", joinstyle="round")
        for index, (x, y) in enumerate(points):
            last = index == count - 1
            radius = 3.6 if last else 2.0
            if last:
                self.create_oval(x - 8, y - 8, x + 8, y + 8, outline=c["cyan"], width=1)
            self.create_oval(x - radius, y - radius, x + radius, y + radius,
                             fill=self._color if last else self._bg,
                             outline=self._color, width=1.4)
        if progress > 0.9:
            last_x, last_y = points[-1]
            self.create_text(last_x - 12, max(top + 6, last_y - 14),
                             text=f"{int(self._values[-1])}%", anchor="e",
                             font=(FONT_FAMILY, 9, "bold"), fill=c["primary_l"])
        step = max(1, count // 6)
        for index in range(0, count, step):
            x = left + (chart_w * index / max(1, count - 1))
            label = self._labels[index] if index < len(self._labels) else ""
            self.create_text(x, height - 7, text=label,
                             font=(FONT_FAMILY, 8), fill=c["text3"])


# ==================================================================
# NAVIGATION + TILES
# ==================================================================
class NavButton(tk.Canvas):
    """Sidebar navigation item with a clear active indicator."""

    def __init__(self, parent, app, icon, label, command, width=224, height=44):
        self.app = app
        self.c = app.c
        self._icon = icon
        self._label = label
        self._command = command
        self._active = False
        self._hover = False
        super().__init__(parent, width=width, height=height, bg=self.c["sidebar"],
                         highlightthickness=0, bd=0, cursor="hand2")
        self._width = width
        self._height = height
        self.bind("<Button-1>", lambda _e=None: self._command(label))
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._draw()

    def _draw(self):
        self.delete("all")
        c = self.c
        if self._active:
            rrect(self, 0, 0, self._width, self._height, 10, fill=c["side_active"])
            rrect(self, 0, self._height * 0.26, 3, self._height * 0.74, 1.5,
                  fill=c["cyan"])
        elif self._hover:
            rrect(self, 0, 0, self._width, self._height, 10,
                  fill=mix(c["sidebar"], c["side_active"], 0.6))
        icon_color = c["cyan"] if self._active else (
            c["side_text"] if self._hover else c["side_text2"])
        text_color = c["side_text"] if (self._active or self._hover) else c["side_text2"]
        draw_icon(self, self._icon, 22, self._height / 2, size=17,
                  color=icon_color, width=1.8)
        self.create_text(42, self._height / 2 + 0.5, text=self._label, anchor="w",
                         font=(FONT_FAMILY, 11, "bold" if self._active else "normal"),
                         fill=text_color)

    def set_active(self, active):
        self._active = bool(active)
        self._draw()

    def _on_enter(self, _event):
        self._hover = True
        self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._draw()


class StatTile(Card):
    """Compact metric tile: value first, then what it means."""

    def __init__(self, parent, app, icon, color, value, label, hint=None, bg=None):
        super().__init__(parent, app, radius=16, pad=(18, 15), bg=bg, hoverable=True)
        c = self.c
        self._value = value
        self._label = label
        self._hint = hint

        top = tk.Frame(self.body, bg=c["card"])
        top.pack(fill="x")
        self._value_label = tk.Label(top, text=value, bg=c["card"], fg=c["text"],
                                     font=f(22, "bold"), anchor="w")
        self._value_label.pack(side="left")
        icon_box = tk.Canvas(top, width=30, height=30, bg=c["card"],
                             highlightthickness=0, bd=0)
        icon_box.pack(side="right")
        rrect(icon_box, 0, 0, 30, 30, 9, fill=mix(color, c["card"], 0.84))
        draw_icon(icon_box, icon, 15, 15, size=16, color=color, width=1.8)

        tk.Label(self.body, text=label, bg=c["card"], fg=c["text2"], font=f(10),
                 anchor="w").pack(fill="x", pady=(6, 0))
        if hint:
            self._hint_label = tk.Label(self.body, text=hint, bg=c["card"],
                                        fg=c["text3"], font=f(9), anchor="w")
            self._hint_label.pack(fill="x", pady=(1, 0))

    def set_value(self, value, hint=None):
        self._value_label.configure(text=value)
        if hint is not None and getattr(self, "_hint_label", None) is not None:
            self._hint_label.configure(text=hint)


class MilestoneRow(tk.Frame):
    """Compact achievement line with an earned / locked state."""

    def __init__(self, parent, app, item, unlock=False):
        c = app.c
        bg = parent.cget("bg")
        super().__init__(parent, bg=bg)
        earned = bool(item.get("earned"))
        self._c = c
        self._bg = bg
        self._icon_name = item["icon"]
        self._color = c["success"] if earned else c["text3"]
        self._track = mix(c["text3"], bg, 0.78)
        self._target = max(0.0, min(1.0, item.get("fraction", 1.0 if earned else 0.0)))
        self._fraction = 0.0 if unlock else self._target
        self.columnconfigure(1, weight=1)

        self._icon = tk.Canvas(self, width=30, height=30, bg=bg,
                               highlightthickness=0, bd=0)
        self._icon.grid(row=0, column=0, sticky="w", padx=(0, 11))
        rrect(self._icon, 0, 0, 30, 30, 9,
              fill=mix(self._color, bg, 0.84) if earned
              else mix(c["surface3"], bg, 0.5))
        draw_icon(self._icon, item["icon"], 15, 15, size=15, color=self._color,
                  width=1.7 if earned else 1.6)

        text = tk.Frame(self, bg=bg)
        text.grid(row=0, column=1, sticky="ew")
        tk.Label(text, text=item["name"], bg=bg,
                 fg=c["text"] if earned else c["text2"], font=f(10, "bold"),
                 anchor="w").pack(anchor="w")
        tk.Label(text, text=item.get("desc", ""), bg=bg, fg=c["text3"], font=f(9),
                 anchor="w").pack(anchor="w")

        self._bar = tk.Canvas(self, width=58, height=4, bg=bg,
                              highlightthickness=0, bd=0)
        self._bar.grid(row=0, column=2, padx=(14, 12))
        self._bar.bind("<Configure>", lambda _e=None: self._draw_bar())

        tk.Label(self, text="Earned" if earned else item.get("progress", ""), bg=bg,
                 fg=c["success"] if earned else c["text3"],
                 font=f(9, "bold" if earned else "normal"), anchor="e", width=7).grid(
            row=0, column=3, sticky="e")

        if unlock:
            self.after(180, self._play_unlock)

    def _draw_bar(self, fraction=None):
        self._bar.delete("all")
        width = self._bar.winfo_width()
        if width < 4:
            return
        value = self._fraction if fraction is None else fraction
        rrect(self._bar, 0, 0, width, 4, 2, fill=self._track)
        if value > 0:
            rrect(self._bar, 0, 0, max(4, width * max(0.0, min(1.0, value))), 4, 2,
                  fill=self._color)

    def _play_unlock(self):
        """Fill the bar from zero, then pulse the badge once."""
        if not self.winfo_exists():
            return
        steps = 12
        target = self._target

        def step(index):
            if not self.winfo_exists():
                return
            t = index / steps
            self._fraction = target * (1 - (1 - t) ** 3)
            self._draw_bar()
            if index < steps:
                self.after(28, lambda: step(index + 1))
            else:
                self._pulse_badge()

        step(1)

    def _pulse_badge(self):
        sizes = (15, 17, 19, 17, 15)

        def pulse(index):
            if not self._icon.winfo_exists():
                return
            self._icon.delete("pulse")
            draw_icon(self._icon, self._icon_name, 15, 15, size=sizes[index],
                      color=self._color, width=1.9, tags=("pulse",))
            if index + 1 < len(sizes):
                self.after(70, lambda: pulse(index + 1))
            else:
                self._icon.delete("pulse")

        pulse(0)

# ==================================================================
# TOASTS
# ==================================================================
def show_toast(root, message, theme, kind="success", duration=2600):
    """Floating confirmation toast with a short fade in / out."""
    accents = {
        "success": theme["success"],
        "info": theme["primary"],
        "warning": theme["warning"],
        "danger": theme["danger"],
        "xp": theme["cyan"],
    }
    icons = {"success": "check", "info": "info", "warning": "bolt",
             "danger": "close", "xp": "spark"}
    accent = accents.get(kind, theme["success"])
    icon = icons.get(kind, "check")

    try:
        if not root.winfo_exists():
            return
        toast = tk.Toplevel(root)
    except tk.TclError:
        return
    toast.overrideredirect(True)
    try:
        toast.attributes("-topmost", True)
    except tk.TclError:
        pass
    width, height = 372, 62
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    toast.geometry(f"{width}x{height}+{screen_w - width - 28}+{screen_h - height - 64}")
    toast.configure(bg=theme["bg"])

    canvas = tk.Canvas(toast, width=width, height=height, bg=theme["bg"],
                       highlightthickness=0, bd=0)
    canvas.pack()
    rrect(canvas, 1, 1, width - 1, height - 1, 14, fill=theme["toast"])
    rrect(canvas, 1, 1, width - 1, height - 1, 14,
          outline=mix(theme["border"], accent, 0.45), width=1)
    rrect(canvas, 1, 16, 4, height - 16, 1.5, fill=accent)
    draw_icon(canvas, icon, 30, height / 2, size=17, color=accent, width=2)
    canvas.create_text(52, height / 2, text=message, anchor="w",
                       font=(FONT_FAMILY, 11), fill=theme["text"])

    try:
        toast.attributes("-alpha", 0.0)
    except tk.TclError:
        pass

    def fade(step, target, done=None):
        if not toast.winfo_exists():
            return
        try:
            toast.attributes("-alpha", 0.0 if target == 0 else step / 6)
        except tk.TclError:
            pass
        if step < 6:
            toast.after(22, lambda: fade(step + 1, target, done))
        elif done:
            done()

    def dismiss():
        fade(6, 0, lambda: toast.winfo_exists() and toast.destroy())

    fade(0, 1)
    toast.after(duration, dismiss)


# ==================================================================
# CELEBRATIONS - short HUD cards used for streaks and milestones
# ==================================================================
class Celebration(tk.Toplevel):
    """A frameless, fading card with confetti.

    Tk cannot make individual widgets translucent, so this lives in its own
    borderless window: the window alpha fades the card in and out, and on
    Windows the background colour is keyed out so only the rounded card
    shows.  Every effect degrades to a plain card where the platform or the
    window manager does not support it.
    """

    WIDTH = 412
    HEIGHT = 132

    def __init__(self, app, title, subtitle, icon, accent, xp=None, on_close=None,
                 kicker="MILESTONE"):
        self.app = app
        self.c = app.c
        self._on_close = on_close
        self._closed = False
        self._phase = "in"
        self._accent = accent
        self._kicker = kicker
        super().__init__(app.root)
        try:
            self.overrideredirect(True)
            self.attributes("-topmost", True)
        except tk.TclError:
            pass
        try:
            self.attributes("-transparentcolor", self.c["bg"])
        except tk.TclError:
            pass
        self.configure(bg=self.c["bg"])

        root = app.root
        try:
            root.update_idletasks()
            x = root.winfo_rootx() + max(0, root.winfo_width() - self.WIDTH - 28)
            y = root.winfo_rooty() + max(0, root.winfo_height() - self.HEIGHT - 28)
        except tk.TclError:
            x, y = 200, 120
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT,
                                bg=self.c["bg"], highlightthickness=0, bd=0,
                                cursor="hand2")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", lambda _e=None: self.dismiss())

        self._draw_card(title, subtitle, icon, accent, xp)
        self._particles = []
        self._spawn(accent, burst=True)
        self._alpha = 0.0
        self._set_alpha(0.0)
        self._fade_in(0)
        self.after(2350, self._hold_end)
        self.after(28, self._tick)

    # -- drawing -----------------------------------------------------
    def _draw_card(self, title, subtitle, icon, accent, xp):
        c = self.c
        width, height = self.WIDTH, self.HEIGHT
        rrect(self.canvas, 1, 1, width - 1, height - 1, 16, fill=c["card"])
        rrect(self.canvas, 1, 1, width - 1, height - 1, 16,
              outline=mix(c["border"], accent, 0.55), width=1)
        rrect(self.canvas, 1, 16, 4, height - 16, 1.6, fill=accent)

        tile_size = 38
        tile = tk.Canvas(self, width=tile_size, height=tile_size, bg=c["card"],
                         highlightthickness=0, bd=0)
        tile.place(x=20, y=(height - tile_size) / 2)
        rrect(tile, 0, 0, tile_size, tile_size, 12, fill=mix(accent, c["card"], 0.80))
        rrect(tile, 0, 0, tile_size, tile_size, 12,
              outline=mix(accent, c["card"], 0.45), width=1)
        draw_icon(tile, icon, tile_size / 2, tile_size / 2, size=19, color=accent,
                  width=1.8)

        text_x = 74
        self.canvas.create_text(text_x, height / 2 - 22, text=self._kicker, anchor="w",
                                font=(FONT_FAMILY, 8, "bold"), fill=accent)
        self.canvas.create_text(text_x, height / 2 + 1, text=title, anchor="w",
                                font=(FONT_FAMILY, 16, "bold"), fill=c["text"])
        self.canvas.create_text(text_x, height / 2 + 23, text=subtitle, anchor="w",
                                font=(FONT_FAMILY, 9), fill=c["text2"])
        if xp:
            self.canvas.create_text(width - 20, height / 2 + 23, text=xp, anchor="e",
                                    font=(FONT_FAMILY, 9, "bold"), fill=c["success"])

    def _spawn(self, accent, burst=False):
        c = self.c
        palette = [accent, c["cyan"], c["purple_l"], c["warning"], c["success"]]
        # geometry() has not been applied yet, so winfo_width() is still 1 here:
        # seed against the known card size or the burst lands in a 1px column.
        width, height = self.WIDTH, self.HEIGHT
        for _ in range(16 if burst else 3):
            size = random.choice((2, 2, 3, 4))
            x = random.uniform(12, width - 12)
            y = random.uniform(4, height * 0.6) if burst else random.uniform(-14, 4)
            item = self.canvas.create_oval(x, y, x + size, y + size,
                                           fill=random.choice(palette), outline="")
            self._particles.append({
                "id": item, "vx": random.uniform(-0.9, 0.9),
                "vy": random.uniform(0.7, 1.9), "size": size,
            })

    # -- animation ---------------------------------------------------
    def _tick(self):
        if self._closed or not self.winfo_exists():
            return
        height = self.HEIGHT
        alive = []
        for particle in self._particles:
            try:
                self.canvas.move(particle["id"], particle["vx"], particle["vy"])
                coords = self.canvas.coords(particle["id"])
            except tk.TclError:
                continue
            particle["vy"] += 0.16
            particle["vx"] *= 0.995
            if coords and (coords[2] < -4 or coords[0] > self.WIDTH + 4):
                self.canvas.delete(particle["id"])
                continue
            if coords and coords[1] > height + 8:
                if self._phase == "hold":
                    x = random.uniform(10, self.WIDTH - 10)
                    self.canvas.coords(particle["id"], x, -6, x + particle["size"],
                                       -6 + particle["size"])
                    particle["vy"] = random.uniform(0.7, 1.7)
                    particle["vx"] = random.uniform(-0.7, 0.7)
                    alive.append(particle)
                else:
                    self.canvas.delete(particle["id"])
            else:
                alive.append(particle)
        self._particles = alive
        if self._phase == "hold" and len(self._particles) < 10:
            self._spawn(self._accent)
        self.after(30, self._tick)

    def _set_alpha(self, value):
        try:
            self.attributes("-alpha", max(0.0, min(1.0, value)))
        except tk.TclError:
            pass

    def _fade_in(self, step):
        if self._closed or not self.winfo_exists():
            return
        self._set_alpha(step / 6)
        if step < 6:
            self.after(24, lambda: self._fade_in(step + 1))
        else:
            self._phase = "hold"

    def _hold_end(self):
        self._phase = "out"
        self._fade_out(6)

    def _fade_out(self, step):
        if self._closed or not self.winfo_exists():
            return
        self._set_alpha(step / 6)
        if step > 0:
            self.after(22, lambda: self._fade_out(step - 1))
        else:
            self.dismiss()

    def dismiss(self):
        if self._closed:
            return
        self._closed = True
        try:
            self.destroy()
        except tk.TclError:
            pass
        if self._on_close:
            self._on_close()

# ==================================================================
# FORM CONTROLS
# ==================================================================
def configure_ttk(root, theme):
    """Theme the ttk widgets Tk does not paint itself (comboboxes)."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(
        "HF.TCombobox",
        fieldbackground=theme["surface2"],
        background=theme["surface2"],
        foreground=theme["text"],
        arrowcolor=theme["text2"],
        bordercolor=theme["border"],
        lightcolor=theme["surface2"],
        darkcolor=theme["surface2"],
        insertcolor=theme["text"],
        padding=7,
    )
    style.map(
        "HF.TCombobox",
        fieldbackground=[("readonly", theme["surface2"]), ("active", theme["surface2"])],
        foreground=[("readonly", theme["text"])],
        bordercolor=[("focus", theme["primary"])],
        arrowcolor=[("active", theme["primary_l"]), ("pressed", theme["primary"])],
    )
    root.option_add("*TCombobox*Listbox.background", theme["surface2"])
    root.option_add("*TCombobox*Listbox.foreground", theme["text"])
    root.option_add("*TCombobox*Listbox.selectBackground", theme["primary"])
    root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")
    root.option_add("*TCombobox*Listbox.font", f(10))


class Switch(tk.Canvas):
    """Small animated on/off switch."""

    def __init__(self, parent, app, value=False, command=None, width=46, height=26, bg=None):
        self.app = app
        self.c = app.c
        self._value = bool(value)
        self._command = command
        self._width = width
        self._height = height
        self._position = 1.0 if value else 0.0
        super().__init__(parent, width=width, height=height, bg=bg or parent.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Button-1>", self._on_click)
        self._draw(self._position)

    def _draw(self, position):
        self.delete("all")
        c = self.c
        track = mix(c["surface3"], c["primary"], position)
        rrect(self, 1, 1, self._width - 1, self._height - 1, (self._height - 2) / 2,
              fill=track)
        rrect(self, 1, 1, self._width - 1, self._height - 1, (self._height - 2) / 2,
              outline=mix(c["border"], c["primary"], position * 0.7), width=1)
        radius = (self._height - 8) / 2
        centre = 4 + radius + position * (self._width - 8 - radius * 2)
        self.create_oval(centre - radius, self._height / 2 - radius,
                         centre + radius, self._height / 2 + radius,
                         fill="#FFFFFF" if self._value else c["text3"], outline="")

    def _on_click(self, _event):
        self._value = not self._value
        target = 1.0 if self._value else 0.0
        steps = 5
        start = self._position

        def step(index):
            if not self.winfo_exists():
                return
            self._position = start + (target - start) * (index / steps)
            self._draw(self._position)
            if index < steps:
                self.after(18, lambda: step(index + 1))

        step(1)
        if self._command:
            self._command(self._value)

    def get(self):
        return self._value


class ChoiceChip(tk.Canvas):
    """Selectable chip used for categories, filters and weekday toggles."""

    def __init__(self, parent, app, text, color=None, selected=False, command=None,
                 height=28, font_size=9, bg=None, dot=False, width=None, radius=None):
        self.app = app
        self.c = app.c
        self._text = text
        self._color = color or self.c["primary"]
        self._selected = selected
        self._command = command
        self._height = height
        self._font = (FONT_FAMILY, font_size, "bold" if selected else "normal")
        self._dot = dot
        self._host = bg or parent.cget("bg")
        text_width = tkfont.Font(font=(FONT_FAMILY, font_size, "bold")).measure(text)
        self._width = width or int(text_width + (36 if dot else 24))
        self._radius = radius or height / 2
        super().__init__(parent, width=self._width, height=height, bg=self._host,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda _e=None: self._draw(hover=True))
        self.bind("<Leave>", lambda _e=None: self._draw(hover=False))
        self._draw()

    def _draw(self, hover=False):
        self.delete("all")
        c = self.c
        self._font = (FONT_FAMILY, self._font[1], "bold" if self._selected else "normal")
        if self._selected:
            rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5, self._radius,
                  fill=mix(self._color, self._host, 0.78),
                  outline=mix(self._color, self._host, 0.35), width=1)
        else:
            rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5, self._radius,
                  fill=mix(self._host, c["surface2"], 0.85) if hover else None,
                  outline=mix(c["border"], self._color, 0.3 if hover else 0.0), width=1)
        fg = self._color if (self._selected or hover) else c["text2"]
        if not self._selected and not hover:
            fg = c["text2"]
        text_x = self._width / 2
        if self._dot:
            self.create_oval(12, self._height / 2 - 3, 18, self._height / 2 + 3,
                             fill=self._color, outline="")
            text_x = 20 + (self._width - 20) / 2
        self.create_text(text_x, self._height / 2 + 0.5, text=self._text,
                         font=self._font, fill=fg)

    def set_selected(self, selected):
        self._selected = bool(selected)
        self._draw()

    def _on_click(self, _event):
        if self._command:
            self._command(self._text)


# ==================================================================
# HABIT DIALOG
# ==================================================================
class TaskDialog(tk.Toplevel):
    """Modal dialog to create or edit a habit (same fields as v1)."""

    def __init__(self, parent, app, task=None):
        super().__init__(parent)
        self.app = app
        self.c = app.c
        self.result = None
        self.task = task
        is_edit = task is not None

        self.title("Edit habit" if is_edit else "New habit")
        self.configure(bg=self.c["bg"])
        self.resizable(False, False)
        self.transient(parent)
        try:
            self.grab_set()
        except tk.TclError:
            pass

        self._build(is_edit)
        if is_edit:
            self._populate()

        self.update_idletasks()
        self._centre_on(parent)
        self.bind("<Escape>", lambda _e=None: self.destroy())
        self.bind("<Return>", self._on_return)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()

    # -- helpers -----------------------------------------------------
    def _centre_on(self, parent):
        try:
            px, py = parent.winfo_rootx(), parent.winfo_rooty()
            pw, ph = parent.winfo_width(), parent.winfo_height()
        except tk.TclError:
            return
        self.geometry(f"+{px + max(0, (pw - self.winfo_reqwidth()) // 2)}"
                      f"+{py + max(0, (ph - self.winfo_reqheight()) // 3)}")

    def _label(self, parent, text):
        return tk.Label(parent, text=text, bg=self.c["bg"], fg=self.c["text2"],
                        font=f(9, "bold"), anchor="w")

    def _entry(self, parent, textvariable):
        c = self.c
        wrap = tk.Frame(parent, bg=c["surface2"], highlightthickness=1,
                        highlightbackground=c["border"], highlightcolor=c["border"])
        entry = tk.Entry(wrap, textvariable=textvariable, bg=c["surface2"],
                         fg=c["text"], insertbackground=c["text"], relief="flat",
                         bd=0, font=f(11), highlightthickness=0,
                         selectbackground=c["primary"], selectforeground="#FFFFFF")
        entry.pack(fill="x", padx=12, pady=10)
        entry.bind("<FocusIn>", lambda _e=None: wrap.configure(highlightbackground=c["primary"]))
        entry.bind("<FocusOut>", lambda _e=None: wrap.configure(highlightbackground=c["border"]))
        return wrap, entry

    # -- build -------------------------------------------------------
    def _build(self, is_edit):
        c = self.c
        outer = tk.Frame(self, bg=c["bg"], padx=26, pady=22)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=c["bg"])
        header.pack(fill="x")
        tile = tk.Canvas(header, width=42, height=42, bg=c["bg"], highlightthickness=0, bd=0)
        tile.pack(side="left")
        rrect(tile, 0, 0, 42, 42, 12, fill=c["primary_soft"])
        rrect(tile, 0, 0, 42, 42, 12, outline=mix(c["primary"], c["bg"], 0.5), width=1)
        draw_icon(tile, "pencil" if is_edit else "plus", 21, 21, size=20,
                  color=c["primary_l"], width=2)

        title_box = tk.Frame(header, bg=c["bg"])
        title_box.pack(side="left", padx=13)
        tk.Label(title_box, text="Edit habit" if is_edit else "New habit",
                 bg=c["bg"], fg=c["text"], font=f(16, "bold"),
                 anchor="w").pack(anchor="w")
        tk.Label(title_box,
                 text="Update the details of this habit." if is_edit
                 else "Small, repeatable, and yours.",
                 bg=c["bg"], fg=c["text2"], font=f(10), anchor="w").pack(anchor="w")
        IconButton(header, self.app, "close", command=self.destroy, size=30,
                   icon_size=15, bg=c["bg"]).pack(side="right", pady=5)

        hairline(outer, self.app, pady=(16, 4))

        body = tk.Frame(outer, bg=c["bg"])
        body.pack(fill="both", expand=True)

        self._label(body, "Habit name").pack(fill="x", pady=(10, 6))
        self.v_name = tk.StringVar()
        name_wrap, self.e_name = self._entry(body, self.v_name)
        name_wrap.pack(fill="x")
        self.lbl_error = tk.Label(body, text="", bg=c["bg"], fg=c["danger"],
                                  font=f(9), anchor="w")
        self.lbl_error.pack(fill="x", pady=(2, 0))

        self._label(body, "Category").pack(fill="x", pady=(10, 6))
        cat_grid = tk.Frame(body, bg=c["bg"])
        cat_grid.pack(fill="x")
        self.v_cat = tk.StringVar(value="Other")
        self._cat_chips = []
        for index, category in enumerate(CATEGORIES):
            chip = ChoiceChip(cat_grid, self.app, category,
                              color=cat_color(category, c), dot=True, bg=c["bg"],
                              height=30,
                              command=lambda name: self._select_category(name))
            chip.grid(row=index // 4, column=index % 4, padx=(0, 8), pady=4, sticky="w")
            self._cat_chips.append(chip)

        row = tk.Frame(body, bg=c["bg"])
        row.pack(fill="x", pady=(6, 0))
        left = tk.Frame(row, bg=c["bg"])
        left.pack(side="left", fill="x", expand=True, padx=(0, 12))
        right = tk.Frame(row, bg=c["bg"])
        right.pack(side="left", fill="x", expand=True)

        self._label(left, "Daily target (optional)").pack(fill="x", pady=(10, 6))
        self.v_target = tk.StringVar()
        target_wrap, _target_entry = self._entry(left, self.v_target)
        target_wrap.pack(fill="x")

        self._label(right, "Repeat").pack(fill="x", pady=(10, 6))
        self.v_rec = tk.StringVar(value="Daily")
        self.combo = ttk.Combobox(right, textvariable=self.v_rec,
                                  values=RECURRENCE_OPTIONS, state="readonly",
                                  style="HF.TCombobox", font=f(10))
        self.combo.pack(fill="x", ipady=3)
        self.combo.bind("<<ComboboxSelected>>", lambda _e=None: self._sync_custom_days())

        self.days_row = tk.Frame(body, bg=c["bg"])
        self.day_vars = []
        self._day_chips = []
        for index, day in enumerate(WEEKDAY_NAMES):
            var = tk.BooleanVar()
            self.day_vars.append(var)
            chip = ChoiceChip(self.days_row, self.app, day, bg=c["bg"], height=28,
                              width=54,
                              command=lambda name, i=index: self._toggle_day(i))
            chip.grid(row=0, column=index, padx=(0, 5), pady=2)
            self._day_chips.append(chip)

        self._label(body, "Notes (optional)").pack(fill="x", pady=(12, 6))
        notes_wrap = tk.Frame(body, bg=c["surface2"], highlightthickness=1,
                              highlightbackground=c["border"])
        notes_wrap.pack(fill="x")
        self.t_notes = tk.Text(notes_wrap, height=3, bg=c["surface2"], fg=c["text"],
                               insertbackground=c["text"], relief="flat", bd=0,
                               font=f(10), wrap="word", padx=10, pady=9,
                               highlightthickness=0,
                               selectbackground=c["primary"], selectforeground="#FFFFFF")
        self.t_notes.pack(fill="x")
        self.t_notes.bind("<FocusIn>",
                          lambda _e=None: notes_wrap.configure(highlightbackground=c["primary"]))
        self.t_notes.bind("<FocusOut>",
                          lambda _e=None: notes_wrap.configure(highlightbackground=c["border"]))

        pin_row = tk.Frame(body, bg=c["bg"])
        pin_row.pack(fill="x", pady=(16, 0))
        self.v_pin = tk.BooleanVar(value=False)
        Switch(pin_row, self.app, value=False, bg=c["bg"],
               command=lambda value: self.v_pin.set(value)).pack(side="left")
        pin_text = tk.Frame(pin_row, bg=c["bg"])
        pin_text.pack(side="left", padx=12)
        tk.Label(pin_text, text="Pin to top", bg=c["bg"], fg=c["text"],
                 font=f(10, "bold"), anchor="w").pack(anchor="w")
        tk.Label(pin_text, text="Keep this habit at the top of today's list",
                 bg=c["bg"], fg=c["text3"], font=f(9), anchor="w").pack(anchor="w")

        hairline(outer, self.app, pady=(18, 12))

        footer = tk.Frame(outer, bg=c["bg"])
        footer.pack(fill="x")
        HoverButton(footer, self.app, "Save habit", command=self._save, icon="check",
                    kind="primary", bg=c["bg"], height=38, padx=18).pack(side="right")
        HoverButton(footer, self.app, "Cancel", command=self.destroy, kind="ghost",
                    bg=c["bg"], height=38, padx=16).pack(side="right", padx=(0, 8))
        tk.Label(footer, text="Enter to save   ·   Esc to cancel", bg=c["bg"],
                 fg=c["text3"], font=f(9)).pack(side="left")

    # -- state -------------------------------------------------------
    def _select_category(self, category):
        self.v_cat.set(category)
        for chip in self._cat_chips:
            chip.set_selected(chip._text == category)

    def _toggle_day(self, index):
        var = self.day_vars[index]
        var.set(not var.get())
        self._day_chips[index].set_selected(var.get())

    def _sync_custom_days(self):
        if self.v_rec.get() == "Custom Days":
            if not self.days_row.winfo_ismapped():
                self.days_row.pack(fill="x", pady=(10, 0))
                for index, chip in enumerate(self._day_chips):
                    chip.set_selected(self.day_vars[index].get())
        elif self.days_row.winfo_ismapped():
            self.days_row.pack_forget()

    def _populate(self):
        task = self.task
        self.v_name.set(task.get("name", ""))
        self._select_category(task.get("category", "Other"))
        self.v_target.set(task.get("daily_target", ""))
        self.v_rec.set(task.get("recurrence", "Daily"))
        self.v_pin.set(bool(task.get("pinned", False)))
        self.t_notes.delete("1.0", "end")
        self.t_notes.insert("1.0", task.get("notes", ""))
        for index, var in enumerate(self.day_vars):
            var.set(index in task.get("recurrence_days", []))
            self._day_chips[index].set_selected(var.get())
        self.combo.set(self.v_rec.get())
        self._sync_custom_days()
        self.e_name.focus_set()
        self.e_name.icursor("end")

    def _on_return(self, _event):
        if isinstance(self.focus_get(), tk.Text):
            return None
        self._save()
        return "break"

    def _save(self):
        name = self.v_name.get().strip()
        if not name:
            self.lbl_error.configure(text="Please give this habit a name.")
            self.e_name.focus_set()
            return
        recurrence = self.v_rec.get()
        recurrence_days = ([i for i, var in enumerate(self.day_vars) if var.get()]
                           if recurrence == "Custom Days" else [])
        if recurrence == "Custom Days" and not recurrence_days:
            self.lbl_error.configure(
                text="Pick at least one weekday, or choose another repeat option.")
            return
        self.lbl_error.configure(text="")
        self.result = {
            "name": name,
            "category": self.v_cat.get(),
            "daily_target": self.v_target.get().strip(),
            "notes": self.t_notes.get("1.0", "end-1c").strip(),
            "recurrence": recurrence,
            "recurrence_days": recurrence_days,
            "pinned": bool(self.v_pin.get()),
        }
        self.destroy()


# ==================================================================
# HABIT ROW
# ==================================================================
class HabitRow(Card):
    """A single habit rendered as a clean, aligned row.

    Layout: completion control | name + metadata | actions.  Completed
    habits keep their full readability - no strikethrough - and change
    state through the check, the border and a small "Done" pill.
    """

    def __init__(self, parent, app, task, done=False, stats=None, on_toggle=None,
                 on_edit=None, on_delete=None, compact=False, show_actions=True):
        self.app = app
        self.task = task
        self._done = bool(done)
        self._stats = stats or {}
        self._on_toggle = on_toggle
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._compact = compact
        self._color = cat_color(task.get("category"), app.c)
        self._done_color = app.c["success"]
        pad = (14, 10) if compact else (16, 13)
        super().__init__(parent, app, radius=14, pad=pad,
                         accent=self._done_color if self._done else self._color,
                         bg=parent.cget("bg"), hoverable=True)
        self._build(show_actions)
        self._apply_state(animate=False)

    # -- construction -------------------------------------------------
    def _build(self, show_actions):
        c = self.c
        body = self.body
        body.columnconfigure(1, weight=1)
        name_size = 11 if self._compact else 12

        self._check = CheckCircle(
            body, self.app, checked=self._done, color=self._done_color,
            command=self._toggle, size=26, bg=c["card"],
        )
        self._check.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 14))

        title = tk.Frame(body, bg=c["card"])
        title.grid(row=0, column=1, sticky="ew")
        self._name = tk.Label(title, text=self.task["name"], bg=c["card"], fg=c["text"],
                              font=f(name_size, "bold"), anchor="w")
        self._name.pack(side="left")
        if self.task.get("pinned"):
            pin = tk.Canvas(title, width=16, height=16, bg=c["card"],
                            highlightthickness=0, bd=0)
            pin.pack(side="left", padx=(7, 0))
            draw_icon(pin, "pin", 8, 8, size=12, color=c["text3"], width=1.6)

        self._done_pill = None
        streak = int((self._stats or {}).get("streak", 0) or 0)
        if streak > 0 and not self._compact:
            self._streak_pill = Pill(title, self.app, f"{streak}d", color=c["warning"],
                                     icon="flame", bg=c["card"], height=20, size=8)
            self._streak_pill.pack(side="left", padx=(8, 0))
        else:
            self._streak_pill = None

        actions = tk.Frame(body, bg=c["card"])
        actions.grid(row=0, column=2, rowspan=2, sticky="e", padx=(10, 0))
        if show_actions and self._on_edit:
            IconButton(actions, self.app, "pencil",
                       command=lambda: self._on_edit(self.task), size=28,
                       icon_size=14, bg=c["card"], color=c["text3"],
                       hover_color=c["primary_l"]).pack(side="left")
        if show_actions and self._on_delete:
            IconButton(actions, self.app, "trash",
                       command=lambda: self._on_delete(self.task), size=28,
                       icon_size=14, bg=c["card"], color=c["text3"],
                       hover_color=c["danger"]).pack(side="left", padx=(2, 0))

        meta = tk.Frame(body, bg=c["card"])
        meta.grid(row=1, column=1, columnspan=2 if not show_actions else 1,
                  sticky="ew", pady=(7, 0))
        Pill(meta, self.app, self.task.get("category", "Other"), dot=True,
             color=self._color, bg=c["card"], height=20, size=8).pack(side="left",
                                                                     padx=(0, 6))
        if self.task.get("daily_target"):
            Pill(meta, self.app, self.task["daily_target"], color=c["text2"],
                 icon="clock", bg=c["card"], height=20, size=8).pack(side="left",
                                                                    padx=(0, 6))
        if self.task.get("recurrence") and self.task["recurrence"] != "Daily" \
                and not self._compact:
            Pill(meta, self.app, self.task["recurrence"], color=c["text2"],
                 bg=c["card"], height=20, size=8).pack(side="left", padx=(0, 6))

        self._notes = None
        note = (self.task.get("notes") or "").strip()
        if note and not self._compact:
            self._notes_font = tkfont.Font(font=f(9))
            self._notes = tk.Label(meta, text="", bg=c["card"], fg=c["text3"],
                                   font=f(9), anchor="w")
            self._notes.pack(side="left", fill="x", expand=True, padx=(2, 0))
            self._notes.bind("<Configure>", self._on_notes_configure)
        self._notes_text = note

    def _on_notes_configure(self, event):
        if self._notes is None:
            return
        text = elide("·  " + self._notes_text, self._notes_font, max(20, event.width - 2))
        if self._notes.cget("text") != text:
            self._notes.configure(text=text)

    # -- state --------------------------------------------------------
    def _apply_state(self, animate=False):
        c = self.c
        self._check.set_checked(self._done, animate=animate)
        self._name.configure(fg=c["text2"] if self._done else c["text"])
        self.set_accent(self._done_color if self._done else self._color)
        self.set_border(mix(c["border"], c["success"], 0.4) if self._done else c["border"])
        self._base_border = self._border
        if self._done:
            if self._done_pill is None:
                self._done_pill = Pill(self._name.master, self.app, "Done",
                                       color=c["success"], bg=c["card"], height=20,
                                       size=8)
            self._done_pill.pack(side="left", padx=(8, 0), before=None)
            if self._streak_pill is not None:
                self._streak_pill.pack_forget()
                self._streak_pill.pack(side="left", padx=(8, 0), after=self._done_pill)
        else:
            if self._done_pill is not None:
                self._done_pill.pack_forget()
            if self._streak_pill is not None:
                self._streak_pill.pack(side="left", padx=(8, 0))

    def set_done(self, done, stats=None, animate=True):
        self._done = bool(done)
        if stats is not None:
            self._stats = stats
        self._apply_state(animate=animate)
        streak = int((self._stats or {}).get("streak", 0) or 0)
        if self._streak_pill is not None:
            for child in self._streak_pill.master.winfo_children():
                pass
        if self._streak_pill is not None and streak > 0:
            self._rebuild_streak_pill(streak)

    def _rebuild_streak_pill(self, streak):
        pill = self._streak_pill
        try:
            pill.destroy()
        except tk.TclError:
            return
        self._streak_pill = Pill(pill.master, self.app, f"{streak}d",
                                 color=self.c["warning"], icon="flame",
                                 bg=self.c["card"], height=20, size=8)
        self._streak_pill.pack(side="left", padx=(8, 0))

    def _toggle(self):
        if not self._on_toggle:
            return
        new_state = self._on_toggle(self.task)
        self.set_done(new_state, stats=self.app.dm.habit_stats(self.task, 30))

# ==================================================================
# VIEW HELPERS
# ==================================================================
class ViewHelpersMixin:
    """Shared page scaffolding so every view uses the same rhythm."""

    def _page(self, subtitle=None):
        c = self.c
        scroll = ScrollableFrame(self.content, c["bg"], padding=0,
                                 track=mix(c["bg"], "#FFFFFF", 0.05),
                                 thumb=mix(c["bg"], "#FFFFFF", 0.18))
        scroll.pack(fill="both", expand=True)
        page = tk.Frame(scroll.inner, bg=c["bg"])
        page.pack(fill="both", expand=True)
        return scroll, page

    def _page_header(self, page, title, subtitle=None, action=None):
        """Title block. Returns the header frame."""
        c = self.c
        header = tk.Frame(page, bg=c["bg"])
        header.pack(fill="x", padx=PAGE_PAD, pady=(28, 0))
        text = tk.Frame(header, bg=c["bg"])
        text.pack(side="left")
        title_label = tk.Label(text, text=title, bg=c["bg"], fg=c["text"],
                               font=f(26, "bold"), anchor="w")
        title_label.pack(anchor="w")
        subtitle_label = None
        if subtitle:
            subtitle_label = tk.Label(text, text=subtitle, bg=c["bg"],
                                      fg=c["text2"], font=f(11), anchor="w")
            subtitle_label.pack(anchor="w", pady=(3, 0))
        if action is not None:
            action(header)
        header.title_label = title_label
        header.subtitle_label = subtitle_label
        return header

    def _section_title(self, parent, text, meta=None, padx=PAGE_PAD, pady=(26, 10)):
        c = self.c
        row = tk.Frame(parent, bg=c["bg"])
        row.pack(fill="x", padx=padx, pady=pady)
        tk.Label(row, text=text, bg=c["bg"], fg=c["text"], font=f(13, "bold"),
                 anchor="w").pack(side="left")
        if meta:
            tk.Label(row, text=meta, bg=c["bg"], fg=c["text3"], font=f(10),
                     anchor="e").pack(side="right")
        return row

    def _empty_state(self, parent, bg, title, description, button_text=None,
                     command=None, icon="spark"):
        c = self.c
        box = tk.Frame(parent, bg=bg)
        box.pack(fill="x", pady=26)
        canvas = tk.Canvas(box, width=54, height=54, bg=bg, highlightthickness=0, bd=0)
        canvas.pack()
        rrect(canvas, 0, 0, 54, 54, 16, fill=mix(c["primary"], bg, 0.86))
        draw_icon(canvas, icon, 27, 27, size=23, color=c["primary_l"], width=1.7)
        tk.Label(box, text=title, bg=bg, fg=c["text"], font=f(12, "bold")).pack(pady=(10, 3))
        tk.Label(box, text=description, bg=bg, fg=c["text2"], font=f(10),
                 wraplength=360, justify="center").pack()
        if button_text and command:
            HoverButton(box, self, button_text, command=command, icon="plus",
                        kind="soft", bg=bg, height=34, font_size=9).pack(pady=(14, 0))

    def _responsive_grid(self, container, widgets, min_width, gap=12, uniform="tile",
                         max_cols=None):
        """Re-flow tiles into as many columns as the width allows."""
        state = {"cols": 0}

        def apply(_event=None):
            try:
                width = container.winfo_width()
            except tk.TclError:
                return
            if width <= 1:
                return
            limit = min(len(widgets), max_cols or len(widgets))
            fit = max(1, min(limit, int((width + gap) // (min_width + gap)) or 1))
            # prefer a column count that divides the tiles evenly, so the last
            # row is never a lonely orphan tile.
            cols = fit
            for candidate in range(fit, 0, -1):
                if len(widgets) % candidate == 0:
                    cols = candidate
                    break
            if cols == state["cols"]:
                return
            state["cols"] = cols
            for widget in widgets:
                widget.grid_forget()
            for column in range(8):
                container.columnconfigure(column, weight=0, uniform="")
            for column in range(cols):
                container.columnconfigure(column, weight=1, uniform=uniform)
            for index, widget in enumerate(widgets):
                row, column = divmod(index, cols)
                widget.grid(row=row, column=column, sticky="nsew",
                            padx=(0 if column == 0 else gap, 0),
                            pady=(0 if row == 0 else gap, 0))

        container.bind("<Configure>", apply)
        container.after(16, apply)


# ==================================================================
# DASHBOARD
# ==================================================================
class DashboardViewMixin(ViewHelpersMixin):

    def _greeting(self):
        hour = datetime.now().hour
        if hour < 5:
            return "Late night focus"
        if hour < 12:
            return "Good morning"
        if hour < 17:
            return "Good afternoon"
        if hour < 22:
            return "Good evening"
        return "Winding down"

    def _score_status(self, pct):
        if pct >= 1.0:
            return "Flawless day", self.c["success"]
        if pct >= 0.8:
            return "Elite progress", self.c["primary_l"]
        if pct >= 0.5:
            return "Strong momentum", self.c["primary"]
        if pct > 0:
            return "Warming up", self.c["warning"]
        return "Ready when you are", self.c["text2"]

    def _achievements(self):
        dm = self.dm
        best = dm.best_streak()
        total = dm.total_checkins()
        perfect = dm.perfect_days_total()
        _xp, level, _lname, _in, _for = dm.get_xp_info()
        consistency = dm.consistency(30)
        return [
            {"icon": "spark", "name": "First light", "desc": "Complete your first habit",
             "earned": total >= 1, "progress": f"{min(total, 1)}/1", "fraction": min(total, 1)},
            {"icon": "flame", "name": "Week of fire", "desc": "7 perfect days in a row",
             "earned": best >= 7, "progress": f"{min(best, 7)}/7", "fraction": best / 7},
            {"icon": "trophy", "name": "Perfect day", "desc": "Finish every habit in a day",
             "earned": perfect >= 1, "progress": f"{min(perfect, 1)}/1",
             "fraction": min(perfect, 1)},
            {"icon": "target", "name": "Steady month", "desc": "80% consistency over 30 days",
             "earned": consistency >= 0.8 and total >= 20,
             "progress": f"{int(round(consistency * 100))}%",
             "fraction": min(1.0, consistency / 0.8)},
            {"icon": "bolt", "name": "Level 5", "desc": "Reach level five",
             "earned": level >= 5, "progress": f"L{level}/5", "fraction": level / 5},
            {"icon": "layers", "name": "Century", "desc": "100 habit check-ins",
             "earned": total >= 100, "progress": f"{min(total, 100)}/100",
             "fraction": min(1.0, total / 100)},
        ]

    def _view_dashboard(self):
        c = self.c
        scroll, page = self._page()
        self._dashboard = {}
        self._dashboard_rows = {}

        tasks = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        total = len(tasks)
        done = sum(1 for t in tasks if t["id"] in done_ids)
        pct = done / total if total else 0.0
        streak = self.dm.calculate_streak()

        # -- header --------------------------------------------------
        today = date.today()

        def header_action(parent):
            HoverButton(parent, self, "New habit", command=self._open_add_task,
                        icon="plus", kind="primary", bg=c["bg"], height=38,
                        padx=18).pack(side="right")

        date_line = (f"{WEEKDAY_FULL[today.weekday()]}, "
                     f"{today.strftime('%d %B %Y')}")
        header = self._page_header(
            page, self._greeting(),
            f"{date_line}  ·  {self._day_phrase(done, total)}",
            header_action,
        )
        self._dashboard["subtitle"] = header.subtitle_label
        self._dashboard["date_line"] = date_line

        # -- hero ----------------------------------------------------
        hero = Card(page, self, radius=CARD_RADIUS + 2, pad=(24, 20),
                    border=mix(c["border"], c["primary"], 0.30))
        hero.pack(fill="x", padx=PAGE_PAD, pady=(SECTION_GAP + 4, 0))
        hero.body.columnconfigure(1, weight=1)

        ring = ProgressRing(hero.body, self, size=142, thickness=10, pct=pct,
                            bg=c["card"], caption="of today's habits")
        ring.grid(row=0, column=0, rowspan=3, sticky="w", padx=(0, 30))

        tk.Label(hero.body, text="TODAY'S PROGRESS", bg=c["card"], fg=c["cyan"],
                 font=(FONT_FAMILY, 9, "bold"), anchor="w").grid(
            row=0, column=1, sticky="w")

        count_row = tk.Frame(hero.body, bg=c["card"])
        count_row.grid(row=1, column=1, sticky="ew", pady=(4, 0))
        count_label = tk.Label(count_row,
                               text=f"{done} of {total}" if total else "No habits yet",
                               bg=c["card"], fg=c["text"], font=f(24, "bold"),
                               anchor="w")
        count_label.pack(side="left")
        tk.Label(count_row, text="completed" if total else "",
                 bg=c["card"], fg=c["text2"], font=f(11), anchor="w").pack(
            side="left", padx=(8, 0), pady=(8, 0))
        status_text, status_color = self._score_status(pct)
        status_label = tk.Label(count_row, text=status_text, bg=c["card"],
                                fg=status_color, font=f(10, "bold"))
        status_label.pack(side="left", padx=(16, 0), pady=(9, 0))

        segments = SegmentBar(hero.body, self, total=total, done=done, height=7,
                              bg=c["card"])
        segments.grid(row=2, column=1, sticky="ew", pady=(10, 0))
        segments.configure(width=1)

        detail_row = tk.Frame(hero.body, bg=c["card"])
        detail_row.grid(row=3, column=1, sticky="ew", pady=(9, 0))
        remaining = max(0, total - done)
        detail_label = tk.Label(
            detail_row,
            text=(f"{remaining} habit{'s' if remaining != 1 else ''} remaining  ·  "
                  f"+{done * XP_PER_TASK} XP earned today") if total
            else "Add your first habit to start today's score",
            bg=c["card"], fg=c["text3"], font=f(10), anchor="w")
        detail_label.pack(side="left")

        actions = tk.Frame(hero.body, bg=c["card"])
        actions.grid(row=4, column=1, sticky="w", pady=(16, 0))
        primary_action = HoverButton(actions, self, "Continue today's habits",
                                     command=lambda: self._show("Habits"),
                                     icon="arrow-right", kind="primary",
                                     bg=c["card"], height=38, padx=18)
        primary_action.pack(side="left")
        mark_all = HoverButton(actions, self, "Complete all", kind="ghost",
                               command=self._shortcut_mark_all, icon="check",
                               bg=c["card"], height=38, font_size=10)
        mark_all.pack(side="left", padx=(6, 0))
        mark_all.set_enabled(bool(total) and done < total)

        self._dashboard.update({
            "ring": ring, "count": count_label, "status": status_label,
            "segments": segments, "detail": detail_label, "mark_all": mark_all,
            "total": total, "done": done,
        })

        # -- metric strip -------------------------------------------
        week = self.dm.get_week_pcts()
        week_avg = round(sum(week) / 7) if week else 0
        _xp, level, level_name, xp_in, xp_for = self.dm.get_xp_info()
        best = self.dm.best_streak()

        strip = tk.Frame(page, bg=c["bg"])
        strip.pack(fill="x", padx=PAGE_PAD, pady=(SECTION_GAP - 2, 0))
        tiles = [
            StatTile(strip, self, "flame", c["warning"], str(streak),
                     "Day streak", f"best {best}", bg=c["bg"]),
            StatTile(strip, self, "trophy", c["primary_l"], str(best),
                     "Best streak", "personal record", bg=c["bg"]),
            StatTile(strip, self, "chart", c["accent"], f"{week_avg}%",
                     "This week", "Mon – Sun", bg=c["bg"]),
            StatTile(strip, self, "bolt", c["purple_l"], f"L{level}",
                     "Level", f"{level_name} · {xp_in}/{xp_for} XP", bg=c["bg"]),
        ]
        self._responsive_grid(strip, tiles, min_width=190, gap=12, max_cols=4)
        self._dashboard["tiles"] = {"streak": tiles[0], "week": tiles[2],
                                    "level": tiles[3]}

        # -- body: habits + week ------------------------------------
        body = tk.Frame(page, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=PAGE_PAD, pady=(SECTION_GAP, 0))
        body.columnconfigure(0, weight=3, uniform="body")
        body.columnconfigure(1, weight=2, uniform="body")

        focus = Card(body, self, radius=CARD_RADIUS, pad=(20, 18))
        focus.grid(row=0, column=0, sticky="nsew", padx=(0, SECTION_GAP))

        head = tk.Frame(focus.body, bg=c["card"])
        head.pack(fill="x")
        tk.Label(head, text="Today's habits", bg=c["card"], fg=c["text"],
                 font=f(13, "bold"), anchor="w").pack(side="left")
        self._dashboard["pill"] = Pill(
            head, self, f"{done}/{total}" if total else "0", color=c["primary"],
            bg=c["card"], filled=False, height=22, size=9)
        self._dashboard["pill"].pack(side="right")
        tk.Label(focus.body, text="Pinned habits stay at the top", bg=c["card"],
                 fg=c["text3"], font=f(9), anchor="w").pack(anchor="w", pady=(3, 12))

        if not tasks:
            self._empty_state(focus.body, c["card"], "Nothing scheduled today",
                              "Add a habit, or change a habit's repeat setting to "
                              "see it here.", "Add a habit", self._open_add_task)
        else:
            rows_holder = tk.Frame(focus.body, bg=c["card"])
            rows_holder.pack(fill="x")
            for task in tasks[:6]:
                row = HabitRow(rows_holder, self, task, task["id"] in done_ids,
                               stats=self.dm.habit_stats(task, 30),
                               on_toggle=self._toggle_task, compact=False,
                               show_actions=False)
                row.pack(fill="x", pady=(0, 8))
                self._dashboard_rows[task["id"]] = row
            if len(tasks) > 6:
                tk.Label(rows_holder, text=f"+{len(tasks) - 6} more habits today",
                         bg=c["card"], fg=c["text3"], font=f(9), anchor="w").pack(
                    anchor="w", pady=(2, 0))
            footer = tk.Frame(focus.body, bg=c["card"])
            footer.pack(fill="x", pady=(10, 0))
            view_all = tk.Label(footer, text="Open habit list", bg=c["card"],
                                fg=c["primary_l"], font=f(10, "bold"), cursor="hand2",
                                anchor="w")
            view_all.pack(side="left")
            view_all.bind("<Button-1>", lambda _e=None: self._show("Habits"))
            draw_arrow = tk.Canvas(footer, width=16, height=16, bg=c["card"],
                                   highlightthickness=0, bd=0)
            draw_arrow.pack(side="left", padx=(4, 0))
            draw_icon(draw_arrow, "arrow-right", 8, 8, size=13,
                      color=c["primary_l"], width=1.8)

        right = tk.Frame(body, bg=c["bg"])
        right.grid(row=0, column=1, sticky="nsew")

        week_card = Card(right, self, radius=CARD_RADIUS, pad=(20, 18))
        week_card.pack(fill="x")
        week_head = tk.Frame(week_card.body, bg=c["card"])
        week_head.pack(fill="x")
        tk.Label(week_head, text="This week", bg=c["card"], fg=c["text"],
                 font=f(13, "bold"), anchor="w").pack(side="left")
        self._dashboard["week_avg"] = tk.Label(
            week_head, text=f"{week_avg}% avg", bg=c["card"], fg=c["primary_l"],
            font=f(10, "bold"), anchor="e")
        self._dashboard["week_avg"].pack(side="right")
        labels = [day.strftime("%a") for day in self.dm.get_week_dates()]
        bars = WeekBars(week_card.body, self, height=170, values=week,
                        labels=labels, highlight=today.weekday(), bg=c["card"])
        bars.pack(fill="x", pady=(12, 0))
        tk.Label(week_card.body, text="Completion rate per day · today highlighted",
                 bg=c["card"], fg=c["text3"], font=f(9), anchor="w").pack(
            anchor="w", pady=(8, 0))
        self._dashboard["bars"] = bars

        # milestones: deliberately not another card, to break the grid up
        milestones = tk.Frame(right, bg=c["bg"])
        milestones.pack(fill="x", pady=(SECTION_GAP + 2, 0))
        milestone_head = tk.Frame(milestones, bg=c["bg"])
        milestone_head.pack(fill="x")
        tk.Label(milestone_head, text="Milestones", bg=c["bg"], fg=c["text"],
                 font=f(13, "bold"), anchor="w").pack(side="left")
        items = self._achievements()
        earned_count = sum(1 for item in items if item["earned"])
        tk.Label(milestone_head, text=f"{earned_count} of {len(items)} earned",
                 bg=c["bg"], fg=c["text3"], font=f(10), anchor="e").pack(side="right")
        hairline(milestones, self, pady=(8, 8))
        self._milestone_holder = tk.Frame(milestones, bg=c["bg"])
        self._milestone_holder.pack(fill="x")
        self._render_milestones(self._milestone_holder, limit=4)

        # -- quote ---------------------------------------------------
        quote, author = self.dm.get_daily_quote()
        quote_card = Card(page, self, radius=CARD_RADIUS, pad=(22, 16),
                          border=mix(c["border"], c["purple"], 0.25))
        quote_card.pack(fill="x", padx=PAGE_PAD, pady=(SECTION_GAP + 4, 28))
        mark = tk.Canvas(quote_card.body, width=24, height=24, bg=c["card"],
                         highlightthickness=0, bd=0)
        mark.pack(side="left", padx=(0, 14))
        draw_icon(mark, "spark", 12, 12, size=16, color=c["purple_l"], width=1.6)
        text_box = tk.Frame(quote_card.body, bg=c["card"])
        text_box.pack(side="left", fill="x", expand=True)
        tk.Label(text_box, text=f"“{quote}”", bg=c["card"], fg=c["text"],
                 font=f(11, "normal", "italic"), anchor="w", justify="left",
                 wraplength=780).pack(anchor="w")
        tk.Label(text_box, text=author, bg=c["card"], fg=c["text3"], font=f(9),
                 anchor="w").pack(anchor="w", pady=(3, 0))

    def _day_phrase(self, done, total):
        if not total:
            return "no habits scheduled"
        if done >= total:
            return "every habit complete"
        return f"{total - done} habit{'s' if total - done != 1 else ''} left today"

    def _render_milestones(self, parent, limit=None, unlock=()):
        for child in parent.winfo_children():
            child.destroy()
        items = self._achievements()
        shown = items if limit is None else items[:limit]
        unlock = set(unlock or ())
        for item in shown:
            row = MilestoneRow(parent, self, item, unlock=item["name"] in unlock)
            row.pack(fill="x", pady=3)

    # -- live updates -------------------------------------------------
    def _refresh_dashboard_progress(self):
        state = self._dashboard
        if not state:
            return
        tasks = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        total = len(tasks)
        done = sum(1 for t in tasks if t["id"] in done_ids)
        pct = done / total if total else 0.0
        streak = self.dm.calculate_streak()
        status_text, status_color = self._score_status(pct)
        remaining = max(0, total - done)

        state["ring"].animate_to(pct, duration=380)
        state["count"].configure(text=f"{done} of {total}" if total else "No habits yet")
        state["status"].configure(text=status_text, fg=status_color)
        state["segments"].set_values(done, total)
        state["detail"].configure(
            text=(f"{remaining} habit{'s' if remaining != 1 else ''} remaining  ·  "
                  f"+{done * XP_PER_TASK} XP earned today") if total
            else "Add your first habit to start today's score")
        state["mark_all"].set_enabled(bool(total) and done < total)

        if state.get("subtitle") is not None:
            state["subtitle"].configure(
                text=f"{state.get('date_line', '')}  ·  "
                     f"{self._day_phrase(done, total)}")
        if state.get("pill") is not None:
            state["pill"].set_text(f"{done}/{total}" if total else "0")
        tiles = state.get("tiles") or {}
        if tiles.get("streak") is not None:
            tiles["streak"].set_value(str(streak), hint=f"best {self.dm.best_streak()}")
        week = self.dm.get_week_pcts()
        week_avg = round(sum(week) / 7) if week else 0
        if state.get("week_avg") is not None:
            state["week_avg"].configure(text=f"{week_avg}% avg")
        if tiles.get("week") is not None:
            tiles["week"].set_value(f"{week_avg}%")
        if state.get("bars") is not None:
            state["bars"].set_values(week, highlight=date.today().weekday())
        if getattr(self, "_milestone_holder", None) is not None:
            try:
                if self._milestone_holder.winfo_exists():
                    self._render_milestones(self._milestone_holder, limit=4)
            except tk.TclError:
                pass

        for task in tasks:
            row = self._dashboard_rows.get(task["id"])
            if row is not None:
                row.set_done(task["id"] in done_ids,
                             stats=self.dm.habit_stats(task, 30), animate=False)
        self._draw_streak_chip()


# ==================================================================
# HABITS LIST
# ==================================================================
class HabitsViewMixin(ViewHelpersMixin):

    def _view_habits(self):
        # This view does not scroll as a page: the habit list has its own
        # scroll region and fills the window, so there is no dead space below.
        c = self.c
        self._task_scroll = None
        self._habit_rows = {}

        page = tk.Frame(self.content, bg=c["bg"])
        page.pack(fill="both", expand=True)

        tasks = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        done = sum(1 for t in tasks if t["id"] in done_ids)

        header = tk.Frame(page, bg=c["bg"])
        header.pack(fill="x", padx=PAGE_PAD, pady=(26, 0))
        text = tk.Frame(header, bg=c["bg"])
        text.pack(side="left")
        tk.Label(text, text="Habits", bg=c["bg"], fg=c["text"], font=f(26, "bold"),
                 anchor="w").pack(anchor="w")
        tk.Label(text, text="Create, edit and complete the routines that run your day",
                 bg=c["bg"], fg=c["text2"], font=f(11), anchor="w").pack(
            anchor="w", pady=(3, 0))
        HoverButton(header, self, "New habit", command=self._open_add_task, icon="plus",
                    kind="primary", bg=c["bg"], height=38, padx=18).pack(side="right")

        toolbar = tk.Frame(page, bg=c["bg"])
        toolbar.pack(fill="x", padx=PAGE_PAD, pady=(SECTION_GAP + 2, 0))

        search_wrap = tk.Frame(toolbar, bg=c["surface2"], width=430, height=40,
                               highlightthickness=1, highlightbackground=c["border"])
        search_wrap.pack(side="left")
        search_wrap.pack_propagate(False)
        search_icon = tk.Canvas(search_wrap, width=34, height=38, bg=c["surface2"],
                                highlightthickness=0, bd=0)
        search_icon.pack(side="left", padx=(8, 0))
        draw_icon(search_icon, "search", 8, 19, size=15, color=c["text3"], width=1.7)
        self._search_entry = tk.Entry(
            search_wrap, textvariable=self._search_var, bg=c["surface2"],
            fg=c["text"], insertbackground=c["text"], relief="flat", bd=0,
            font=f(10), highlightthickness=0, readonlybackground=c["surface2"],
            selectbackground=c["primary"], selectforeground="#FFFFFF",
        )
        self._search_entry.pack(side="left", fill="both", expand=True, padx=(6, 12))

        self._habit_mark_all = HoverButton(
            toolbar, self, "Complete all", command=self._shortcut_mark_all,
            icon="check", kind="soft", height=40, font_size=10, bg=c["bg"])
        self._habit_mark_all.pack(side="right")

        filters = tk.Frame(page, bg=c["bg"])
        filters.pack(fill="x", padx=PAGE_PAD, pady=(12, 0))
        self._filter_chips = {}
        for category in ["All"] + CAT_LIST:
            color = c["primary"] if category == "All" else cat_color(category, c)
            chip = ChoiceChip(filters, self, category, color=color,
                              selected=self._filter_cat.get() == category,
                              bg=c["bg"], height=28, font_size=9)
            chip.bind("<Button-1>",
                      lambda _e, cat=category: self._set_cat_filter(cat), add="+")
            chip.pack(side="left", padx=(0, 6))
            self._filter_chips[category] = chip

        summary = tk.Frame(page, bg=c["bg"])
        summary.pack(fill="x", padx=PAGE_PAD, pady=(18, 10))
        self._habit_counts_label = tk.Label(
            summary, text=self._habit_header_text(tasks, done), bg=c["bg"],
            fg=c["text"], font=f(13, "bold"), anchor="w")
        self._habit_counts_label.pack(side="left")

        bar_holder = tk.Frame(summary, bg=c["bg"], width=200, height=6)
        bar_holder.pack(side="right", pady=(7, 0))
        bar_holder.pack_propagate(False)
        self._habit_segments = SegmentBar(bar_holder, self, total=len(tasks),
                                          done=done, height=6, bg=c["bg"], gap=4)
        self._habit_segments.pack(fill="both", expand=True)

        list_card = Card(page, self, radius=CARD_RADIUS, pad=(12, 12))
        list_card.pack(fill="both", expand=True, padx=PAGE_PAD, pady=(0, 26))
        self._task_scroll = ScrollableFrame(list_card.body, c["card"], padding=0,
                                            track=c["card"], thumb=c["border_hi"])
        self._task_scroll.pack(fill="both", expand=True)
        self._render_habit_list()
        self._update_habit_header()

    def _habit_header_text(self, tasks=None, done=None):
        tasks = self.dm.get_scheduled_today() if tasks is None else tasks
        done_ids = self.dm.get_completed_today()
        done = sum(1 for t in tasks if t["id"] in done_ids) if done is None else done
        if not tasks:
            return "No habits scheduled today"
        return f"{done} of {len(tasks)} habits complete"

    def _update_habit_header(self):
        tasks = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        done = sum(1 for t in tasks if t["id"] in done_ids)
        label = getattr(self, "_habit_counts_label", None)
        if label is not None:
            try:
                label.configure(text=self._habit_header_text(tasks, done))
            except tk.TclError:
                pass
        segments = getattr(self, "_habit_segments", None)
        if segments is not None:
            try:
                segments.set_values(done, len(tasks), animate=False)
            except tk.TclError:
                pass
        mark_all = getattr(self, "_habit_mark_all", None)
        if mark_all is not None:
            mark_all.set_enabled(bool(tasks) and done < len(tasks))

    def _set_cat_filter(self, category):
        self._filter_cat.set(category)
        for name, chip in getattr(self, "_filter_chips", {}).items():
            chip.set_selected(name == category)
        self._render_habit_list()

    def _on_search_changed(self):
        if self._active_view == "Habits" and self._task_scroll is not None:
            try:
                if self._task_scroll.winfo_exists():
                    self._render_habit_list()
            except tk.TclError:
                pass

    def _clear_filters(self):
        self._search_var.set("")
        self._filter_cat.set("All")
        self._set_cat_filter("All")

    def _render_habit_list(self):
        if self._task_scroll is None:
            return
        try:
            if not self._task_scroll.winfo_exists():
                return
            inner = self._task_scroll.inner
        except tk.TclError:
            return

        for widget in inner.winfo_children():
            widget.destroy()
        self._habit_rows = {}

        c = self.c
        tasks = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        query = self._search_var.get().strip().lower()
        category = self._filter_cat.get()

        visible = tasks
        if query:
            visible = [t for t in visible
                       if query in t["name"].lower()
                       or query in t.get("notes", "").lower()
                       or query in t.get("category", "").lower()]
        if category != "All":
            visible = [t for t in visible if t.get("category") == category]

        if not tasks:
            holder = tk.Frame(inner, bg=c["card"])
            holder.pack(fill="x", padx=8, pady=6)
            self._empty_state(holder, c["card"], "Nothing scheduled today",
                              "Every habit is either unscheduled for today or not "
                              "created yet. Add one to get started.",
                              "New habit", self._open_add_task)
            return
        if not visible:
            holder = tk.Frame(inner, bg=c["card"])
            holder.pack(fill="x", padx=8, pady=6)
            self._empty_state(holder, c["card"], "No habits match",
                              "Try a different search term or clear the category "
                              "filter.", "Clear filters", self._clear_filters,
                              icon="search")
            return

        pinned = [t for t in visible if t.get("pinned")]
        others = [t for t in visible if not t.get("pinned")]

        def section(title, items, show_header=True):
            if not items:
                return
            if show_header:
                head = tk.Frame(inner, bg=c["card"])
                head.pack(fill="x", padx=8, pady=(10, 6))
                if title == "Pinned":
                    icon = tk.Canvas(head, width=14, height=14, bg=c["card"],
                                     highlightthickness=0, bd=0)
                    icon.pack(side="left", padx=(0, 6))
                    draw_icon(icon, "pin", 7, 7, size=12, color=c["text3"], width=1.6)
                tk.Label(head, text=title, bg=c["card"], fg=c["text3"],
                         font=(FONT_FAMILY, 9, "bold"), anchor="w").pack(side="left")
                tk.Label(head, text=str(len(items)), bg=c["card"], fg=c["text3"],
                         font=f(9), anchor="w").pack(side="left", padx=(7, 0))
            for task in items:
                row = HabitRow(
                    inner, self, task, task["id"] in done_ids,
                    stats=self.dm.habit_stats(task, 30),
                    on_toggle=self._toggle_task,
                    on_edit=self._open_edit_task,
                    on_delete=self._delete_task,
                )
                row.pack(fill="x", padx=8, pady=(0, 8))
                self._habit_rows[task["id"]] = row

        if pinned:
            section("PINNED", pinned)
            section("TODAY", others, show_header=True)
        else:
            section("TODAY", others, show_header=False)
        tk.Frame(inner, bg=c["card"], height=6).pack()

# ==================================================================
# STATISTICS
# ==================================================================
class StatsViewMixin(ViewHelpersMixin):

    def _view_stats(self):
        c = self.c
        scroll, page = self._page()
        today = date.today()
        week = self.dm.get_week_pcts()
        month_all = self.dm.get_month_pcts()
        elapsed = today.day
        month_elapsed = month_all[:elapsed]
        week_avg = round(sum(week) / len(week)) if week else 0
        month_avg = round(sum(month_elapsed) / len(month_elapsed)) if month_elapsed else 0
        perfect_month = self.dm.perfect_days_in_month()
        perfect_total = self.dm.perfect_days_total()
        streak = self.dm.calculate_streak()
        best = self.dm.best_streak()
        xp, level, level_name, xp_in, xp_for = self.dm.get_xp_info()
        consistency = self.dm.consistency(30)

        self._page_header(
            page, "Performance",
            f"{today.strftime('%B %Y')}  ·  {elapsed} days logged this month  ·  "
            f"{perfect_total} perfect days all time",
        )

        strip = tk.Frame(page, bg=c["bg"])
        strip.pack(fill="x", padx=PAGE_PAD, pady=(SECTION_GAP + 2, 0))
        tiles = [
            StatTile(strip, self, "chart", c["primary_l"], f"{week_avg}%",
                     "Weekly average", "Mon – Sun", bg=c["bg"]),
            StatTile(strip, self, "target", c["accent"], f"{month_avg}%",
                     "Monthly average", "elapsed days", bg=c["bg"]),
            StatTile(strip, self, "trophy", c["success"], str(perfect_month),
                     "Perfect days", "this month", bg=c["bg"]),
            StatTile(strip, self, "flame", c["warning"], str(streak),
                     "Current streak", f"best {best}", bg=c["bg"]),
            StatTile(strip, self, "spark", c["purple_l"],
                     f"{int(round(consistency * 100))}%", "30-day consistency",
                     "average rate", bg=c["bg"]),
            StatTile(strip, self, "bolt", c["primary_l"], f"{xp:,}",
                     "Total XP", f"L{level} {level_name}  ·  {xp_in}/{xp_for}",
                     bg=c["bg"]),
        ]
        self._responsive_grid(strip, tiles, min_width=235, gap=12, max_cols=3)

        # -- week + achievements ------------------------------------
        body = tk.Frame(page, bg=c["bg"])
        body.pack(fill="x", padx=PAGE_PAD, pady=(SECTION_GAP, 0))
        body.columnconfigure(0, weight=3, uniform="stats")
        body.columnconfigure(1, weight=2, uniform="stats")
        body.rowconfigure(0, weight=1)

        week_card = Card(body, self, radius=CARD_RADIUS, pad=(20, 18))
        week_card.grid(row=0, column=0, sticky="nsew", padx=(0, SECTION_GAP))
        head = tk.Frame(week_card.body, bg=c["card"])
        head.pack(fill="x")
        tk.Label(head, text="Last 7 days", bg=c["card"], fg=c["text"],
                 font=f(13, "bold"), anchor="w").pack(side="left")
        tk.Label(head, text=f"{week_avg}% average", bg=c["card"], fg=c["primary_l"],
                 font=f(10, "bold"), anchor="e").pack(side="right")
        labels = [day.strftime("%a") for day in self.dm.get_week_dates()]
        chart_holder = tk.Frame(week_card.body, bg=c["card"], height=196)
        chart_holder.pack(fill="both", expand=True, pady=(10, 0))
        chart_holder.pack_propagate(False)
        WeekBars(chart_holder, self, height=196, values=week, labels=labels,
                 highlight=today.weekday(), bg=c["card"]).pack(fill="both", expand=True)
        tk.Label(week_card.body, text="Completion rate per day · today highlighted",
                 bg=c["card"], fg=c["text3"], font=f(9), anchor="w").pack(
            anchor="w", pady=(8, 0))

        achievements_card = Card(body, self, radius=CARD_RADIUS, pad=(20, 18))
        achievements_card.grid(row=0, column=1, sticky="nsew")
        items = self._achievements()
        head = tk.Frame(achievements_card.body, bg=c["card"])
        head.pack(fill="x", pady=(0, 8))
        tk.Label(head, text="Achievements", bg=c["card"], fg=c["text"],
                 font=f(13, "bold"), anchor="w").pack(side="left")
        tk.Label(head, text=f"{sum(1 for i in items if i['earned'])}/{len(items)}",
                 bg=c["card"], fg=c["text2"], font=f(10), anchor="e").pack(side="right")
        for item in items:
            MilestoneRow(achievements_card.body, self, item).pack(fill="x", pady=3)
        missing = [i for i in items if not i["earned"]]
        if missing:
            hairline(achievements_card.body, self, pady=(10, 8))
            nxt = missing[0]
            tk.Label(achievements_card.body,
                     text=f"Next up  ·  {nxt['name']} — {nxt['desc']}",
                     bg=c["card"], fg=c["text3"], font=f(9), anchor="w",
                     justify="left", wraplength=280).pack(anchor="w")

        # -- month trend --------------------------------------------
        trend_card = Card(page, self, radius=CARD_RADIUS, pad=(20, 18))
        trend_card.pack(fill="x", padx=PAGE_PAD, pady=(SECTION_GAP, 0))
        head = tk.Frame(trend_card.body, bg=c["card"])
        head.pack(fill="x")
        tk.Label(head, text=f"Month trend  ·  {today.strftime('%B')}", bg=c["card"],
                 fg=c["text"], font=f(13, "bold"), anchor="w").pack(side="left")
        tk.Label(head, text=f"{month_avg}% average", bg=c["card"], fg=c["accent"],
                 font=f(10, "bold"), anchor="e").pack(side="right")
        if any(value > 0 for value in month_elapsed):
            TrendChart(trend_card.body, self, month_elapsed,
                       labels=[str(index + 1) for index in range(len(month_elapsed))],
                       height=200, bg=c["card"]).pack(fill="x", pady=(10, 0))
        else:
            tk.Label(trend_card.body,
                     text="Complete a few habits to see your month take shape.",
                     bg=c["card"], fg=c["text3"], font=f(10), anchor="w").pack(
                anchor="w", pady=24)

        # -- per-habit consistency ----------------------------------
        consistency_card = Card(page, self, radius=CARD_RADIUS, pad=(20, 18))
        consistency_card.pack(fill="x", padx=PAGE_PAD, pady=(SECTION_GAP, 28))
        head = tk.Frame(consistency_card.body, bg=c["card"])
        head.pack(fill="x", pady=(0, 6))
        tk.Label(head, text="Habit consistency", bg=c["card"], fg=c["text"],
                 font=f(13, "bold"), anchor="w").pack(side="left")
        tk.Label(head, text="last 30 days", bg=c["card"], fg=c["text3"],
                 font=f(10), anchor="e").pack(side="right")

        tasks = sorted(self.dm.data["tasks"],
                       key=lambda t: self.dm.habit_stats(t, 30)["rate"], reverse=True)
        if not tasks:
            tk.Label(consistency_card.body,
                     text="No habits yet — add one to start tracking.",
                     bg=c["card"], fg=c["text3"], font=f(10), anchor="w").pack(
                anchor="w", pady=10)
        for task in tasks:
            stats = self.dm.habit_stats(task, 30)
            color = cat_color(task.get("category"), c)
            row = tk.Frame(consistency_card.body, bg=c["card"])
            row.pack(fill="x", pady=5)
            row.columnconfigure(1, weight=1)

            dot = tk.Canvas(row, width=10, height=10, bg=c["card"],
                            highlightthickness=0, bd=0)
            dot.grid(row=0, column=0, padx=(0, 9))
            rrect(dot, 0, 0, 10, 10, 3, fill=color)

            name = tk.Label(row, text=task["name"], bg=c["card"], fg=c["text"],
                            font=f(10), anchor="w")
            name.grid(row=0, column=1, sticky="ew")

            ratio = tk.Label(row, text=f"{int(round(stats['rate'] * 100))}%",
                             bg=c["card"], fg=c["text2"], font=f(10, "bold"),
                             width=5, anchor="e")
            ratio.grid(row=0, column=3, padx=(10, 0))

            bar = tk.Canvas(row, height=6, bg=c["card"], highlightthickness=0, bd=0)
            bar.grid(row=0, column=2, sticky="ew", padx=(16, 0))
            row.columnconfigure(2, weight=1)

            def draw(_event=None, canvas=bar, fraction=stats["rate"], fill=color):
                canvas.delete("all")
                width = canvas.winfo_width()
                if width < 4:
                    return
                rrect(canvas, 0, 0, width, 6, 3, fill=c["track"])
                if fraction > 0:
                    rrect(canvas, 0, 0, max(6, width * fraction), 6, 3, fill=fill)

            bar.bind("<Configure>", draw)
            tk.Label(row, text=f"{stats['done']}/{stats['scheduled']} due",
                     bg=c["card"], fg=c["text3"], font=f(9), anchor="e").grid(
                row=0, column=4, padx=(12, 0))


# ==================================================================
# CALENDAR
# ==================================================================
class CalendarViewMixin(ViewHelpersMixin):

    def _view_calendar(self):
        c = self.c
        scroll, page = self._page()
        self._page_header(page, "Calendar",
                          "Every day you showed up, at a glance")

        card = Card(page, self, radius=CARD_RADIUS, pad=(22, 18))
        card.pack(fill="both", expand=True, padx=PAGE_PAD, pady=(SECTION_GAP + 4, 28))

        head = tk.Frame(card.body, bg=c["card"])
        head.pack(fill="x")
        self.lbl_cal_month = tk.Label(head, text="", bg=c["card"], fg=c["text"],
                                      font=f(15, "bold"), anchor="w")
        self.lbl_cal_month.pack(side="left")

        controls = tk.Frame(head, bg=c["card"])
        controls.pack(side="right")
        HoverButton(controls, self, "Today", command=self._cal_today, kind="ghost",
                    height=32, font_size=9, bg=c["card"]).pack(side="left",
                                                               padx=(0, 6))
        for icon, command in (("chevron-left", self._cal_prev),
                              ("chevron-right", self._cal_next)):
            IconButton(controls, self, icon, command=command, size=32, icon_size=15,
                       bg=c["card"]).pack(side="left", padx=(2, 0))

        self.lbl_cal_summary = tk.Label(card.body, text="", bg=c["card"],
                                        fg=c["text3"], font=f(10), anchor="w")
        self.lbl_cal_summary.pack(fill="x", pady=(6, 14))

        self.cal_grid_frame = tk.Frame(card.body, bg=c["card"])
        self.cal_grid_frame.pack(fill="both", expand=True)

        legend = tk.Frame(card.body, bg=c["card"])
        legend.pack(fill="x", pady=(16, 0))
        for label, color in (("Perfect", c["success"]), ("Partial", c["warning"]),
                             ("Missed", c["danger"]), ("No habits", c["text3"]),
                             ("Upcoming", c["border_hi"])):
            item = tk.Frame(legend, bg=c["card"])
            item.pack(side="left", padx=(0, 18))
            dot = tk.Canvas(item, width=8, height=8, bg=c["card"],
                            highlightthickness=0, bd=0)
            dot.pack(side="left", padx=(0, 6))
            rrect(dot, 0, 0, 8, 8, 2.5, fill=color)
            tk.Label(item, text=label, bg=c["card"], fg=c["text3"],
                     font=f(9)).pack(side="left")

        self._cal_year = tk.IntVar(value=date.today().year)
        self._cal_month = tk.IntVar(value=date.today().month)
        self._render_calendar()

    def _render_calendar(self):
        if not hasattr(self, "cal_grid_frame"):
            return
        try:
            if not self.cal_grid_frame.winfo_exists():
                return
        except tk.TclError:
            return
        for widget in self.cal_grid_frame.winfo_children():
            widget.destroy()

        c = self.c
        year = self._cal_year.get()
        month = self._cal_month.get()
        today = date.today()
        self.lbl_cal_month.configure(text=f"{cal_module.month_name[month]} {year}")
        days_in_month = cal_module.monthrange(year, month)[1]
        first_weekday = cal_module.monthrange(year, month)[0]

        for index, name in enumerate(WEEKDAY_NAMES):
            tk.Label(self.cal_grid_frame, text=name.upper(), bg=c["card"],
                     fg=c["text3"], font=(FONT_FAMILY, 8, "bold")).grid(
                row=0, column=index, sticky="w", padx=6, pady=(0, 8))
            self.cal_grid_frame.columnconfigure(index, weight=1, uniform="cal")

        row, column = 1, first_weekday
        perfect = partial = missed = 0
        for day_number in range(1, days_in_month + 1):
            day = date(year, month, day_number)
            scheduled = self.dm.get_scheduled_for(day)
            pct = self.dm.completion_pct(day)
            future = day > today
            if future:
                state = "future"
            elif not scheduled:
                state = "none"
            elif pct >= 1.0:
                state = "perfect"
                perfect += 1
            elif pct > 0:
                state = "partial"
                partial += 1
            else:
                state = "missed"
                missed += 1
            cell = CalendarCell(self.cal_grid_frame, self, day_number, state, pct,
                                day == today, c["card"])
            cell.grid(row=row, column=column, sticky="nsew", padx=3, pady=3)
            column += 1
            if column == 7:
                column = 0
                row += 1

        label = self._cal_month_summary(year, month, perfect, partial, missed)
        if hasattr(self, "lbl_cal_summary"):
            try:
                self.lbl_cal_summary.configure(text=label)
            except tk.TclError:
                pass

    @staticmethod
    def _cal_month_summary(year, month, perfect, partial, missed):
        if date(year, month, 1) > date.today():
            return "This month has not started yet."
        return f"{perfect} perfect  ·  {partial} partial  ·  {missed} missed"

    def _shift_month(self, delta):
        month = self._cal_month.get() + delta
        year = self._cal_year.get()
        while month < 1:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1
        self._cal_month.set(month)
        self._cal_year.set(year)
        self._render_calendar()

    def _cal_prev(self):
        self._shift_month(-1)

    def _cal_next(self):
        self._shift_month(1)

    def _cal_today(self):
        self._cal_year.set(date.today().year)
        self._cal_month.set(date.today().month)
        self._render_calendar()


class CalendarCell(tk.Canvas):
    """One day cell of the history calendar."""

    HEIGHT = 68
    STATES = {
        "perfect": ("success", 0.80),
        "partial": ("warning", 0.84),
        "missed": ("danger", 0.93),
        "none": ("surface3", 0.55),
        "future": ("surface", 0.80),
    }

    def __init__(self, parent, app, day, state, pct, is_today, bg):
        self.app = app
        self.c = app.c
        self._day = day
        self._state = state
        self._pct = pct
        self._today = is_today
        super().__init__(parent, height=self.HEIGHT, bg=bg, highlightthickness=0, bd=0)
        self.bind("<Configure>", lambda _e=None: self._draw())

    def _draw(self):
        self.delete("all")
        c = self.c
        width = self.winfo_width()
        height = self.HEIGHT
        if width < 8:
            return
        color_key, ratio = self.STATES.get(self._state, ("surface3", 0.5))
        fill = mix(c[color_key], c["card"], ratio)
        outline = c["primary"] if self._today else mix(fill, c["border"], 0.6)
        rrect(self, 1, 1, width - 1, height - 1, 10, fill=fill)
        rrect(self, 1, 1, width - 1, height - 1, 10, outline=outline,
              width=1.5 if self._today else 1)

        text_color = (c["primary_l"] if self._today else
                      c[color_key] if self._state in ("perfect", "partial")
                      else c["text3"])
        self.create_text(10, 10, text=str(self._day), anchor="nw",
                         font=(FONT_FAMILY, 9, "bold" if self._today else "normal"),
                         fill=text_color)

        if self._state == "perfect":
            draw_icon(self, "check", width - 17, height - 16, size=14,
                      color=c["success"], width=2.2)
        elif self._state == "partial":
            self.create_text(width - 9, height - 9, text=f"{int(round(self._pct * 100))}%",
                             anchor="se", font=(FONT_FAMILY, 8, "bold"),
                             fill=c["warning"])
        elif self._state == "missed":
            self.create_oval(width - 16, height - 16, width - 10, height - 10,
                             fill=mix(c["danger"], fill, 0.25), outline="")
        elif self._today:
            self.create_text(width - 9, height - 9, text="today", anchor="se",
                             font=(FONT_FAMILY, 8, "bold"), fill=c["primary_l"])


# ==================================================================
# SETTINGS
# ==================================================================
class SettingsViewMixin(ViewHelpersMixin):

    def _view_settings(self):
        c = self.c
        scroll, page = self._page()
        self._page_header(page, "Settings",
                          "Everything stays on this device — no account, no sync")

        self._settings_section(page, "Appearance")
        appearance = Card(page, self, radius=CARD_RADIUS, pad=(20, 18))
        appearance.pack(fill="x", padx=PAGE_PAD)
        row = tk.Frame(appearance.body, bg=c["card"])
        row.pack(fill="x")
        IconTile(row, self, "sun" if self._theme_name == "dark" else "moon",
                 color=c["primary_l"], size=36, bg=c["card"]).pack(side="left")
        text_box = tk.Frame(row, bg=c["card"])
        text_box.pack(side="left", padx=14)
        tk.Label(text_box, text="Color theme", bg=c["card"], fg=c["text"],
                 font=f(11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(text_box, text="Dark command center, or a lighter workspace",
                 bg=c["card"], fg=c["text3"], font=f(10), anchor="w").pack(anchor="w")
        Segmented(row, self, ["Dark", "Light"],
                  "Dark" if self._theme_name == "dark" else "Light",
                  command=lambda label: self._apply_theme(label.lower()),
                  bg=c["card"], option_width=86, height=32).pack(side="right")

        self._settings_section(page, "Window & motion")
        window_card = Card(page, self, radius=CARD_RADIUS, pad=(20, 18))
        window_card.pack(fill="x", padx=PAGE_PAD)
        glass_row = tk.Frame(window_card.body, bg=c["card"])
        glass_row.pack(fill="x")
        IconTile(glass_row, self, "layers", color=c["cyan"], size=36,
                 bg=c["card"]).pack(side="left")
        glass_text = tk.Frame(glass_row, bg=c["card"])
        glass_text.pack(side="left", padx=14)
        tk.Label(glass_text, text="Glass window", bg=c["card"], fg=c["text"],
                 font=f(11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(glass_text, text="Let the desktop show through the window",
                 bg=c["card"], fg=c["text3"], font=f(10), anchor="w").pack(anchor="w")
        Segmented(glass_row, self, ["Solid", "Glass", "Clear"], self.glass_label(),
                  command=self.set_glass, bg=c["card"], option_width=72,
                  height=32).pack(side="right")

        hairline(window_card.body, self, pady=(16, 14))

        motion_row = tk.Frame(window_card.body, bg=c["card"])
        motion_row.pack(fill="x")
        IconTile(motion_row, self, "spark", color=c["purple_l"], size=36,
                 bg=c["card"]).pack(side="left")
        motion_text = tk.Frame(motion_row, bg=c["card"])
        motion_text.pack(side="left", padx=14)
        tk.Label(motion_text, text="Celebration animations", bg=c["card"],
                 fg=c["text"], font=f(11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(motion_text,
                 text="Confetti cards for perfect days, streaks and achievements",
                 bg=c["card"], fg=c["text3"], font=f(10), anchor="w").pack(anchor="w")
        Switch(motion_row, self, value=self.animations_on(), bg=c["card"],
               command=self.set_animations).pack(side="right")

        tk.Label(window_card.body,
                 text="Window opacity is applied by the operating system compositor; "
                      "without one the window stays solid.",
                 bg=c["card"], fg=c["text3"], font=f(9), anchor="w",
                 justify="left", wraplength=780).pack(anchor="w", pady=(14, 0))

        self._settings_section(page, "Your data")
        data_card = Card(page, self, radius=CARD_RADIUS, pad=(20, 18))
        data_card.pack(fill="x", padx=PAGE_PAD)
        info = tk.Frame(data_card.body, bg=c["card"])
        info.pack(fill="x")
        IconTile(info, self, "archive", color=c["accent"], size=36,
                 bg=c["card"]).pack(side="left")
        info_text = tk.Frame(info, bg=c["card"])
        info_text.pack(side="left", padx=14)
        tk.Label(info_text, text="Local data file", bg=c["card"], fg=c["text"],
                 font=f(11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(info_text, text=DATA_FILE, bg=c["card"], fg=c["text3"],
                 font=mono(9), anchor="w").pack(anchor="w")
        buttons = tk.Frame(data_card.body, bg=c["card"])
        buttons.pack(fill="x", pady=(16, 0))
        HoverButton(buttons, self, "Export JSON", command=self._export,
                    icon="download", kind="soft", height=36, font_size=10,
                    bg=c["card"]).pack(side="left")
        HoverButton(buttons, self, "Import JSON", command=self._import,
                    icon="upload", kind="soft", height=36, font_size=10,
                    bg=c["card"]).pack(side="left", padx=8)
        HoverButton(buttons, self, "Create backup", command=self._backup,
                    icon="archive", kind="success", height=36, font_size=10,
                    bg=c["card"]).pack(side="left")
        HoverButton(buttons, self, "Reset all data", command=self._reset_data,
                    icon="reset", kind="danger", height=36, font_size=10,
                    bg=c["card"]).pack(side="right")
        tk.Label(data_card.body,
                 text="Import replaces the current data file and keeps an automatic "
                      "backup first.",
                 bg=c["card"], fg=c["text3"], font=f(9), anchor="w").pack(
            anchor="w", pady=(12, 0))

        self._settings_section(page, "Keyboard shortcuts")
        shortcuts_card = Card(page, self, radius=CARD_RADIUS, pad=(20, 16))
        shortcuts_card.pack(fill="x", padx=PAGE_PAD)
        shortcuts = [
            ("Ctrl+N", "Create a new habit"),
            ("Ctrl+D", "Complete every habit scheduled today"),
            ("Ctrl+F", "Focus the habit search field"),
            ("Ctrl+1 … 5", "Jump between views"),
            ("F5", "Refresh the current view"),
            ("Esc", "Close the habit dialog"),
        ]
        for keys, description in shortcuts:
            row = tk.Frame(shortcuts_card.body, bg=c["card"])
            row.pack(fill="x", pady=3)
            self._key_chip(row, keys).pack(side="left")
            tk.Label(row, text=description, bg=c["card"], fg=c["text2"],
                     font=f(10), anchor="w").pack(side="left", padx=14)

        self._settings_section(page, "About", pady=(24, 10))
        about = Card(page, self, radius=CARD_RADIUS, pad=(20, 18))
        about.pack(fill="x", padx=PAGE_PAD, pady=(0, 28))
        head = tk.Frame(about.body, bg=c["card"])
        head.pack(fill="x")
        logo = tk.Canvas(head, width=38, height=38, bg=c["card"],
                         highlightthickness=0, bd=0)
        logo.pack(side="left")
        rrect(logo, 0, 0, 38, 38, 12, fill=c["primary_d"])
        rrect(logo, 0, 0, 38, 38, 12, outline=c["primary"], width=1)
        draw_icon(logo, "layers", 19, 19, size=19, color="#FFFFFF", width=1.7)
        title_box = tk.Frame(head, bg=c["card"])
        title_box.pack(side="left", padx=14)
        tk.Label(title_box, text=f"{APP_NAME} {VERSION}", bg=c["card"], fg=c["text"],
                 font=f(12, "bold"), anchor="w").pack(anchor="w")
        tk.Label(title_box, text="Offline habit tracking, built on tkinter",
                 bg=c["card"], fg=c["text3"], font=f(10), anchor="w").pack(anchor="w")
        tk.Label(about.body,
                 text="Your habits, streaks and XP live in one JSON file on this "
                      "computer. Nothing leaves the device.",
                 bg=c["card"], fg=c["text2"], font=f(10), anchor="w",
                 justify="left", wraplength=760).pack(anchor="w", pady=(14, 0))

    def _settings_section(self, parent, title, pady=(24, 10)):
        tk.Label(parent, text=title.upper(), bg=self.c["bg"], fg=self.c["text3"],
                 font=(FONT_FAMILY, 8, "bold"), anchor="w").pack(
            fill="x", padx=PAGE_PAD, pady=pady)

    def _key_chip(self, parent, text):
        c = self.c
        width = tkfont.Font(font=mono(9, "bold")).measure(text) + 20
        canvas = tk.Canvas(parent, width=width, height=24, bg=c["card"],
                           highlightthickness=0, bd=0)
        rrect(canvas, 0.5, 0.5, width - 0.5, 23.5, 6, fill=c["surface2"])
        rrect(canvas, 0.5, 0.5, width - 0.5, 23.5, 6, outline=c["border"], width=1)
        canvas.create_text(width / 2, 12.5, text=text, font=mono(9, "bold"),
                           fill=c["text2"])
        return canvas

    # -- data actions -------------------------------------------------
    def _export(self):
        path = filedialog.asksaveasfilename(
            title="Export HabitFlow data", defaultextension=".json",
            filetypes=[("JSON files", "*.json")], initialfile="habitflow_export.json",
            parent=self.root,
        )
        if not path:
            return
        try:
            self.dm.export_json(path)
            self.toast(f"Exported to {os.path.basename(path)}", "success")
        except Exception as error:
            messagebox.showerror("Export failed", str(error), parent=self.root)

    def _import(self):
        path = filedialog.askopenfilename(
            title="Import HabitFlow data", filetypes=[("JSON files", "*.json")],
            parent=self.root,
        )
        if not path:
            return
        try:
            self.dm.import_json(path)
        except Exception as error:
            messagebox.showerror("Import failed", str(error), parent=self.root)
            return
        self._reload_after_data_change("Dashboard")
        self.toast("Data imported · backup created", "success")

    def _backup(self):
        try:
            destination = self.dm.backup()
        except Exception as error:
            messagebox.showerror("Backup failed", str(error), parent=self.root)
            return
        if destination:
            self.toast(f"Backup saved · {os.path.basename(destination)}", "success")

    def _reset_data(self):
        if not messagebox.askyesno(
            "Reset all data",
            "This permanently deletes every habit, completion record, streak and "
            "XP point.\n\nA backup is created first. Continue?",
            icon="warning", parent=self.root,
        ):
            return
        self.dm.reset()
        self._reload_after_data_change("Dashboard")
        self.toast("Data reset · fresh start", "info")

    def _reload_after_data_change(self, view="Dashboard"):
        self._active_view = view
        self._apply_theme(self._theme_name)

# ==================================================================
# SHARED WIDGETS
# ==================================================================
class IconTile(tk.Canvas):
    """Rounded icon chip used in cards and lists."""

    def __init__(self, parent, app, icon, color=None, size=36, bg=None, soft=True,
                 icon_size=18):
        self.c = app.c
        color = color or self.c["primary"]
        host = bg or parent.cget("bg")
        super().__init__(parent, width=size, height=size, bg=host,
                         highlightthickness=0, bd=0)
        rrect(self, 0, 0, size, size, size * 0.3,
              fill=mix(color, host, 0.82) if soft else color)
        draw_icon(self, icon, size / 2, size / 2, size=icon_size,
                  color=color if soft else readable_on(color), width=1.8)


class Segmented(tk.Canvas):
    """Two-or-more option segmented control."""

    def __init__(self, parent, app, options, value, command=None, height=34,
                 option_width=92, bg=None):
        self.app = app
        self.c = app.c
        self._segments = list(options)
        self._value = value
        self._command = command
        self._height = height
        self._bg = bg or parent.cget("bg")
        width = option_width * len(options) + 8
        super().__init__(parent, width=width, height=height, bg=self._bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self._width = width
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        c = self.c
        radius = self._height / 2
        rrect(self, 0, 0, self._width, self._height, radius, fill=c["surface2"])
        rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5, radius,
              outline=c["border"], width=1)
        index = self._segments.index(self._value) if self._value in self._segments else 0
        pad = 4
        slot = self._width / len(self._segments)
        pill_w = slot - pad
        rrect(self, pad + index * slot, pad, pad + index * slot + pill_w,
              self._height - pad, (self._height - pad * 2) / 2, fill=c["primary"])
        for position, option in enumerate(self._segments):
            centre = slot * position + slot / 2
            active = position == index
            self.create_text(centre, self._height / 2 + 0.5, text=option,
                             font=(FONT_FAMILY, 9, "bold" if active else "normal"),
                             fill="#FFFFFF" if active else c["text2"])

    def _on_click(self, event):
        slot = self._width / len(self._segments)
        index = min(len(self._segments) - 1, max(0, int(event.x // slot)))
        value = self._segments[index]
        if value != self._value:
            self._value = value
            self._draw()
            if self._command:
                self._command(value)


# ==================================================================
# MAIN WINDOW
# ==================================================================
class HabitFlowApp(DashboardViewMixin, HabitsViewMixin, StatsViewMixin,
                   CalendarViewMixin, SettingsViewMixin):
    """HabitFlow 2.1 - a command center for daily discipline."""

    NAV_ITEMS = [
        ("grid", "Dashboard"),
        ("list", "Habits"),
        ("chart", "Statistics"),
        ("calendar", "Calendar"),
        ("settings", "Settings"),
    ]

    VIEW_SUBTITLES = {
        "Dashboard": "Your day at a glance",
        "Habits": "Create, edit and complete",
        "Statistics": "Consistency, trends and streaks",
        "Calendar": "Perfect-day history",
        "Settings": "Preferences and data",
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.dm = DataManager()
        theme_name = self.dm.data["settings"].get("theme", "dark")
        if theme_name not in THEMES:
            theme_name = "dark"
        self._theme_name = theme_name
        self.c = THEMES[theme_name]

        init_fonts(root)
        configure_ttk(root, self.c)

        self._active_view = None
        self._clock_job = None
        self._nav_buttons = {}
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_args: self._on_search_changed())
        self._filter_cat = tk.StringVar(value="All")
        self._search_entry = None
        self._task_scroll = None
        self._habit_rows = {}
        self._dashboard_rows = {}
        self._dashboard = {}
        self._celebration_active = None
        self._celebration_queue = []

        self._setup_window()
        self._build_layout()
        self._show("Dashboard")
        self._tick_clock()
        # some window managers reset wm attributes on first map
        self.root.after(120, self._apply_window_alpha)

        if self.dm.award_perfect_day_if_due():
            self.root.after(600, lambda: self.toast("Perfect day complete  ·  +50 XP", "xp"))

    # -- window ------------------------------------------------------
    def _setup_window(self):
        self.root.title(f"{APP_NAME}  ·  {VERSION}")
        self.root.configure(bg=self.c["bg"])
        self.root.geometry("1360x860")
        self.root.minsize(1024, 700)
        self.root.bind("<Control-n>", lambda _e=None: self._open_add_task())
        self.root.bind("<Control-d>", self._shortcut_mark_all)
        self.root.bind("<F5>", lambda _e=None: self._refresh())
        self.root.bind("<Control-f>", lambda _e=None: self._focus_search())
        self.root.bind("<Control-q>", lambda _e=None: self.on_close())
        for index, (_icon, name) in enumerate(self.NAV_ITEMS):
            self.root.bind(f"<Control-Key-{index + 1}>",
                           lambda _e, n=name: self._show(n))
        self._apply_window_alpha()

    # -- window glass & motion ----------------------------------------
    def window_alpha(self):
        try:
            value = float(self.dm.data["settings"].get("window_alpha", 0.96))
        except (TypeError, ValueError):
            value = 0.96
        return max(0.70, min(1.0, value))

    def _apply_window_alpha(self):
        try:
            self.root.attributes("-alpha", self.window_alpha())
        except tk.TclError:
            pass

    def set_window_alpha(self, alpha):
        alpha = max(0.70, min(1.0, float(alpha)))
        self.dm.data["settings"]["window_alpha"] = round(alpha, 2)
        self.dm.save()
        self._apply_window_alpha()

    def glass_label(self):
        alpha = self.window_alpha()
        if alpha >= 0.995:
            return "Solid"
        if alpha >= 0.93:
            return "Glass"
        return "Clear"

    def set_glass(self, label):
        self.set_window_alpha({"Solid": 1.0, "Glass": 0.95, "Clear": 0.88}.get(label, 0.95))

    def animations_on(self):
        return bool(self.dm.data["settings"].get("animations", True))

    def set_animations(self, value):
        self.dm.data["settings"]["animations"] = bool(value)
        self.dm.save()
        if not value:
            self._celebration_queue = []
            self._close_celebration()

    def toast(self, message, kind="success"):
        show_toast(self.root, message, self.c, kind=kind)

    # -- celebrations --------------------------------------------------
    def celebrate(self, title, subtitle, icon, accent, xp=None, kicker="MILESTONE"):
        """Queue a HUD celebration card; only one is ever on screen."""
        if not self.animations_on():
            return
        if getattr(self, "_celebration_active", None) is not None:
            self._celebration_queue.append((title, subtitle, icon, accent, xp, kicker))
            return
        self._show_celebration(title, subtitle, icon, accent, xp, kicker)

    def _show_celebration(self, title, subtitle, icon, accent, xp=None,
                          kicker="MILESTONE"):
        try:
            self._celebration_active = Celebration(
                self, title, subtitle, icon, accent, xp=xp, kicker=kicker,
                on_close=self._celebration_finished)
        except tk.TclError:
            self._celebration_active = None

    def _celebration_finished(self):
        self._celebration_active = None
        queue = getattr(self, "_celebration_queue", [])
        if queue:
            nxt = queue.pop(0)
            try:
                self.root.after(120, lambda: self._show_celebration(*nxt))
            except tk.TclError:
                pass

    def _close_celebration(self):
        overlay = getattr(self, "_celebration_active", None)
        if overlay is not None:
            try:
                overlay.dismiss()
            except tk.TclError:
                pass
        self._celebration_active = None

    # -- layout ------------------------------------------------------
    def _build_layout(self):
        self._build_sidebar()
        self.main = tk.Frame(self.root, bg=self.c["bg"])
        self.main.pack(side="left", fill="both", expand=True)
        self._build_topbar()
        self.content = tk.Frame(self.main, bg=self.c["bg"])
        self.content.pack(fill="both", expand=True)

    def _build_sidebar(self):
        c = self.c
        self.sidebar = tk.Frame(self.root, bg=c["sidebar"], width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Frame(self.sidebar, bg=c["border"], width=1).pack(side="right", fill="y")

        brand = tk.Frame(self.sidebar, bg=c["sidebar"])
        brand.pack(fill="x", padx=20, pady=(24, 22))
        logo = tk.Canvas(brand, width=40, height=40, bg=c["sidebar"],
                         highlightthickness=0, bd=0)
        logo.pack(side="left")
        rrect(logo, 0, 0, 40, 40, 12, fill=c["primary_d"])
        rrect(logo, 0, 0, 40, 40, 12, outline=c["primary"], width=1)
        draw_icon(logo, "layers", 20, 20, size=20, color="#FFFFFF", width=1.8)

        brand_text = tk.Frame(brand, bg=c["sidebar"])
        brand_text.pack(side="left", padx=11)
        tk.Label(brand_text, text=APP_NAME, bg=c["sidebar"], fg=c["side_text"],
                 font=f(15, "bold"), anchor="w").pack(anchor="w")
        tk.Label(brand_text, text="COMMAND CENTER", bg=c["sidebar"], fg=c["text3"],
                 font=(FONT_FAMILY, 8, "bold"), anchor="w").pack(anchor="w")

        tk.Label(self.sidebar, text="WORKSPACE", bg=c["sidebar"], fg=c["text3"],
                 font=(FONT_FAMILY, 8, "bold"), anchor="w").pack(
            fill="x", padx=22, pady=(8, 8))

        for icon, label in self.NAV_ITEMS:
            button = NavButton(self.sidebar, self, icon, label, self._show,
                               width=222, height=44)
            button.pack(padx=8, pady=2)
            self._nav_buttons[label] = button

        footer = tk.Frame(self.sidebar, bg=c["sidebar"])
        footer.pack(side="bottom", fill="x", padx=14, pady=16)

        level_card = Card(footer, self, radius=14, pad=(14, 12),
                          fill=c["sidebar2"],
                          border=mix(c["sidebar2"], "#FFFFFF", 0.07))
        level_card.pack(fill="x")

        xp, level, level_name, xp_in, xp_for = self.dm.get_xp_info()
        top = tk.Frame(level_card.body, bg=c["sidebar2"])
        top.pack(fill="x")
        self._sidebar_level_label = tk.Label(
            top, text=f"LEVEL {level}", bg=c["sidebar2"], fg=c["cyan"],
            font=(FONT_FAMILY, 8, "bold"), anchor="w")
        self._sidebar_level_label.pack(side="left")
        self._sidebar_level_name = tk.Label(
            top, text=level_name, bg=c["sidebar2"], fg=c["side_text2"],
            font=f(9), anchor="e")
        self._sidebar_level_name.pack(side="right")
        self._sidebar_fraction = min(1.0, xp_in / xp_for) if xp_for else 1.0
        self._sidebar_bar = tk.Canvas(level_card.body, height=6, bg=c["sidebar2"],
                                      highlightthickness=0, bd=0)
        self._sidebar_bar.pack(fill="x", pady=(9, 6))
        self._sidebar_bar.bind("<Configure>", self._draw_sidebar_bar)
        self._sidebar_xp_label = tk.Label(
            level_card.body, text=f"{xp:,} XP  ·  {max(0, xp_for - xp_in):,} to next",
            bg=c["sidebar2"], fg=c["text3"], font=(FONT_FAMILY, 8), anchor="w")
        self._sidebar_xp_label.pack(fill="x")
        self.root.after(60, self._draw_sidebar_bar)

        tk.Label(footer, text=f"v{VERSION}  ·  offline & private", bg=c["sidebar"],
                 fg=c["text3"], font=(FONT_FAMILY, 8), anchor="w").pack(
            fill="x", pady=(12, 0))

    def _draw_sidebar_bar(self, _event=None):
        bar = getattr(self, "_sidebar_bar", None)
        if bar is None:
            return
        try:
            if not bar.winfo_exists():
                return
            width = bar.winfo_width() or 160
            bar.delete("all")
            rrect(bar, 0, 0, width, 6, 3, fill=mix(self.c["sidebar2"], "#FFFFFF", 0.09))
            if self._sidebar_fraction > 0.015:
                rrect(bar, 0, 0, max(6, width * self._sidebar_fraction), 6, 3,
                      fill=self.c["primary"])
        except tk.TclError:
            pass

    def _refresh_sidebar_xp(self):
        xp, level, level_name, xp_in, xp_for = self.dm.get_xp_info()
        self._sidebar_fraction = min(1.0, xp_in / xp_for) if xp_for else 1.0
        try:
            self._sidebar_level_label.configure(text=f"LEVEL {level}")
            self._sidebar_level_name.configure(text=level_name)
            self._sidebar_xp_label.configure(
                text=f"{xp:,} XP  ·  {max(0, xp_for - xp_in):,} to next")
        except (tk.TclError, AttributeError):
            return
        self._draw_sidebar_bar()

    def _build_topbar(self):
        c = self.c
        bar = tk.Frame(self.main, bg=c["bg"], height=64)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        inner = tk.Frame(bar, bg=c["bg"])
        inner.pack(fill="both", expand=True, padx=PAGE_PAD)

        left = tk.Frame(inner, bg=c["bg"])
        left.pack(side="left", pady=20)
        tk.Label(left, text=APP_NAME.upper(), bg=c["bg"], fg=c["text3"],
                 font=(FONT_FAMILY, 8, "bold"), anchor="w").pack(side="left")
        tk.Label(left, text="/", bg=c["bg"], fg=c["border_hi"],
                 font=f(10)).pack(side="left", padx=9)
        self.lbl_crumb = tk.Label(left, text="Dashboard", bg=c["bg"], fg=c["text2"],
                                  font=f(10, "bold"), anchor="w")
        self.lbl_crumb.pack(side="left")

        right = tk.Frame(inner, bg=c["bg"])
        right.pack(side="right", pady=14)

        self.btn_theme = IconButton(
            right, self, "sun" if self._theme_name == "dark" else "moon",
            command=self._toggle_theme, size=34, icon_size=17, bg=c["bg"],
            color=c["text2"], hover_color=c["primary_l"], radius=9,
        )
        self.btn_theme.pack(side="right", padx=(12, 0))

        clock = tk.Frame(right, bg=c["bg"])
        clock.pack(side="right", padx=(0, 6))
        self.lbl_clock = tk.Label(clock, text="", bg=c["bg"], fg=c["text"],
                                  font=f(11, "bold"), anchor="e")
        self.lbl_clock.pack(anchor="e")
        self.lbl_clock_date = tk.Label(clock, text="", bg=c["bg"], fg=c["text3"],
                                       font=f(9), anchor="e")
        self.lbl_clock_date.pack(anchor="e")

        self._streak_chip = tk.Canvas(right, height=32, width=10, bg=c["bg"],
                                      highlightthickness=0, bd=0)
        self._streak_chip.pack(side="right", padx=(0, 14))
        self._draw_streak_chip()

        tk.Frame(self.main, bg=c["border"], height=1).pack(fill="x")

    def _draw_streak_chip(self, pulse=False):
        canvas = self._streak_chip
        c = self.c
        streak = self.dm.calculate_streak()
        label = f"{streak}-day streak" if streak else "No streak yet"
        font = tkfont.Font(family=FONT_FAMILY, size=10, weight="bold")
        width = font.measure(label) + 52
        canvas.configure(width=width)
        canvas.delete("all")
        highlight = streak > 0
        color = c["warning"] if highlight else c["text2"]
        rrect(canvas, 0, 0, width, 32, 16,
              fill=mix(color, c["bg"], 0.86),
              outline=mix(c["border"], color, 0.40 if highlight else 0.2), width=1)
        draw_icon(canvas, "flame", 20, 16, size=15, color=color, width=1.8)
        canvas.create_text(32, 16, anchor="w", text=label, font=font,
                           fill=c["text"] if highlight else c["text2"])
        if pulse and highlight and self.animations_on():
            self._pulse_streak_chip(width, color)

    def _pulse_streak_chip(self, width, color):
        """Expand a ring around the streak chip and float a +1 label."""
        canvas = self._streak_chip
        c = self.c
        steps = 10

        def frame(step):
            if not canvas.winfo_exists():
                return
            canvas.delete("fx")
            t = step / steps
            grow = 1 + 9 * t
            fade = mix(color, c["bg"], min(1.0, 0.15 + t))
            rrect(canvas, -grow, -grow, width + grow, 32 + grow, 16 + grow,
                  outline=fade, width=1.2, tags=("fx",))
            if step < 5:
                size = 15 + 4 * math.sin(math.pi * step / 5)
                draw_icon(canvas, "flame", 20, 16, size=size, color=color,
                          width=1.9, tags=("fx",))
            if step < 6:
                canvas.create_text(width / 2, 9 - step * 1.7, text="+1",
                                   font=(FONT_FAMILY, 9, "bold"),
                                   fill=mix(color, c["bg"], step / 6), tags=("fx",))
            if step < steps:
                canvas.after(45, lambda: frame(step + 1))
            else:
                canvas.delete("fx")

        frame(0)

    # -- navigation --------------------------------------------------
    def _show(self, view_name: str):
        if view_name not in {name for _icon, name in self.NAV_ITEMS}:
            view_name = "Dashboard"
        for widget in self.content.winfo_children():
            widget.destroy()
        self._dashboard_rows = {}
        self._dashboard = {}
        self._task_scroll = None
        self._search_entry = None
        self._habit_rows = {}
        self._milestone_holder = None

        self._active_view = view_name
        try:
            self.lbl_crumb.configure(text=view_name)
        except (tk.TclError, AttributeError):
            pass
        for name, button in self._nav_buttons.items():
            button.set_active(name == view_name)
        self._draw_streak_chip()

        {
            "Dashboard": self._view_dashboard,
            "Habits": self._view_habits,
            "Statistics": self._view_stats,
            "Calendar": self._view_calendar,
            "Settings": self._view_settings,
        }[view_name]()

        for child in list(self.content.winfo_children()):
            self._transition_page(child)

    def _transition_page(self, page):
        """Slide a freshly built page up into place behind a short HUD sweep."""
        if not self.animations_on():
            return
        try:
            page.pack_forget()
            page.place(x=0, y=18, relwidth=1, relheight=1)
        except tk.TclError:
            return
        sweep = tk.Canvas(self.content, bg=self.c["bg"], highlightthickness=0, bd=0)
        sweep.place(x=0, y=0, relwidth=1, height=2)
        started = time.perf_counter()
        span = 0.22

        def step():
            try:
                if not page.winfo_exists():
                    return
                t = min(1.0, (time.perf_counter() - started) / span)
                eased = 1 - (1 - t) ** 3
                page.place_configure(y=int(round(18 * (1 - eased))))
                width = max(1, self.content.winfo_width())
                head = int(width * eased)
                sweep.delete("all")
                for index in range(16):
                    x = head - index * 7
                    if x < 0 or x > width:
                        continue
                    fade = max(0.0, 0.55 * (1 - index / 16.0))
                    sweep.create_line(x, 1, x + 10, 1, width=2,
                                      fill=mix(self.c["bg"], self.c["cyan"], fade))
                if t < 1.0:
                    self.root.after(16, step)
                else:
                    page.place_forget()
                    page.pack(fill="both", expand=True)
                    sweep.destroy()
            except tk.TclError:
                pass

        step()

    def _refresh(self):
        self._show(self._active_view or "Dashboard")

    def _focus_search(self):
        if self._search_entry is not None:
            try:
                self._search_entry.focus_set()
            except tk.TclError:
                pass

    # -- completion handling -----------------------------------------
    def _earned_achievements(self):
        return {item["name"] for item in self._achievements() if item["earned"]}

    def _progress_snapshot(self):
        return {"earned": self._earned_achievements(),
                "streak": self.dm.calculate_streak()}

    def _toggle_task(self, task):
        done_ids = self.dm.get_completed_today()
        new_state = task["id"] not in done_ids
        before = self._progress_snapshot()
        self.dm.toggle_task(task["id"], new_state)
        self._after_completion_change(task, new_state, before)
        return new_state

    def _after_completion_change(self, task, completed, before=None):
        if self.dm.award_perfect_day_if_due():
            self.toast("Perfect day complete  ·  +50 XP", "xp")
        elif completed:
            self.toast(f"{task['name']} complete  ·  +{XP_PER_TASK} XP", "success")
        if self._active_view == "Dashboard":
            self._refresh_dashboard_progress()
            self._refresh_sidebar_xp()
        elif self._active_view == "Habits":
            self._update_habit_header()
            self._draw_streak_chip()
            self._refresh_sidebar_xp()
            summary = getattr(self, "_habit_summary_bar", None)
        elif self._active_view == "Calendar":
            self._render_calendar()
            self._refresh_sidebar_xp()
        else:
            self._refresh_sidebar_xp()
        if completed and before is not None:
            self._celebrate_progress(before)

    def _celebrate_progress(self, before):
        """Fire the motion for a streak extension, milestones and perfect days."""
        if not self.animations_on():
            return
        today = date.today()
        streak = self.dm.calculate_streak()
        perfect = self.dm.is_perfect_day(today)
        new_achievements = self._earned_achievements() - before.get("earned", set())

        if perfect:
            self.celebrate("Perfect day", "Every habit complete", "trophy",
                           self.c["success"], xp=f"+{XP_PERFECT_DAY} XP",
                           kicker="DAY COMPLETE")
        else:
            for item in self._achievements():
                if item["name"] in new_achievements:
                    self.celebrate(item["name"], item["desc"], item["icon"],
                                   self.c["primary_l"], xp="Unlocked",
                                   kicker="ACHIEVEMENT")

        if streak > before.get("streak", 0):
            self._draw_streak_chip(pulse=True)
            if streak in (3, 7, 14, 30, 60, 100, 180, 365):
                self.celebrate(f"{streak}-day streak", "Consistency compounding",
                               "flame", self.c["warning"], kicker="STREAK")

        holder = getattr(self, "_milestone_holder", None)
        if holder is not None and new_achievements:
            try:
                if holder.winfo_exists():
                    self._render_milestones(holder, limit=4, unlock=new_achievements)
            except tk.TclError:
                pass

    # -- habit actions ------------------------------------------------
    def _open_add_task(self, _event=None):
        dialog = TaskDialog(self.root, self)
        if dialog.result:
            task = self.dm.add_task(**dialog.result)
            self._show(self._active_view or "Dashboard")
            self.toast(f"{task['name']} added", "success")

    def _open_edit_task(self, task):
        dialog = TaskDialog(self.root, self, task=task)
        if dialog.result:
            self.dm.update_task(task["id"], **dialog.result)
            self._show(self._active_view or "Habits")
            self.toast("Habit updated", "info")

    def _delete_task(self, task):
        if messagebox.askyesno("Delete habit",
                               f"Delete “{task['name']}”?\n\n"
                               "Its completion history for this habit will be "
                               "removed too.", parent=self.root):
            self.dm.delete_task(task["id"])
            self._show(self._active_view or "Habits")
            self.toast("Habit deleted", "danger")

    def _shortcut_mark_all(self, _event=None):
        tasks = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        pending = [t for t in tasks if t["id"] not in done_ids]
        if not pending:
            self.toast("Everything is already complete", "info")
            return
        before = self._progress_snapshot()
        for task in pending:
            self.dm.toggle_task(task["id"], True)
        self.dm.award_perfect_day_if_due()
        self._refresh_sidebar_xp()
        self._show(self._active_view or "Dashboard")
        self.toast(f"{len(pending)} habit{'s' if len(pending) != 1 else ''} completed",
                   "success")
        self._celebrate_progress(before)

    # -- theme --------------------------------------------------------
    def _toggle_theme(self):
        self._apply_theme("light" if self._theme_name == "dark" else "dark")

    def _apply_theme(self, name: str):
        if name not in THEMES:
            return
        self._theme_name = name
        self.c = THEMES[name]
        self.dm.data["settings"]["theme"] = name
        self.dm.save()
        view = self._active_view or "Dashboard"
        for widget in self.root.winfo_children():
            widget.destroy()
        init_fonts(self.root)
        configure_ttk(self.root, self.c)
        self._nav_buttons = {}
        self._task_scroll = None
        self._search_entry = None
        self._dashboard_rows = {}
        self._dashboard = {}
        self._setup_window()
        self._build_layout()
        self._show(view)

    # -- clock ---------------------------------------------------------
    def _tick_clock(self):
        now = datetime.now()
        try:
            if hasattr(self, "lbl_clock") and self.lbl_clock.winfo_exists():
                self.lbl_clock.configure(text=now.strftime("%H:%M"))
                self.lbl_clock_date.configure(text=now.strftime("%a %d %b"))
            self._clock_job = self.root.after(20000, self._tick_clock)
        except tk.TclError:
            pass

    def on_close(self):
        if self._clock_job:
            try:
                self.root.after_cancel(self._clock_job)
            except tk.TclError:
                pass
        self._close_celebration()
        try:
            self.dm.save()
        finally:
            self.root.destroy()


# ==================================================================
# ENTRY POINT
# ==================================================================
def main():
    root = tk.Tk()

    # Crisp text on high-DPI Windows displays
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    app = HabitFlowApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = max(0, (root.winfo_screenheight() - root.winfo_height()) // 3)
    root.geometry(f"+{max(0, x)}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()
