from __future__ import annotations

import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import ImageTk

from .core import make_qr, parse_hex, to_hex

PREVIEW_SIZE = 300
SIZES = ("128", "256", "512", "1024")


class QRApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self._photo: ImageTk.PhotoImage | None = None
        self._debounce_id: str | None = None

        root.title("QR Generator")
        root.minsize(760, 460)
        self._build_ui()
        self._schedule_refresh()

    def _build_ui(self) -> None:
        container = ttk.Frame(self.root, padding=12)
        container.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        left = ttk.Frame(container)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        self._build_input(left)
        self._build_preview(right)
        self._build_colors(right)
        self._build_export(right)

    def _build_input(self, parent: ttk.Frame) -> None:
        type_frame = ttk.Frame(parent)
        type_frame.pack(fill="x")
        ttk.Label(type_frame, text="Type:").pack(side="left")
        self.type_var = tk.StringVar(value="URL")
        type_combo = ttk.Combobox(
            type_frame,
            textvariable=self.type_var,
            values=("URL", "Text"),
            state="readonly",
            width=10,
        )
        type_combo.pack(side="left", padx=(8, 0))
        type_combo.bind("<<ComboboxSelected>>", lambda _e: self._schedule_refresh())

        ttk.Label(parent, text="Content:").pack(anchor="w", pady=(12, 4))
        self.text = tk.Text(parent, wrap="word", height=12)
        self.text.pack(fill="both", expand=True)
        self.text.bind("<KeyRelease>", lambda _e: self._schedule_refresh())

    def _build_preview(self, parent: ttk.Frame) -> None:
        frame = ttk.LabelFrame(parent, text="Preview", padding=8)
        frame.pack(fill="both", expand=True)

        self.preview_box = tk.Frame(
            frame, width=PREVIEW_SIZE, height=PREVIEW_SIZE, bg="#f0f0f0"
        )
        self.preview_box.pack()
        self.preview_box.pack_propagate(False)

        self.preview_label = tk.Label(
            self.preview_box, bg="#f0f0f0", borderwidth=0
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

    def _build_colors(self, parent: ttk.Frame) -> None:
        config = ttk.LabelFrame(parent, text="Colors", padding=8)
        config.pack(fill="x", pady=(12, 0))

        self.bg_mode = tk.StringVar(value="transparent")
        self.bg_color_var = tk.StringVar(value="#FFFFFF")
        self.fg_color_var = tk.StringVar(value="#000000")

        ttk.Label(config, text="Background:").grid(row=0, column=0, sticky="w")

        bg_row = ttk.Frame(config)
        bg_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Radiobutton(
            bg_row, text="Transparent", variable=self.bg_mode, value="transparent",
            command=self._schedule_refresh,
        ).pack(side="left")
        ttk.Radiobutton(
            bg_row, text="Color", variable=self.bg_mode, value="color",
            command=self._schedule_refresh,
        ).pack(side="left", padx=(8, 0))
        self.bg_color_entry = ttk.Entry(
            bg_row, textvariable=self.bg_color_var, width=10
        )
        self.bg_color_entry.pack(side="left", padx=(8, 0))
        self.bg_color_entry.bind("<KeyRelease>", lambda _e: self._schedule_refresh())

        ttk.Label(config, text="Foreground:").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        self.fg_entry = ttk.Entry(config, textvariable=self.fg_color_var, width=10)
        self.fg_entry.grid(row=2, column=1, sticky="w", pady=(8, 0))
        self.fg_entry.bind("<KeyRelease>", lambda _e: self._schedule_refresh())

    def _build_export(self, parent: ttk.Frame) -> None:
        export = ttk.LabelFrame(parent, text="Export", padding=8)
        export.pack(fill="x", pady=(12, 0))

        ttk.Label(export, text="Size:").pack(side="left")
        self.size_var = tk.StringVar(value="1024")
        size_combo = ttk.Combobox(
            export, textvariable=self.size_var, values=SIZES, state="readonly", width=6
        )
        size_combo.pack(side="left", padx=(8, 12))

        ttk.Label(export, text="Margin (px):").pack(side="left")
        self.margin_var = tk.StringVar(value="0")
        margin_entry = ttk.Entry(export, textvariable=self.margin_var, width=5)
        margin_entry.pack(side="left", padx=(8, 12))
        margin_entry.bind("<KeyRelease>", lambda _e: self._schedule_refresh())

        ttk.Button(export, text="Export PNG", command=self.export).pack(side="right")

    def _schedule_refresh(self, _event=None) -> None:
        if self._debounce_id is not None:
            self.root.after_cancel(self._debounce_id)
        self._debounce_id = self.root.after(150, self._refresh)

    def _resolve_colors(self) -> tuple[str, str]:
        fg = to_hex(parse_hex(self.fg_color_var.get(), (0, 0, 0)))
        if self.bg_mode.get() == "transparent":
            bg = "transparent"
        else:
            bg = to_hex(parse_hex(self.bg_color_var.get(), (255, 255, 255)))
        return fg, bg

    def _resolve_margin(self) -> int:
        try:
            return max(0, int(self.margin_var.get().strip()))
        except ValueError:
            return 0

    def _refresh(self) -> None:
        self._debounce_id = None
        data = self.text.get("1.0", "end-1c").strip()
        if not data:
            self.preview_label.config(image="")
            self._photo = None
            return
        fg, bg = self._resolve_colors()
        margin = self._resolve_margin()
        try:
            img = make_qr(data, fg, bg, PREVIEW_SIZE, margin)
        except Exception:
            self.preview_label.config(image="")
            self._photo = None
            return
        self._photo = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self._photo)

    def export(self) -> None:
        data = self.text.get("1.0", "end-1c").strip()
        if not data:
            messagebox.showwarning("QR Generator", "Enter some text or URL first.")
            return
        try:
            size = int(self.size_var.get())
        except ValueError:
            size = 1024

        fg, bg = self._resolve_colors()
        margin = self._resolve_margin()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        default_name = f"qr-{timestamp}.png"

        path = filedialog.asksaveasfilename(
            title="Export QR Code",
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
        )
        if not path:
            return

        img = make_qr(data, fg, bg, size, margin)
        img.save(path)
        messagebox.showinfo("QR Generator", f"Saved {path}")
