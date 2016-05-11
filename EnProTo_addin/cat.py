# -*- coding: utf-8 -*-
import glob

files = glob.glob("mod/*.py")

with open("Install/EnProTo_addin_addin.py", "wb") as outfile:
    for f in files:
        with open(f, "rb") as infile:
            outfile.write(infile.read())