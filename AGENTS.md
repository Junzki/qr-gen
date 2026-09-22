# AGENTS.md

QR Generator is a desktop app that previews a QR code and exports it as a PNG. It targets Python 3.14 and is managed with uv. The window is Tkinter. Image work uses Pillow and the `qrcode` library. The license is BSD-3-Clause.

## Layout

- `src/qr_gen/core.py` — QR rendering. No Tkinter. This is what the tests cover.
- `src/qr_gen/app.py` — the window: content, colors, preview, and export.
- `src/qr_gen/__init__.py` — `main()` starts the Tk event loop. Importing the package imports tkinter.
- `main.py` — PyInstaller entry point. Calls `qr_gen.main`.
- `build.py` — packages a macOS `.app` or a Windows `.exe`.
- `tests/test_qr_gen.py` — unit tests for `core`.
- `.github/workflows/tests.yml` — on Ubuntu: `uv sync --all-groups`, then `pytest`.
- `.github/workflows/release.yml` — manual release: bump the version, tag, build both platforms, publish a GitHub release.
- `.github/scripts/resolve_version.py` — reads and writes the `version` field in `pyproject.toml`.

## Commands

Run these from the repo root:

```bash
uv sync --all-groups
uv run qr-gen                  # installed console script
uv run python main.py          # same app; this is the file PyInstaller freezes
uv run pytest
uv run pytest tests/test_qr_gen.py::test_make_qr_size_and_mode
uv run python build.py         # package for the current OS
uv run python build.py --target macos --name "QR Generator"
```

`build.py --target` accepts `auto` (the default), `macos`, or `windows`. PyInstaller cannot cross-compile, and the script exits when the requested target is not the host OS. There is no checked-in `.spec`. `build.py` is the packaging source of truth. Optional icons live at `assets/icon.icns` and `assets/icon.ico`. The app name is `QR Generator`. The macOS bundle id is `com.tektome.qrgen`.

## Rendering contract

`make_qr(data, fill_color, back_color, target_size, margin=0)` returns an RGBA image of exactly `target_size` by `target_size`.

- `back_color == "transparent"` is a fully transparent canvas. Any other background is a `#rrggbb` string, parsed by `parse_hex`.
- `margin` is a quiet zone in pixels, clamped to `[0, target_size // 2 - 1]`. The code is centered in the remaining space.
- Modules are drawn at 1px and scaled with `Image.NEAREST` so edges stay sharp. Error correction is `ERROR_CORRECT_L`. The library border is `0` because this module applies the margin itself.
- Invalid hex falls back to the caller's default color. Color parsing does not raise.

The preview is 300px and refreshes 150ms after the last edit. Export sizes are 128, 256, 512, and 1024. Defaults are export size 1024, margin 0, transparent background, and foreground `#000000`.

## Conventions

- Match the file you are editing: type hints, and `from __future__ import annotations` in modules that already have it.
- Keep QR math in `core.py`. The UI collects strings and calls `make_qr`.
- No formatter or type checker is configured. Add one only when asked.
- The version line in `pyproject.toml` must stay `version = "X.Y.Z"`. `resolve_version.py` depends on that shape. The Release workflow owns bumps (`major`, `minor`, `patch`, or an explicit version) and commits `chore: bump version to <version>`. Leave the version alone unless the task is a release.
- The name `QR Generator` is repeated in `build.py` and in the artifact paths in `release.yml`. Change those together.

## Testing

CI runs `uv run pytest` on Ubuntu and does not open a window. Tests have to pass without a display session.

- When you change `core.py`, update `tests/test_qr_gen.py`.
- Assert size, mode, and pixels. A transparent background stays RGBA.
- Do not start `mainloop` in tests. Importing `qr_gen` or `qr_gen.core` loads tkinter through `src/qr_gen/__init__.py`, so the interpreter must be built with Tk. Assert on image output, not on widget structure.

## Boundaries

- Do not commit `build/`, `dist/`, `.venv/`, `__pycache__/`, or `*.spec`. They are gitignored.
- Do not commit secrets. The release workflow authenticates with `github.token` only.
- A local package build only covers the machine it ran on. Treat the other platform as unverified until that build has actually run.
