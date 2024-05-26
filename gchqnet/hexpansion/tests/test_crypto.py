from gchqnet.hexpansion.crypto import badge_response_calculation, generate_diversified_key


def test_generate_diversified_key() -> None:
    key = generate_diversified_key(
        b"a" * 64,
        [0x04] * 32,
        0,
    )
    assert key == b"m\x1b:\x83i\xde2iE\xe6\xf7\x02\xd4/\x0c4VH\x91\xc7\xa15\n-\\\x12'\x96\xd7\xeb\xc2S"


def test_badge_response_calculation__good() -> None:
    # check against a set of data provided by a real badge
    badge_mac = "DC-54-75-D8-6E-88"

    serial = b"\x01#]\xc2Q-\xb7a\xee"
    random = b"N\xab\x86\xb4\xfc\xe89`\\\xb5\xe0\x9f\xb8H`\xdbN_\xe3g\x81\x86\xff\x17\xfc\x88\xb0.\xea\xf4#\xcb"
    response = (
        b"b\x84\xa1\xf1E\xdb\xde\xdb\xc6\xf7\x92\xe1\xed*\xc1\x81E\xc1\xe2O\x81_\xf0\xe6_\xa9\x06\x00\x8b_\xe4\xbb"
    )

    key_0 = bytearray.fromhex("8" * 64)

    expected = badge_response_calculation(serial, random, badge_mac, key_0)

    assert response == expected


def test_badge_response_calculation__bad() -> None:
    # check against a set of data provided by a real badge
    badge_mac = "DC-54-75-D8-6E-88"

    serial = b"\x01#]\xc2Q-\xb7a\xee"
    random = b"N\xab\x86\xb4\xfc\xe89`\\\xb5\xe0\x9f\xb8H`\xdbN_\xe3g\x81\x86\xff\x17\xfc\x88\xb0.\xea\xf4#\xcb"
    response = b"a" * 64

    key_0 = bytearray.fromhex("8" * 64)

    expected = badge_response_calculation(serial, random, badge_mac, key_0)

    assert response != expected
