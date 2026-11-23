#!/usr/bin/env python3
"""Copy entry.png to the output directory, verifying it is a valid 1024x1024 PNG."""

import os
import struct
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
MAX_BYTES = 1 * 1024 * 1024  # 1 MiB


def verify_png(path):
    with open(path, "rb") as f:
        # PNG signature
        if f.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError("not a valid PNG: bad signature")

        # Byte size check
        size = os.path.getsize(path)
        if size > MAX_BYTES:
            raise ValueError(f"PNG too large: {size} bytes (max {MAX_BYTES})")

        saw_ihdr = False
        saw_iend = False
        pos = 8
        while pos < size:
            f.seek(pos)
            length_bytes = f.read(4)
            if len(length_bytes) != 4:
                raise ValueError("not a valid PNG: truncated chunk length")
            (length,) = struct.unpack(">I", length_bytes)
            chunk_type = f.read(4)
            if len(chunk_type) != 4:
                raise ValueError("not a valid PNG: truncated chunk type")
            if not saw_ihdr:
                if chunk_type != b"IHDR":
                    raise ValueError("not a valid PNG: IHDR not first chunk")
                data = f.read(13)
                if len(data) != 13:
                    raise ValueError("not a valid PNG: truncated IHDR")
                width, height = struct.unpack(">II", data[:8])
                if width != 1024 or height != 1024:
                    raise ValueError(f"not 1024x1024: got {width}x{height}")
                saw_ihdr = True
            if chunk_type == b"IEND":
                saw_iend = True
                break
            pos = pos + 12 + length
        if not saw_ihdr:
            raise ValueError("not a valid PNG: missing IHDR")
        if not saw_iend:
            raise ValueError("not a valid PNG: missing IEND")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    try:
        verify_png(SRC)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    dest = os.path.join(out_dir, "entry.png")
    with open(SRC, "rb") as src, open(dest, "wb") as dst:
        dst.write(src.read())
    print(f"{dest} {os.path.getsize(dest)}")


if __name__ == "__main__":
    main()
