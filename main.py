#!/usr/bin/env python3
"""Verify entry.png is a valid 1024x1024 PNG and copy it to the output dir.

Uses only the Python standard library.

Checks:
  - PNG signature
  - IHDR width/height == 1024
  - IHDR sanity (bit depth, color type)
  - IEND chunk present
  - file size <= 1 MiB
"""

import os
import struct
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_SIZE = 1024 * 1024  # 1 MiB
WIDTH = 1024
HEIGHT = 1024


def verify_png(path):
    """Return (errors, size). errors is a list of human-readable problems."""
    errors = []

    with open(path, "rb") as f:
        data = f.read()

    size = len(data)

    if size > MAX_SIZE:
        errors.append("size %d exceeds 1 MiB limit" % size)

    if len(data) < 8:
        errors.append("file too small to be a PNG")
        return errors, size

    if data[:8] != PNG_SIGNATURE:
        errors.append("invalid PNG signature")
        return errors, size

    if len(data) < 33:
        errors.append("missing IHDR chunk")
        return errors, size

    # IHDR chunk: length(4) + type(4) + data(13) + crc(4)
    length, = struct.unpack(">I", data[8:12])
    chunk_type = data[12:16]
    if chunk_type != b"IHDR":
        errors.append("first chunk is not IHDR")
        return errors, size
    if length != 13:
        errors.append("IHDR length is not 13")
        return errors, size

    ihdr = data[16:29]
    if len(ihdr) < 13:
        errors.append("truncated IHDR data")
        return errors, size

    width, height, bit_depth, color_type, comp, filt, interlace = struct.unpack(
        ">IIBBBBB", ihdr
    )

    if width != WIDTH:
        errors.append("width is %d, expected %d" % (width, WIDTH))
    if height != HEIGHT:
        errors.append("height is %d, expected %d" % (height, HEIGHT))
    if bit_depth != 8:
        errors.append("bit depth is %d, expected 8" % bit_depth)
    if color_type not in (2, 6):
        errors.append("unexpected color type %d" % color_type)
    if comp != 0:
        errors.append("unsupported compression method %d" % comp)
    if filt != 0:
        errors.append("unsupported filter method %d" % filt)
    if interlace != 0:
        errors.append("unsupported interlace method %d" % interlace)

    # IEND chunk must be present as the final 12-byte chunk (length 0).
    if len(data) < 12:
        errors.append("missing IEND chunk")
    else:
        iend_len, = struct.unpack(">I", data[-12:-8])
        iend_type = data[-8:-4]
        if iend_type != b"IEND":
            errors.append("missing IEND chunk")
        elif iend_len != 0:
            errors.append("IEND length is not 0")

    return errors, size


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)

    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

    errors, size = verify_png(src)
    if errors:
        for e in errors:
            sys.stderr.write("error: %s\n" % e)
        return 1

    dst = os.path.join(out_dir, "entry.png")
    with open(src, "rb") as f:
        data = f.read()
    with open(dst, "wb") as f:
        f.write(data)

    print("%s %d" % (dst, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())