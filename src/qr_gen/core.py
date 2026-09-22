from __future__ import annotations

import re

import qrcode
from PIL import Image


def parse_hex(value: str, default: tuple[int, int, int]) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if re.fullmatch(r"[0-9a-fA-F]{6}", value):
        return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))
    return default


def to_hex(rgb: tuple[int, int, int]) -> str:
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def make_qr(data: str, fill_color: str, back_color: str, target_size: int, margin: int = 0) -> Image.Image:
    margin = max(0, min(margin, target_size // 2 - 1))

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=0,
    )
    qr.add_data(data)
    qr.make(fit=True)

    modules = len(qr.get_matrix())
    inner = max(1, target_size - 2 * margin)
    box = max(1, inner // modules)
    size = box * modules

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img = img.resize((size, size), Image.NEAREST)

    if back_color == "transparent":
        canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    else:
        rgb = parse_hex(back_color, (255, 255, 255))
        canvas = Image.new("RGBA", (target_size, target_size), (*rgb, 255))

    offset = margin + (inner - size) // 2
    canvas.paste(img, (offset, offset))
    return canvas
