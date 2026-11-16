#!/usr/bin/env python3
"""Share one investigation between formats. usage: derive.py <from-slug> <to-slug>
Copies work/<from>/research.json and img/ to work/<to>/ so both scripts cite the same sources and pictures.
Typical use: research the long video (<slug>-largo, up to 30 pictures), then derive the Short (<slug>) from it."""
import os, shutil, sys
from common import path, die

if len(sys.argv) < 3:
    die(__doc__)
src = path("work", sys.argv[1], "x")[:-2]; dst = path("work", sys.argv[2], "x")[:-2]
os.path.exists(os.path.join(src, "research.json")) or die("run wiki.py for the source slug first")
shutil.copy(os.path.join(src, "research.json"), os.path.join(dst, "research.json"))
if os.path.isdir(os.path.join(src, "img")):
    shutil.copytree(os.path.join(src, "img"), os.path.join(dst, "img"), dirs_exist_ok=True)
print(f"work/{sys.argv[2]} ready with the research and pictures of {sys.argv[1]}")
