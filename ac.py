import tkinter as tk
from tkinter import ttk
import threading, time, random
from pynput import mouse, keyboard

# ======================================================
#                 AUTCLICKER CORE
#               (YOUR ORIGINAL CODE)
# ======================================================

class AutoClicker:
    def __init__(self):
        self.running = False
        self.mode = "Hold"
        self.keybind = None
        self.listener = None
        self.mouse = mouse.Controller()

    def set_mode(self, mode):
        self.mode = mode

    def set_keybind(self, key):
        self.keybind = key
        self.start_listener()

    def start_listener(self):
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass

        if self.keybind is None:
            return

        def on_press(key):
            try:
                if key == self.keybind:
                    if self.mode == "Hold":
                        self.running = True
                    elif self.mode == "Toggle":
                        self.running = not self.running
            except:
                pass

        def on_release(key):
            if key == self.keybind and self.mode == "Hold":
                self.running = False

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.daemon = True
        self.listener.start()

    def click_loop(self, get_min, get_max):
        while True:
            if self.running:
                # More realistic CPS randomness
                cps = random.gauss(
                    (get_min() + get_max()) / 2,
                    (get_max() - get_min()) / 3
                )
                cps = max(get_min(), min(get_max(), cps))
                delay = 1.0 / cps

                self.mouse.click(mouse.Button.left)
                time.sleep(delay)
            else:
                time.sleep(0.01)

clicker = AutoClicker()

# ======================================================
#               YOUR ORIGINAL AUTCLICKER GUI
# ======================================================

class ClickerGUI:
    def __init__(self, root):
        self.root = root
        root.title("")
        root.geometry("700x450")
        root.configure(bg="#0a0a0a")
        root.resizable(False, False)

        self.bg = "#0a0a0a"
        self.panel = "#120a20"
        self.purple = "#b366ff"
        self.dim_purple = "#552288"
        self.muted = "#9a86b3"
        self.mono = ("Consolas", 12)
        self.mono_bold = ("Consolas", 14, "bold")
        self.mono_huge = ("Consolas", 18, "bold")

        self.min_cps_var = tk.DoubleVar(value=8)
        self.max_cps_var = tk.DoubleVar(value=12)
        self.mode_var = tk.StringVar(value="Hold")
        self.keybind_var = tk.StringVar(value="None")

        self._create_header()
        self._create_main_area()
        self._create_statusbar()

        threading.Thread(
            target=clicker.click_loop,
            args=(lambda: self.min_cps_var.get(), lambda: self.max_cps_var.get()),
            daemon=True
        ).start()

    def _create_header(self):
        header = tk.Frame(self.root, bg=self.panel, height=60)
        header.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(header, text="Anti Anti-Cheat🤓", fg=self.purple, bg=self.panel, font=self.mono_huge).pack(anchor="w")
        tk.Label(header, text="Made by misk & chatgpt", fg=self.muted, bg=self.panel, font=self.mono).pack(anchor="w")

    def _create_main_area(self):
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

        left = tk.Frame(main, bg=self.panel)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,6))

        tk.Label(left, text="Minimum CPS", fg=self.purple, bg=self.panel, font=self.mono).pack(anchor="w", pady=(8,2))
        tk.Entry(left, textvariable=self.min_cps_var, fg=self.purple, bg="#1a0a30", font=self.mono, insertbackground=self.purple, bd=0).pack(fill=tk.X, pady=2)

        tk.Label(left, text="Maximum CPS", fg=self.purple, bg=self.panel, font=self.mono).pack(anchor="w", pady=(8,2))
        tk.Entry(left, textvariable=self.max_cps_var, fg=self.purple, bg="#1a0a30", font=self.mono, insertbackground=self.purple, bd=0).pack(fill=tk.X, pady=2)

        tk.Label(left, text="Mode", fg=self.purple, bg=self.panel, font=self.mono).pack(anchor="w", pady=(8,2))
        ttk.OptionMenu(left, self.mode_var, "Hold", "Hold", "Toggle").pack(fill=tk.X, pady=2)

        tk.Label(left, text="Keybind", fg=self.purple, bg=self.panel, font=self.mono).pack(anchor="w", pady=(8,2))
        tk.Button(left, text="Set Keybind", command=self._set_keybind, bg=self.dim_purple, fg="#fff", font=self.mono, bd=0).pack(fill=tk.X, pady=2)
        tk.Label(left, textvariable=self.keybind_var, fg=self.purple, bg=self.panel, font=self.mono).pack(anchor="w", pady=2)

        tk.Button(left, text="Save Settings", command=self._save_settings, bg=self.purple, fg="#0a0a0a", font=self.mono_bold, bd=0).pack(fill=tk.X, pady=(12,0))

        right = tk.Frame(main, bg="#050012")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.log = tk.Text(right, bg="#050012", fg=self.purple, font=self.mono, bd=0, wrap="word", insertbackground=self.purple)
        self.log.pack(fill=tk.BOTH, expand=True)
        self._log("-- AutoClicker Ready --")

    def _create_statusbar(self):
        status = tk.Frame(self.root, bg=self.bg, height=24)
        status.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0,10))
        self.status_label = tk.Label(status, text="STATUS: idle", fg=self.dim_purple, bg=self.bg, font=self.mono)
        self.status_label.pack(side=tk.LEFT)

    def _log(self, text):
        self.log.config(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.config(state=tk.DISABLED)

    def _set_keybind(self):
        self.keybind_var.set("Press a key...")

        def on_press(key):
            clicker.set_keybind(key)
            self.keybind_var.set(str(key))
            listener.stop()
            return False

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def _save_settings(self):
        clicker.set_mode(self.mode_var.get())
        clicker.start_listener()
        self._log(
            f"Settings saved: min {self.min_cps_var.get()}, max {self.max_cps_var.get()}, mode {self.mode_var.get()}, key {self.keybind_var.get()}"
        )
        self.status_label.config(text="STATUS: settings saved")


# ======================================================
#                   SECRET CALCULATOR
# ======================================================

class SecretCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.geometry("290x400")
        self.root.configure(bg="#1a1025")
        self.root.resizable(False, False)

        self.expr = ""

        self.display = tk.Entry(self.root, font=("Consolas", 22),
                                bg="#261335", fg="#c09cff",
                                justify="right", bd=0)
        self.display.pack(fill="x", padx=12, pady=12, ipady=12)

        self._make_buttons()

        self.root.mainloop()

    def _press(self, val):
        self.expr += str(val)
        self._render()

    def _render(self):
        self.display.delete(0, tk.END)
        self.display.insert(0, self.expr)

    def _clear(self):
        self.expr = ""
        self._render()

    def _equals(self):
        # SECRET TRIGGER
        if self.expr.replace(" ", "") == "6+7":
            win = tk.Toplevel(self.root)
            ClickerGUI(win)
            return

        try:
            result = str(eval(self.expr))
        except:
            result = "ERR"

        self.expr = result
        self._render()

    def _make_buttons(self):
        frame = tk.Frame(self.root, bg="#1a1025")
        frame.pack(expand=True)

        buttons = [
            ("7",1,0), ("8",1,1), ("9",1,2), ("/",1,3),
            ("4",2,0), ("5",2,1), ("6",2,2), ("*",2,3),
            ("1",3,0), ("2",3,1), ("3",3,2), ("-",3,3),
            ("0",4,0), (".",4,1), ("=",4,2), ("+",4,3)
        ]

        for (txt, r, c) in buttons:
            cmd = (self._equals if txt == "=" else lambda x=txt: self._press(x))

            tk.Button(
                frame, text=txt, width=4, height=2,
                font=("Consolas", 18),
                bg="#301a45", fg="#d6b8ff",
                activebackground="#4c2e6b", bd=0,
                command=cmd
            ).grid(row=r, column=c, padx=5, pady=5)

        tk.Button(
            self.root, text="CLEAR", font=("Consolas", 14),
            bg="#452064", fg="#e5d4ff",
            activebackground="#60308a", bd=0,
            command=self._clear
        ).pack(fill="x", padx=15, pady=10)


# ======================================================
#                   START PROGRAM
# ======================================================

SecretCalculator()
