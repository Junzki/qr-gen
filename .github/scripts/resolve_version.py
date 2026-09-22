"""Resolve the release version/tag for the release workflow.

Reads the current version from ``pyproject.toml`` and, depending on how the
workflow was triggered, either derives the version from the git tag or applies
the requested version/bump rule. Writes the resolved ``tag`` and ``version`` to
the GitHub Actions output file.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


def read_version() -> str:
    text = Path("pyproject.toml").read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        sys.exit("Could not find version in pyproject.toml")
    return match.group(1)


def write_version(version: str) -> None:
    path = Path("pyproject.toml")
    text = path.read_text()
    text = re.sub(
        r'(^version\s*=\s*)"([^"]+)"',
        lambda m: f'{m.group(1)}"{version}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    path.write_text(text)


def write_outputs(tag: str, version: str) -> None:
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        f.write(f"tag={tag}\n")
        f.write(f"version={version}\n")


def main() -> None:
    input_version = os.environ.get("INPUT_VERSION", "minor")
    is_tag = os.environ.get("IS_TAG", "false") == "true"
    ref = os.environ["GITHUB_REF"]

    if is_tag:
        tag = ref.removeprefix("refs/tags/")
        match = SEMVER.match(tag)
        version = (
            f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
            if match
            else tag.lstrip("v")
        )
        write_outputs(tag, version)
        print(f"Tag release: version={version} tag={tag}")
        return

    current = read_version()
    match = SEMVER.match(input_version)
    if match:
        version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
    elif input_version in ("major", "minor", "patch"):
        major, minor, patch = (int(x) for x in current.split(".")[:3])
        if input_version == "major":
            major, minor, patch = major + 1, 0, 0
        elif input_version == "minor":
            minor, patch = minor + 1, 0
        else:
            patch += 1
        version = f"{major}.{minor}.{patch}"
    else:
        sys.exit(f"Invalid version input: {input_version!r}")

    write_version(version)
    tag = f"v{version}"
    write_outputs(tag, version)
    print(f"Version bump: {current} -> {version} (tag {tag})")


if __name__ == "__main__":
    main()
