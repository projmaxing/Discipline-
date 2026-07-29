#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║           HabitFlow — Personal Offline Habit Tracker            ║
║      No accounts. No internet. No cloud. 100% yours.            ║
╠══════════════════════════════════════════════════════════════════╣
║  Requirements:  Python 3.8+  (tkinter is built-in)              ║
║  Optional:      pip install matplotlib  →  enhanced charts       ║
║                 pip install plyer       →  desktop notifications  ║
║                                                                  ║
║  Run:   python habitflow.py                                      ║
║  Data:  ~/.habitflow/data.json  (fully local)                    ║
╚══════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════
# IMPORTS
# ═══════════════════════════════════════════════════════════════════
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json, os, uuid, random, shutil, sys
from datetime import datetime, date, timedelta
import calendar as cal_module

# ── Optional: matplotlib for richer charts ──────────────────────────
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.patches as mpatches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ── Optional: plyer for native desktop notifications ────────────────
try:
    from plyer import notification as _plyer_notif
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

APP_NAME   = "HabitFlow"
VERSION    = "1.0.0"
DATA_DIR   = os.path.join(os.path.expanduser("~"), ".habitflow")
DATA_FILE  = os.path.join(DATA_DIR, "data.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# ── XP & levelling thresholds ──────────────────────────────────────
XP_PER_TASK    = 10
XP_PERFECT_DAY = 50
LEVELS = [0, 100, 250, 500, 1000, 2000, 4000, 8000, 16000, 32000, 99_999]
LEVEL_NAMES = [
    "Beginner", "Apprentice", "Practitioner", "Adept",
    "Expert", "Master", "Grandmaster", "Legend", "Mythic", "Ascended"
]

# ── Category → accent colour ───────────────────────────────────────
CATEGORIES = {
    "Health":   "#22c55e",
    "Study":    "#3b82f6",
    "Fitness":  "#f97316",
    "Personal": "#a855f7",
    "Work":     "#f59e0b",
    "Social":   "#ec4899",
    "Sleep":    "#6366f1",
    "Other":    "#64748b",
}
CAT_LIST = list(CATEGORIES.keys())

RECURRENCE_OPTIONS = ["Daily", "Weekdays", "Weekends", "Weekly", "Monthly", "Custom Days"]
WEEKDAY_NAMES      = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# ── Motivational quotes ─────────────────────────────────────────────
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

# ── Default starter tasks ───────────────────────────────────────────
DEFAULT_TASKS = [
    {"name": "Drink 4L of water",  "category": "Health",   "daily_target": "4L",    "notes": "Stay hydrated throughout the day"},
    {"name": "Revise notes",        "category": "Study",    "daily_target": "",      "notes": "Review today's study material"},
    {"name": "Gym / Workout",       "category": "Fitness",  "daily_target": "45min", "notes": ""},
    {"name": "Social interaction",  "category": "Social",   "daily_target": "",      "notes": "Connect meaningfully with someone"},
    {"name": "Learn something new", "category": "Study",    "daily_target": "",      "notes": "Read, watch, or explore"},
    {"name": "Sleep 7-8 hours",     "category": "Sleep",    "daily_target": "7-8h",  "notes": "Consistent sleep schedule"},
    {"name": "Deep work (2 hours)", "category": "Work",     "daily_target": "2h",    "notes": "No distractions, fully focused"},
    {"name": "Daily reflection",    "category": "Personal", "daily_target": "10min", "notes": "Journal or meditate before bed"},
]

# ═══════════════════════════════════════════════════════════════════
# COLOUR THEMES
# ═══════════════════════════════════════════════════════════════════
THEMES = {
    "dark": {
        "bg":          "#0d1117",
        "surface":     "#161b22",
        "surface2":    "#21262d",
        "surface3":    "#30363d",
        "border":      "#30363d",
        "primary":     "#7c3aed",
        "primary_l":   "#a78bfa",
        "primary_d":   "#5b21b6",
        "accent":      "#10b981",
        "danger":      "#ef4444",
        "warning":     "#f59e0b",
        "success":     "#22c55e",
        "text":        "#e6edf3",
        "text2":       "#8b949e",
        "text3":       "#484f58",
        "sidebar":     "#010409",
        "card":        "#161b22",
        "prog_bg":     "#21262d",
        "highlight":   "#1f2937",
    },
    "light": {
        "bg":          "#f0f4f8",
        "surface":     "#ffffff",
        "surface2":    "#f1f5f9",
        "surface3":    "#e2e8f0",
        "border":      "#cbd5e1",
        "primary":     "#7c3aed",
        "primary_l":   "#a78bfa",
        "primary_d":   "#5b21b6",
        "accent":      "#10b981",
        "danger":      "#ef4444",
        "warning":     "#f59e0b",
        "success":     "#22c55e",
        "text":        "#0f172a",
        "text2":       "#475569",
        "text3":       "#94a3b8",
        "sidebar":     "#1e293b",
        "card":        "#ffffff",
        "prog_bg":     "#e2e8f0",
        "highlight":   "#f8fafc",
    },
}


# ═══════════════════════════════════════════════════════════════════
# DATA MANAGER — all persistence and business logic
# ═══════════════════════════════════════════════════════════════════
class DataManager:
    """Handles all read/write operations and business-logic calculations."""

    def __init__(self):
        os.makedirs(DATA_DIR,   exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        self.data = self._load()

    # ── Persistence ─────────────────────────────────────────────────
    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass   # corrupted — start fresh
        return self._fresh_data()

    def _fresh_data(self):
        tasks = []
        for i, t in enumerate(DEFAULT_TASKS):
            tasks.append({
                "id":            str(uuid.uuid4()),
                "name":          t["name"],
                "category":      t["category"],
                "notes":         t.get("notes", ""),
                "daily_target":  t.get("daily_target", ""),
                "recurrence":    "Daily",
                "recurrence_days": [],
                "pinned":        False,
                "order":         i,
                "created_date":  date.today().isoformat(),
            })
        return {
            "tasks":       tasks,
            "completions": {},   # {"2024-01-15": ["task_id1", ...]}
            "settings": {
                "theme":                "dark",
                "xp":                   0,
                "level":                1,
                "notifications":        True,
                "created_date":         date.today().isoformat(),
                "daily_quote_date":     "",
                "daily_quote_idx":      0,
            }
        }

    def save(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    # ── Task CRUD ────────────────────────────────────────────────────
    def add_task(self, name, category="Other", notes="", daily_target="",
                 recurrence="Daily", recurrence_days=None, pinned=False):
        task = {
            "id":             str(uuid.uuid4()),
            "name":           name.strip(),
            "category":       category,
            "notes":          notes.strip(),
            "daily_target":   daily_target.strip(),
            "recurrence":     recurrence,
            "recurrence_days": recurrence_days or [],
            "pinned":         pinned,
            "order":          len(self.data["tasks"]),
            "created_date":   date.today().isoformat(),
        }
        self.data["tasks"].append(task)
        self.save()
        return task

    def update_task(self, task_id, **kwargs):
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                t.update(kwargs)
                break
        self.save()

    def delete_task(self, task_id):
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        # Also remove completions for this task
        for day in self.data["completions"]:
            self.data["completions"][day] = [
                tid for tid in self.data["completions"][day] if tid != task_id
            ]
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
        self.save()

    # ── Scheduling: is a task due on a given date? ──────────────────
    def is_scheduled(self, task, check_date: date) -> bool:
        rec = task.get("recurrence", "Daily")
        wd  = check_date.weekday()   # 0=Mon … 6=Sun
        if rec == "Daily":
            return True
        if rec == "Weekdays":
            return wd < 5
        if rec == "Weekends":
            return wd >= 5
        if rec == "Weekly":
            created = date.fromisoformat(task["created_date"])
            return wd == created.weekday()
        if rec == "Monthly":
            created = date.fromisoformat(task["created_date"])
            return check_date.day == created.day
        if rec == "Custom Days":
            return wd in task.get("recurrence_days", [])
        return True

    def get_scheduled_today(self):
        """Return tasks scheduled for today, pinned first."""
        today = date.today()
        tasks = [t for t in self.data["tasks"] if self.is_scheduled(t, today)]
        tasks.sort(key=lambda t: (not t.get("pinned", False), t.get("order", 0)))
        return tasks

    def get_scheduled_for(self, check_date: date):
        return [t for t in self.data["tasks"] if self.is_scheduled(t, check_date)]

    # ── Completion helpers ───────────────────────────────────────────
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

    # ── Streak calculation ───────────────────────────────────────────
    def calculate_streak(self) -> int:
        streak = 0
        check = date.today() - timedelta(days=1)  # start from yesterday
        for _ in range(366):
            if self.is_perfect_day(check):
                streak += 1
                check -= timedelta(days=1)
            else:
                break
        # Also count today if perfect so far and all tasks done
        if self.is_perfect_day(date.today()):
            streak += 1
        return streak

    # ── XP & levels ─────────────────────────────────────────────────
    def _add_xp(self, amount: int):
        s = self.data["settings"]
        s["xp"] = max(0, s["xp"] + amount)
        # Compute current level
        for i, threshold in enumerate(LEVELS):
            if s["xp"] < threshold:
                s["level"] = i  # i is the next level; actual = i-1+1 = i
                break
        else:
            s["level"] = len(LEVELS)

    def give_perfect_day_xp(self):
        self._add_xp(XP_PERFECT_DAY)
        self.save()

    def get_xp_info(self):
        """Return (xp, level, level_name, xp_in_level, xp_for_level)."""
        xp  = self.data["settings"]["xp"]

        # Calculate level: how many thresholds (from LEVELS[1:]) are <= xp, plus 1
        lvl = 1
        for threshold in LEVELS[1:]:  # Skip the first element (0)
            if xp >= threshold:
                lvl += 1
            else:
                break

        # Cap at maximum level defined in LEVEL_NAMES
        lvl = min(lvl, len(LEVEL_NAMES))

        # Calculate progress within current level
        prev_threshold = LEVELS[lvl - 1]
        next_threshold = LEVELS[lvl] if lvl < len(LEVELS) else LEVELS[-1]
        xp_in_level = xp - prev_threshold
        xp_for_level = next_threshold - prev_threshold

        return xp, lvl, LEVEL_NAMES[lvl - 1], xp_in_level, xp_for_level

    # ── Statistics ──────────────────────────────────────────────────
    def get_week_pcts(self):
        """Return list of 7 completion percentages (Mon→Sun this week)."""
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        return [round(self.completion_pct(monday + timedelta(days=i)) * 100)
                for i in range(7)]

    def get_month_pcts(self):
        """Return completion % per day for current month."""
        today   = date.today()
        n_days  = cal_module.monthrange(today.year, today.month)[1]
        base    = date(today.year, today.month, 1)
        return [round(self.completion_pct(base + timedelta(days=i)) * 100)
                for i in range(n_days)]

    def get_daily_quote(self):
        s    = self.data["settings"]
        today = date.today().isoformat()
        if s.get("daily_quote_date") != today:
            s["daily_quote_date"] = today
            s["daily_quote_idx"]  = random.randrange(len(QUOTES))
            self.save()
        return QUOTES[s["daily_quote_idx"]]

    # ── Backup / Export / Import ─────────────────────────────────────
    def backup(self):
        if not os.path.exists(DATA_FILE):
            return None
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(BACKUP_DIR, f"backup_{ts}.json")
        shutil.copy2(DATA_FILE, dest)
        return dest

    def export_json(self, path: str):
        shutil.copy2(DATA_FILE, path)

    def import_json(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            new_data = json.load(f)
        # Basic validation
        if "tasks" not in new_data or "completions" not in new_data:
            raise ValueError("Invalid HabitFlow data file.")
        self.backup()   # auto-backup before overwriting
        self.data = new_data
        self.save()


# ═══════════════════════════════════════════════════════════════════
# SCROLLABLE FRAME HELPER
# ═══════════════════════════════════════════════════════════════════
class ScrollableFrame(tk.Frame):
    """A Frame that scrolls vertically with mousewheel support."""

    def __init__(self, parent, bg, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self._sb     = tk.Scrollbar(self, orient="vertical",
                                    command=self._canvas.yview)
        self.inner   = tk.Frame(self._canvas, bg=bg)
        self._win    = self._canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self._canvas.configure(yscrollcommand=self._sb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        self._sb.pack(side="right",  fill="y")

        self.inner.bind("<Configure>", self._on_inner)
        self._canvas.bind("<Configure>", self._on_canvas)
        self._canvas.bind("<Enter>", self._bind_wheel)
        self._canvas.bind("<Leave>", self._unbind_wheel)

    def _on_inner(self, _):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas(self, e):
        self._canvas.itemconfig(self._win, width=e.width)

    def _bind_wheel(self, _):
        self._canvas.bind_all("<MouseWheel>", self._on_wheel)
        self._canvas.bind_all("<Button-4>",   self._on_wheel_up)
        self._canvas.bind_all("<Button-5>",   self._on_wheel_dn)

    def _unbind_wheel(self, _):
        self._canvas.unbind_all("<MouseWheel>")
        self._canvas.unbind_all("<Button-4>")
        self._canvas.unbind_all("<Button-5>")

    def _on_wheel(self, e):
        self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _on_wheel_up(self, _):
        self._canvas.yview_scroll(-1, "units")

    def _on_wheel_dn(self, _):
        self._canvas.yview_scroll(1, "units")

    def scroll_to_top(self):
        self._canvas.yview_moveto(0)


# ═══════════════════════════════════════════════════════════════════
# TOAST NOTIFICATION (cross-platform in-app)
# ═══════════════════════════════════════════════════════════════════
def show_toast(root, message, duration=3000, color="#7c3aed"):
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)
    toast.configure(bg=color)

    w, h = 320, 64
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    x, y   = sw - w - 24, sh - h - 56
    toast.geometry(f"{w}x{h}+{x}+{y}")

    tk.Label(toast, text=message, bg=color, fg="white",
             font=("Segoe UI", 11), wraplength=290,
             padx=16, pady=12).pack(fill="both", expand=True)
    toast.after(duration, toast.destroy)


# ═══════════════════════════════════════════════════════════════════
# UTILITY WIDGETS
# ═══════════════════════════════════════════════════════════════════
def make_card(parent, bg, border_color, padx=16, pady=12):
    """Return a frame styled as a card."""
    outer = tk.Frame(parent, bg=border_color, padx=1, pady=1)
    inner = tk.Frame(outer, bg=bg, padx=padx, pady=pady)
    inner.pack(fill="both", expand=True)
    return outer, inner


def draw_progress_bar(canvas, pct, fg, bg, height=14, radius=7):
    """Draw a rounded progress bar on a Canvas widget."""
    canvas.delete("all")
    w = canvas.winfo_width() or 400
    if w < 10:
        return
    # Background track
    canvas.create_rounded_rect = _rr.__get__(canvas, tk.Canvas)
    _draw_rr(canvas, 0, 0, w, height, radius, fill=bg, outline="")
    # Foreground fill
    fill_w = max(0, min(int(w * pct), w))
    if fill_w > radius * 2:
        _draw_rr(canvas, 0, 0, fill_w, height, radius, fill=fg, outline="")
    elif fill_w > 0:
        canvas.create_rectangle(0, 0, fill_w, height, fill=fg, outline="")


def _draw_rr(canvas, x1, y1, x2, y2, r, **kw):
    points = [
        x1+r, y1, x2-r, y1,
        x2, y1, x2, y1+r,
        x2, y2-r, x2, y2,
        x2-r, y2, x1+r, y2,
        x1, y2, x1, y2-r,
        x1, y1+r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kw)


def _rr(self, *a, **kw):  # unused stub to avoid name error
    pass


# ═══════════════════════════════════════════════════════════════════
# TASK DIALOG — add or edit a task
# ═══════════════════════════════════════════════════════════════════
class TaskDialog(tk.Toplevel):
    """Modal dialog to create or edit a task."""

    def __init__(self, parent, theme, task=None):
        super().__init__(parent)
        self.c       = theme
        self.result  = None
        self.task    = task
        is_edit      = task is not None

        self.title("Edit Task" if is_edit else "New Task")
        self.configure(bg=self.c["surface"])
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)

        w, h = 520, 560
        self.geometry(f"{w}x{h}+{parent.winfo_rootx()+60}+{parent.winfo_rooty()+60}")

        self._build(is_edit)
        if is_edit:
            self._populate()

        self.bind("<Return>", lambda _: self._save())
        self.bind("<Escape>", lambda _: self.destroy())
        self.wait_window()

    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=self.c["surface"], fg=self.c["text2"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(12, 2))

    def _entry(self, parent, textvariable=None, show=None):
        e = tk.Entry(parent, textvariable=textvariable,
                     bg=self.c["surface2"], fg=self.c["text"],
                     insertbackground=self.c["text"],
                     relief="flat", font=("Segoe UI", 11),
                     highlightthickness=1, highlightcolor=self.c["primary"],
                     highlightbackground=self.c["border"])
        e.pack(fill="x", ipady=6)
        return e

    def _build(self, is_edit):
        pad = tk.Frame(self, bg=self.c["surface"], padx=24, pady=20)
        pad.pack(fill="both", expand=True)

        # Title
        tk.Label(pad, text="Edit Task" if is_edit else "Add New Task",
                 bg=self.c["surface"], fg=self.c["text"],
                 font=("Segoe UI", 14, "bold")).pack(anchor="w")

        # Name
        self._label(pad, "Task Name *")
        self.v_name = tk.StringVar()
        self._entry(pad, self.v_name)

        # Category
        self._label(pad, "Category")
        self.v_cat = tk.StringVar(value="Other")
        cat_row = tk.Frame(pad, bg=self.c["surface"])
        cat_row.pack(fill="x")
        for cat, col in CATEGORIES.items():
            btn = tk.Label(cat_row, text=cat, bg=self.c["surface2"],
                           fg=self.c["text2"], font=("Segoe UI", 8),
                           padx=8, pady=4, cursor="hand2")
            btn.pack(side="left", padx=(0, 4), pady=2)
            btn.bind("<Button-1>", lambda e, c=cat, b=btn: self._sel_cat(c, b))
            btn._cat = cat
        self._cat_buttons = cat_row.winfo_children()
        self._cur_cat_btn = None

        # Daily target & notes in 2-column grid
        row2 = tk.Frame(pad, bg=self.c["surface"])
        row2.pack(fill="x")
        col1 = tk.Frame(row2, bg=self.c["surface"])
        col1.pack(side="left", fill="x", expand=True, padx=(0, 8))
        col2 = tk.Frame(row2, bg=self.c["surface"])
        col2.pack(side="left", fill="x", expand=True)

        tk.Label(col1, text="Daily Target", bg=self.c["surface"], fg=self.c["text2"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(12, 2))
        self.v_target = tk.StringVar()
        self._entry(col1, self.v_target)

        tk.Label(col2, text="Recurrence", bg=self.c["surface"], fg=self.c["text2"],
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(12, 2))
        self.v_rec = tk.StringVar(value="Daily")
        rec_cb = ttk.Combobox(col2, textvariable=self.v_rec,
                              values=RECURRENCE_OPTIONS, state="readonly",
                              font=("Segoe UI", 10))
        rec_cb.pack(fill="x", ipady=4)
        rec_cb.bind("<<ComboboxSelected>>", self._on_rec_change)

        # Custom days row (shown only for Custom Days)
        self.custom_row = tk.Frame(pad, bg=self.c["surface"])
        self.custom_row.pack(fill="x")
        self.day_vars = []
        for i, d in enumerate(WEEKDAY_NAMES):
            v = tk.BooleanVar()
            self.day_vars.append(v)
            tk.Checkbutton(self.custom_row, text=d, variable=v,
                           bg=self.c["surface"], fg=self.c["text"],
                           selectcolor=self.c["primary"],
                           activebackground=self.c["surface"],
                           font=("Segoe UI", 9)).pack(side="left", padx=2)
        self.custom_row.pack_forget()

        # Notes
        self._label(pad, "Notes (optional)")
        self.t_notes = tk.Text(pad, height=3, bg=self.c["surface2"],
                               fg=self.c["text"], font=("Segoe UI", 10),
                               relief="flat", insertbackground=self.c["text"],
                               highlightthickness=1, highlightcolor=self.c["primary"],
                               highlightbackground=self.c["border"])
        self.t_notes.pack(fill="x")

        # Pin
        self.v_pin = tk.BooleanVar()
        tk.Checkbutton(pad, text="📌  Pin to top", variable=self.v_pin,
                       bg=self.c["surface"], fg=self.c["text"],
                       selectcolor=self.c["primary"],
                       activebackground=self.c["surface"],
                       font=("Segoe UI", 10)).pack(anchor="w", pady=(10, 0))

        # Buttons
        btn_row = tk.Frame(pad, bg=self.c["surface"])
        btn_row.pack(fill="x", pady=(20, 0))
        tk.Button(btn_row, text="Cancel", command=self.destroy,
                  bg=self.c["surface3"], fg=self.c["text"],
                  relief="flat", font=("Segoe UI", 10),
                  padx=16, pady=6, cursor="hand2").pack(side="left")
        tk.Button(btn_row, text="Save Task", command=self._save,
                  bg=self.c["primary"], fg="white",
                  relief="flat", font=("Segoe UI", 10, "bold"),
                  padx=16, pady=6, cursor="hand2").pack(side="right")

    def _sel_cat(self, cat, btn):
        self.v_cat.set(cat)
        for b in self._cat_buttons:
            b.configure(bg=self.c["surface2"], fg=self.c["text2"])
        col = CATEGORIES.get(cat, self.c["primary"])
        btn.configure(bg=col, fg="white")

    def _on_rec_change(self, _=None):
        if self.v_rec.get() == "Custom Days":
            self.custom_row.pack(fill="x", after=self.custom_row.master.winfo_children()[-3])
        else:
            self.custom_row.pack_forget()

    def _populate(self):
        t = self.task
        self.v_name.set(t.get("name", ""))
        self.v_cat.set(t.get("category", "Other"))
        self.v_target.set(t.get("daily_target", ""))
        self.v_rec.set(t.get("recurrence", "Daily"))
        self.v_pin.set(t.get("pinned", False))
        self.t_notes.insert("1.0", t.get("notes", ""))
        # Highlight selected category
        for b in self._cat_buttons:
            if b._cat == t.get("category"):
                col = CATEGORIES.get(b._cat, self.c["primary"])
                b.configure(bg=col, fg="white")
        # Custom days
        for i, v in enumerate(self.day_vars):
            v.set(i in t.get("recurrence_days", []))
        self._on_rec_change()

    def _save(self):
        name = self.v_name.get().strip()
        if not name:
            messagebox.showwarning("Required", "Task name cannot be empty.", parent=self)
            return
        rec_days = [i for i, v in enumerate(self.day_vars) if v.get()] \
            if self.v_rec.get() == "Custom Days" else []
        self.result = {
            "name":             name,
            "category":         self.v_cat.get(),
            "daily_target":     self.v_target.get().strip(),
            "notes":            self.t_notes.get("1.0", "end-1c").strip(),
            "recurrence":       self.v_rec.get(),
            "recurrence_days":  rec_days,
            "pinned":           self.v_pin.get(),
        }
        self.destroy()


# ═══════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════
class HabitFlowApp:
    """Main application window."""

    NAV_ITEMS = [
        ("🏠", "Dashboard"),
        ("✅", "Tasks"),
        ("📊", "Statistics"),
        ("📅", "Calendar"),
        ("⚙", "Settings"),
    ]

    def __init__(self, root: tk.Tk):
        self.root  = root
        self.dm    = DataManager()
        theme_name = self.dm.data["settings"].get("theme", "dark")
        self.c     = THEMES[theme_name]
        self._theme_name = theme_name

        self._active_view  = None
        self._clock_job    = None
        self._perfect_awarded_today = False
        self._search_var   = tk.StringVar()
        self._filter_cat   = tk.StringVar(value="All")

        self._setup_window()
        self._build_layout()
        self._show("Dashboard")
        self._tick_clock()

    # ── Window setup ─────────────────────────────────────────────────
    def _setup_window(self):
        self.root.title(f"{APP_NAME}  v{VERSION}")
        self.root.configure(bg=self.c["bg"])
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)

        # Keyboard shortcuts
        self.root.bind("<Control-d>", self._shortcut_mark_all)
        self.root.bind("<Control-n>", lambda _: self._open_add_task())
        self.root.bind("<F5>",        lambda _: self._refresh())

    # ── Layout skeleton ──────────────────────────────────────────────
    def _build_layout(self):
        # ── Sidebar ──────────────────────────────────────────────────
        self.sidebar = tk.Frame(self.root, bg=self.c["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # App logo
        tk.Label(self.sidebar, text=f"🌊  {APP_NAME}",
                 bg=self.c["sidebar"], fg=self.c["primary_l"],
                 font=("Segoe UI", 15, "bold"),
                 padx=20, pady=22).pack(anchor="w")

        tk.Frame(self.sidebar, bg=self.c["border"], height=1).pack(fill="x", padx=16)

        # Nav buttons
        self._nav_btns = {}
        for icon, label in self.NAV_ITEMS:
            btn = tk.Label(self.sidebar,
                           text=f"  {icon}  {label}",
                           bg=self.c["sidebar"], fg=self.c["text2"],
                           font=("Segoe UI", 11),
                           anchor="w", padx=12, pady=10, cursor="hand2")
            btn.pack(fill="x", padx=8, pady=2)
            btn.bind("<Button-1>", lambda _, v=label: self._show(v))
            btn.bind("<Enter>",    lambda e, b=btn: b.configure(bg=self.c["highlight"]))
            btn.bind("<Leave>",    lambda e, b=btn: self._nav_leave(b))
            self._nav_btns[label] = btn

        # Version at bottom
        tk.Label(self.sidebar, text=f"v{VERSION}",
                 bg=self.c["sidebar"], fg=self.c["text3"],
                 font=("Segoe UI", 8)).place(relx=0.5, rely=0.97, anchor="s")

        # ── Main area ─────────────────────────────────────────────────
        self.main = tk.Frame(self.root, bg=self.c["bg"])
        self.main.pack(side="left", fill="both", expand=True)

        # Top bar
        self._build_topbar()

        # Content frame (views are stacked here)
        self.content = tk.Frame(self.main, bg=self.c["bg"])
        self.content.pack(fill="both", expand=True)

    def _build_topbar(self):
        bar = tk.Frame(self.main, bg=self.c["surface"], height=52)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Clock
        self.lbl_clock = tk.Label(bar, text="", bg=self.c["surface"], fg=self.c["text2"],
                                  font=("Segoe UI", 10))
        self.lbl_clock.pack(side="right", padx=20)

        # Search
        srch = tk.Frame(bar, bg=self.c["surface2"], padx=6, pady=4)
        srch.pack(side="right", padx=(0, 12), pady=10)
        tk.Label(srch, text="🔍", bg=self.c["surface2"], fg=self.c["text2"]).pack(side="left")
        tk.Entry(srch, textvariable=self._search_var, bg=self.c["surface2"],
                 fg=self.c["text"], insertbackground=self.c["text"],
                 relief="flat", font=("Segoe UI", 10), width=18).pack(side="left")

        # Theme toggle
        self.btn_theme = tk.Label(bar, text="☀" if self._theme_name == "dark" else "🌙",
                                  bg=self.c["surface"], fg=self.c["text2"],
                                  font=("Segoe UI", 14), cursor="hand2", padx=10)
        self.btn_theme.pack(side="right")
        self.btn_theme.bind("<Button-1>", lambda _: self._toggle_theme())

        # Page title
        self.lbl_page = tk.Label(bar, text="Dashboard",
                                 bg=self.c["surface"], fg=self.c["text"],
                                 font=("Segoe UI", 14, "bold"), padx=20)
        self.lbl_page.pack(side="left")

    # ── Navigation ───────────────────────────────────────────────────
    def _nav_leave(self, btn):
        if btn.cget("text").strip().endswith(self._active_view):
            return
        btn.configure(bg=self.c["sidebar"])

    def _show(self, view_name: str):
        # Clear content area
        for w in self.content.winfo_children():
            w.destroy()

        self._active_view = view_name
        self.lbl_page.configure(text=view_name)

        # Highlight active nav
        for name, btn in self._nav_btns.items():
            if name == view_name:
                btn.configure(bg=self.c["primary_d"], fg="white")
            else:
                btn.configure(bg=self.c["sidebar"], fg=self.c["text2"])

        # Route to builder
        {
            "Dashboard":  self._view_dashboard,
            "Tasks":      self._view_tasks,
            "Statistics": self._view_stats,
            "Calendar":   self._view_calendar,
            "Settings":   self._view_settings,
        }[view_name]()

    def _refresh(self):
        self._show(self._active_view)

    # ─────────────────────────────────────────────────────────────────
    # VIEW — DASHBOARD
    # ─────────────────────────────────────────────────────────────────
    def _view_dashboard(self):
        frame = ScrollableFrame(self.content, self.c["bg"])
        frame.pack(fill="both", expand=True)
        p = frame.inner

        pad = 20

        # ── Greeting + date ──────────────────────────────────────────
        now    = datetime.now()
        hour   = now.hour
        greet  = ("Good Morning ☀️" if hour < 12 else
                  "Good Afternoon 🌤" if hour < 17 else "Good Evening 🌙")
        today  = date.today()
        date_s = today.strftime("%A, %B %d %Y")

        top = tk.Frame(p, bg=self.c["bg"])
        top.pack(fill="x", padx=pad, pady=(20, 8))
        tk.Label(top, text=greet, bg=self.c["bg"], fg=self.c["text"],
                 font=("Segoe UI", 22, "bold")).pack(anchor="w")
        tk.Label(top, text=date_s, bg=self.c["bg"], fg=self.c["text2"],
                 font=("Segoe UI", 11)).pack(anchor="w")

        # ── Progress section ─────────────────────────────────────────
        tasks     = self.dm.get_scheduled_today()
        done_ids  = self.dm.get_completed_today()
        n_total   = len(tasks)
        n_done    = sum(1 for t in tasks if t["id"] in done_ids)
        n_left    = n_total - n_done
        pct       = n_done / n_total if n_total else 0

        prog_card_o, prog_card = make_card(p, self.c["card"], self.c["border"])
        prog_card_o.pack(fill="x", padx=pad, pady=(4, 8))

        tk.Label(prog_card, text="Today's Progress",
                 bg=self.c["card"], fg=self.c["text2"],
                 font=("Segoe UI", 10)).pack(anchor="w")

        pct_row = tk.Frame(prog_card, bg=self.c["card"])
        pct_row.pack(fill="x", pady=(4, 6))
        tk.Label(pct_row, text=f"{int(pct*100)}%",
                 bg=self.c["card"], fg=self.c["text"],
                 font=("Segoe UI", 28, "bold")).pack(side="left")
        tk.Label(pct_row, text=f"  of tasks complete",
                 bg=self.c["card"], fg=self.c["text2"],
                 font=("Segoe UI", 11)).pack(side="left", pady=8)

        prog_canvas = tk.Canvas(prog_card, height=14, bg=self.c["card"],
                                highlightthickness=0)
        prog_canvas.pack(fill="x", pady=(0, 8))
        prog_canvas.bind("<Configure>",
                         lambda _: _draw_rr_bar(prog_canvas, pct,
                                                self.c["primary"], self.c["prog_bg"]))

        def _draw_rr_bar(cv, p2, fg, bg, h=14, r=7):
            cv.delete("all")
            w = cv.winfo_width() or 600
            _draw_rr(cv, 0, 0, w, h, r, fill=bg, outline="")
            fw = max(0, min(int(w * p2), w))
            if fw > r*2:
                _draw_rr(cv, 0, 0, fw, h, r, fill=fg, outline="")
            elif fw > 0:
                cv.create_rectangle(0, 0, fw, h, fill=fg, outline="")

        prog_canvas.after(50, lambda: _draw_rr_bar(prog_canvas, pct,
                                                    self.c["primary"], self.c["prog_bg"]))

        # ── Stats cards row ───────────────────────────────────────────
        streak = self.dm.calculate_streak()

        stats_row = tk.Frame(p, bg=self.c["bg"])
        stats_row.pack(fill="x", padx=pad, pady=(0, 8))
        for label, value, color in [
            ("Total Tasks",      n_total, self.c["text2"]),
            ("Completed",        n_done,  self.c["success"]),
            ("Remaining",        n_left,  self.c["warning"]),
            ("🔥 Streak (days)", streak,  self.c["primary_l"]),
        ]:
            co, ci = make_card(stats_row, self.c["card"], self.c["border"], 14, 14)
            co.pack(side="left", fill="x", expand=True, padx=(0, 8))
            tk.Label(ci, text=str(value), bg=self.c["card"], fg=color,
                     font=("Segoe UI", 24, "bold")).pack(anchor="center")
            tk.Label(ci, text=label, bg=self.c["card"], fg=self.c["text2"],
                     font=("Segoe UI", 9)).pack(anchor="center")

        # ── XP bar ───────────────────────────────────────────────────
        xp, lvl, lvl_name, xp_in, xp_for = self.dm.get_xp_info()
        xp_o, xp_i = make_card(p, self.c["card"], self.c["border"])
        xp_o.pack(fill="x", padx=pad, pady=(0, 8))

        xp_top = tk.Frame(xp_i, bg=self.c["card"])
        xp_top.pack(fill="x")
        tk.Label(xp_top, text=f"⚡ Level {lvl} — {lvl_name}",
                 bg=self.c["card"], fg=self.c["primary_l"],
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(xp_top, text=f"{xp:,} XP",
                 bg=self.c["card"], fg=self.c["text2"],
                 font=("Segoe UI", 10)).pack(side="right")

        xp_cv = tk.Canvas(xp_i, height=10, bg=self.c["card"], highlightthickness=0)
        xp_cv.pack(fill="x", pady=(6, 2))
        xp_pct = xp_in / xp_for if xp_for else 1

        def _draw_xp(_=None):
            xp_cv.delete("all")
            w = xp_cv.winfo_width() or 600
            _draw_rr(xp_cv, 0, 0, w, 10, 5, fill=self.c["prog_bg"], outline="")
            fw = max(0, min(int(w * xp_pct), w))
            if fw > 10:
                _draw_rr(xp_cv, 0, 0, fw, 10, 5, fill="#f59e0b", outline="")
        xp_cv.bind("<Configure>", _draw_xp)
        xp_cv.after(80, _draw_xp)

        tk.Label(xp_i, text=f"{xp_in:,} / {xp_for:,} XP to next level",
                 bg=self.c["card"], fg=self.c["text3"],
                 font=("Segoe UI", 8)).pack(anchor="e")

        # ── Perfect day badge ─────────────────────────────────────────
        if pct >= 1.0:
            badge_o, badge_i = make_card(p, "#1c1030", self.c["primary"])
            badge_o.pack(fill="x", padx=pad, pady=(0, 8))
            tk.Label(badge_i, text="🏆  Perfect Day!  All tasks complete. Amazing work!",
                     bg="#1c1030", fg=self.c["primary_l"],
                     font=("Segoe UI", 12, "bold")).pack()
            # Award XP once per day
            if not self._perfect_awarded_today:
                self._perfect_awarded_today = True
                self.dm.give_perfect_day_xp()
                show_toast(self.root, "🏆 Perfect Day! +50 XP bonus!", color="#7c3aed")

        # ── Today's task snapshot (top 4) ─────────────────────────────
        snap_o, snap_i = make_card(p, self.c["card"], self.c["border"])
        snap_o.pack(fill="x", padx=pad, pady=(0, 8))
        hdr = tk.Frame(snap_i, bg=self.c["card"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="Today's Tasks", bg=self.c["card"], fg=self.c["text"],
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        tk.Label(hdr, text="→ View all", bg=self.c["card"], fg=self.c["primary_l"],
                 font=("Segoe UI", 9), cursor="hand2").pack(side="right")
        hdr.winfo_children()[-1].bind("<Button-1>", lambda _: self._show("Tasks"))

        for t in tasks[:5]:
            done = t["id"] in done_ids
            row  = tk.Frame(snap_i, bg=self.c["card"])
            row.pack(fill="x", pady=3)
            col  = CATEGORIES.get(t["category"], "#64748b")
            tk.Label(row, text="✓" if done else "○",
                     bg=self.c["card"], fg=self.c["success"] if done else self.c["text3"],
                     font=("Segoe UI", 12)).pack(side="left", padx=(0, 8))
            tk.Label(row, text=t["name"],
                     bg=self.c["card"],
                     fg=self.c["text3"] if done else self.c["text"],
                     font=("Segoe UI", 10,
                           "overstrike" if done else "normal")).pack(side="left")
            if t.get("category"):
                tk.Label(row, text=f" {t['category']}",
                         bg=col, fg="white",
                         font=("Segoe UI", 7), padx=4, pady=1).pack(side="right")

        # ── Motivational quote ────────────────────────────────────────
        quote, author = self.dm.get_daily_quote()
        q_o, q_i = make_card(p, self.c["surface2"], self.c["border"])
        q_o.pack(fill="x", padx=pad, pady=(0, 24))
        tk.Label(q_i, text=f'"{quote}"',
                 bg=self.c["surface2"], fg=self.c["text"],
                 font=("Segoe UI", 11, "italic"),
                 wraplength=680, justify="left").pack(anchor="w")
        tk.Label(q_i, text=f"— {author}",
                 bg=self.c["surface2"], fg=self.c["text2"],
                 font=("Segoe UI", 9)).pack(anchor="e", pady=(4, 0))

    # ─────────────────────────────────────────────────────────────────
    # VIEW — TASKS
    # ─────────────────────────────────────────────────────────────────
    def _view_tasks(self):
        # Top controls
        ctrl = tk.Frame(self.content, bg=self.c["bg"])
        ctrl.pack(fill="x", padx=20, pady=(16, 8))

        # Category filter pills
        filter_frame = tk.Frame(ctrl, bg=self.c["bg"])
        filter_frame.pack(side="left")

        self._filter_btns = {}
        for cat in ["All"] + CAT_LIST:
            col = CATEGORIES.get(cat, self.c["surface2"])
            btn = tk.Label(filter_frame, text=cat,
                           bg=self.c["surface2"] if cat != "All" else self.c["primary"],
                           fg=self.c["text"] if cat != "All" else "white",
                           font=("Segoe UI", 9), padx=10, pady=4, cursor="hand2")
            btn.pack(side="left", padx=(0, 4))
            btn.bind("<Button-1>", lambda _, c=cat: self._set_cat_filter(c))
            self._filter_btns[cat] = btn

        # Buttons
        btn_row = tk.Frame(ctrl, bg=self.c["bg"])
        btn_row.pack(side="right")
        tk.Button(btn_row, text="Ctrl+D  Mark all done",
                  bg=self.c["surface2"], fg=self.c["text"],
                  relief="flat", font=("Segoe UI", 9),
                  padx=10, pady=4, cursor="hand2",
                  command=self._shortcut_mark_all).pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="＋  Add Task",
                  bg=self.c["primary"], fg="white",
                  relief="flat", font=("Segoe UI", 10, "bold"),
                  padx=12, pady=4, cursor="hand2",
                  command=self._open_add_task).pack(side="left")

        # Search
        srch_frame = tk.Frame(self.content, bg=self.c["bg"])
        srch_frame.pack(fill="x", padx=20, pady=(0, 8))
        self._search_var.trace_add("write", lambda *_: self._render_task_list())

        # Scrollable task list
        self._task_scroll = ScrollableFrame(self.content, self.c["bg"])
        self._task_scroll.pack(fill="both", expand=True, padx=20)
        self._render_task_list()

    def _set_cat_filter(self, cat):
        self._filter_cat.set(cat)
        for name, btn in self._filter_btns.items():
            if name == cat:
                btn.configure(bg=CATEGORIES.get(cat, self.c["primary"]) if cat != "All"
                              else self.c["primary"], fg="white")
            else:
                btn.configure(bg=self.c["surface2"], fg=self.c["text"])
        self._render_task_list()

    def _render_task_list(self):
        if not hasattr(self, "_task_scroll"):
            return
        inner = self._task_scroll.inner
        for w in inner.winfo_children():
            w.destroy()

        tasks    = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        query    = self._search_var.get().lower()
        cat_f    = self._filter_cat.get()

        if query:
            tasks = [t for t in tasks if query in t["name"].lower()
                     or query in t.get("notes", "").lower()]
        if cat_f != "All":
            tasks = [t for t in tasks if t.get("category") == cat_f]

        # Pinned section
        pinned   = [t for t in tasks if t.get("pinned")]
        unpinned = [t for t in tasks if not t.get("pinned")]

        if pinned:
            tk.Label(inner, text="📌  Pinned", bg=self.c["bg"], fg=self.c["text2"],
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 2))
            for t in pinned:
                self._task_row(inner, t, done_ids)
            tk.Frame(inner, bg=self.c["border"], height=1).pack(fill="x", pady=6)

        if unpinned:
            tk.Label(inner, text="Tasks", bg=self.c["bg"], fg=self.c["text2"],
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(4, 2))
            for t in unpinned:
                self._task_row(inner, t, done_ids)

        if not tasks:
            tk.Label(inner, text="No tasks match your search / filter.",
                     bg=self.c["bg"], fg=self.c["text3"],
                     font=("Segoe UI", 11)).pack(pady=40)

        # Spacer
        tk.Frame(inner, bg=self.c["bg"], height=32).pack()

    def _task_row(self, parent, task, done_ids):
        tid  = task["id"]
        done = tid in done_ids
        cat  = task.get("category", "Other")
        col  = CATEGORIES.get(cat, "#64748b")

        card_o = tk.Frame(parent, bg=self.c["border"], pady=1, padx=1)
        card_o.pack(fill="x", pady=3)
        card_i = tk.Frame(card_o, bg=self.c["card"], padx=12, pady=10)
        card_i.pack(fill="both")

        # Left: category stripe
        stripe = tk.Frame(card_i, bg=col, width=4)
        stripe.pack(side="left", fill="y", padx=(0, 12))

        # Checkbox canvas
        cb_size = 22
        cb = tk.Canvas(card_i, width=cb_size, height=cb_size,
                       bg=self.c["card"], highlightthickness=0, cursor="hand2")
        cb.pack(side="left", padx=(0, 10))
        self._draw_checkbox(cb, done, col)
        cb.bind("<Button-1>", lambda _, t=task, c=cb: self._toggle_task(t, c))

        # Middle: name + meta
        mid = tk.Frame(card_i, bg=self.c["card"])
        mid.pack(side="left", fill="both", expand=True)

        name_row = tk.Frame(mid, bg=self.c["card"])
        name_row.pack(fill="x")
        name_lbl = tk.Label(name_row, text=task["name"],
                            bg=self.c["card"],
                            fg=self.c["text3"] if done else self.c["text"],
                            font=("Segoe UI", 11,
                                  "overstrike" if done else "normal"))
        name_lbl.pack(side="left")
        if task.get("pinned"):
            tk.Label(name_row, text="📌", bg=self.c["card"],
                     font=("Segoe UI", 9)).pack(side="left", padx=4)

        meta_row = tk.Frame(mid, bg=self.c["card"])
        meta_row.pack(fill="x", pady=(2, 0))

        # Category badge
        tk.Label(meta_row, text=cat, bg=col, fg="white",
                 font=("Segoe UI", 7), padx=5, pady=1).pack(side="left", padx=(0, 6))

        if task.get("daily_target"):
            tk.Label(meta_row, text=f"🎯 {task['daily_target']}",
                     bg=self.c["card"], fg=self.c["text2"],
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 6))
        if task.get("recurrence") and task["recurrence"] != "Daily":
            tk.Label(meta_row, text=f"🔁 {task['recurrence']}",
                     bg=self.c["card"], fg=self.c["text2"],
                     font=("Segoe UI", 8)).pack(side="left", padx=(0, 6))
        if task.get("notes"):
            tk.Label(meta_row, text=f"📝 {task['notes'][:50]}{'…' if len(task['notes'])>50 else ''}",
                     bg=self.c["card"], fg=self.c["text3"],
                     font=("Segoe UI", 8)).pack(side="left")

        # Right: actions
        act = tk.Frame(card_i, bg=self.c["card"])
        act.pack(side="right")

        tk.Button(act, text="✏", bg=self.c["card"], fg=self.c["text2"],
                  relief="flat", font=("Segoe UI", 12), cursor="hand2",
                  command=lambda t=task: self._open_edit_task(t)).pack(side="left")
        tk.Button(act, text="🗑", bg=self.c["card"], fg=self.c["danger"],
                  relief="flat", font=("Segoe UI", 12), cursor="hand2",
                  command=lambda t=task: self._delete_task(t)).pack(side="left")

        # Space key on row
        card_i.bind("<space>", lambda _, t=task, c=cb: self._toggle_task(t, c))
        card_i.bind("<Button-1>", lambda _: card_i.focus_set())

    def _draw_checkbox(self, canvas, checked, color):
        canvas.delete("all")
        size = 22
        if checked:
            _draw_rr(canvas, 2, 2, size-2, size-2, 5, fill=color, outline="")
            canvas.create_text(size//2, size//2, text="✓", fill="white",
                               font=("Segoe UI", 11, "bold"))
        else:
            _draw_rr(canvas, 2, 2, size-2, size-2, 5,
                     fill=self.c["surface2"], outline=self.c["border"])

    def _toggle_task(self, task, cb_canvas):
        done_ids = self.dm.get_completed_today()
        is_done  = task["id"] in done_ids
        self.dm.toggle_task(task["id"], not is_done)

        # Redraw checkbox
        col = CATEGORIES.get(task.get("category"), self.c["primary"])
        self._draw_checkbox(cb_canvas, not is_done, col)

        # Check perfect day
        tasks = self.dm.get_scheduled_today()
        new_done = self.dm.get_completed_today()
        if len(new_done) == len(tasks) and not self._perfect_awarded_today:
            self._perfect_awarded_today = True
            self.dm.give_perfect_day_xp()
            show_toast(self.root, "🏆 Perfect Day! +50 XP bonus!", color="#7c3aed")

        # Re-render task list to update strikethrough
        self._render_task_list()

    def _open_add_task(self, _=None):
        dlg = TaskDialog(self.root, self.c)
        if dlg.result:
            self.dm.add_task(**dlg.result)
            if self._active_view == "Tasks":
                self._render_task_list()
            show_toast(self.root, f"✅ Task added: {dlg.result['name']}", color="#10b981")

    def _open_edit_task(self, task):
        dlg = TaskDialog(self.root, self.c, task=task)
        if dlg.result:
            self.dm.update_task(task["id"], **dlg.result)
            self._render_task_list()
            show_toast(self.root, "✏ Task updated.", color="#3b82f6")

    def _delete_task(self, task):
        if messagebox.askyesno("Delete Task",
                               f'Delete "{task["name"]}"?\nThis cannot be undone.',
                               parent=self.root):
            self.dm.delete_task(task["id"])
            self._render_task_list()

    def _shortcut_mark_all(self, _=None):
        tasks    = self.dm.get_scheduled_today()
        done_ids = self.dm.get_completed_today()
        for t in tasks:
            if t["id"] not in done_ids:
                self.dm.toggle_task(t["id"], True)
        if self._active_view == "Tasks":
            self._render_task_list()
        elif self._active_view == "Dashboard":
            self._show("Dashboard")
        show_toast(self.root, "✅ All tasks marked complete!", color="#10b981")

    # ─────────────────────────────────────────────────────────────────
    # VIEW — STATISTICS
    # ─────────────────────────────────────────────────────────────────
    def _view_stats(self):
        frame = ScrollableFrame(self.content, self.c["bg"])
        frame.pack(fill="both", expand=True)
        p = frame.inner

        pad = 20
        tk.Label(p, text="Your Statistics", bg=self.c["bg"], fg=self.c["text"],
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=pad, pady=(20, 4))

        # ── Weekly bar chart ─────────────────────────────────────────
        week_pcts = self.dm.get_week_pcts()
        wday_lbls = [cal_module.day_abbr[(date.today().weekday() - 6 + i) % 7]
                     for i in range(7)]
        today_wd  = date.today().weekday()
        monday    = date.today() - timedelta(days=today_wd)
        wday_lbls = [( monday + timedelta(days=i)).strftime("%a") for i in range(7)]

        wo, wi = make_card(p, self.c["card"], self.c["border"])
        wo.pack(fill="x", padx=pad, pady=(0, 12))
        tk.Label(wi, text="This Week — Daily Completion %",
                 bg=self.c["card"], fg=self.c["text"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")

        if HAS_MPL:
            fig = Figure(figsize=(7, 2.4), dpi=96, facecolor=self.c["card"])
            ax  = fig.add_subplot(111)
            ax.set_facecolor(self.c["card"])
            bars = ax.bar(wday_lbls, week_pcts,
                          color=[self.c["primary"] if i <= today_wd else self.c["surface3"]
                                 for i in range(7)],
                          width=0.6, zorder=2)
            ax.set_ylim(0, 110)
            ax.set_ylabel("%", color=self.c["text2"], fontsize=9)
            ax.tick_params(colors=self.c["text2"])
            for spine in ax.spines.values():
                spine.set_color(self.c["border"])
            ax.yaxis.label.set_color(self.c["text2"])
            ax.grid(axis="y", color=self.c["border"], linestyle="--", alpha=0.5, zorder=1)
            for bar, val in zip(bars, week_pcts):
                if val > 0:
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                            f"{val}%", ha="center", color=self.c["text2"], fontsize=8)
            # Highlight today
            bars[today_wd].set_color(self.c["accent"])
            fig.tight_layout(pad=1)
            cv = FigureCanvasTkAgg(fig, master=wi)
            cv.draw()
            cv.get_tk_widget().pack(fill="x")
        else:
            self._canvas_bar_chart(wi, week_pcts, wday_lbls, self.c["primary"])

        # ── Monthly chart ─────────────────────────────────────────────
        month_pcts = self.dm.get_month_pcts()
        day_labels = [str(i+1) for i in range(len(month_pcts))]

        mo, mi = make_card(p, self.c["card"], self.c["border"])
        mo.pack(fill="x", padx=pad, pady=(0, 12))
        tk.Label(mi, text=f"This Month — Daily Completion %",
                 bg=self.c["card"], fg=self.c["text"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")

        if HAS_MPL:
            fig2 = Figure(figsize=(7, 2.4), dpi=96, facecolor=self.c["card"])
            ax2  = fig2.add_subplot(111)
            ax2.set_facecolor(self.c["card"])
            x_idx = list(range(len(month_pcts)))
            ax2.fill_between(x_idx, month_pcts, alpha=0.3, color=self.c["primary"])
            ax2.plot(x_idx, month_pcts, color=self.c["primary"], linewidth=2)
            ax2.set_xticks(x_idx[::3])
            ax2.set_xticklabels(day_labels[::3], fontsize=8)
            ax2.tick_params(colors=self.c["text2"])
            ax2.set_ylim(0, 110)
            ax2.set_ylabel("%", color=self.c["text2"], fontsize=9)
            ax2.grid(color=self.c["border"], linestyle="--", alpha=0.4)
            for spine in ax2.spines.values():
                spine.set_color(self.c["border"])
            fig2.tight_layout(pad=1)
            cv2 = FigureCanvasTkAgg(fig2, master=mi)
            cv2.draw()
            cv2.get_tk_widget().pack(fill="x")
        else:
            self._canvas_bar_chart(mi, month_pcts, day_labels, self.c["accent"])

        # ── Summary numbers ───────────────────────────────────────────
        so, si = make_card(p, self.c["card"], self.c["border"])
        so.pack(fill="x", padx=pad, pady=(0, 24))
        tk.Label(si, text="Summary", bg=self.c["card"], fg=self.c["text"],
                 font=("Segoe UI", 11, "bold")).pack(anchor="w")

        week_avg = round(sum(week_pcts) / 7) if week_pcts else 0
        month_avg = round(sum(month_pcts) / len(month_pcts)) if month_pcts else 0
        perfect_days = sum(1 for d in range(len(month_pcts)) if month_pcts[d] == 100)
        streak = self.dm.calculate_streak()
        xp, lvl, lname, _, _ = self.dm.get_xp_info()

        metrics = [
            ("Weekly Avg",    f"{week_avg}%",    self.c["primary_l"]),
            ("Monthly Avg",   f"{month_avg}%",   self.c["accent"]),
            ("Perfect Days",  str(perfect_days), self.c["success"]),
            ("Streak",        f"{streak} days",  self.c["warning"]),
            ("Total XP",      f"{xp:,}",         "#f59e0b"),
            ("Level",         f"{lvl} — {lname}", self.c["primary_l"]),
        ]
        met_row = tk.Frame(si, bg=self.c["card"])
        met_row.pack(fill="x", pady=(8, 0))
        for label, val, color in metrics:
            col = tk.Frame(met_row, bg=self.c["card"])
            col.pack(side="left", fill="x", expand=True)
            tk.Label(col, text=val, bg=self.c["card"], fg=color,
                     font=("Segoe UI", 18, "bold")).pack()
            tk.Label(col, text=label, bg=self.c["card"], fg=self.c["text2"],
                     font=("Segoe UI", 8)).pack()

    def _canvas_bar_chart(self, parent, data, labels, color):
        """Fallback bar chart using tkinter Canvas (no matplotlib)."""
        cv = tk.Canvas(parent, height=180, bg=self.c["card"], highlightthickness=0)
        cv.pack(fill="x", pady=6)

        def draw(_=None):
            cv.delete("all")
            w = cv.winfo_width() or 500
            h = cv.winfo_height() or 180
            ml, mr, mt, mb = 36, 12, 20, 36
            cw = w - ml - mr
            ch = h - mt - mb
            n  = len(data)
            if n == 0:
                return
            max_v = max(data) or 100
            bw    = cw / n * 0.65
            gap   = cw / n * 0.35

            for i, (val, lbl) in enumerate(zip(data, labels)):
                x   = ml + i * (cw / n)
                bh  = (val / max_v) * ch
                y   = mt + ch - bh
                fill = self.c["accent"] if i == len(data) - 1 else color
                cv.create_rectangle(x + gap/2, y, x + bw + gap/2,
                                    mt + ch, fill=fill, outline="")
                if val:
                    cv.create_text(x + (bw + gap)/2, y - 6,
                                   text=f"{val}%", fill=self.c["text2"],
                                   font=("Segoe UI", 7))
                if i % max(1, n // 8) == 0:
                    cv.create_text(x + (bw + gap)/2, mt + ch + 14,
                                   text=lbl, fill=self.c["text2"],
                                   font=("Segoe UI", 7))

            # Y-axis
            cv.create_line(ml, mt, ml, mt + ch, fill=self.c["border"])
            for pct in [0, 25, 50, 75, 100]:
                y = mt + ch - (pct / 100) * ch
                cv.create_text(ml - 4, y, text=f"{pct}", anchor="e",
                               fill=self.c["text3"], font=("Segoe UI", 7))
                cv.create_line(ml, y, w - mr, y,
                               fill=self.c["border"], dash=(2, 4))

        cv.bind("<Configure>", draw)
        cv.after(100, draw)

    # ─────────────────────────────────────────────────────────────────
    # VIEW — CALENDAR
    # ─────────────────────────────────────────────────────────────────
    def _view_calendar(self):
        frame = tk.Frame(self.content, bg=self.c["bg"])
        frame.pack(fill="both", expand=True, padx=20, pady=16)

        # Month nav
        self._cal_year  = tk.IntVar(value=date.today().year)
        self._cal_month = tk.IntVar(value=date.today().month)

        nav = tk.Frame(frame, bg=self.c["bg"])
        nav.pack(fill="x", pady=(0, 12))
        tk.Button(nav, text="◀", command=self._cal_prev,
                  bg=self.c["surface2"], fg=self.c["text"],
                  relief="flat", font=("Segoe UI", 12), cursor="hand2").pack(side="left")
        self.lbl_cal_month = tk.Label(nav, text="", bg=self.c["bg"], fg=self.c["text"],
                                      font=("Segoe UI", 14, "bold"))
        self.lbl_cal_month.pack(side="left", padx=16)
        tk.Button(nav, text="▶", command=self._cal_next,
                  bg=self.c["surface2"], fg=self.c["text"],
                  relief="flat", font=("Segoe UI", 12), cursor="hand2").pack(side="left")
        tk.Button(nav, text="Today", command=self._cal_today,
                  bg=self.c["primary"], fg="white",
                  relief="flat", font=("Segoe UI", 9), cursor="hand2").pack(side="left", padx=8)

        # Legend
        leg = tk.Frame(nav, bg=self.c["bg"])
        leg.pack(side="right")
        for text, col in [("✓ Perfect", "#22c55e"), ("~ Partial", "#f59e0b"),
                          ("✗ Missed", "#ef4444"), ("Future", self.c["surface2"])]:
            tk.Label(leg, text=f"  {text}", bg=self.c["bg"], fg=col,
                     font=("Segoe UI", 9)).pack(side="left")

        # Calendar grid container
        self.cal_grid_frame = tk.Frame(frame, bg=self.c["bg"])
        self.cal_grid_frame.pack(fill="both", expand=True)

        self._render_calendar()

    def _render_calendar(self):
        for w in self.cal_grid_frame.winfo_children():
            w.destroy()

        yr  = self._cal_year.get()
        mo  = self._cal_month.get()
        self.lbl_cal_month.configure(
            text=f"{cal_module.month_name[mo]}  {yr}")

        today    = date.today()
        n_days   = cal_module.monthrange(yr, mo)[1]
        first_wd = cal_module.monthrange(yr, mo)[0]   # 0=Mon

        # Day headers
        for i, name in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
            tk.Label(self.cal_grid_frame, text=name,
                     bg=self.c["bg"], fg=self.c["text2"],
                     font=("Segoe UI", 9, "bold")).grid(
                         row=0, column=i, padx=4, pady=(0, 4), sticky="nsew")

        # Empty cells before first day
        row, col_idx = 1, first_wd
        for _ in range(first_wd):
            tk.Frame(self.cal_grid_frame, bg=self.c["bg"]).grid(
                row=1, column=_)

        for day in range(1, n_days + 1):
            d     = date(yr, mo, day)
            is_today = (d == today)
            future   = (d > today)
            pct      = self.dm.completion_pct(d)

            if future:
                bg, fg_val = self.c["surface2"], self.c["text3"]
                txt = ""
            elif pct == 0:
                if self.dm.get_scheduled_for(d):
                    bg, fg_val = "#3f0f0f", "#ef4444"   # missed
                    txt = "✗"
                else:
                    bg, fg_val = self.c["surface2"], self.c["text3"]
                    txt = ""
            elif pct == 1.0:
                bg, fg_val = "#0f3f1f", "#22c55e"   # perfect
                txt = "✓"
            else:
                bg, fg_val = "#3f3000", "#f59e0b"   # partial
                txt = f"{int(pct*100)}%"

            border_col = self.c["primary"] if is_today else self.c["border"]

            cell_o = tk.Frame(self.cal_grid_frame, bg=border_col,
                              padx=1 if is_today else 0,
                              pady=1 if is_today else 0)
            cell_o.grid(row=row, column=col_idx, padx=3, pady=3, sticky="nsew")
            cell_i = tk.Frame(cell_o, bg=bg, width=72, height=64)
            cell_i.pack(fill="both", expand=True)
            cell_i.pack_propagate(False)

            tk.Label(cell_i, text=str(day), bg=bg,
                     fg=self.c["primary_l"] if is_today else fg_val,
                     font=("Segoe UI", 11, "bold" if is_today else "normal")).pack(pady=(6, 0))
            if txt:
                tk.Label(cell_i, text=txt, bg=bg, fg=fg_val,
                         font=("Segoe UI", 9)).pack()

            col_idx += 1
            if col_idx == 7:
                col_idx = 0
                row += 1

        # Make columns stretch evenly
        for i in range(7):
            self.cal_grid_frame.columnconfigure(i, weight=1)

    def _cal_prev(self):
        m = self._cal_month.get() - 1
        y = self._cal_year.get()
        if m < 1:
            m, y = 12, y - 1
        self._cal_month.set(m)
        self._cal_year.set(y)
        self._render_calendar()

    def _cal_next(self):
        m = self._cal_month.get() + 1
        y = self._cal_year.get()
        if m > 12:
            m, y = 1, y + 1
        self._cal_month.set(m)
        self._cal_year.set(y)
        self._render_calendar()

    def _cal_today(self):
        self._cal_year.set(date.today().year)
        self._cal_month.set(date.today().month)
        self._render_calendar()

    # ─────────────────────────────────────────────────────────────────
    # VIEW — SETTINGS
    # ─────────────────────────────────────────────────────────────────
    def _view_settings(self):
        frame = ScrollableFrame(self.content, self.c["bg"])
        frame.pack(fill="both", expand=True)
        p = frame.inner

        pad = 20
        tk.Label(p, text="Settings", bg=self.c["bg"], fg=self.c["text"],
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=pad, pady=(20, 4))

        def section(title):
            tk.Label(p, text=title, bg=self.c["bg"], fg=self.c["text2"],
                     font=("Segoe UI", 9, "bold")).pack(
                         anchor="w", padx=pad, pady=(16, 4))

        def card_row(parent, label, widget_fn):
            row = tk.Frame(parent, bg=self.c["card"])
            row.pack(fill="x")
            tk.Label(row, text=label, bg=self.c["card"], fg=self.c["text"],
                     font=("Segoe UI", 10)).pack(side="left", padx=12, pady=10)
            widget_fn(row)

        # ── Appearance ───────────────────────────────────────────────
        section("APPEARANCE")
        ao, ai = make_card(p, self.c["card"], self.c["border"])
        ao.pack(fill="x", padx=pad, pady=(0, 4))

        def theme_widget(row):
            v = tk.StringVar(value=self._theme_name)
            for name, label in [("dark", "🌙 Dark"), ("light", "☀ Light")]:
                tk.Radiobutton(row, text=label, variable=v, value=name,
                               bg=self.c["card"], fg=self.c["text"],
                               selectcolor=self.c["primary"],
                               activebackground=self.c["card"],
                               command=lambda n=name: self._apply_theme(n),
                               font=("Segoe UI", 10)).pack(side="right", padx=8, pady=6)

        card_row(ai, "Color Theme", theme_widget)

        # ── Data ─────────────────────────────────────────────────────
        section("DATA MANAGEMENT")
        do, di = make_card(p, self.c["card"], self.c["border"])
        do.pack(fill="x", padx=pad, pady=(0, 4))

        btn_cfg = dict(relief="flat", font=("Segoe UI", 10),
                       padx=14, pady=6, cursor="hand2")

        actions = [
            ("Export Data (JSON)", self.c["surface3"], self.c["text"],  self._export),
            ("Import Data (JSON)", self.c["surface3"], self.c["text"],  self._import),
            ("Create Backup",      self.c["accent"],   "white",          self._backup),
            ("Reset All Data",     self.c["danger"],   "white",          self._reset_data),
        ]
        btn_row = tk.Frame(di, bg=self.c["card"])
        btn_row.pack(fill="x", pady=6)
        for label, bg, fg, cmd in actions:
            tk.Button(btn_row, text=label, bg=bg, fg=fg,
                      command=cmd, **btn_cfg).pack(side="left", padx=(0, 8), pady=4)

        # Data location
        tk.Label(di, text=f"📁  Data stored at:  {DATA_FILE}",
                 bg=self.c["card"], fg=self.c["text3"],
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(0, 8))

        # ── About ─────────────────────────────────────────────────────
        section("ABOUT")
        about_o, about_i = make_card(p, self.c["card"], self.c["border"])
        about_o.pack(fill="x", padx=pad, pady=(0, 24))
        for line in [
            f"{APP_NAME}  v{VERSION}",
            "A personal, fully offline habit & productivity tracker.",
            "No accounts. No internet. No cloud. All data is yours.",
            "",
            "Keyboard Shortcuts:",
            "  Ctrl+N   → Add new task",
            "  Ctrl+D   → Mark all tasks complete",
            "  F5       → Refresh current view",
        ]:
            tk.Label(about_i, text=line,
                     bg=self.c["card"],
                     fg=self.c["text"] if not line.startswith(" ") else self.c["text2"],
                     font=("Segoe UI", 9 if line.startswith(" ") else 10,
                           "bold" if line == f"{APP_NAME}  v{VERSION}" else "normal"),
                     anchor="w").pack(anchor="w")

    def _export(self):
        path = filedialog.asksaveasfilename(
            title="Export HabitFlow Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialfile="habitflow_export.json")
        if path:
            self.dm.export_json(path)
            show_toast(self.root, f"✅ Exported to {os.path.basename(path)}", color="#10b981")

    def _import(self):
        path = filedialog.askopenfilename(
            title="Import HabitFlow Data",
            filetypes=[("JSON files", "*.json")])
        if path:
            try:
                self.dm.import_json(path)
                messagebox.showinfo("Imported",
                    "Data imported successfully.\nA backup was created automatically.",
                    parent=self.root)
                self._show(self._active_view)
            except Exception as e:
                messagebox.showerror("Import Error", str(e), parent=self.root)

    def _backup(self):
        dest = self.dm.backup()
        if dest:
            show_toast(self.root, f"💾 Backup saved: {os.path.basename(dest)}", color="#10b981")

    def _reset_data(self):
        if messagebox.askyesno("Reset All Data",
                               "⚠ This will permanently delete ALL tasks, history, XP, and settings.\n\n"
                               "A backup will be created first. Continue?",
                               parent=self.root):
            self.dm.backup()
            self.dm.data = self.dm._fresh_data()
            self.dm.save()
            self._perfect_awarded_today = False
            self._show("Dashboard")
            show_toast(self.root, "🔄 Data reset. Fresh start!", color="#7c3aed")

    # ── Theme switching ───────────────────────────────────────────────
    def _toggle_theme(self):
        new = "light" if self._theme_name == "dark" else "dark"
        self._apply_theme(new)

    def _apply_theme(self, name: str):
        self._theme_name = name
        self.c = THEMES[name]
        self.dm.data["settings"]["theme"] = name
        self.dm.save()
        # Rebuild entire UI
        for w in self.root.winfo_children():
            w.destroy()
        self._setup_window()
        self._build_layout()
        self._show(self._active_view or "Dashboard")

    # ── Clock ticker ─────────────────────────────────────────────────
    def _tick_clock(self):
        now = datetime.now().strftime("%H:%M:%S  —  %a %d %b")
        if hasattr(self, "lbl_clock") and self.lbl_clock.winfo_exists():
            self.lbl_clock.configure(text=now)
        self._clock_job = self.root.after(1000, self._tick_clock)

    def on_close(self):
        if self._clock_job:
            self.root.after_cancel(self._clock_job)
        self.dm.save()
        self.root.destroy()


# ═══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════
def main():
    root = tk.Tk()

    # High-DPI awareness on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # Apply default icon (suppresses the tk feather icon on most OSes)
    try:
        root.iconbitmap(default="")
    except Exception:
        pass

    app = HabitFlowApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth()  - root.winfo_width())  // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()