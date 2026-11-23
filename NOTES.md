# Notes

entry.png is a Monday 23 November 2026 newspaper front page with a winner-pattern headline featuring 35 date-checked stories across 9 regions, verified by main.py.

This program verifies that entry.png is a valid 1024x1024 PNG (signature, IHDR width/height, IEND chunk, and 1 MiB size limit) using only the Python standard library.
It then copies entry.png into the directory from the MAKEFUN_OUTPUT_DIR environment variable (default /output) and prints the destination path and byte size.
