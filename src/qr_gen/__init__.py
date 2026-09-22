import tkinter as tk


def main() -> None:
    from .app import QRApp

    root = tk.Tk()
    QRApp(root)
    root.mainloop()
