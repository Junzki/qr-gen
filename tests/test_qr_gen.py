from qr_gen.core import make_qr, parse_hex, to_hex


def test_parse_hex_with_hash():
    assert parse_hex("#ff0000", (0, 0, 0)) == (255, 0, 0)


def test_parse_hex_without_hash():
    assert parse_hex("00ff00", (0, 0, 0)) == (0, 255, 0)


def test_parse_hex_invalid_returns_default():
    assert parse_hex("not-a-color", (1, 2, 3)) == (1, 2, 3)


def test_to_hex():
    assert to_hex((255, 0, 0)) == "#ff0000"
    assert to_hex((0, 16, 255)) == "#0010ff"


def test_make_qr_size_and_mode():
    img = make_qr("https://example.com", "#000000", "#ffffff", 256)
    assert img.size == (256, 256)
    assert img.mode == "RGBA"


def test_make_qr_transparent_background():
    img = make_qr("hello", "#000000", "transparent", 128)
    assert img.size == (128, 128)
    assert img.mode == "RGBA"
