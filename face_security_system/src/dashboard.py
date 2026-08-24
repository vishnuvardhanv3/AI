import os
import sys
import tkinter as tk
from tkinter import ttk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from database import init_db, get_today_attendance, get_recent_logs, get_people


def refresh():
    for item in attendance.get_children():
        attendance.delete(item)
    for row in get_today_attendance():
        attendance.insert("", "end", values=(row["name"], row["date"], row["time"]))
    for item in logs.get_children():
        logs.delete(item)
    for row in get_recent_logs():
        distance = "-" if row["distance"] is None else f'{row["distance"]:.1f}'
        logs.insert("", "end", values=(row["name"], row["status"], distance, row["date"], row["time"]))
    people_count.config(text=f"Registered people: {len(get_people())}")
    root.after(2000, refresh)


init_db()
root = tk.Tk()
root.title("Face Security Dashboard")
root.geometry("850x600")
ttk.Label(root, text="REAL-TIME FACE SECURITY DASHBOARD", font=("Segoe UI", 18, "bold")).pack(pady=15)
people_count = ttk.Label(root, text="")
people_count.pack(pady=5)
ttk.Label(root, text="Today's Attendance", font=("Segoe UI", 12, "bold")).pack(pady=(15,5))
attendance = ttk.Treeview(root, columns=("name","date","time"), show="headings", height=8)
for col in ("name","date","time"):
    attendance.heading(col, text=col.title())
attendance.pack(fill="x", padx=20)
ttk.Label(root, text="Recent Access Logs", font=("Segoe UI", 12, "bold")).pack(pady=(20,5))
logs = ttk.Treeview(root, columns=("name","status","distance","date","time"), show="headings", height=10)
for col in ("name","status","distance","date","time"):
    logs.heading(col, text=col.title())
logs.pack(fill="both", expand=True, padx=20, pady=(0,15))
refresh()
root.mainloop()
