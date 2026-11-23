# Notes

This program verifies that entry.png is a valid 1024x1024 PNG (signature, IHDR width/height, IEND chunk, and 1 MiB size limit) using only the Python standard library.
It then copies entry.png into the directory from the MAKEFUN_OUTPUT_DIR environment variable (default /output) and prints the destination path and byte size.
