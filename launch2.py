import tkinter as tk
from tkinter import messagebox
import platform
import subprocess
import os
from auth import login_or_register

# === Constants ===
ROOT = os.path.dirname(__file__)
SESSION_FILE = os.path.join(ROOT, "session.txt")
LAST_CHOICE_FILE = os.path.join(ROOT, "last_choice.txt")

# === Authenticate User ===
username = login_or_register()
if not username:
    messagebox.showerror("Login Failed", "Could not authenticate user.")
    exit()

# === Save Session ===
with open(SESSION_FILE, "w") as f:
    f.write(username)

# === Script Mapping ===
SCRIPTS = {
    1: ("🇮🇳 Prompt Globalizer", "day17.py", "Connect India to the United States"),
    2: ("🚪 Exit", None, "Close this launcher"),
}




def run_streamlit_script(script_name):
    command = f"streamlit run {script_name}"
    try:
        if platform.system() == "Windows":
            subprocess.run(["start", "cmd", "/k", command], shell=True)
        else:
            subprocess.run(["gnome-terminal", "--", "bash", "-c", f"{command}; exec bash"])
    except Exception as e:
        messagebox.showerror("Launch Failed", f"❌ Could not launch {script_name}:\n{e}")

def on_button_click(choice):
    if SCRIPTS[choice][1]:
        run_streamlit_script(SCRIPTS[choice][1])
        with open(LAST_CHOICE_FILE, "w") as f:
            f.write(str(choice))
    else:
        root.destroy()

def create_tooltip(widget, text):
    tooltip = tk.Label(root, text=text, bg="#ffffff", fg="#333333", font=("Segoe UI", 9), wraplength=240)
    tooltip.place_forget()

    def on_enter(event):
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() - root.winfo_rootx()
        y += widget.winfo_rooty() - root.winfo_rooty() + 30
        tooltip.place(x=x, y=y)

    def on_leave(event):
        tooltip.place_forget()

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
    return tooltip

# === GUI Setup ===
root = tk.Tk()
root.title("🧠 TraceForge Launcher")

# Full-screen mode
try:
    root.state("zoomed")
except:
    root.attributes("-zoomed", True)

root.configure(bg="#f7f7f7")

header = tk.Label(root, text=f"🧠 Welcome, {username}", font=("Segoe UI", 22, "bold"),
                  bg="#f7f7f7", fg="#222222")
header.pack(pady=(15, 10))

# === Scrollable Canvas Frame ===
canvas = tk.Canvas(root, borderwidth=0, background="#f7f7f7")
outer_frame = tk.Frame(canvas, background="#f7f7f7")
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview, width=40)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((0, 0), window=outer_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

outer_frame.bind("<Configure>", on_frame_configure)

# === Centering Wrapper Frame ===
center_frame = tk.Frame(outer_frame, background="#f7f7f7")
center_frame.pack(anchor="center", expand=True)

# === Buttons ===
buttons = []
tooltips = []

for idx in SCRIPTS:
    label, script, tip = SCRIPTS[idx]
    btn = tk.Button(center_frame, text=f"{idx}. {label}",
                    font=("Segoe UI", 13),
                    width=42, pady=10,
                    bg="#e6e6e6", fg="#111111",
                    activebackground="#d4d4d4", activeforeground="#003366",
                    relief="flat", borderwidth=1,
                    command=lambda c=idx: on_button_click(c))
    btn.pack(pady=10, padx=500, anchor="w")
    tooltip = create_tooltip(btn, tip)
    buttons.append(btn)
    tooltips.append(tooltip)

# === Last Run Restore ===
if os.path.exists(LAST_CHOICE_FILE):
    try:
        with open(LAST_CHOICE_FILE) as f:
            last = int(f.read().strip())
            if last in SCRIPTS:
                header.config(text=f"🧠 Welcome, {username}")
    except:
        pass

root.mainloop()
