"""
Mobile Lab Case V2 — Full Assembly Preview

Composes all subsystems into a single cadquery-server view.
Three pages stacked with visual gaps, hinges attached,
Starlink pedestal in Page 1, electronics bay in Page 2 spine,
latches on front edge.

This is the file symlinked by cadquery-server git-sync.
"""

# Bootstrap: add repo root to sys.path so package imports work
# when loaded by cadquery-server from a symlink
import sys
import os
_this_dir = os.path.dirname(os.path.realpath(__file__))
_repo_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# Suppress subsystem standalone previews when importing as dependencies
os.environ['_CQ_ASSEMBLY'] = '1'

import cadquery as cq

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False

from designs.shell.page1_shell import build_page1
from designs.shell.page2_shell import build_page2
from designs.shell.page3_shell import build_page3
from designs.hinge.hinge_knuckles import build_hinge_knuckles
from designs.hinge.latch_mechanism import build_latch_housing, build_latch_catch
from designs.hinge.hinge_servo_mount import build_servo_mount
from designs.starlink.pedestal_base import build_pedestal_base
from designs.starlink.pedestal_platform import build_pedestal_platform
from designs.electronics.electronics_bay import build_electronics_bay
from designs.common.constants import (
    CASE_OUTER_W, CASE_OUTER_D,
    PAGE1_H, PAGE2_H, PAGE3_H,
)

# Clean up so standalone modules loaded later in the same process aren't affected
del os.environ['_CQ_ASSEMBLY']


# ============================================================
# Build all pages
# ============================================================
page1 = build_page1()
page2 = build_page2()
page3 = build_page3()

# ============================================================
# Add hinge knuckles to each page
# ============================================================
# Page 1 top: even knuckles with gear sector
p1_hinges = build_hinge_knuckles(PAGE1_H, parity="even", gear_sector_index=2)
page1 = page1.union(p1_hinges)

# Page 2 bottom: odd knuckles
p2_hinges_bot = build_hinge_knuckles(0, parity="odd")
# Page 2 top: even knuckles with gear sector
p2_hinges_top = build_hinge_knuckles(PAGE2_H, parity="even", gear_sector_index=2)
page2 = page2.union(p2_hinges_bot).union(p2_hinges_top)

# Page 3 bottom: odd knuckles
p3_hinges = build_hinge_knuckles(0, parity="odd")
page3 = page3.union(p3_hinges)

if _cq_server:
    # ============================================================
    # Show in stacked assembly view
    # ============================================================
    show_object(page1, name="Page 1 - Bottom (Power)",
                options={"color": (0.27, 0.51, 0.71, 0.7)})

    p2_z = PAGE1_H + 2  # 2mm visual gap
    page2_view = page2.translate((0, 0, p2_z))
    show_object(page2_view, name="Page 2 - Middle (Screens)",
                options={"color": (0.56, 0.74, 0.56, 0.7)})

    p3_z = p2_z + PAGE2_H + 2
    page3_view = page3.translate((0, 0, p3_z))
    show_object(page3_view, name="Page 3 - Top (Accessories)",
                options={"color": (1.0, 0.63, 0.48, 0.7)})

    # ============================================================
    # Show key subsystems as separate objects
    # ============================================================
    # Starlink pedestal base (inside Page 1)
    pedestal = build_pedestal_base()
    pedestal_view = pedestal.translate((0, 0, 3))  # on Page 1 floor
    show_object(pedestal_view, name="Starlink Pedestal Base",
                options={"color": (0.3, 0.3, 0.6, 0.5)})

    # Starlink platform (raised position for visual)
    platform = build_pedestal_platform()
    platform_view = platform.translate((0, 0, PAGE1_H + 20))  # shown in raised position
    show_object(platform_view, name="Starlink Platform (raised)",
                options={"color": (0.3, 0.5, 0.7, 0.5)})

    # Electronics bay (in Page 2 spine)
    ebay = build_electronics_bay()
    ebay_view = ebay.rotate((0, 0, 0), (0, 1, 0), 90).translate((
        -CASE_OUTER_W / 2 + 5, 0, p2_z + PAGE2_H / 2
    ))
    show_object(ebay_view, name="Electronics Bay",
                options={"color": (0.2, 0.2, 0.2, 0.6)})
