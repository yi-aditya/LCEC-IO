#!/usr/bin/env python3
"""Last step of the library pipeline: upgrade lib/lcsc.kicad_sym to native KiCad 10 format.

Run after import_lcsc.py, make_manual_parts.py, fix_symbols.py and relayout_symbols.py.
Committing the native file means the library KiCad loads is byte-for-byte what the schematics embed
(no 'symbol does not match library' warnings). The other scripts still read it with kiutils.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "lib", "lcsc.kicad_sym")

r = subprocess.run(["kicad-cli", "sym", "upgrade", "--force", LIB], capture_output=True, text=True)
print((r.stdout + r.stderr).strip())
sys.exit(r.returncode)
