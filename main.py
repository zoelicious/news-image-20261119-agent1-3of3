#!/usr/bin/env python3
"""Entry point for make.fun news-image-20261119 (agent 1, 3/3).

Standard library only. The entry image is drawn in advance by draw.py
and shipped in this repository as entry.png; this program only copies
it to the output directory, so both grading runs write identical bytes.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst, os.path.getsize(dst), "bytes")


if __name__ == "__main__":
    sys.exit(main())
