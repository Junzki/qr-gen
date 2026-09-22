# Changelog

All notable changes to QR Generator are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-22

First release.

### Added

- Desktop window for entering a URL or plain text, previewing the QR code, and exporting it as a PNG.
- Foreground color, and a background that is either transparent or a solid color. An invalid hex value falls back to black for the foreground and white for a solid background.
- Export sizes of 128, 256, 512, and 1024 pixels, plus a quiet-zone margin in pixels. The default export is 1024 pixels, with no margin and a transparent background.
- Live preview at 300 pixels that refreshes shortly after the last edit. Modules are drawn at 1 pixel and scaled with nearest-neighbor so the edges stay sharp. Error correction is level L.
- macOS `.app` and Windows `.exe` builds, produced by the Release workflow and attached to the GitHub release.
- Rendering tests, run on Ubuntu for pushes to `master`, tags, and pull requests.

### Fixed

- Release publishing no longer needs a checkout of the repository. `gh` is given the repository explicitly, and a tag that already exists can be replaced.

[Unreleased]: https://github.com/Junzki/qr-gen/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Junzki/qr-gen/releases/tag/v0.1.0
