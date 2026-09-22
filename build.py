#!/usr/bin/env python3
from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"

APP_NAME = "QR Generator"
BUNDLE_ID = "com.tektome.qrgen"


def run(cmd: list[str]) -> None:
    print("+ " + " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def resolve_icon(target: str) -> Path | None:
    suffix = "icns" if target == "macos" else "ico"
    path = ROOT / "assets" / f"icon.{suffix}"
    return path if path.exists() else None


def build_macos(name: str, icon: Path | None) -> None:
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name", name,
        "--osx-bundle-identifier", BUNDLE_ID,
        "--paths", str(ROOT / "src"),
    ]
    if icon:
        args += ["--icon", str(icon)]
    args += [str(ROOT / "main.py")]
    run(args)
    print(f"Built: {DIST / f'{name}.app'}")


def build_windows(name: str, icon: Path | None) -> None:
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", name,
        "--paths", str(ROOT / "src"),
    ]
    if icon:
        args += ["--icon", str(icon)]
    args += [str(ROOT / "main.py")]
    run(args)
    print(f"Built: {DIST / f'{name}.exe'}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the QR app as a macOS .app bundle or Windows .exe"
    )
    parser.add_argument(
        "--target",
        choices=["macos", "windows", "auto"],
        default="auto",
        help="Which platform to build for (default: current OS)",
    )
    parser.add_argument("--name", default=APP_NAME, help="Output app name")
    args = parser.parse_args()

    host = {"darwin": "macos", "windows": "windows"}.get(platform.system().lower())
    if host is None:
        sys.exit(
            "Unsupported build host. PyInstaller must run on macOS or Windows "
            "(it cannot cross-compile)."
        )

    target = host if args.target == "auto" else args.target
    if target != host:
        sys.exit(
            f"PyInstaller cannot cross-compile: you are on {host} but requested "
            f"{target}. Run this script on the target OS."
        )

    icon = resolve_icon(target)
    if target == "macos":
        build_macos(args.name, icon)
    else:
        build_windows(args.name, icon)


if __name__ == "__main__":
    main()
