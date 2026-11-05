#!/bin/bash
# Setup script for the Claude Code cloud environment (paste into the
# environment's "Setup script" field). Runs as root on Ubuntu 24.04
# before each new session; the result is cached for about 7 days.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

# KiCad 10 stable from the official KiCad PPA (gives kicad-cli),
# plus poppler-utils for rendering exported PDFs to PNG.
apt-get update
apt-get install -y software-properties-common
add-apt-repository --yes ppa:kicad/kicad-10.0-releases
apt-get update
apt-get install -y --no-install-recommends kicad poppler-utils
# Standard symbol and footprint libraries (skip the large 3D models
# to keep setup under the 5-minute cache limit).
apt-get install -y --no-install-recommends kicad-symbols kicad-footprints || \
  echo "KiCad library packages not found; continuing without them"

# Python tools for importing LCSC parts and generating schematics.
pip install --break-system-packages easyeda2kicad kiutils

kicad-cli version
