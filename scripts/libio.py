"""Shared save helper for scripts that edit lib/lcsc.kicad_sym with kiutils.

kiutils writes the old (KiCad 6) syntax. If the file was read in native KiCad 10 format its header
still says so, which would mix formats; force the old header on write. scripts/finalize_lib.py then
upgrades the finished library to native KiCad 10 format (the form that is committed).
"""


def save(lib, path):
    lib.version = "20211014"
    lib.generator = "kiutils"
    lib.to_file(path)
