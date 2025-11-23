import tkinter as tk
from tkinter import ttk
import threading, time, random
from pynput import mouse, keyboard

# ======================================================
#                 AUTOCLICKER CORE
# ======================================================
class AutoClicker:
    def __init__(self):
        self.running = False
        self.mode = "Hold"
        self.keybind = None  # can be keyboard.Key/KeyCode or mouse.Button
        self.mouse_button = mouse.Button.left
        self.k_listener = None
        self.m_listener = None
        self.mouse = mouse.Controller()
        self._listener_lock = threading.Lock()
        self.paused = False  # pause listening with F6

    def set_mode(self, mode):
        self.mode = mode

    def set_mouse_button(self, button):
        self.mouse_button = button

    def set_keybind(self, key):
        self.keybind = key
        self._ensure_runtime_listeners()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.running = False

    def _ensure_runtime_listeners(self):
        with self._listener_lock:
            if self.k_listener is None:
                def on_k_press(k):
                    if self.paused: return
                    try:
                        if self.keybind is None: return
                        if isinstance(self.keybind, (keyboard.Key, keyboard.KeyCode)) and k == self.keybind:
                            if self.mode == "Hold":
                                self.running = True
                            elif self.mode == "Toggle":
                                self.running = not self.running
                        # F6 pause toggle
                        if k == keyboard.Key.f6:
                            self.toggle_pause()
                    except: pass

                def on_k_release(k):
                    if self.paused: return
                    try:
                        if self.keybind is None: return
                        if isinstance(self.keybind, (keyboard.Key, keyboard.KeyCode)) and k == self.keybind and self.mode == "Hold":
                            self.running = False
                    except: pass

                self.k_listener = keyboard.Listener(on_press=on_k_press, on_release=on_k_release)
                self.k_listener.daemon = True
                self.k_listener.start()

            if self.m_listener is None:
                def on_m_click(x, y, button, pressed):
                    if self.paused: return
                    try:
                        if self.keybind is None: return
                        if isinstance(self.keybind, mouse.Button) and button == self.keybind:
                            if pressed:
                                if self.mode == "Hold":
                                    self.running = True
                                elif self.mode == "Toggle":
                                    self.running = not self.running
                            else:
                                if self.mode == "Hold":
                                    self.running = False
                    except: pass

                self.m_listener = mouse.Listener(on_click=on_m_click)
                self.m_listener.daemon = True
                self.m_listener.start()

    def start_listeners(self):
        self._ensure_runtime_listeners()

    def click_loop(self, get_min, get_max):
        next_click_time = time.time()
        while True:
            try:
                if self.running:
                    min_cps = float(get_min())
                    max_cps = float(get_max())
                    if min_cps <= 0: min_cps = 1.0
                    if max_cps <= 0: max_cps = 1.0
                    if min_cps > max_cps: min_cps, max_cps = max_cps, min_cps

                    burst_len = random.randint(1, 4)
                    burst_cps = random.uniform(min_cps, max_cps)

                    for _ in range(burst_len):
                        if not self.running: break
                        jitter_factor = random.uniform(0.8, 1.2)
                        delay = (1.0 / burst_cps) * jitter_factor
                        delay += random.uniform(-0.008, 0.008)
                        if delay < 0.005: delay = 0.005

                        now = time.time()
                        if now >= next_click_time:
                            self.mouse.click(self.mouse_button)
                            next_click_time = now + delay
                        else:
                            time.sleep(min(next_click_time - now, 0.01))
                            continue

                        if random.random() < 0.06:
                            time.sleep(random.uniform(0.03, 0.12))
                else:
                    time.sleep(0.01)
            except:
                time.sleep(0.05)

clicker = AutoClicker()

# ======================================================
#               AUTOCLICKER GUI
# ======================================================
class ClickerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Anti Anti-Cheat🤓")
        root.geometry("700x500")  # increased height
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
        self.mouse_button_var = tk.StringVar(value="Leftclick")

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

        tk.Label(left, text="Mouse Button", fg=self.purple, bg=self.panel, font=self.mono).pack(anchor="w", pady=(8,2))
        ttk.OptionMenu(left, self.mouse_button_var, "Leftclick", "Leftclick", "Rightclick").pack(fill=tk.X, pady=2)

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

    # ---------- Keybind picker ----------
    def _set_keybind(self):
        self.keybind_var.set("Press any key or mouse button...")

        caught = {"done": False}

        def finish(key):
            if caught["done"]: return
            caught["done"] = True
            clicker.set_keybind(key)
            if isinstance(key, mouse.Button):
                self.keybind_var.set(str(key))
            else:
                self.keybind_var.set(str(key))
            try: k_tmp.stop()
            except: pass
            try: m_tmp.stop()
            except: pass
            return False

        def on_k_press(k): finish(k); return False
        def on_m_click(x,y,button,pressed):
            if pressed: finish(button)
            return False

        k_tmp = keyboard.Listener(on_press=on_k_press)
        m_tmp = mouse.Listener(on_click=on_m_click)
        k_tmp.start()
        m_tmp.start()

    def _save_settings(self):
        clicker.set_mode(self.mode_var.get())
        if self.mouse_button_var.get() == "Leftclick":
            clicker.set_mouse_button(mouse.Button.left)
        else:
            clicker.set_mouse_button(mouse.Button.right)
        clicker.start_listeners()
        self._log(f"Settings saved: min {self.min_cps_var.get()}, max {self.max_cps_var.get()}, mode {self.mode_var.get()}, key {self.keybind_var.get()}, mouse {self.mouse_button_var.get()}")
        self.status_label.config(text="STATUS: settings saved")

# ======================================================
#                   SECRET CALCULATOR
# ======================================================
class SecretCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.geometry("290x500")  # taller for CLEAR button
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
        frame.pack(expand=True, pady=(0,10))

        buttons = [
            ("7",1,0), ("8",1,1), ("9",1,2), ("/",1,3),
            ("4",2,0), ("5",2,1), ("6",2,2), ("*",2,3),
            ("1",3,0), ("2",3,1), ("3",3,2), ("-",3,3),
            ("0",4,0), (".",4,1), ("=",4,2), ("+",4,3)
        ]

        for (txt,r,c) in buttons:
            cmd = (self._equals if txt=="=" else lambda x=txt: self._press(x))
            tk.Button(frame, text=txt, width=4, height=2,
                      font=("Consolas",18), bg="#301a45", fg="#d6b8ff",
                      activebackground="#4c2e6b", bd=0, command=cmd).grid(row=r,column=c,padx=5,pady=5)

        tk.Button(self.root, text="CLEAR", font=("Consolas",14),
                  bg="#452064", fg="#e5d4ff", activebackground="#60308a",
                  bd=0, command=self._clear).pack(fill="x", padx=15, pady=(0,15))

# ======================================================
#                      START
# ======================================================
if __name__ == "__main__":
    SecretCalculator()
