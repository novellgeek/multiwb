import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import ctypes
import ctypes.wintypes
import webview

class MultiMonitorApp:
    def get_windows_monitors(self):
        monitors = []
        dpi_scale = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100.0 if hasattr(ctypes.windll, 'shcore') else 1.0

        def _callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            r = lprcMonitor.contents
            monitors.append({
                'x': int(r.left * dpi_scale),
                'y': int(r.top * dpi_scale),
                'width': int((r.right - r.left) * dpi_scale),
                'height': int((r.bottom - r.top) * dpi_scale)
            })
            return 1

        MONITORENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.wintypes.HMONITOR,
            ctypes.wintypes.HDC,
            ctypes.POINTER(ctypes.wintypes.RECT),
            ctypes.wintypes.LPARAM
        )

        ctypes.windll.user32.SetProcessDPIAware()
        ctypes.windll.user32.EnumDisplayMonitors(
            0, 0, MONITORENUMPROC(_callback), 0
        )

        return sorted(monitors, key=lambda m: (m['x'], m['y']))

    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Monitor Web Launcher")

        self.urls = []
        self.assignments = []
        self.fullscreens = []
        self.monitors = self.get_windows_monitors()

        self.mode = tk.StringVar(value="list")
        self.fullscreen = tk.BooleanVar(value=False)
        self.grid_rows = tk.IntVar(value=2)
        self.grid_cols = tk.IntVar(value=2)

        self.build_gui()

    def build_gui(self):
        def apply_theme_preset(preset):
            themes = {
                "Dark": ("#ffffff", "#222222"),
                "Light": ("#000000", "#ffffff"),
                "Neon": ("#00ffff", "#000000"),
                "Military": ("#ffffcc", "#003300")
            }
            if preset in themes:
                self.overlay_fg, self.overlay_bg = themes[preset]
                text_color.delete(0, tk.END)
                text_color.insert(0, self.overlay_fg)
                bg_color.delete(0, tk.END)
                bg_color.insert(0, self.overlay_bg)
        def update_overlay_geometry(event=None):
            self.overlay_size = (int(width_slider.get()), int(height_slider.get()))
            offset_text = offset_pos.get()
            positions = {
                "Top Left": (50, 50),
                "Top Right": (-250, 50),
                "Center": (-100, -50),
                "Bottom Left": (50, -150),
                "Bottom Right": (-250, -150)
            }
            self.overlay_offset = positions.get(offset_text, (50, 50))
        self.overlay_duration = 3000  # milliseconds
        self.overlay_size = (200, 100)
        self.overlay_offset = (50, 50)
        self.overlay_font = ("Arial", 18, "bold")
        self.overlay_bg = "#222222"
        self.overlay_fg = "#ffffff"
        frame = ttk.Frame(self.root, padding=10)
        frame.grid(row=0, column=0, sticky="nsew")

        url_label = ttk.Label(frame, text="URLs with Monitor Assignment:")
        url_label.grid(row=0, column=0, columnspan=4, sticky="w")

        self.url_frame = ttk.Frame(frame)
        self.url_frame.grid(row=1, column=0, columnspan=4, sticky="we")

        add_url_btn = ttk.Button(frame, text="Add URL", command=self.add_url)
        add_url_btn.grid(row=2, column=0, sticky="we")
        del_url_btn = ttk.Button(frame, text="Delete Selected", command=self.del_url)
        del_url_btn.grid(row=2, column=1, sticky="we")
        preview_btn = ttk.Button(frame, text="Preview Grid", command=self.show_preview)
        show_ids_btn = ttk.Button(frame, text="Show Monitor IDs", command=self.show_monitor_ids)
        show_ids_btn.grid(row=2, column=3, sticky="we")
        preview_btn.grid(row=2, column=2, sticky="we")

        mode_frame = ttk.LabelFrame(frame, text="Mode")
        mode_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="we")

        ttk.Radiobutton(mode_frame, text="List Mode", variable=self.mode, value="list").pack(anchor="w")
        ttk.Radiobutton(mode_frame, text="Grid Mode", variable=self.mode, value="grid").pack(anchor="w")

        grid_frame = ttk.Frame(mode_frame)
        grid_frame.pack(pady=5)
        ttk.Label(grid_frame, text="Rows:").grid(row=0, column=0)
        ttk.Entry(grid_frame, textvariable=self.grid_rows, width=5).grid(row=0, column=1)
        ttk.Label(grid_frame, text="Cols:").grid(row=0, column=2)
        ttk.Entry(grid_frame, textvariable=self.grid_cols, width=5).grid(row=0, column=3)

        ttk.Checkbutton(frame, text="Default Fullscreen", variable=self.fullscreen).grid(row=4, column=0, sticky="w")

        control_frame = ttk.Frame(frame)
        control_frame.grid(row=6, column=0, columnspan=4, pady=10)
        ttk.Button(control_frame, text="Save Config", command=self.save_config).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="Load Config", command=self.load_config).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="Launch", command=self.launch_windows).grid(row=0, column=2, padx=5)

        # Overlay controls
        overlay_frame = ttk.LabelFrame(self.root, text="Overlay Options")
        overlay_frame.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="we")

        ttk.Label(overlay_frame, text="Text Color:").grid(row=2, column=0)
        text_color = ttk.Entry(overlay_frame)
        text_color.insert(0, self.overlay_fg)
        text_color.grid(row=2, column=1)

        ttk.Label(overlay_frame, text="Background Color:").grid(row=2, column=2)
        bg_color = ttk.Entry(overlay_frame)
        bg_color.insert(0, self.overlay_bg)
        bg_color.grid(row=2, column=3)

        def update_theme():
            self.overlay_fg = text_color.get()
            self.overlay_bg = bg_color.get()

        ttk.Button(overlay_frame, text="Apply Theme", command=update_theme).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Label(overlay_frame, text="Presets:").grid(row=3, column=2)
        theme_select = ttk.Combobox(overlay_frame, values=["Dark", "Light", "Neon", "Military"])
        theme_select.set("Dark")
        theme_select.grid(row=3, column=3)
        theme_select.bind("<<ComboboxSelected>>", lambda e: apply_theme_preset(theme_select.get()))

        ttk.Label(overlay_frame, text="Width:").grid(row=0, column=0)
        width_slider = ttk.Scale(overlay_frame, from_=100, to=800, orient="horizontal", command=update_overlay_geometry)
        width_slider.set(self.overlay_size[0])
        width_slider.grid(row=0, column=1, padx=5)

        ttk.Label(overlay_frame, text="Height:").grid(row=0, column=2)
        height_slider = ttk.Scale(overlay_frame, from_=50, to=400, orient="horizontal", command=update_overlay_geometry)
        height_slider.set(self.overlay_size[1])
        height_slider.grid(row=0, column=3, padx=5)

        ttk.Label(overlay_frame, text="Position:").grid(row=1, column=0)
        offset_pos = ttk.Combobox(overlay_frame, values=["Top Left", "Top Right", "Center", "Bottom Left", "Bottom Right"])
        offset_pos.set("Top Left")
        offset_pos.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
        offset_pos.bind("<<ComboboxSelected>>", update_overlay_geometry)

    def show_preview(self):
        preview = tk.Toplevel(self.root)
        preview.title("Monitor Assignment Preview")
        for idx, mon in enumerate(self.monitors):
            label = f"Monitor {idx+1}"
            assigned_urls = [self.urls[i] for i, a in enumerate(self.assignments) if a == label]
            text = "\n".join(assigned_urls) if assigned_urls else "(None)"
            frame = ttk.LabelFrame(preview, text=label, padding=10)
            frame.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky="nsew")
            label_widget = tk.Label(frame, text=text, justify="left")
            label_widget.pack()

        self.show_monitor_ids()

    def show_monitor_ids(self):
        for idx, mon in enumerate(self.monitors):
            overlay = tk.Toplevel()
            overlay.overrideredirect(True)
            overlay.attributes("-topmost", True)
            overlay.geometry(f"{self.overlay_size[0]}x{self.overlay_size[1]}+{mon['x'] + self.overlay_offset[0]}+{mon['y'] + self.overlay_offset[1]}")
            label = tk.Label(
                overlay,
                text=f"Monitor {idx+1}",
                font=self.overlay_font,
                bg=self.overlay_bg,
                fg=self.overlay_fg
            )
            label.pack(expand=True, fill="both")
            overlay.after(self.overlay_duration, overlay.destroy)

    def refresh_url_list(self):
        for widget in self.url_frame.winfo_children():
            widget.destroy()

        for i, url in enumerate(self.urls):
            tk.Label(self.url_frame, text=url).grid(row=i, column=0, sticky="w")
            combo = ttk.Combobox(self.url_frame, values=[f"Monitor {j+1}" for j in range(len(self.monitors))], width=15)
            combo.grid(row=i, column=1, padx=5)
            if i < len(self.assignments):
                combo.set(self.assignments[i])
            else:
                combo.set("")
                self.assignments.append("")
            combo.bind("<<ComboboxSelected>>", lambda e, idx=i: self.update_assignment(idx, e))

            fs_chk = ttk.Checkbutton(self.url_frame, text="Fullscreen", command=lambda idx=i: self.toggle_fullscreen(idx))
            fs_chk.grid(row=i, column=2)
            if i >= len(self.fullscreens):
                self.fullscreens.append(self.fullscreen.get())

    def update_assignment(self, index, event):
        combo = event.widget
        self.assignments[index] = combo.get()

    def toggle_fullscreen(self, index):
        self.fullscreens[index] = not self.fullscreens[index]

    def add_url(self):
        new_url = simpledialog.askstring("Add URL", "Enter URL:")
        if new_url:
            self.urls.append(new_url)
            self.assignments.append("Monitor 1")
            self.fullscreens.append(self.fullscreen.get())
            self.refresh_url_list()

    def del_url(self):
        if not self.urls:
            return
        index = len(self.urls) - 1
        self.urls.pop(index)
        self.assignments.pop(index)
        self.fullscreens.pop(index)
        self.refresh_url_list()

    def save_config(self):
        config = {
            "urls": self.urls,
            "assignments": self.assignments,
            "fullscreens": self.fullscreens,
            "mode": self.mode.get(),
            "fullscreen": self.fullscreen.get(),
            "grid": {
                "rows": self.grid_rows.get(),
                "cols": self.grid_cols.get()
            },
            "overlay": {
                "duration": self.overlay_duration,
                "size": self.overlay_size,
                "offset": self.overlay_offset,
                "font": self.overlay_font,
                "bg": self.overlay_bg,
                "fg": self.overlay_fg
            }
        }
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(config, f, indent=2)

    def load_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                config = json.load(f)
                self.urls = config.get("urls", [])
                self.assignments = config.get("assignments", ["" for _ in self.urls])
                self.fullscreens = config.get("fullscreens", [self.fullscreen.get() for _ in self.urls])
                self.mode.set(config.get("mode", "list"))
                self.fullscreen.set(config.get("fullscreen", False))
                grid = config.get("grid", {})
                self.grid_rows.set(grid.get("rows", 2))
                self.grid_cols.set(grid.get("cols", 2))

                overlay = config.get("overlay", {})
                self.overlay_duration = overlay.get("duration", self.overlay_duration)
                self.overlay_size = tuple(overlay.get("size", self.overlay_size))
                self.overlay_offset = tuple(overlay.get("offset", self.overlay_offset))
                self.overlay_font = tuple(overlay.get("font", self.overlay_font))
                self.overlay_bg = overlay.get("bg", self.overlay_bg)
                self.overlay_fg = overlay.get("fg", self.overlay_fg)

                self.refresh_url_list()

    def launch_windows(self):
        import subprocess
        import tempfile
        from collections import defaultdict
        if not self.urls:
            messagebox.showwarning("No URLs", "Please add at least one URL.")
            return

        window_configs = []

        if self.mode.get() == "list":
            # Existing list mode logic
            tiling_map = defaultdict(list)
            for i, url in enumerate(self.urls):
                assigned = self.assignments[i]
                if not assigned or not assigned.startswith("Monitor"):
                    messagebox.showerror("Monitor Assignment Missing", f"Please assign a monitor for URL {i+1}.")
                    return
                tiling_map[assigned].append(i)

            for monitor_label, indices in tiling_map.items():
                mon_index = int(monitor_label.split(" ")[1]) - 1
                mon = self.monitors[mon_index]
                tile_count = len(indices)
                tile_w = mon['width'] // tile_count
                for pos, i in enumerate(indices):
                    window_configs.append({
                        "title": f"Display {i+1}",
                        "url": self.urls[i],
                        "x": mon['x'] + pos * tile_w,
                        "y": mon['y'],
                        "width": tile_w,
                        "height": mon['height'],
                        "fullscreen": self.fullscreens[i]
                    })
        else:
            # NEW: grid mode supports up to 4 windows per monitor (or as set in GUI)
            rows, cols = self.grid_rows.get(), self.grid_cols.get()
            max_cells = rows * cols

            monitor_map = defaultdict(list)
            for i, assigned in enumerate(self.assignments):
                if assigned and assigned.startswith("Monitor"):
                    mon_index = int(assigned.split(" ")[1]) - 1
                    monitor_map[mon_index].append(i)

            for mon_index, indices in monitor_map.items():
                mon = self.monitors[mon_index]
                cell_w = mon['width'] // cols
                cell_h = mon['height'] // rows
                for cell_idx, i in enumerate(indices):
                    if cell_idx >= max_cells:
                        messagebox.showerror("Grid Too Small", f"Monitor {mon_index+1}: Too many URLs assigned for the selected grid size (max {max_cells}).")
                        break  # Only up to grid size per monitor
                    r = cell_idx // cols
                    c = cell_idx % cols
                    window_configs.append({
                        "title": f"Grid {i+1}",
                        "url": self.urls[i],
                        "x": mon['x'] + c * cell_w,
                        "y": mon['y'] + r * cell_h,
                        "width": cell_w,
                        "height": cell_h,
                        "fullscreen": self.fullscreens[i]
                    })

        with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as tf:
            json.dump({"windows": window_configs}, tf)
            tf.flush()
            import threading
            threading.Thread(target=lambda: subprocess.Popen(["python", "launch_windows_runner.py", tf.name]), daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiMonitorApp(root)
    root.mainloop()
