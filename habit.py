#!/usr/bin/env python3
"""
+------------------------------------------------------------------+
|           HabitFlow - Personal Offline Habit Tracker             |
|      No accounts. No internet. No cloud. 100% yours.             |
+------------------------------------------------------------------+
|  Requirements:  Python 3.8+  (tkinter is built-in)               |
|  Dependencies:  none - all charts are drawn with tkinter         |
|                                                                  |
|  Run:   python habit.py                                          |
|  Data:  ~/.habitflow/data.json  (fully local)                    |
+------------------------------------------------------------------+

v2.0 "Command Center" - visual redesign of the v1 HabitFlow tracker.
Every data structure, storage path and business rule from v1 is
preserved; this file changes how the app looks and feels, not what
it stores.
"""

# ==================================================================
# IMPORTS
# ==================================================================
import calendar as cal_module
import json
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
VERSION = "2.0.0"
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

# -- Category -> accent colour --------------------------------------
CATEGORIES = {
    "Health": "#34D399",
    "Study": "#60A5FA",
    "Fitness": "#FB923C",
    "Personal": "#A78BFA",
    "Work": "#FBBF24",
    "Social": "#F472B6",
    "Sleep": "#818CF8",
    "Other": "#7E8CA0",
}
CAT_LIST = list(CATEGORIES.keys())

RECURRENCE_OPTIONS = ["Daily", "Weekdays", "Weekends", "Weekly", "Monthly", "Custom Days"]
WEEKDAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_FULL = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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
# Near-black + charcoal surfaces, neon blue primary, restrained
# purple secondary. The sidebar stays dark in both themes so the app
# keeps its "command center" identity even in light mode.
THEMES = {
    "dark": {
        "name": "dark",
        "bg": "#070A12",
        "bg_alt": "#080D17",
        "surface": "#0E1522",
        "surface2": "#131C2B",
        "surface3": "#1A2436",
        "card": "#0E1522",
        "card2": "#111A29",
        "border": "#1B2637",
        "border_hi": "#27384F",
        "primary": "#3D8BFF",
        "primary_l": "#7FB2FF",
        "primary_d": "#1E4FA8",
        "primary_soft": "#122340",
        "purple": "#8B5CF6",
        "purple_l": "#B79CFF",
        "purple_soft": "#1A1533",
        "accent": "#22D3A5",
        "success": "#2BD48A",
        "warning": "#F5B84B",
        "danger": "#F0616B",
        "text": "#E9EFFA",
        "text2": "#93A4BC",
        "text3": "#5B6B82",
        "sidebar": "#080D16",
        "sidebar2": "#0B1220",
        "side_text": "#E9EFFA",
        "side_text2": "#8EA0B9",
        "side_active": "#122035",
        "prog_bg": "#182233",
        "ring_track": "#182233",
        "highlight": "#16233A",
        "shadow": "#04060C",
        "on_accent": "#04121B",
        "scrim": "#070A12",
        "toast": "#101A2B",
    },
    "light": {
        "name": "light",
        "bg": "#F1F5FC",
        "bg_alt": "#E9EFF9",
        "surface": "#FFFFFF",
        "surface2": "#F5F8FE",
        "surface3": "#E8EFFA",
        "card": "#FFFFFF",
        "card2": "#F8FAFF",
        "border": "#DCE5F3",
        "border_hi": "#C3D2E8",
        "primary": "#2563EB",
        "primary_l": "#1D4ED8",
        "primary_d": "#1E40AF",
        "primary_soft": "#E6EEFE",
        "purple": "#7C3AED",
        "purple_l": "#6D28D9",
        "purple_soft": "#EFE9FE",
        "accent": "#0E9F7E",
        "success": "#16A34A",
        "warning": "#C2820B",
        "danger": "#DC2626",
        "text": "#0C1524",
        "text2": "#4C5D74",
        "text3": "#8394AB",
        "sidebar": "#0B1220",
        "sidebar2": "#101A2B",
        "side_text": "#E9EFFA",
        "side_text2": "#93A4BC",
        "side_active": "#18263C",
        "prog_bg": "#E4ECF9",
        "ring_track": "#E4ECF9",
        "highlight": "#EDF3FE",
        "shadow": "#D7E1F0",
        "on_accent": "#04121B",
        "scrim": "#F1F5FC",
        "toast": "#FFFFFF",
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


# ==================================================================
# TYPOGRAPHY
# ==================================================================
FONT_STACK = [
    "Segoe UI Variable Text",
    "Segoe UI",
    "SF Pro Text",
    "Helvetica Neue",
    "Inter",
    "Ubuntu",
    "Noto Sans",
    "DejaVu Sans",
    "Arial",
]
MONO_STACK = ["Cascadia Mono", "Consolas", "SF Mono", "JetBrains Mono", "DejaVu Sans Mono", "Courier New"]

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


def f(size=11, weight="normal", slant="roman"):
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
        circle(12, 12, 4.4)
        for angle in range(0, 360, 45):
            import math as _math

            rad = _math.radians(angle)
            line([12 + 7 * _math.cos(rad), 12 + 7 * _math.sin(rad),
                  12 + 9.2 * _math.cos(rad), 12 + 9.2 * _math.sin(rad)], w=1.5)
    elif name == "moon":
        canvas.create_arc(X(3.5), Y(3), X(20.5), Y(21), start=60, extent=245,
                          style="arc", outline=color, width=width + 0.2, tags=tags)
        line([16.5, 6, 19, 9])
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


# ==================================================================
# SCROLLING
# ==================================================================
class SlimScrollbar(tk.Canvas):
    """A 6px rounded scrollbar that replaces the dated native one."""

    def __init__(self, parent, bg, track, thumb, command, width=8):
        super().__init__(parent, width=width, bg=bg, highlightthickness=0, bd=0, cursor="arrow")
        self._track = track
        self._thumb = thumb
        self._command = command
        self._first = 0.0
        self._last = 1.0
        self._drag_offset = None
        self.bind("<Configure>", lambda _e: self._draw())
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", lambda _e: setattr(self, "_drag_offset", None))
        self.bind("<Enter>", lambda _e: self.configure(bg=bg))

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
        bottom = max(self._last * height, top + 26)
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
    """Vertically scrollable container with mousewheel + slim scrollbar."""

    def __init__(self, parent, bg, padding=0, track=None, thumb=None, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((padding, padding), window=self.inner, anchor="nw")
        self._padding = padding
        self.scrollbar = SlimScrollbar(self, bg, track or shade(bg, 1.25),
                                       thumb or shade(bg, 2.4), self._on_scroll_command)
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
        delta = -1 * int(event.delta / 120) if abs(event.delta) >= 120 else (-1 if event.delta > 0 else 1)
        self.canvas.yview_scroll(delta, "units")

    def _on_wheel_up(self, _event):
        self.canvas.yview_scroll(-1, "units")

    def _on_wheel_down(self, _event):
        self.canvas.yview_scroll(1, "units")

    def scroll_to_top(self):
        self.canvas.yview_moveto(0)


# ==================================================================
# CARD - rounded, bordered surface with an embedded content frame
# ==================================================================
class Card(tk.Frame):
    """A rounded glass-style card whose height follows its content."""

    def __init__(self, parent, app, radius=16, padding=(18, 16), fill=None,
                 border=None, glow=False, height=None, bg=None, accent=None):
        self.app = app
        self.c = app.c
        self._radius = radius
        self._pad_x, self._pad_y = padding
        self._fill = fill or self.c["card"]
        self._border = border or self.c["border"]
        self._glow = glow
        self._accent = accent
        self._fixed_height = height
        self._hover_glow = None

        super().__init__(parent, bg=bg or parent.cget("bg"), highlightthickness=0, bd=0)
        self.canvas = tk.Canvas(self, bg=bg or parent.cget("bg"), highlightthickness=0, bd=0,
                                height=height or 40)
        self.canvas.pack(fill="both", expand=True)
        self.body = tk.Frame(self.canvas, bg=self._fill)
        self._win = self.canvas.create_window(self._pad_x, self._pad_y,
                                              window=self.body, anchor="nw")
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.body.bind("<Configure>", self._on_body_configure)
        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, event):
        if event.widget is self:
            self._hover_glow = None

    def _on_body_configure(self, _event=None):
        if self._fixed_height:
            return
        try:
            needed = self.body.winfo_reqheight() + self._pad_y * 2
        except tk.TclError:
            return
        if abs(int(self.canvas.cget("height")) - needed) > 1:
            self.canvas.configure(height=needed)

    def _on_canvas_configure(self, event):
        self._draw(event.width, event.height)
        self.canvas.itemconfigure(self._win, width=max(1, event.width - self._pad_x * 2))

    def _draw(self, width, height, glow_color=None):
        self.canvas.delete("card_bg")
        if width <= 2 or height <= 2:
            return
        border = glow_color or self._border
        if glow_color is None and self._glow:
            border = mix(self._border, self.c["primary"], 0.35)
        rrect(self.canvas, 0.5, 0.5, width - 0.5, height - 0.5, self._radius,
              fill=self._fill, tags=("card_bg",))
        rrect(self.canvas, 0.5, 0.5, width - 0.5, height - 0.5, self._radius,
              outline=border, width=1, tags=("card_bg",))
        if self._accent:
            rrect(self.canvas, 0.5, height * 0.22, 3.5, height * 0.78, 1.5,
                  fill=self._accent, tags=("card_bg",))
        self.canvas.tag_lower("card_bg")

    def set_glow(self, active: bool):
        """Subtle accent border used for hover / completion feedback."""
        try:
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
        except tk.TclError:
            return
        self._draw(width, height, mix(self._border, self.c["primary"], 0.55) if active else None)

    def set_accent(self, color):
        self._accent = color
        try:
            self._draw(self.canvas.winfo_width(), self.canvas.winfo_height())
        except tk.TclError:
            pass


class Chip(tk.Canvas):
    """Small rounded label used for categories and metadata."""

    def __init__(self, parent, app, text, color=None, bg=None, filled=True,
                 font_size=8, height=20, radius=7, fg=None):
        self.c = app.c
        color = color or self.c["surface3"]
        bg = bg or parent.cget("bg")
        font = (FONT_FAMILY, font_size, "bold")
        text_width = tkfont.Font(font=font).measure(text)
        width = text_width + 16
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, bd=0)
        self._draw(width, height, radius, color, filled, fg)
        self.create_text(width / 2, height / 2 + 0.5, text=text, font=font,
                         fill=fg or (readable_on(color) if filled else color))

    def _draw(self, width, height, radius, color, filled, fg):
        if filled:
            rrect(self, 0, 0, width, height, radius, fill=color)
        else:
            rrect(self, 0.5, 0.5, width - 0.5, height - 0.5, radius,
                  outline=color, width=1)


def divider(parent, app, padx=0, pady=0, color=None):
    line = tk.Frame(parent, bg=color or app.c["border"], height=1)
    line.pack(fill="x", padx=padx, pady=pady)
    return line
# ==================================================================
# INTERACTIVE WIDGETS
# ==================================================================
BUTTON_STYLES = {
    "primary": {"fill": "primary", "fg": "#FFFFFF", "border": "primary"},
    "soft": {"fill": "surface2", "fg": "text", "border": "border"},
    "outline": {"fill": None, "fg": "primary_l", "border": "primary_d"},
    "ghost": {"fill": None, "fg": "text2", "border": None},
    "success": {"fill": "success", "fg": "#04140D", "border": "success"},
    "danger": {"fill": None, "fg": "danger", "border": "danger"},
}


class HoverButton(tk.Canvas):
    """Rounded button with a soft hover transition."""

    def __init__(self, parent, app, text, command=None, icon=None, kind="primary",
                 height=38, radius=10, font_size=10, bg=None, padx=16, min_width=0,
                 tooltip=None, bold=True):
        self.app = app
        self.c = app.c
        style = BUTTON_STYLES.get(kind, BUTTON_STYLES["primary"])
        self._kind = kind
        self._command = command
        self._font = (FONT_FAMILY, font_size, "bold" if bold else "normal")
        self._icon = icon
        self._padx = padx
        self._radius = radius
        self._height = height
        self._bg = bg or parent.cget("bg")
        self._enabled = True
        self._hover = False
        self._animation = None
        self._tooltip_text = tooltip
        self._tooltip = None

        text_width = tkfont.Font(font=self._font).measure(text)
        icon_width = (16 + 7) if icon else 0
        width = max(min_width, text_width + icon_width + padx * 2)

        super().__init__(parent, width=width, height=height, bg=self._bg,
                         highlightthickness=0, bd=0, cursor="hand2")
        self._width = width
        self._style = style
        self._text = text

        self._base_fill, self._hover_fill, self._press_fill = self._palette(style)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._draw(self._base_fill)

    def _color(self, value):
        """Resolve a theme key, or pass a literal colour straight through."""
        if isinstance(value, str):
            return self.c.get(value, value)
        return value

    def _palette(self, style):
        c = self.c
        if style["fill"]:
            base = self._color(style["fill"])
            return base, shade(base, 1.14), shade(base, 0.88)
        hover = c["surface2"] if self._kind != "danger" else mix(c["surface2"], c["danger"], 0.18)
        return None, hover, mix(hover, c["text"], 0.06)

    def _draw(self, fill=None, text_color=None):
        self.delete("all")
        c = self.c
        border = self._color(self._style["border"]) if self._style["border"] else None
        fill = fill if fill is not None else self._base_fill
        if fill:
            rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5, self._radius, fill=fill)
        if border:
            rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5, self._radius,
                  outline=border, width=1)
        color = text_color or self._color(self._style["fg"])
        if self._icon:
            text_width = tkfont.Font(font=self._font).measure(self._text)
            total = 16 + 7 + text_width
            start = (self._width - total) / 2
            draw_icon(self, self._icon, start + 8, self._height / 2, size=15,
                      color=color, width=1.8)
            self.create_text(start + 23 + text_width / 2, self._height / 2 + 0.5,
                             text=self._text, font=self._font, fill=color)
        else:
            self.create_text(self._width / 2, self._height / 2 + 0.5, text=self._text,
                             font=self._font, fill=color)

    def _on_enter(self, _event):
        if not self._enabled:
            return
        self._hover = True
        self._animate_to(self._hover_fill)
        if self._style["fill"] is None and self._kind != "danger":
            self._draw(self._hover_fill, self.c["text"])

    def _on_leave(self, _event):
        self._hover = False
        self._cancel_animation()
        self._draw(self._base_fill)

    def _on_press(self, _event):
        if not self._enabled:
            return
        self._cancel_animation()
        self._draw(self._press_fill or self._base_fill)

    def _on_release(self, event):
        if not self._enabled:
            return
        inside = 0 <= event.x <= self._width and 0 <= event.y <= self._height
        self._draw(self._hover_fill if inside else self._base_fill)
        if inside and self._command:
            self._command()

    def _cancel_animation(self):
        if self._animation is not None:
            try:
                self.after_cancel(self._animation)
            except tk.TclError:
                pass
            self._animation = None

    def _animate_to(self, target):
        if not self._base_fill or not target:
            return
        self._cancel_animation()
        start = self._base_fill
        steps = 4

        def step(index):
            if not self.winfo_exists():
                return
            self._draw(mix(start, target, index / steps))
            if index < steps:
                self._animation = self.after(28, lambda: step(index + 1))

        step(1)

    def set_enabled(self, enabled: bool):
        self._enabled = bool(enabled)
        self.configure(cursor="hand2" if enabled else "arrow")
        if enabled:
            self._draw(self._base_fill)
        else:
            self._draw(self.c["surface2"], self.c["text3"])


class IconButton(tk.Canvas):
    """Compact square icon button (edit / delete / theme toggle)."""

    def __init__(self, parent, app, icon, command=None, size=30, icon_size=16,
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
        bg = bg or parent.cget("bg")
        super().__init__(parent, width=size, height=size, bg=bg, highlightthickness=0,
                         bd=0, cursor="hand2")
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self):
        self.delete("all")
        if self._hover:
            rrect(self, 0, 0, self._size, self._size, self._radius, fill=self.c["surface2"])
        draw_icon(self, self._icon, self._size / 2, self._size / 2, size=self._icon_size,
                  color=self._hover_color if self._hover else self._color, width=1.7)

    def _on_enter(self, _event):
        self._hover = True
        self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._draw()

    def _on_click(self, _event):
        if self._command:
            self._command()


class CheckCircle(tk.Canvas):
    """Habit completion control: rounded square that fills when done."""

    def __init__(self, parent, app, checked=False, color=None, command=None,
                 size=26, bg=None):
        self.app = app
        self.c = app.c
        self._checked = bool(checked)
        self._color = color or self.c["primary"]
        self._command = command
        self._size = size
        self._pulse_items = []
        super().__init__(parent, width=size, height=size, bg=bg or parent.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Enter>", lambda _e: self._draw(hover=True))
        self.bind("<Leave>", lambda _e: self._draw(hover=False))
        self.bind("<Button-1>", self._on_click)
        self._draw()

    def _draw(self, hover=False):
        self.delete("all")
        size = self._size
        inset = 1.5
        radius = size * 0.32
        if self._checked:
            rrect(self, inset, inset, size - inset, size - inset, radius, fill=self._color)
            draw_icon(self, "check", size / 2, size / 2, size=size * 0.62,
                      color=readable_on(self._color), width=2.4)
        else:
            outline = self._color if hover else self.c["border_hi"]
            rrect(self, inset, inset, size - inset, size - inset, radius,
                  outline=outline, width=1.6)

    def _on_click(self, _event):
        self._pulse()
        if self._command:
            self._command()

    def _pulse(self):
        size = self._size
        for item in self._pulse_items:
            try:
                self.delete(item)
            except tk.TclError:
                pass
        self._pulse_items = rrect(self, -2, -2, size + 2, size + 2, size * 0.36,
                                  outline=self._color, width=1)
        self.after(180, self._clear_pulse)

    def _clear_pulse(self):
        for item in self._pulse_items:
            try:
                self.delete(item)
            except tk.TclError:
                pass
        self._pulse_items = []

    def set_checked(self, checked: bool):
        self._checked = bool(checked)
        self._draw()


class ProgressRing(tk.Canvas):
    """Arc-based completion ring with an eased fill animation."""

    def __init__(self, parent, app, size=176, thickness=12, pct=0.0, bg=None,
                 color=None, caption="complete", sub=None):
        self.app = app
        self.c = app.c
        self._size = size
        self._thickness = thickness
        self._color = color or self.c["primary"]
        self._pct = 0.0
        self._target = max(0.0, min(1.0, pct))
        self._caption = caption
        self._sub = sub
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
        steps = 20
        interval = max(12, int(duration / steps))

        def step(index):
            if not self.winfo_exists():
                return
            t = index / steps
            eased = 1 - (1 - t) ** 3
            self._pct = start + (pct - start) * eased
            self._draw(self._pct)
            if index < steps:
                self._animation = self.after(interval, lambda: step(index + 1))

        step(1)

    def set_labels(self, caption=None, sub=None):
        if caption is not None:
            self._caption = caption
        self._sub = sub
        self._draw(self._pct)

    def _draw(self, pct):
        self.delete("all")
        size = self._size
        pad = self._thickness / 2 + 2
        box = (pad, pad, size - pad, size - pad)
        self.create_oval(*box, outline=self.c["ring_track"], width=self._thickness)
        if pct > 0.001:
            self.create_arc(*box, start=90, extent=-359.99 * pct, style="arc",
                            outline=self._color, width=self._thickness)
            # bright cap for a subtle neon shoulder
            self.create_arc(*box, start=90, extent=-min(359.99 * pct, 8), style="arc",
                            outline=mix(self._color, "#FFFFFF", 0.45), width=self._thickness - 2)
        self.create_text(size / 2, size / 2 - 6, text=f"{int(round(pct * 100))}%",
                         font=(FONT_FAMILY, int(size * 0.19), "bold"), fill=self.c["text"])
        self.create_text(size / 2, size / 2 + int(size * 0.14), text=self._caption,
                         font=(FONT_FAMILY, 9), fill=self.c["text2"])
        if self._sub:
            self.create_text(size / 2, size / 2 + int(size * 0.14) + 17, text=self._sub,
                             font=(FONT_FAMILY, 9, "bold"), fill=self.c["primary_l"])


class WeekBars(tk.Canvas):
    """Seven-day completion chart drawn with rounded neon bars."""

    def __init__(self, parent, app, height=136, values=None, labels=None,
                 highlight=None, bg=None, show_values=True):
        self.app = app
        self.c = app.c
        self._values = list(values or [])
        self._labels = list(labels or [])
        self._highlight = highlight
        self._show_values = show_values
        self._progress = 0.0
        self._bg = bg or parent.cget("bg")
        super().__init__(parent, height=height, bg=self._bg, highlightthickness=0, bd=0)
        self.bind("<Configure>", lambda _e: self._draw(self._progress))
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
        if not self.winfo_exists():
            return
        self._progress = min(1.0, self._progress + 0.14)
        self._draw(1 - (1 - self._progress) ** 2.4 if self._progress < 1 else 1.0)
        if self._progress < 1:
            self.after(24, self._animate)

    def _draw(self, progress):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 10 or height <= 10 or not self._values:
            return
        c = self.c
        label_band = 22
        value_band = 16
        chart_height = height - label_band - value_band
        baseline = value_band + chart_height
        slot = width / len(self._values)
        bar_width = min(30, max(10, slot * 0.44))

        for index, value in enumerate(self._values):
            centre = slot * index + slot / 2
            is_today = self._highlight == index
            # Faint track behind every slot so empty days read as empty, not noise.
            rrect(self, centre - bar_width / 2, baseline - chart_height,
                  centre + bar_width / 2, baseline, min(7, bar_width / 2),
                  fill=mix(self._bg, c["surface3"], 0.22))
            bar_height = max(3.0, (value / 100.0) * chart_height * progress)
            top = baseline - bar_height
            if is_today:
                color = c["primary"]
            elif value > 0:
                color = mix(c["primary_d"], c["primary"], 0.45)
            else:
                color = c["surface3"]
            rrect(self, centre - bar_width / 2, top, centre + bar_width / 2, baseline,
                  min(7, bar_width / 2), fill=color)
            if is_today:
                rrect(self, centre - bar_width / 2 - 3, top - 3,
                      centre + bar_width / 2 + 3, baseline + 3,
                      min(10, bar_width / 2 + 3), outline=mix(c["primary"], c["bg"], 0.55),
                      width=1)
            if self._show_values and value > 0 and progress > 0.85:
                self.create_text(centre, top - 9, text=f"{int(value)}%",
                                 font=(FONT_FAMILY, 8, "bold"),
                                 fill=c["primary_l"] if is_today else c["text3"])
            label = self._labels[index] if index < len(self._labels) else ""
            self.create_text(centre, baseline + 13, text=label,
                             font=(FONT_FAMILY, 9, "bold" if is_today else "normal"),
                             fill=c["primary_l"] if is_today else c["text2"])


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
        self._option_width = option_width
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
        rrect(self, 0, 0, self._width, self._height, self._height / 2, fill=c["surface2"])
        rrect(self, 0.5, 0.5, self._width - 0.5, self._height - 0.5, self._height / 2,
              outline=c["border"], width=1)
        index = self._segments.index(self._value) if self._value in self._segments else 0
        pad = 4
        pill_w = self._width / len(self._segments) - pad
        rrect(self, pad + index * (self._width / len(self._segments)), pad,
              pad + index * (self._width / len(self._segments)) + pill_w,
              self._height - pad, (self._height - pad * 2) / 2, fill=c["primary"])
        for position, option in enumerate(self._segments):
            centre = (self._width / len(self._segments)) * position + self._width / len(self._segments) / 2
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
# TOASTS
# ==================================================================
def show_toast(root, message, theme, kind="success", duration=2600):
    """Floating confirmation toast with a short fade in/out."""
    accents = {
        "success": theme["success"],
        "info": theme["primary"],
        "warning": theme["warning"],
        "danger": theme["danger"],
        "xp": theme["primary_l"],
    }
    icons = {"success": "check", "info": "info", "warning": "bolt", "danger": "close", "xp": "spark"}
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
    width, height = 360, 62
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    x = screen_w - width - 28
    y = screen_h - height - 64
    toast.geometry(f"{width}x{height}+{x}+{y}")
    toast.configure(bg=theme["bg"])

    canvas = tk.Canvas(toast, width=width, height=height, bg=theme["bg"],
                       highlightthickness=0, bd=0)
    canvas.pack()
    rrect(canvas, 1, 1, width - 1, height - 1, 14, fill=theme["toast"])
    rrect(canvas, 1, 1, width - 1, height - 1, 14,
          outline=mix(theme["border"], accent, 0.45), width=1)
    rrect(canvas, 1, 14, 4, height - 14, 1.5, fill=accent)
    draw_icon(canvas, icon, 30, height / 2, size=17, color=accent, width=2)
    canvas.create_text(52, height / 2, text=message, anchor="w",
                       font=(FONT_FAMILY, 10), fill=theme["text"])

    try:
        toast.attributes("-alpha", 0.0)
    except tk.TclError:
        pass

    def fade(step, target, done=None):
        if not toast.winfo_exists():
            return
        alpha = step / 6
        try:
            toast.attributes("-alpha", 0.0 if target == 0 else alpha)
        except tk.TclError:
            pass
        if step < 6:
            toast.after(22, lambda: fade(step + 1, target, done))
        elif done:
            done()

    def dismiss():
        def close():
            if toast.winfo_exists():
                toast.destroy()

        fade(6, 0, close)

    fade(0, 1)
    toast.after(duration, dismiss)
# ==================================================================
# FORM CONTROLS + HABIT DIALOG
# ==================================================================
def configure_ttk(root, theme):
    """Theme the ttk widgets that Tk does not paint itself (comboboxes)."""
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
        padding=6,
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
    style.configure("HF.Vertical.TScrollbar", background=theme["surface3"])


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
        rrect(self, 1, 1, self._width - 1, self._height - 1, (self._height - 2) / 2, fill=track)
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
    """Selectable chip used for categories and weekday toggles."""

    def __init__(self, parent, app, text, color=None, selected=False, command=None,
                 height=28, font_size=9, bg=None, dot=False, width=None):
        self.app = app
        self.c = app.c
        self._text = text
        self._color = color or self.c["primary"]
        self._selected = selected
        self._command = command
        self._height = height
        self._font = (FONT_FAMILY, font_size, "bold")
        self._dot = dot
        text_width = tkfont.Font(font=self._font).measure(text)
        self._width = width or text_width + (34 if dot else 22)
        super().__init__(parent, width=self._width, height=height, bg=bg or parent.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", lambda _e: self._draw(hover=True))
        self.bind("<Leave>", lambda _e: self._draw(hover=False))
        self._draw()

    def _draw(self, hover=False):
        self.delete("all")
        c = self.c
        if self._selected:
            rrect(self, 1, 1, self._width - 1, self._height - 1, self._height / 2,
                  fill=self._color)
        else:
            border = mix(c["border"], self._color, 0.55 if hover else 0.25)
            rrect(self, 1, 1, self._width - 1, self._height - 1, self._height / 2,
                  fill=c["surface2"] if hover else None,
                  outline=border, width=1)
        fg = readable_on(self._color) if self._selected else (self._color if hover else c["text2"])
        text_x = self._width / 2
        if self._dot:
            self.create_oval(11, self._height / 2 - 3, 17, self._height / 2 + 3,
                             fill=fg, outline="")
            text_x = 20 + (self._width - 20) / 2
        self.create_text(text_x, self._height / 2 + 0.5, text=self._text, font=self._font, fill=fg)

    def set_selected(self, selected: bool):
        self._selected = bool(selected)
        self._draw()

    def _on_click(self, _event):
        if self._command:
            self._command(self._text)


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
        self.bind("<Escape>", lambda _e: self.destroy())
        self.bind("<Return>", self._on_return)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()

    # -- layout helpers ----------------------------------------------
    def _centre_on(self, parent):
        try:
            px, py = parent.winfo_rootx(), parent.winfo_rooty()
            pw, ph = parent.winfo_width(), parent.winfo_height()
        except tk.TclError:
            return
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = px + max(0, (pw - width) // 2)
        y = py + max(0, (ph - height) // 3)
        self.geometry(f"+{x}+{y}")

    def _label(self, parent, text, top=14):
        return tk.Label(parent, text=text, bg=self.c["bg"] if parent is self._outer else self.c["surface"],
                        fg=self.c["text2"], font=f(9, "bold"), anchor="w")

    def _entry(self, parent, textvariable):
        wrap = tk.Frame(parent, bg=self.c["surface2"], highlightthickness=1,
                        highlightbackground=self.c["border"], highlightcolor=self.c["border"])
        entry = tk.Entry(wrap, textvariable=textvariable, bg=self.c["surface2"],
                         fg=self.c["text"], insertbackground=self.c["text"],
                         relief="flat", bd=0, font=f(11), highlightthickness=0)
        entry.pack(fill="x", padx=11, pady=9)
        entry.bind("<FocusIn>", lambda _e: wrap.configure(highlightbackground=self.c["primary"]))
        entry.bind("<FocusOut>", lambda _e: wrap.configure(highlightbackground=self.c["border"]))
        return wrap, entry

    # -- build -------------------------------------------------------
    def _build(self, is_edit):
        c = self.c
        outer = tk.Frame(self, bg=c["bg"], padx=24, pady=20)
        outer.pack(fill="both", expand=True)
        self._outer = outer

        header = tk.Frame(outer, bg=c["bg"])
        header.pack(fill="x")

        tile = tk.Canvas(header, width=40, height=40, bg=c["bg"], highlightthickness=0, bd=0)
        tile.pack(side="left")
        rrect(tile, 0, 0, 40, 40, 12, fill=c["primary_soft"])
        draw_icon(tile, "pencil" if is_edit else "plus", 20, 20, size=19, color=c["primary_l"], width=2)

        title_box = tk.Frame(header, bg=c["bg"])
        title_box.pack(side="left", padx=12)
        tk.Label(title_box, text="Edit habit" if is_edit else "New habit",
                 bg=c["bg"], fg=c["text"], font=f(15, "bold"), anchor="w").pack(anchor="w")
        tk.Label(title_box, text="Small, repeatable, and yours." if not is_edit else "Update the details of this habit.",
                 bg=c["bg"], fg=c["text2"], font=f(9), anchor="w").pack(anchor="w")

        close = IconButton(header, self.app, "close", command=self.destroy,
                           size=30, icon_size=15, bg=c["bg"])
        close.pack(side="right", pady=4)

        divider(outer, self.app, pady=(16, 6))

        body = tk.Frame(outer, bg=c["bg"])
        body.pack(fill="both", expand=True)

        # Name
        self._label(body, "Habit name").pack(fill="x", pady=(8, 5))
        self.v_name = tk.StringVar()
        name_wrap, self.e_name = self._entry(body, self.v_name)
        name_wrap.pack(fill="x")
        self.lbl_error = tk.Label(body, text="", bg=c["bg"], fg=c["danger"], font=f(9), anchor="w")
        self.lbl_error.pack(fill="x")

        # Category
        self._label(body, "Category").pack(fill="x", pady=(8, 5))
        cat_grid = tk.Frame(body, bg=c["bg"])
        cat_grid.pack(fill="x")
        self.v_cat = tk.StringVar(value="Other")
        self._cat_chips = []
        for index, (category, colour) in enumerate(CATEGORIES.items()):
            chip = ChoiceChip(cat_grid, self.app, category, color=colour, dot=True,
                              bg=c["bg"], height=28,
                              command=lambda name: self._select_category(name))
            chip.grid(row=index // 4, column=index % 4, padx=(0, 6), pady=3, sticky="w")
            self._cat_chips.append(chip)
        self._select_category("Other")

        # Target + recurrence
        row = tk.Frame(body, bg=c["bg"])
        row.pack(fill="x", pady=(6, 0))
        left = tk.Frame(row, bg=c["bg"])
        left.pack(side="left", fill="x", expand=True, padx=(0, 10))
        right = tk.Frame(row, bg=c["bg"])
        right.pack(side="left", fill="x", expand=True)

        self._label(left, "Daily target (optional)").pack(fill="x", pady=(8, 5))
        self.v_target = tk.StringVar()
        target_wrap, _target_entry = self._entry(left, self.v_target)
        target_wrap.pack(fill="x")

        self._label(right, "Repeat").pack(fill="x", pady=(8, 5))
        self.v_rec = tk.StringVar(value="Daily")
        self.combo = ttk.Combobox(right, textvariable=self.v_rec, values=RECURRENCE_OPTIONS,
                                  state="readonly", style="HF.TCombobox", font=f(10))
        self.combo.pack(fill="x", ipady=2)
        self.combo.bind("<<ComboboxSelected>>", lambda _e: self._sync_custom_days())

        # Custom weekdays (only for "Custom Days")
        self.days_row = tk.Frame(body, bg=c["bg"])
        self.day_vars = []
        self._day_chips = []
        for index, day in enumerate(WEEKDAY_NAMES):
            var = tk.BooleanVar()
            self.day_vars.append(var)
            chip = ChoiceChip(self.days_row, self.app, day, bg=c["bg"], height=28, width=52,
                              command=lambda name, i=index: self._toggle_day(i))
            chip.grid(row=0, column=index, padx=(0, 4), pady=2)
            self._day_chips.append(chip)

        # Notes
        self._label(body, "Notes (optional)").pack(fill="x", pady=(10, 5))
        notes_wrap = tk.Frame(body, bg=c["surface2"], highlightthickness=1,
                              highlightbackground=c["border"])
        notes_wrap.pack(fill="x")
        self.t_notes = tk.Text(notes_wrap, height=3, bg=c["surface2"], fg=c["text"],
                               insertbackground=c["text"], relief="flat", bd=0,
                               font=f(10), wrap="word", padx=9, pady=8)
        self.t_notes.pack(fill="x")
        self.t_notes.bind("<FocusIn>", lambda _e: notes_wrap.configure(highlightbackground=c["primary"]))
        self.t_notes.bind("<FocusOut>", lambda _e: notes_wrap.configure(highlightbackground=c["border"]))

        # Pin
        pin_row = tk.Frame(body, bg=c["bg"])
        pin_row.pack(fill="x", pady=(14, 0))
        self.v_pin = tk.BooleanVar(value=False)
        switch = Switch(pin_row, self.app, value=False, bg=c["bg"],
                        command=lambda value: self.v_pin.set(value))
        switch.pack(side="left")
        pin_text = tk.Frame(pin_row, bg=c["bg"])
        pin_text.pack(side="left", padx=10)
        tk.Label(pin_text, text="Pin to top", bg=c["bg"], fg=c["text"],
                 font=f(10, "bold"), anchor="w").pack(anchor="w")
        tk.Label(pin_text, text="Keep this habit at the top of today's list",
                 bg=c["bg"], fg=c["text3"], font=f(9), anchor="w").pack(anchor="w")

        # Footer
        divider(outer, self.app, pady=(18, 12))
        footer = tk.Frame(outer, bg=c["bg"])
        footer.pack(fill="x")
        HoverButton(footer, self.app, "Save habit", command=self._save, icon="check",
                    kind="primary", bg=c["bg"], height=38, padx=18).pack(side="right")
        HoverButton(footer, self.app, "Cancel", command=self.destroy, kind="soft",
                    bg=c["bg"], height=38, padx=16).pack(side="right", padx=(0, 8))
        tk.Label(footer, text="Enter to save  ·  Esc to cancel", bg=c["bg"],
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
        for widget in self.winfo_children():
            for child in widget.winfo_children():
                pass
        # keep the pin switch in sync with stored state
        self.v_pin.set(bool(task.get("pinned", False)))
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
        recurrence_days = [i for i, var in enumerate(self.day_vars) if var.get()] \
            if recurrence == "Custom Days" else []
        if recurrence == "Custom Days" and not recurrence_days:
            self.lbl_error.configure(text="Pick at least one weekday, or choose another repeat option.")
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
    """A single habit, rendered as an interactive card."""

    def __init__(self, parent, app, task, done=False, stats=None, on_toggle=None,
                 on_edit=None, on_delete=None, compact=False):
        self.app = app
        self.task = task
        self._done = bool(done)
        self._stats = stats or {}
        self._on_toggle = on_toggle
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._compact = compact
        self._hover = False
        color = CATEGORIES.get(task.get("category"), app.c["primary"])
        super().__init__(
            parent, app,
            radius=12,
            padding=(12, 9) if compact else (14, 11),
            accent=color,
            bg=parent.cget("bg"),
        )
        self._category_color = color
        self._build()

    # -- construction -------------------------------------------------
    def _build(self):
        c = self.c
        body = self.body
        body.columnconfigure(1, weight=1)

        self._check = CheckCircle(
            body, self.app, checked=self._done, color=self._category_color,
            command=self._handle_toggle, size=24 if self._compact else 26, bg=c["card"],
        )
        self._check.grid(row=0, column=0, rowspan=2, padx=(0, 12), sticky="w")

        name_row = tk.Frame(body, bg=c["card"])
        name_row.grid(row=0, column=1, sticky="ew")

        self._name = tk.Label(
            name_row, text=self.task["name"], bg=c["card"],
            fg=c["text"], font=f(11 if not self._compact else 10, "bold"), anchor="w",
        )
        self._name.pack(side="left")
        if self.task.get("pinned"):
            pin = tk.Canvas(name_row, width=16, height=16, bg=c["card"],
                            highlightthickness=0, bd=0)
            pin.pack(side="left", padx=(6, 0))
            draw_icon(pin, "pin", 8, 8, size=13, color=c["text3"], width=1.6)

        streak = (self._stats or {}).get("streak", 0)
        self._streak_label = None
        if streak > 0:
            chip_frame = tk.Frame(name_row, bg=mix(c["warning"], c["card"], 0.86), padx=6, pady=1)
            chip_frame.pack(side="left", padx=(8, 0))
            flame = tk.Canvas(chip_frame, width=12, height=12, bg=chip_frame.cget("bg"),
                              highlightthickness=0, bd=0)
            flame.pack(side="left", padx=(0, 3))
            draw_icon(flame, "flame", 6, 6, size=11, color=c["warning"], width=1.6)
            self._streak_label = tk.Label(
                chip_frame, text=f"{streak}", bg=chip_frame.cget("bg"),
                fg=c["warning"], font=f(8, "bold"),
            )
            self._streak_label.pack(side="left")

        actions = tk.Frame(body, bg=c["card"])
        actions.grid(row=0, column=2, rowspan=2, sticky="e", padx=(8, 0))
        if self._on_edit:
            IconButton(actions, self.app, "pencil", command=lambda: self._on_edit(self.task),
                       size=28, icon_size=14, bg=c["card"], color=c["text3"],
                       hover_color=c["primary_l"]).pack(side="left")
        if self._on_delete:
            IconButton(actions, self.app, "trash", command=lambda: self._on_delete(self.task),
                       size=28, icon_size=14, bg=c["card"], color=c["text3"],
                       hover_color=c["danger"]).pack(side="left", padx=(2, 0))

        meta = tk.Frame(body, bg=c["card"])
        meta.grid(row=1, column=1, sticky="ew", pady=(3, 0))
        Chip(meta, self.app, self.task.get("category", "Other"),
             color=self._category_color, bg=c["card"]).pack(side="left", padx=(0, 6))
        if self.task.get("daily_target"):
            Chip(meta, self.app, self.task["daily_target"], color=c["text2"], filled=False,
                 bg=c["card"]).pack(side="left", padx=(0, 6))
        if self.task.get("recurrence") and self.task["recurrence"] != "Daily":
            Chip(meta, self.app, self.task["recurrence"], color=c["text2"], filled=False,
                 bg=c["card"]).pack(side="left", padx=(0, 6))
        if self.task.get("notes") and not self._compact:
            note = self.task["notes"]
            if len(note) > 64:
                note = note[:64].rstrip() + "…"
            tk.Label(meta, text=note, bg=c["card"], fg=c["text3"], font=f(8),
                     anchor="w").pack(side="left", padx=(2, 0))

        bind_tree(self, "<Enter>", self._on_enter, skip=("Button",))
        bind_tree(self, "<Leave>", self._on_leave, skip=("Button",))
        self._apply_state()

    # -- state --------------------------------------------------------
    def _apply_state(self):
        c = self.c
        done = self._done
        if done:
            self._name.configure(fg=c["text3"], font=f(10, "bold", "overstrike"))
            self._border = mix(c["border"], c["success"], 0.45)
        else:
            self._name.configure(fg=c["text"], font=f(11 if not self._compact else 10, "bold"))
            self._border = c["border"]
        try:
            self._draw(self.canvas.winfo_width(), self.canvas.winfo_height())
        except tk.TclError:
            pass

    def set_done(self, done, stats=None):
        self._done = bool(done)
        if stats is not None:
            self._stats = stats
        self._check.set_checked(self._done)
        self._apply_state()
        if self._streak_label is not None:
            streak = (self._stats or {}).get("streak", 0)
            self._streak_label.configure(text=f"{streak}")

    def _handle_toggle(self):
        if self._on_toggle:
            new_state = self._on_toggle(self.task, self._check)
            self.set_done(new_state, self.app.dm.habit_stats(self.task, 30))

    # -- hover --------------------------------------------------------
    def _on_enter(self, _event=None):
        if self._hover:
            return
        self._hover = True
        self.set_glow(True)

    def _on_leave(self, _event=None):
        self.after(70, self._check_leave)

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
        self.set_glow(False)


# ==================================================================
# VIEW - HABITS
# ==================================================================
class HabitsViewMixin:
    """Habits list with search, category filters and empty states."""

    def _view_habits(self):
        c = self.c
        tasks = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        done = sum(1 for t in tasks if t["id"] in done_ids)

        toolbar = tk.Frame(self.content, bg=c["bg"])
        toolbar.pack(fill="x", padx=28, pady=(20, 0))
        left = tk.Frame(toolbar, bg=c["bg"])
        left.pack(side="left")
        self._habit_counts_label = tk.Label(
            left, text=self._habit_header_text(tasks, done), bg=c["bg"], fg=c["text"],
            font=f(13, "bold"), anchor="w",
        )
        self._habit_counts_label.pack(anchor="w")
        tk.Label(left, text="Pinned habits stay on top · completed habits dim down",
                 bg=c["bg"], fg=c["text3"], font=f(9), anchor="w").pack(anchor="w")

        actions = tk.Frame(toolbar, bg=c["bg"])
        actions.pack(side="right")
        HoverButton(actions, self, "New habit", command=self._open_add_task, icon="plus",
                    kind="primary", height=36, bg=c["bg"]).pack(side="left", padx=(8, 0))
        self._habit_mark_all = HoverButton(
            actions, self, "Complete all", command=self._shortcut_mark_all, icon="check",
            kind="soft", height=36, font_size=9, bg=c["bg"],
        )
        self._habit_mark_all.pack(side="left", padx=(0, 8))
        self._habit_mark_all.set_enabled(bool(tasks) and done < len(tasks))

        search_wrap = tk.Frame(actions, bg=c["surface2"], highlightthickness=1,
                               highlightbackground=c["border"])
        search_wrap.pack(side="left", padx=(0, 10))
        search_icon = tk.Canvas(search_wrap, width=26, height=30, bg=c["surface2"],
                                highlightthickness=0, bd=0)
        search_icon.pack(side="left", padx=(6, 0))
        draw_icon(search_icon, "search", 13, 15, size=14, color=c["text3"], width=1.7)
        self._search_entry = tk.Entry(
            search_wrap, textvariable=self._search_var, bg=c["surface2"], fg=c["text"],
            insertbackground=c["text"], relief="flat", bd=0, font=f(9), width=20,
            highlightthickness=0, readonlybackground=c["surface2"],
            selectbackground=c["primary"], selectforeground="#FFFFFF",
        )
        self._search_entry.pack(side="left", padx=(4, 10), pady=6)

        filters = tk.Frame(self.content, bg=c["bg"])
        filters.pack(fill="x", padx=28, pady=(14, 10))
        self._filter_chips = {}
        for category in ["All"] + CAT_LIST:
            color = c["primary"] if category == "All" else CATEGORIES.get(category)
            selected = self._filter_cat.get() == category
            chip = ChoiceChip(filters, self, category, color=color, selected=selected,
                              bg=c["bg"], height=26, font_size=8)
            chip.configure(cursor="hand2")
            chip.bind("<Button-1>", lambda _e, cat=category: self._set_cat_filter(cat), add="+")
            chip.pack(side="left", padx=(0, 6))
            self._filter_chips[category] = chip

        self._task_scroll = ScrollableFrame(
            self.content, c["bg"], padding=0,
            track=mix(c["border"], c["bg"], 0.4), thumb=c["border_hi"],
        )
        self._task_scroll.pack(fill="both", expand=True, padx=28, pady=(0, 16))

        self._render_habit_list()

    def _habit_header_text(self, tasks=None, done=None):
        tasks = self.dm.get_scheduled_today() if tasks is None else tasks
        done_ids = self.dm.get_completed_today()
        done = sum(1 for t in tasks if t["id"] in done_ids) if done is None else done
        if not tasks:
            return "No habits scheduled today"
        return f"{done} of {len(tasks)} habits complete today"

    def _update_habit_header(self):
        label = getattr(self, "_habit_counts_label", None)
        if label is not None:
            try:
                label.configure(text=self._habit_header_text())
            except tk.TclError:
                pass
        mark_all = getattr(self, "_habit_mark_all", None)
        if mark_all is not None:
            tasks = self.dm.get_scheduled_today()
            done_ids = self.dm.get_completed_today()
            mark_all.set_enabled(bool(tasks) and sum(1 for t in tasks if t["id"] in done_ids) < len(tasks))

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
            self._empty_state(inner, c["bg"], "Nothing scheduled today",
                              "Every habit is either unscheduled for today or not created yet. "
                              "Add a habit to get started.", "New habit", self._open_add_task)
            return
        if not visible:
            self._empty_state(inner, c["bg"], "No habits match",
                              "Try a different search term or clear the category filter.",
                              "Clear filters", self._clear_filters, icon="search")
            return

        pinned = [t for t in visible if t.get("pinned")]
        others = [t for t in visible if not t.get("pinned")]

        def section(title, items):
            if not items:
                return
            head = tk.Frame(inner, bg=c["bg"])
            head.pack(fill="x", pady=(10, 4))
            if title == "Pinned":
                icon = tk.Canvas(head, width=14, height=14, bg=c["bg"],
                                 highlightthickness=0, bd=0)
                icon.pack(side="left", padx=(0, 5))
                draw_icon(icon, "pin", 7, 7, size=12, color=c["text3"], width=1.6)
            tk.Label(head, text=title.upper(), bg=c["bg"], fg=c["text3"],
                     font=(FONT_FAMILY, 8, "bold"), anchor="w").pack(side="left")
            tk.Label(head, text=f"{len(items)}", bg=c["bg"], fg=c["text3"],
                     font=f(8), anchor="w").pack(side="left", padx=(6, 0))
            for task in items:
                row = HabitRow(
                    inner, self, task, task["id"] in done_ids,
                    stats=self.dm.habit_stats(task, 30),
                    on_toggle=self._toggle_from_list,
                    on_edit=self._open_edit_task,
                    on_delete=self._delete_task,
                )
                row.pack(fill="x", pady=3)
                self._habit_rows[task["id"]] = row

        section("Pinned", pinned)
        section("Today", others)
        tk.Frame(inner, bg=c["bg"], height=18).pack()
# ==================================================================
# CHARTS + STATISTICS VIEW
# ==================================================================
class TrendChart(tk.Canvas):
    """Smooth completion trend with a stippled area fill (no dependencies)."""

    def __init__(self, parent, app, values, labels=None, height=180, color=None, bg=None):
        self.c = app.c
        self._values = list(values)
        self._labels = list(labels or [])
        self._color = color or self.c["primary"]
        self._bg = bg or parent.cget("bg")
        self._progress = 0.0
        super().__init__(parent, height=height, bg=self._bg, highlightthickness=0, bd=0)
        self.bind("<Configure>", lambda _e: self._draw(self._progress))
        self.after(80, self._animate)

    def _animate(self):
        if not self.winfo_exists():
            return
        self._progress = min(1.0, self._progress + 0.12)
        self._draw(1 - (1 - self._progress) ** 2.5 if self._progress < 1 else 1.0)
        if self._progress < 1:
            self.after(26, self._animate)

    def _draw(self, progress=1.0):
        self.delete("all")
        c = self.c
        width = self.winfo_width()
        height = self.winfo_height()
        if width < 40 or height < 40 or not self._values:
            return
        left, right, top, bottom = 34, 14, 16, 24
        chart_w = width - left - right
        chart_h = height - top - bottom
        count = len(self._values)

        for level in (0, 25, 50, 75, 100):
            y = top + chart_h - (level / 100) * chart_h
            self.create_line(left, y, width - right, y, fill=c["border"], dash=(2, 5))
            self.create_text(left - 8, y, text=str(level), anchor="e",
                             font=(FONT_FAMILY, 7), fill=c["text3"])

        def point(index, value):
            x = left + (chart_w * index / max(1, count - 1))
            y = top + chart_h - (max(0.0, min(100.0, value)) / 100) * chart_h * progress
            return x, y

        points = [point(index, value) for index, value in enumerate(self._values)]
        if len(points) > 1:
            area = points + [(points[-1][0], top + chart_h), (points[0][0], top + chart_h)]
            flat = [coord for pair in area for coord in pair]
            self.create_polygon(*flat, fill=self._color, stipple="gray25", outline="")
            line = [coord for pair in points for coord in pair]
            self.create_line(*line, fill=self._color, width=2, smooth=True,
                             splinesteps=12, capstyle="round", joinstyle="round")
        for index, (x, y) in enumerate(points):
            last = index == len(points) - 1
            radius = 3.4 if last else 2.2
            self.create_oval(x - radius, y - radius, x + radius, y + radius,
                             fill=self._color if last else c["surface"],
                             outline=self._color, width=1.4)
            if last and progress > 0.9:
                self.create_oval(x - 7, y - 7, x + 7, y + 7, outline=self._color,
                                 width=1, dash=(2, 3))
                value = self._values[index]
                self.create_text(min(width - right - 18, x + 4), max(top + 8, y - 13),
                                 text=f"{int(value)}%", anchor="e",
                                 font=(FONT_FAMILY, 8, "bold"), fill=c["primary_l"])
        step = max(1, count // 7)
        for index in range(0, count, step):
            x = left + (chart_w * index / max(1, count - 1))
            label = self._labels[index] if index < len(self._labels) else ""
            self.create_text(x, height - 8, text=label, font=(FONT_FAMILY, 8), fill=c["text2"])


def inline_progress(parent, app, fraction, color=None, height=6, width=150):
    canvas = tk.Canvas(parent, height=height, width=width, bg=parent.cget("bg"),
                       highlightthickness=0, bd=0)
    fraction = max(0.0, min(1.0, fraction))

    def draw(_event=None):
        canvas.delete("all")
        total = canvas.winfo_width() or width
        rrect(canvas, 0, 0, total, height, height / 2, fill=app.c["prog_bg"])
        if fraction > 0:
            rrect(canvas, 0, 0, max(height, total * fraction), height, height / 2,
                  fill=color or app.c["primary"])

    canvas.bind("<Configure>", draw)
    canvas.after(30, draw)
    return canvas


class StatsViewMixin:
    """Statistics overview built entirely from stored data."""

    def _section_label(self, parent, text, pady=(18, 8)):
        tk.Label(parent, text=text.upper(), bg=self.c["bg"], fg=self.c["text3"],
                 font=(FONT_FAMILY, 8, "bold"), anchor="w").pack(fill="x", padx=28, pady=pady)

    def _view_stats(self):
        c = self.c
        scroll = ScrollableFrame(self.content, c["bg"], padding=0,
                                 track=mix(c["border"], c["bg"], 0.4), thumb=c["border_hi"])
        scroll.pack(fill="both", expand=True)
        page = scroll.inner
        pad = 28

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

        header = tk.Frame(page, bg=c["bg"])
        header.pack(fill="x", padx=pad, pady=(22, 0))
        tk.Label(header, text="Performance overview", bg=c["bg"], fg=c["text"],
                 font=f(20, "bold"), anchor="w").pack(anchor="w")
        tk.Label(header, text=f"{today.strftime('%B %Y')}  ·  {elapsed} days tracked this month",
                 bg=c["bg"], fg=c["text2"], font=f(10), anchor="w").pack(anchor="w", pady=(2, 0))

        tiles = [
            ("chart", f"{week_avg}%", "Weekly average", "Mon to Sun", c["primary_l"]),
            ("target", f"{month_avg}%", "Monthly average", "elapsed days", c["accent"]),
            ("trophy", f"{perfect_month}", "Perfect days", "this month", c["success"]),
            ("flame", f"{streak}", "Current streak", f"best {best}", c["warning"]),
            ("spark", f"{consistency * 100:.0f}%", "30-day consistency", "average", c["purple_l"]),
            ("bolt", f"{xp:,}", "Total XP", f"level {level} · {level_name}", c["primary_l"]),
        ]
        grid = tk.Frame(page, bg=c["bg"])
        grid.pack(fill="x", padx=pad, pady=(16, 0))
        for index, (icon, value, label, hint, color) in enumerate(tiles):
            tile = Card(grid, self, radius=14, padding=(14, 12))
            column = index % 3
            row = index // 3
            tile.grid(row=row, column=column, sticky="nsew",
                      padx=(0 if column == 0 else 10, 0), pady=(0 if row == 0 else 10, 0))
            grid.columnconfigure(column, weight=1, uniform="stat")
            top = tk.Frame(tile.body, bg=c["card"])
            top.pack(fill="x")
            IconTile(top, self, icon, color=color, size=32, bg=c["card"]).pack(side="left")
            value_box = tk.Frame(top, bg=c["card"])
            value_box.pack(side="left", padx=10)
            tk.Label(value_box, text=value, bg=c["card"], fg=c["text"], font=f(17, "bold"),
                     anchor="w").pack(anchor="w")
            tk.Label(value_box, text=label, bg=c["card"], fg=c["text2"], font=f(8),
                     anchor="w").pack(anchor="w")
            tk.Label(tile.body, text=hint, bg=c["card"], fg=c["text3"], font=f(8),
                     anchor="w").pack(anchor="w", pady=(7, 0))

        body = tk.Frame(page, bg=c["bg"])
        body.pack(fill="both", expand=True, padx=pad, pady=(14, 0))
        body.columnconfigure(0, weight=3, uniform="stats")
        body.columnconfigure(1, weight=2, uniform="stats")

        week_card = Card(body, self, radius=16, padding=(18, 16))
        week_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        head = tk.Frame(week_card.body, bg=c["card"])
        head.pack(fill="x")
        tk.Label(head, text="Last 7 days", bg=c["card"], fg=c["text"],
                 font=f(12, "bold"), anchor="w").pack(side="left")
        tk.Label(head, text=f"{week_avg}% average", bg=c["card"], fg=c["primary_l"],
                 font=f(9, "bold"), anchor="e").pack(side="right")
        labels = [day.strftime("%a") for day in self.dm.get_week_dates()]
        WeekBars(week_card.body, self, height=150, values=week, labels=labels,
                 highlight=today.weekday(), bg=c["card"]).pack(fill="x", pady=(10, 4))
        tk.Label(week_card.body, text="Completion rate per day. Today is highlighted.",
                 bg=c["card"], fg=c["text3"], font=f(8), anchor="w").pack(anchor="w")

        achievements_card = Card(body, self, radius=16, padding=(18, 16))
        achievements_card.grid(row=0, column=1, sticky="nsew")
        items = self._achievements()
        head = tk.Frame(achievements_card.body, bg=c["card"])
        head.pack(fill="x", pady=(0, 6))
        tk.Label(head, text="Achievements", bg=c["card"], fg=c["text"],
                 font=f(12, "bold"), anchor="w").pack(side="left")
        tk.Label(head, text=f"{sum(1 for i in items if i['earned'])}/{len(items)}",
                 bg=c["card"], fg=c["text2"], font=f(9), anchor="e").pack(side="right")
        for item in items:
            self._achievement_row(achievements_card.body, item)

        trend_card = Card(page, self, radius=16, padding=(18, 16))
        trend_card.pack(fill="x", padx=pad, pady=(14, 0))
        head = tk.Frame(trend_card.body, bg=c["card"])
        head.pack(fill="x")
        tk.Label(head, text=f"Month trend  ·  {today.strftime('%B')}", bg=c["card"],
                 fg=c["text"], font=f(12, "bold"), anchor="w").pack(side="left")
        tk.Label(head, text=f"{month_avg}% average", bg=c["card"], fg=c["accent"],
                 font=f(9, "bold"), anchor="e").pack(side="right")
        if any(value > 0 for value in month_elapsed):
            TrendChart(trend_card.body, self, month_elapsed,
                       labels=[str(index + 1) for index in range(len(month_elapsed))],
                       height=190, bg=c["card"]).pack(fill="x", pady=(10, 0))
        else:
            tk.Label(trend_card.body, text="Complete a few habits to see your month take shape.",
                     bg=c["card"], fg=c["text3"], font=f(9), anchor="w").pack(anchor="w", pady=18)

        consistency_card = Card(page, self, radius=16, padding=(18, 16))
        consistency_card.pack(fill="x", padx=pad, pady=(14, 24))
        head = tk.Frame(consistency_card.body, bg=c["card"])
        head.pack(fill="x", pady=(0, 8))
        tk.Label(head, text="Habit consistency", bg=c["card"], fg=c["text"],
                 font=f(12, "bold"), anchor="w").pack(side="left")
        tk.Label(head, text="last 30 days", bg=c["card"], fg=c["text3"],
                 font=f(9), anchor="e").pack(side="right")

        tasks = sorted(self.dm.data["tasks"],
                       key=lambda t: self.dm.habit_stats(t, 30)["rate"], reverse=True)
        if not tasks:
            tk.Label(consistency_card.body, text="No habits yet — add one to start tracking.",
                     bg=c["card"], fg=c["text3"], font=f(9), anchor="w").pack(anchor="w")
        for task in tasks:
            stats = self.dm.habit_stats(task, 30)
            color = CATEGORIES.get(task.get("category"), c["primary"])
            row = tk.Frame(consistency_card.body, bg=c["card"])
            row.pack(fill="x", pady=4)
            dot = tk.Canvas(row, width=10, height=10, bg=c["card"], highlightthickness=0, bd=0)
            dot.pack(side="left", padx=(0, 8))
            rrect(dot, 0, 0, 10, 10, 3, fill=color)
            tk.Label(row, text=task["name"], bg=c["card"], fg=c["text"], font=f(9),
                     anchor="w", width=24).pack(side="left")
            inline_progress(row, self, stats["rate"], color=color, width=150).pack(
                side="left", padx=(4, 10))
            tk.Label(row, text=f"{int(round(stats['rate'] * 100))}%", bg=c["card"],
                     fg=c["text2"], font=f(9, "bold"), width=4, anchor="e").pack(side="left")
            tk.Label(row, text=f"{stats['done']}/{stats['scheduled']}", bg=c["card"],
                     fg=c["text3"], font=f(8), width=7, anchor="e").pack(side="left", padx=(4, 8))
            if stats["streak"] > 0:
                chip = tk.Frame(row, bg=mix(c["warning"], c["card"], 0.86), padx=6, pady=1)
                chip.pack(side="right")
                tk.Label(chip, text=f"{stats['streak']} day streak",
                         bg=chip.cget("bg"), fg=c["warning"], font=f(8, "bold")).pack()

    # -- calendar -----------------------------------------------------
    def _view_calendar(self):
        c = self.c
        frame = tk.Frame(self.content, bg=c["bg"])
        frame.pack(fill="both", expand=True, padx=28, pady=(20, 16))

        nav = tk.Frame(frame, bg=c["bg"])
        nav.pack(fill="x", pady=(0, 12))
        left = tk.Frame(nav, bg=c["bg"])
        left.pack(side="left")
        tk.Label(left, text="History", bg=c["bg"], fg=c["text"], font=f(15, "bold"),
                 anchor="w").pack(anchor="w")
        self.lbl_cal_month = tk.Label(left, text="", bg=c["bg"], fg=c["text2"],
                                      font=f(9), anchor="w")
        self.lbl_cal_month.pack(anchor="w")

        controls = tk.Frame(nav, bg=c["bg"])
        controls.pack(side="right")
        HoverButton(controls, self, "Today", command=self._cal_today, kind="soft",
                    height=32, font_size=9, bg=c["bg"]).pack(side="right", padx=(8, 0))
        next_btn = IconButton(controls, self, "chevron-right", command=self._cal_next,
                              size=32, icon_size=16, bg=c["bg"], color=c["text2"])
        next_btn.pack(side="right", padx=(4, 0))
        prev_btn = IconButton(controls, self, "chevron-left", command=self._cal_prev,
                              size=32, icon_size=16, bg=c["bg"], color=c["text2"])
        prev_btn.pack(side="right")

        legend = tk.Frame(frame, bg=c["bg"])
        legend.pack(fill="x", pady=(0, 10))
        for label, color in (("Perfect", c["success"]), ("Partial", c["warning"]),
                             ("Missed", c["danger"]), ("Future", c["text3"])):
            dot = tk.Canvas(legend, width=10, height=10, bg=c["bg"],
                            highlightthickness=0, bd=0)
            dot.pack(side="left", padx=(0, 5))
            rrect(dot, 0, 0, 10, 10, 3, fill=color)
            tk.Label(legend, text=label, bg=c["bg"], fg=c["text2"], font=f(8)).pack(
                side="left", padx=(0, 14))

        self.cal_grid_frame = tk.Frame(frame, bg=c["bg"])
        self.cal_grid_frame.pack(fill="both", expand=True)
        self.lbl_cal_summary = tk.Label(frame, text="", bg=c["bg"], fg=c["text3"],
                                        font=f(9), anchor="w")
        self.lbl_cal_summary.pack(fill="x", pady=(10, 0))

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
            tk.Label(self.cal_grid_frame, text=name.upper(), bg=c["bg"], fg=c["text3"],
                     font=(FONT_FAMILY, 7, "bold")).grid(row=0, column=index, sticky="w",
                                                         padx=6, pady=(0, 6))
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
                                day == today, c["bg"])
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
        return (f"{perfect} perfect  ·  {partial} partial  ·  {missed} missed  ·  "
                f"{date(year, month, 1).strftime('%B')} {year}")

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

    HEIGHT = 66
    STATES = {
        "perfect": ("success", 0.80),
        "partial": ("warning", 0.84),
        "missed": ("danger", 0.86),
        "none": ("surface", 0.55),
        "future": ("surface", 0.35),
    }

    def __init__(self, parent, app, day, state, pct, is_today, bg):
        self.app = app
        self.c = app.c
        self._day = day
        self._state = state
        self._pct = pct
        self._today = is_today
        super().__init__(parent, height=self.HEIGHT, bg=bg, highlightthickness=0, bd=0)
        self.bind("<Configure>", lambda _e: self._draw())

    def _draw(self):
        self.delete("all")
        c = self.c
        width = self.winfo_width()
        height = self.HEIGHT
        if width < 8:
            return
        color_key, mix_ratio = self.STATES.get(self._state, ("surface", 0.4))
        fill = mix(c[color_key], c["bg"], mix_ratio)
        outline = c["primary"] if self._today else mix(fill, c["border"], 0.55)
        rrect(self, 1, 1, width - 1, height - 1, 10, fill=fill)
        rrect(self, 1, 1, width - 1, height - 1, 10, outline=outline,
              width=1.4 if self._today else 1)

        text_color = c["primary_l"] if self._today else (
            c[color_key] if self._state in ("perfect", "partial", "missed") else c["text3"])
        self.create_text(10, 10, text=str(self._day), anchor="nw",
                         font=(FONT_FAMILY, 9, "bold" if self._today else "normal"),
                         fill=text_color)

        if self._state == "perfect":
            draw_icon(self, "check", width - 16, height - 16, size=14,
                      color=c["success"], width=2.2)
        elif self._state == "partial":
            self.create_text(width - 9, height - 9, text=f"{int(round(self._pct * 100))}%",
                             anchor="se", font=(FONT_FAMILY, 8, "bold"), fill=c["warning"])
        elif self._state == "missed":
            draw_icon(self, "close", width - 16, height - 16, size=12,
                      color=c["danger"], width=1.8)
        elif self._today:
            self.create_text(width - 9, height - 9, text="today", anchor="se",
                             font=(FONT_FAMILY, 7, "bold"), fill=c["primary_l"])
# ==================================================================
# VIEW - SETTINGS
# ==================================================================
class SettingsViewMixin:
    """Appearance, data management and about information."""

    def _view_settings(self):
        c = self.c
        scroll = ScrollableFrame(self.content, c["bg"], padding=0,
                                 track=mix(c["border"], c["bg"], 0.4), thumb=c["border_hi"])
        scroll.pack(fill="both", expand=True)
        page = scroll.inner
        pad = 28

        tk.Label(page, text="Preferences", bg=c["bg"], fg=c["text"], font=f(20, "bold"),
                 anchor="w").pack(fill="x", padx=pad, pady=(22, 0))
        tk.Label(page, text="Everything stays on this device — no account, no sync, no tracking.",
                 bg=c["bg"], fg=c["text2"], font=f(9), anchor="w").pack(
            fill="x", padx=pad, pady=(2, 0))

        # Appearance
        self._settings_section(page, "Appearance")
        appearance = Card(page, self, radius=16, padding=(18, 16))
        appearance.pack(fill="x", padx=pad)
        row = tk.Frame(appearance.body, bg=c["card"])
        row.pack(fill="x")
        IconTile(row, self, "sun" if self._theme_name == "dark" else "moon",
                 color=c["primary_l"], size=36, bg=c["card"]).pack(side="left")
        text_box = tk.Frame(row, bg=c["card"])
        text_box.pack(side="left", padx=12)
        tk.Label(text_box, text="Color theme", bg=c["card"], fg=c["text"],
                 font=f(10, "bold"), anchor="w").pack(anchor="w")
        tk.Label(text_box, text="Dark command center or a lighter workspace",
                 bg=c["card"], fg=c["text3"], font=f(9), anchor="w").pack(anchor="w")
        Segmented(row, self, ["Dark", "Light"],
                  "Dark" if self._theme_name == "dark" else "Light",
                  command=lambda label: self._apply_theme(label.lower()),
                  bg=c["card"]).pack(side="right")

        # Data
        self._settings_section(page, "Your data")
        data_card = Card(page, self, radius=16, padding=(18, 16))
        data_card.pack(fill="x", padx=pad)
        info = tk.Frame(data_card.body, bg=c["card"])
        info.pack(fill="x")
        IconTile(info, self, "archive", color=c["accent"], size=36, bg=c["card"]).pack(side="left")
        info_text = tk.Frame(info, bg=c["card"])
        info_text.pack(side="left", padx=12)
        tk.Label(info_text, text="Local data file", bg=c["card"], fg=c["text"],
                 font=f(10, "bold"), anchor="w").pack(anchor="w")
        tk.Label(info_text, text=DATA_FILE, bg=c["card"], fg=c["text3"], font=mono(8),
                 anchor="w").pack(anchor="w")
        buttons = tk.Frame(data_card.body, bg=c["card"])
        buttons.pack(fill="x", pady=(14, 0))
        HoverButton(buttons, self, "Export JSON", command=self._export, icon="download",
                    kind="soft", height=36, font_size=9, bg=c["card"]).pack(side="left")
        HoverButton(buttons, self, "Import JSON", command=self._import, icon="upload",
                    kind="soft", height=36, font_size=9, bg=c["card"]).pack(side="left", padx=8)
        HoverButton(buttons, self, "Create backup", command=self._backup, icon="archive",
                    kind="success", height=36, font_size=9, bg=c["card"]).pack(side="left")
        HoverButton(buttons, self, "Reset all data", command=self._reset_data, icon="reset",
                    kind="danger", height=36, font_size=9, bg=c["card"]).pack(side="right")
        tk.Label(data_card.body,
                 text="Import replaces the current data file and keeps an automatic backup first.",
                 bg=c["card"], fg=c["text3"], font=f(8), anchor="w").pack(anchor="w", pady=(10, 0))

        # Shortcuts
        self._settings_section(page, "Keyboard shortcuts")
        shortcuts_card = Card(page, self, radius=16, padding=(18, 14))
        shortcuts_card.pack(fill="x", padx=pad)
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
            tk.Label(row, text=description, bg=c["card"], fg=c["text2"], font=f(9),
                     anchor="w").pack(side="left", padx=12)

        # About
        self._settings_section(page, "About")
        about = Card(page, self, radius=16, padding=(18, 16), glow=True)
        about.pack(fill="x", padx=pad, pady=(0, 24))
        head = tk.Frame(about.body, bg=c["card"])
        head.pack(fill="x")
        logo = tk.Canvas(head, width=38, height=38, bg=c["card"], highlightthickness=0, bd=0)
        logo.pack(side="left")
        rrect(logo, 0, 0, 38, 38, 12, fill=c["primary_d"])
        draw_icon(logo, "layers", 19, 19, size=19, color="#FFFFFF", width=1.7)
        title_box = tk.Frame(head, bg=c["card"])
        title_box.pack(side="left", padx=12)
        tk.Label(title_box, text=f"{APP_NAME} {VERSION}", bg=c["card"], fg=c["text"],
                 font=f(11, "bold"), anchor="w").pack(anchor="w")
        tk.Label(title_box, text="Offline habit tracking · built on tkinter",
                 bg=c["card"], fg=c["text3"], font=f(9), anchor="w").pack(anchor="w")
        tk.Label(about.body,
                 text="Your habits, streaks and XP are stored in a single JSON file on this "
                      "computer. Nothing leaves the device.",
                 bg=c["card"], fg=c["text2"], font=f(9), anchor="w", justify="left",
                 wraplength=760).pack(anchor="w", pady=(12, 0))

    def _settings_section(self, parent, title):
        tk.Label(parent, text=title.upper(), bg=self.c["bg"], fg=self.c["text3"],
                 font=(FONT_FAMILY, 8, "bold"), anchor="w").pack(
            fill="x", padx=28, pady=(20, 8))

    def _key_chip(self, parent, text):
        c = self.c
        width = tkfont.Font(font=mono(8, "bold")).measure(text) + 18
        canvas = tk.Canvas(parent, width=width, height=24, bg=c["card"],
                           highlightthickness=0, bd=0)
        rrect(canvas, 0.5, 0.5, width - 0.5, 23.5, 6, fill=c["surface2"])
        rrect(canvas, 0.5, 0.5, width - 0.5, 23.5, 6, outline=c["border"], width=1)
        canvas.create_text(width / 2, 12.5, text=text, font=mono(8, "bold"), fill=c["text2"])
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
            "This permanently deletes every habit, completion record, streak and XP point.\n\n"
            "A backup is created first. Continue?",
            icon="warning", parent=self.root,
        ):
            return
        self.dm.reset()
        self._reload_after_data_change("Dashboard")
        self.toast("Data reset · fresh start", "info")

    def _reload_after_data_change(self, view="Dashboard"):
        """Rebuild the whole shell so every counter reflects the new data."""
        self._active_view = view
        self._apply_theme(self._theme_name)
# ==================================================================
# SHARED UI HELPERS
# ==================================================================
def bind_tree(widget, sequence, callback, skip=("Canvas",)):
    """Bind an event on a widget and all of its descendants."""
    widget.bind(sequence, callback)
    for child in widget.winfo_children():
        if child.winfo_class() in skip:
            continue
        bind_tree(child, sequence, callback, skip)


def muted_label(parent, text, bg, color=None, size=9, weight="normal"):
    return tk.Label(parent, text=text, bg=bg, fg=color, font=f(size, weight), anchor="w")


class IconTile(tk.Canvas):
    """Small rounded icon chip used in cards and lists."""

    def __init__(self, parent, app, icon, color=None, size=36, bg=None, soft=True, icon_size=18):
        self.c = app.c
        color = color or self.c["primary"]
        super().__init__(parent, width=size, height=size, bg=bg or parent.cget("bg"),
                         highlightthickness=0, bd=0)
        rrect(self, 0, 0, size, size, size * 0.3,
              fill=mix(color, self.c["card"], 0.82) if soft else color)
        draw_icon(self, icon, size / 2, size / 2, size=icon_size,
                  color=color if soft else readable_on(color), width=1.8)


class NavButton(tk.Canvas):
    """Sidebar navigation item with an active-state accent bar."""

    def __init__(self, parent, app, icon, label, command, width=212, height=42):
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
        self.bind("<Button-1>", lambda _e: self._command(label))
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._draw()

    def _draw(self):
        self.delete("all")
        c = self.c
        if self._active:
            rrect(self, 4, 1, self._width - 6, self._height - 1, 10, fill=c["side_active"])
            rrect(self, 4, self._height * 0.28, 6.5, self._height * 0.72, 1.25,
                  fill=c["primary"])
        elif self._hover:
            rrect(self, 4, 1, self._width - 6, self._height - 1, 10,
                  fill=mix(c["sidebar"], c["side_active"], 0.55))
        icon_color = c["primary_l"] if self._active else (c["side_text"] if self._hover else c["side_text2"])
        text_color = c["side_text"] if self._active or self._hover else c["side_text2"]
        draw_icon(self, self._icon, 24, self._height / 2, size=18, color=icon_color, width=1.8)
        self.create_text(44, self._height / 2 + 0.5, text=self._label, anchor="w",
                         font=(FONT_FAMILY, 10, "bold" if self._active else "normal"),
                         fill=text_color)

    def set_active(self, active: bool):
        self._active = bool(active)
        self._draw()

    def _on_enter(self, _event):
        self._hover = True
        self._draw()

    def _on_leave(self, _event):
        self._hover = False
        self._draw()


def xp_bar(parent, app, fraction, height=6, color=None, track=None):
    canvas = tk.Canvas(parent, height=height, bg=parent.cget("bg"),
                       highlightthickness=0, bd=0)
    fraction = max(0.0, min(1.0, fraction))

    def draw(_event=None):
        canvas.delete("all")
        width = canvas.winfo_width() or 160
        rrect(canvas, 0, 0, width, height, height / 2, fill=track or app.c["prog_bg"])
        if fraction > 0:
            filled = max(height, width * fraction)
            rrect(canvas, 0, 0, filled, height, height / 2, fill=color or app.c["primary"])

    canvas.bind("<Configure>", draw)
    canvas.after(30, draw)
    return canvas


# ==================================================================
# MAIN WINDOW
# ==================================================================
class HabitFlowApp(HabitsViewMixin, StatsViewMixin, SettingsViewMixin):
    """HabitFlow 2.0 - a command center for daily discipline."""

    NAV_ITEMS = [
        ("grid", "Dashboard"),
        ("list", "Habits"),
        ("chart", "Statistics"),
        ("calendar", "Calendar"),
        ("settings", "Settings"),
    ]

    VIEW_SUBTITLES = {
        "Dashboard": "Your day at a glance",
        "Habits": "Create, edit and complete your routines",
        "Statistics": "Consistency, trends and streaks",
        "Calendar": "Your perfect-day history",
        "Settings": "Preferences, data and shortcuts",
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
        self._dashboard_rows = {}
        self._dashboard = {}

        self._setup_window()
        self._build_layout()
        self._show("Dashboard")
        self._tick_clock()

        if self.dm.award_perfect_day_if_due():
            self.root.after(600, lambda: self.toast("Perfect day complete  ·  +50 XP", "xp"))

    # -- window ------------------------------------------------------
    def _setup_window(self):
        self.root.title(f"{APP_NAME}  ·  {VERSION}")
        self.root.configure(bg=self.c["bg"])
        self.root.geometry("1280x820")
        self.root.minsize(1040, 700)
        self.root.bind("<Control-n>", lambda _e: self._open_add_task())
        self.root.bind("<Control-d>", self._shortcut_mark_all)
        self.root.bind("<F5>", lambda _e: self._refresh())
        self.root.bind("<Control-f>", lambda _e: self._focus_search())
        self.root.bind("<Control-q>", lambda _e: self.on_close())
        for index, (_icon, name) in enumerate(self.NAV_ITEMS):
            self.root.bind(f"<Control-Key-{index + 1}>", lambda _e, n=name: self._show(n))

    def toast(self, message, kind="success"):
        show_toast(self.root, message, self.c, kind=kind)

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
        self.sidebar = tk.Frame(self.root, bg=c["sidebar"], width=236)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=c["sidebar"])
        brand.pack(fill="x", padx=18, pady=(22, 18))
        logo = tk.Canvas(brand, width=38, height=38, bg=c["sidebar"],
                         highlightthickness=0, bd=0)
        logo.pack(side="left")
        rrect(logo, 0, 0, 38, 38, 12, fill=c["primary_d"])
        rrect(logo, 0, 0, 38, 38, 12, outline=c["primary"], width=1)
        draw_icon(logo, "layers", 19, 19, size=19, color="#FFFFFF", width=1.7)

        brand_text = tk.Frame(brand, bg=c["sidebar"])
        brand_text.pack(side="left", padx=10)
        tk.Label(brand_text, text=APP_NAME, bg=c["sidebar"], fg=c["side_text"],
                 font=f(14, "bold"), anchor="w").pack(anchor="w")
        tk.Label(brand_text, text="COMMAND CENTER", bg=c["sidebar"], fg=c["text3"],
                 font=(FONT_FAMILY, 7, "bold"), anchor="w").pack(anchor="w")

        tk.Label(self.sidebar, text="WORKSPACE", bg=c["sidebar"], fg=c["text3"],
                 font=(FONT_FAMILY, 7, "bold"), anchor="w").pack(fill="x", padx=24, pady=(6, 6))

        for icon, label in self.NAV_ITEMS:
            button = NavButton(self.sidebar, self, icon, label, self._show)
            button.pack(fill="x", padx=8, pady=1)
            self._nav_buttons[label] = button

        footer = tk.Frame(self.sidebar, bg=c["sidebar"])
        footer.pack(side="bottom", fill="x", padx=14, pady=14)

        xp, level, level_name, xp_in, xp_for = self.dm.get_xp_info()
        level_card = tk.Frame(footer, bg=c["sidebar"])
        level_card.pack(fill="x")
        level_box = tk.Frame(level_card, bg=c["sidebar2"], padx=12, pady=10)
        level_box.pack(fill="x")
        top = tk.Frame(level_box, bg=c["sidebar2"])
        top.pack(fill="x")
        self._sidebar_level_label = tk.Label(
            top, text=f"LEVEL {level}", bg=c["sidebar2"], fg=c["primary_l"],
            font=(FONT_FAMILY, 8, "bold"), anchor="w")
        self._sidebar_level_label.pack(side="left")
        self._sidebar_level_name = tk.Label(
            top, text=level_name, bg=c["sidebar2"], fg=c["side_text2"],
            font=f(8), anchor="e")
        self._sidebar_level_name.pack(side="right")
        self._sidebar_xp_fraction = min(1.0, xp_in / xp_for) if xp_for else 1.0
        self._sidebar_bar = tk.Canvas(level_box, height=6, bg=c["sidebar2"],
                                     highlightthickness=0, bd=0)
        self._sidebar_bar.pack(fill="x", pady=(7, 5))
        self._sidebar_bar.bind("<Configure>", self._draw_sidebar_bar)
        self._sidebar_xp_label = tk.Label(
            level_box, text=f"{xp:,} XP  ·  {max(0, xp_for - xp_in):,} to next",
            bg=c["sidebar2"], fg=c["text3"], font=(FONT_FAMILY, 7), anchor="w")
        self._sidebar_xp_label.pack(fill="x")
        self.root.after(60, self._draw_sidebar_bar)

        tk.Label(footer, text=f"v{VERSION}  ·  offline & private", bg=c["sidebar"],
                 fg=c["text3"], font=(FONT_FAMILY, 7), anchor="w").pack(fill="x", pady=(10, 0))

    def _draw_sidebar_bar(self, _event=None):
        bar = getattr(self, "_sidebar_bar", None)
        if bar is None:
            return
        try:
            if not bar.winfo_exists():
                return
            width = bar.winfo_width() or 160
            bar.delete("all")
            rrect(bar, 0, 0, width, 6, 3, fill=shade(self.c["sidebar2"], 2.1))
            filled = max(6, width * self._sidebar_xp_fraction)
            rrect(bar, 0, 0, filled, 6, 3, fill=self.c["primary"])
        except tk.TclError:
            pass

    def _refresh_sidebar_xp(self):
        xp, level, level_name, xp_in, xp_for = self.dm.get_xp_info()
        self._sidebar_xp_fraction = min(1.0, xp_in / xp_for) if xp_for else 1.0
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
        bar = tk.Frame(self.main, bg=c["bg"])
        bar.pack(fill="x")
        inner = tk.Frame(bar, bg=c["bg"], height=70)
        inner.pack(fill="x", padx=28, pady=(16, 10))
        inner.pack_propagate(False)

        titles = tk.Frame(inner, bg=c["bg"])
        titles.pack(side="left")
        self.lbl_page = tk.Label(titles, text="Dashboard", bg=c["bg"], fg=c["text"],
                                 font=f(17, "bold"), anchor="w")
        self.lbl_page.pack(anchor="w")
        self.lbl_subtitle = tk.Label(titles, text="", bg=c["bg"], fg=c["text2"],
                                     font=f(9), anchor="w")
        self.lbl_subtitle.pack(anchor="w")

        right = tk.Frame(inner, bg=c["bg"])
        right.pack(side="right")

        self.btn_theme = IconButton(
            right, self, "sun" if self._theme_name == "dark" else "moon",
            command=self._toggle_theme, size=32, icon_size=16, bg=c["bg"],
            color=c["text2"], hover_color=c["primary_l"],
        )
        self.btn_theme.pack(side="right", padx=(10, 0))

        self.lbl_clock = tk.Label(right, text="", bg=c["bg"], fg=c["text2"], font=f(9))
        self.lbl_clock.pack(side="right", padx=(0, 4))

        self._streak_chip = tk.Canvas(right, height=32, width=112, bg=c["bg"],
                                     highlightthickness=0, bd=0)
        self._streak_chip.pack(side="right", padx=(0, 12))
        self._draw_streak_chip()

        tk.Frame(self.main, bg=c["border"], height=1).pack(fill="x")

    def _draw_streak_chip(self):
        canvas = self._streak_chip
        c = self.c
        streak = self.dm.calculate_streak()
        label = f"{streak} day{'s' if streak != 1 else ''}"
        bold = tkfont.Font(family=FONT_FAMILY, size=9, weight="bold")
        small = tkfont.Font(family=FONT_FAMILY, size=8)
        # Size the chip to its text so it never overlaps the clock beside it.
        text_x = 36
        streak_x = text_x + bold.measure(label) + 5
        width = streak_x + small.measure("streak") + 14
        canvas.configure(width=width)
        canvas.delete("all")
        rrect(canvas, 0, 0, width, 32, 16, fill=mix(c["warning"], c["bg"], 0.82),
              outline=mix(c["border"], c["warning"], 0.35), width=1)
        draw_icon(canvas, "flame", 20, 16, size=15, color=c["warning"], width=1.8)
        canvas.create_text(text_x, 16, anchor="w", text=label,
                           font=(FONT_FAMILY, 9, "bold"), fill=c["text"])
        canvas.create_text(streak_x, 16, anchor="w", text="streak",
                           font=(FONT_FAMILY, 8), fill=c["text2"])

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

        self._active_view = view_name
        self.lbl_page.configure(text=view_name)
        self.lbl_subtitle.configure(text=self.VIEW_SUBTITLES.get(view_name, ""))
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

    def _refresh(self):
        self._show(self._active_view or "Dashboard")

    def _focus_search(self):
        if self._search_entry is not None:
            try:
                self._search_entry.focus_set()
            except tk.TclError:
                pass

    # -- dashboard ---------------------------------------------------
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
             "earned": total >= 1, "progress": f"{min(total, 1)}/1"},
            {"icon": "flame", "name": "Week of fire", "desc": "7 perfect days in a row",
             "earned": best >= 7, "progress": f"{min(best, 7)}/7"},
            {"icon": "trophy", "name": "Perfect day", "desc": "Finish every habit in a day",
             "earned": perfect >= 1, "progress": f"{min(perfect, 1)}/1"},
            {"icon": "target", "name": "Steady month", "desc": "80% consistency over 30 days",
             "earned": consistency >= 0.8 and total >= 20,
             "progress": f"{int(round(consistency * 100))}/80%"},
            {"icon": "bolt", "name": "Level 5", "desc": "Reach level five",
             "earned": level >= 5, "progress": f"L{level}/5"},
            {"icon": "layers", "name": "Century", "desc": "100 habit check-ins",
             "earned": total >= 100, "progress": f"{min(total, 100)}/100"},
        ]

    def _view_dashboard(self):
        c = self.c
        scroll = ScrollableFrame(self.content, c["bg"], padding=0,
                                 track=mix(c["border"], c["bg"], 0.4),
                                 thumb=c["border_hi"])
        scroll.pack(fill="both", expand=True)
        page = scroll.inner
        pad = 28

        tasks = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        total = len(tasks)
        done = sum(1 for t in tasks if t["id"] in done_ids)
        pct = done / total if total else 0.0
        streak = self.dm.calculate_streak()

        # Header
        header = tk.Frame(page, bg=c["bg"])
        header.pack(fill="x", padx=pad, pady=(22, 0))
        left = tk.Frame(header, bg=c["bg"])
        left.pack(side="left")
        tk.Label(left, text=self._greeting(), bg=c["bg"], fg=c["text"],
                 font=f(23, "bold"), anchor="w").pack(anchor="w")
        today = date.today()
        date_line = f"{WEEKDAY_FULL[today.weekday()]}, {today.strftime('%d %B %Y')}"
        tk.Label(left, text=date_line, bg=c["bg"], fg=c["text2"], font=f(10),
                 anchor="w").pack(anchor="w", pady=(2, 0))
        HoverButton(header, self, "New habit", command=self._open_add_task, icon="plus",
                    kind="primary", bg=c["bg"], height=38).pack(side="right", pady=6)

        # Hero
        hero = Card(page, self, radius=20, padding=(24, 22), glow=True)
        hero.pack(fill="x", padx=pad, pady=(16, 0))
        hero.body.columnconfigure(0, weight=0)
        hero.body.columnconfigure(1, weight=1)

        ring = ProgressRing(hero.body, self, size=168, thickness=12, pct=pct,
                            bg=c["card"], caption="today's habits")
        ring.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 26))

        score_box = tk.Frame(hero.body, bg=c["card"])
        score_box.grid(row=0, column=1, sticky="ew")
        tk.Label(score_box, text="DAILY SCORE", bg=c["card"], fg=c["text3"],
                 font=(FONT_FAMILY, 8, "bold"), anchor="w").pack(anchor="w")
        score_row = tk.Frame(score_box, bg=c["card"])
        score_row.pack(fill="x", pady=(0, 2))
        status_text, status_color = self._score_status(pct)
        score_value = tk.Label(score_row, text=str(int(round(pct * 100))), bg=c["card"],
                               fg=c["text"], font=f(34, "bold"))
        score_value.pack(side="left")
        tk.Label(score_row, text="/100", bg=c["card"], fg=c["text3"],
                 font=f(12)).pack(side="left", pady=(12, 0), padx=(4, 10))
        status = tk.Label(score_row, text=status_text, bg=c["card"], fg=status_color,
                          font=f(10, "bold"))
        status.pack(side="left", pady=(12, 0))

        if total == 0:
            summary_text = "No habits scheduled today."
        elif done == total:
            summary_text = f"All {total} habits complete. Perfect day secured."
        else:
            summary_text = f"{done} of {total} habits complete  ·  {total - done} to go"
        summary = tk.Label(score_box, text=summary_text, bg=c["card"], fg=c["text2"],
                           font=f(10), anchor="w")
        summary.pack(anchor="w", pady=(0, 12))

        chips = tk.Frame(score_box, bg=c["card"])
        chips.pack(anchor="w")
        chip_data = [
            ("check", f"{done} done", c["success"]),
            ("target", f"{max(0, total - done)} remaining", c["warning"] if total - done else c["text2"]),
            ("flame", f"{streak} day streak", c["primary_l"]),
        ]
        for icon, text, color in chip_data:
            chip = tk.Frame(chips, bg=mix(color, c["card"], 0.86), padx=9, pady=4)
            chip.pack(side="left", padx=(0, 8))
            icon_canvas = tk.Canvas(chip, width=14, height=14, bg=chip.cget("bg"),
                                    highlightthickness=0, bd=0)
            icon_canvas.pack(side="left", padx=(0, 5))
            draw_icon(icon_canvas, icon, 7, 7, size=12, color=color, width=1.8)
            tk.Label(chip, text=text, bg=chip.cget("bg"), fg=color,
                     font=f(8, "bold")).pack(side="left")

        actions = tk.Frame(hero.body, bg=c["card"])
        actions.grid(row=1, column=1, sticky="ew", pady=(16, 0))
        HoverButton(actions, self, "Today's habits", command=lambda: self._show("Habits"),
                    icon="arrow-right", kind="soft", bg=c["card"], height=34,
                    font_size=9).pack(side="left")
        mark_all = HoverButton(actions, self, "Complete all", command=self._shortcut_mark_all,
                               icon="check", kind="ghost", bg=c["card"], height=34,
                               font_size=9)
        mark_all.pack(side="left", padx=(8, 0))
        if total == 0 or done == total:
            mark_all.set_enabled(False)

        self._dashboard.update({
            "ring": ring,
            "score": score_value,
            "status": status,
            "summary": summary,
            "streak_chip": chips,
            "mark_all": mark_all,
        })

        # KPI tiles
        kpis = tk.Frame(page, bg=c["bg"])
        kpis.pack(fill="x", padx=pad, pady=(14, 0))
        week = self.dm.get_week_pcts()
        week_avg = round(sum(week) / 7) if week else 0
        _xp, level, level_name, _in, _for = self.dm.get_xp_info()
        best = self.dm.best_streak()
        tiles = [
            ("flame", f"{streak}", "Current streak", "days in a row", c["warning"]),
            ("trophy", f"{best}", "Best streak", "personal record", c["primary_l"]),
            ("chart", f"{week_avg}%", "Weekly average", "Mon to Sun", c["accent"]),
            ("bolt", f"L{level}", "Level", level_name, c["purple_l"]),
        ]
        for index, (icon, value, label, hint, color) in enumerate(tiles):
            tile = Card(kpis, self, radius=14, padding=(16, 14))
            tile.grid(row=0, column=index, sticky="nsew",
                      padx=(0 if index == 0 else 10, 0))
            kpis.columnconfigure(index, weight=1, uniform="kpi")
            row = tk.Frame(tile.body, bg=c["card"])
            row.pack(fill="x")
            IconTile(row, self, icon, color=color, size=34, bg=c["card"]).pack(side="left")
            value_box = tk.Frame(row, bg=c["card"])
            value_box.pack(side="left", padx=10)
            tk.Label(value_box, text=value, bg=c["card"], fg=c["text"],
                     font=f(18, "bold"), anchor="w").pack(anchor="w")
            tk.Label(value_box, text=label, bg=c["card"], fg=c["text2"],
                     font=f(8), anchor="w").pack(anchor="w")
            tk.Label(tile.body, text=hint, bg=c["card"], fg=c["text3"],
                     font=f(8), anchor="w").pack(anchor="w", pady=(8, 0))

        # Two-column body
        columns = tk.Frame(page, bg=c["bg"])
        columns.pack(fill="both", expand=True, padx=pad, pady=(14, 0))
        columns.columnconfigure(0, weight=3, uniform="cols")
        columns.columnconfigure(1, weight=2, uniform="cols")

        # Today's focus
        focus = Card(columns, self, radius=16, padding=(18, 16))
        focus.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        focus_header = tk.Frame(focus.body, bg=c["card"])
        focus_header.pack(fill="x")
        tk.Label(focus_header, text="Today's focus", bg=c["card"], fg=c["text"],
                 font=f(12, "bold"), anchor="w").pack(side="left")
        view_all = tk.Label(focus_header, text="View all", bg=c["card"], fg=c["primary_l"],
                            font=f(9, "bold"), cursor="hand2")
        view_all.pack(side="right")
        view_all.bind("<Button-1>", lambda _e: self._show("Habits"))
        tk.Label(focus.body, text=f"{done} of {total} complete", bg=c["card"], fg=c["text2"],
                 font=f(9), anchor="w").pack(anchor="w", pady=(2, 10))

        if not tasks:
            self._empty_state(focus.body, self.c["card"], "No habits scheduled today",
                              "Add a habit or adjust its repeat settings to see it here.",
                              button_text="Add a habit", command=self._open_add_task)
        else:
            for task in tasks[:6]:
                row = HabitRow(focus.body, self, task, task["id"] in done_ids,
                               stats=self.dm.habit_stats(task, 30), on_toggle=self._toggle_from_list,
                               compact=True)
                row.pack(fill="x", pady=3)
                self._dashboard_rows[task["id"]] = row
            if len(tasks) > 6:
                more = tk.Label(focus.body, text=f"+{len(tasks) - 6} more habits",
                                bg=c["card"], fg=c["text3"], font=f(9), anchor="w")
                more.pack(anchor="w", pady=(8, 0))

        # Right column
        right = tk.Frame(columns, bg=c["bg"])
        right.grid(row=0, column=1, sticky="nsew")

        week_card = Card(right, self, radius=16, padding=(18, 16))
        week_card.pack(fill="x")
        week_header = tk.Frame(week_card.body, bg=c["card"])
        week_header.pack(fill="x")
        tk.Label(week_header, text="This week", bg=c["card"], fg=c["text"],
                 font=f(12, "bold"), anchor="w").pack(side="left")
        tk.Label(week_header, text=f"{week_avg}% avg", bg=c["card"], fg=c["primary_l"],
                 font=f(9, "bold"), anchor="e").pack(side="right")
        labels = [day.strftime("%a") for day in self.dm.get_week_dates()]
        bars = WeekBars(week_card.body, self, height=132, values=week, labels=labels,
                        highlight=date.today().weekday(), bg=c["card"])
        bars.pack(fill="x", pady=(10, 0))

        milestone_card = Card(right, self, radius=16, padding=(18, 16))
        milestone_card.pack(fill="x", pady=(12, 0))
        header = tk.Frame(milestone_card.body, bg=c["card"])
        header.pack(fill="x", pady=(0, 8))
        tk.Label(header, text="Milestones", bg=c["card"], fg=c["text"],
                 font=f(12, "bold"), anchor="w").pack(side="left")
        earned_count = sum(1 for item in self._achievements() if item["earned"])
        tk.Label(header, text=f"{earned_count}/{len(self._achievements())}", bg=c["card"],
                 fg=c["text2"], font=f(9), anchor="e").pack(side="right")
        for item in self._achievements()[:4]:
            self._achievement_row(milestone_card.body, item, compact=True)

        # Quote
        quote, author = self.dm.get_daily_quote()
        quote_card = Card(page, self, radius=16, padding=(20, 16), fill=c["surface"])
        quote_card.pack(fill="x", padx=pad, pady=(14, 24))
        quote_row = tk.Frame(quote_card.body, bg=c["surface"])
        quote_row.pack(fill="x")
        mark = tk.Canvas(quote_row, width=26, height=26, bg=c["surface"],
                         highlightthickness=0, bd=0)
        mark.pack(side="left", padx=(0, 12), anchor="n")
        draw_icon(mark, "spark", 13, 13, size=16, color=c["purple_l"], width=1.6)
        text_box = tk.Frame(quote_row, bg=c["surface"])
        text_box.pack(side="left", fill="x", expand=True)
        tk.Label(text_box, text=f"“{quote}”", bg=c["surface"], fg=c["text"],
                 font=f(11, "normal", "italic"), wraplength=780,
                 justify="left", anchor="w").pack(anchor="w")
        tk.Label(text_box, text=f"— {author}", bg=c["surface"], fg=c["text2"],
                 font=f(9), anchor="w").pack(anchor="w", pady=(4, 0))

    def _achievement_row(self, parent, item, compact=False):
        c = self.c
        bg = parent.cget("bg")
        row = tk.Frame(parent, bg=bg)
        row.pack(fill="x", pady=2)
        color = c["primary_l"] if item["earned"] else c["text3"]
        IconTile(row, self, item["icon"], color=color, size=28,
                 bg=bg, soft=True, icon_size=15).pack(side="left", padx=(0, 9))
        text_box = tk.Frame(row, bg=bg)
        text_box.pack(side="left", fill="x", expand=True)
        tk.Label(text_box, text=item["name"], bg=bg,
                 fg=c["text"] if item["earned"] else c["text2"],
                 font=f(9, "bold"), anchor="w").pack(anchor="w")
        if not compact:
            tk.Label(text_box, text=item["desc"], bg=bg, fg=c["text3"],
                     font=f(8), anchor="w").pack(anchor="w")
        state = tk.Label(row, text=item["progress"] if not item["earned"] else "Earned",
                         bg=bg, fg=c["success"] if item["earned"] else c["text3"],
                         font=f(8, "bold"))
        state.pack(side="right")

    def _empty_state(self, parent, bg, title, description, button_text=None, command=None,
                     icon="spark"):
        box = tk.Frame(parent, bg=bg)
        box.pack(fill="x", pady=18)
        canvas = tk.Canvas(box, width=52, height=52, bg=bg, highlightthickness=0, bd=0)
        canvas.pack()
        rrect(canvas, 0, 0, 52, 52, 16, fill=mix(self.c["primary"], bg, 0.88))
        draw_icon(canvas, icon, 26, 26, size=22, color=self.c["primary_l"], width=1.7)
        tk.Label(box, text=title, bg=bg, fg=self.c["text"], font=f(11, "bold")).pack(pady=(8, 2))
        tk.Label(box, text=description, bg=bg, fg=self.c["text2"], font=f(9),
                 wraplength=320, justify="center").pack()
        if button_text and command:
            HoverButton(box, self, button_text, command=command, icon="plus",
                        kind="soft", bg=bg, height=34, font_size=9).pack(pady=(12, 0))

    # -- completion handling -----------------------------------------
    def _toggle_from_list(self, task, control):
        done_ids = self.dm.get_completed_today()
        new_state = task["id"] not in done_ids
        self.dm.toggle_task(task["id"], new_state)
        self._after_completion_change(task, new_state)
        return new_state

    def _after_completion_change(self, task, completed):
        if self.dm.award_perfect_day_if_due():
            self.toast("Perfect day complete  ·  +50 XP", "xp")
        elif completed:
            self.toast(f"{task['name']} complete  ·  +{XP_PER_TASK} XP", "success")
        if self._active_view == "Dashboard":
            self._refresh_dashboard_progress()
        elif self._active_view == "Habits":
            self._update_habit_header()
            self._draw_streak_chip()
        elif self._active_view == "Calendar":
            self._render_calendar()
        self._refresh_sidebar_xp()

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

        state["ring"].animate_to(pct)
        state["ring"].set_labels(caption="today's habits")
        state["score"].configure(text=str(int(round(pct * 100))))
        state["status"].configure(text=status_text, fg=status_color)
        if total == 0:
            summary = "No habits scheduled today."
        elif done == total:
            summary = f"All {total} habits complete. Perfect day secured."
        else:
            summary = f"{done} of {total} habits complete  ·  {total - done} to go"
        state["summary"].configure(text=summary)
        state["mark_all"].set_enabled(0 < total and done < total)
        self._draw_streak_chip()
        for task in tasks:
            row = self._dashboard_rows.get(task["id"])
            if row is not None:
                row.set_done(task["id"] in done_ids,
                             stats=self.dm.habit_stats(task, 30))

        # counters inside the hero chips are rebuilt on next view; refresh in place
        chips = state.get("streak_chip")
        if chips is not None:
            for child in list(chips.winfo_children()):
                child.destroy()
            for icon, text, color in (
                ("check", f"{done} done", self.c["success"]),
                ("target", f"{max(0, total - done)} remaining",
                 self.c["warning"] if total - done else self.c["text2"]),
                ("flame", f"{streak} day streak", self.c["primary_l"]),
            ):
                chip = tk.Frame(chips, bg=mix(color, self.c["card"], 0.86), padx=9, pady=4)
                chip.pack(side="left", padx=(0, 8))
                icon_canvas = tk.Canvas(chip, width=14, height=14, bg=chip.cget("bg"),
                                        highlightthickness=0, bd=0)
                icon_canvas.pack(side="left", padx=(0, 5))
                draw_icon(icon_canvas, icon, 7, 7, size=12, color=color, width=1.8)
                tk.Label(chip, text=text, bg=chip.cget("bg"), fg=color,
                         font=f(8, "bold")).pack(side="left")

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
                               "Its completion history for this habit will be removed too.",
                               parent=self.root):
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
        for task in pending:
            self.dm.toggle_task(task["id"], True)
        self.dm.award_perfect_day_if_due()
        self._show(self._active_view or "Dashboard")
        self.toast(f"{len(pending)} habit{'s' if len(pending) != 1 else ''} completed", "success")

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

    # -- clock --------------------------------------------------------
    def _tick_clock(self):
        now = datetime.now()
        text = now.strftime("%H:%M") + "  ·  " + now.strftime("%d %b")
        try:
            if hasattr(self, "lbl_clock") and self.lbl_clock.winfo_exists():
                self.lbl_clock.configure(text=text)
            self._clock_job = self.root.after(20000, self._tick_clock)
        except tk.TclError:
            pass

    def on_close(self):
        if self._clock_job:
            try:
                self.root.after_cancel(self._clock_job)
            except tk.TclError:
                pass
        try:
            self.dm.save()
        finally:
            self.root.destroy()
# ==================================================================
# ENTRY POINT# ==================================================================
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
