"""
Electronics Bay Enclosure

Enclosed box (120x40x30mm internal) that mounts in the Page 2 spine wall.
Contains ESP32, PCA9685, TP4056, boost converter, LiPo cell.
Removable lid with M2 screws. USB-C port cutout on one end.
"""

import os
import sys
import cadquery as cq

# Bootstrap sys.path for cadquery-server symlink loading
_this_dir = os.path.dirname(os.path.realpath(__file__))
_repo_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from designs.common.constants import (
    EBAY_INNER_W, EBAY_INNER_D, EBAY_INNER_H, EBAY_WALL,
    EBAY_LID_SCREW,
    M3_CLEARANCE_DIA,
)

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False


def build_electronics_bay():
    """Build the electronics bay box (without lid)."""
    ow = EBAY_INNER_W + EBAY_WALL * 2
    od = EBAY_INNER_D + EBAY_WALL * 2
    oh = EBAY_INNER_H + EBAY_WALL

    box = (
        cq.Workplane("XY")
        .rect(ow, od)
        .extrude(oh)
    )
    try:
        box = box.edges("|Z").fillet(2)
    except Exception:
        pass
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=EBAY_WALL)
        .rect(EBAY_INNER_W, EBAY_INNER_D)
        .extrude(EBAY_INNER_H + 1)
    )
    box = box.cut(cavity)

    usbc_w = 10
    usbc_h = 4
    usbc_cutout = (
        cq.Workplane("XZ")
        .center(-ow / 2, EBAY_WALL + EBAY_INNER_H / 2)
        .rect(usbc_h, usbc_w)
        .extrude(EBAY_WALL + 2, both=True)
    )
    usbc_cutout2 = (
        cq.Workplane("YZ")
        .center(-od / 2, EBAY_WALL + EBAY_INNER_H / 2)
        .rect(usbc_h, usbc_w)
        .extrude(EBAY_WALL + 2, both=True)
    )
    box = box.cut(usbc_cutout2)

    for dx in [-EBAY_INNER_W / 2 + 5, EBAY_INNER_W / 2 - 5]:
        for dy in [-EBAY_INNER_D / 2 + 5, EBAY_INNER_D / 2 - 5]:
            boss = (
                cq.Workplane("XY")
                .workplane(offset=oh - 3)
                .center(dx, dy)
                .circle(EBAY_LID_SCREW + 2)
                .extrude(3)
            )
            hole = (
                cq.Workplane("XY")
                .workplane(offset=oh - 4)
                .center(dx, dy)
                .circle(EBAY_LID_SCREW / 2)
                .extrude(5)
            )
            box = box.union(boss).cut(hole)

    for dx in [-EBAY_INNER_W / 2 + 8, EBAY_INNER_W / 2 - 8]:
        for dy in [-EBAY_INNER_D / 2 + 8, EBAY_INNER_D / 2 - 8]:
            hole = (
                cq.Workplane("XY")
                .center(dx, dy)
                .circle(M3_CLEARANCE_DIA / 2)
                .extrude(EBAY_WALL + 1)
            )
            box = box.cut(hole)

    return box


def build_electronics_bay_lid():
    """Build the removable lid for the electronics bay."""
    ow = EBAY_INNER_W + EBAY_WALL * 2
    od = EBAY_INNER_D + EBAY_WALL * 2
    lid_h = EBAY_WALL

    lid = (
        cq.Workplane("XY")
        .rect(ow, od)
        .extrude(lid_h)
    )
    try:
        lid = lid.edges("|Z").fillet(2)
    except Exception:
        pass
    lip = (
        cq.Workplane("XY")
        .workplane(offset=-2)
        .rect(EBAY_INNER_W - 0.5, EBAY_INNER_D - 0.5)
        .extrude(2)
    )
    lid = lid.union(lip)
    for dx in [-EBAY_INNER_W / 2 + 5, EBAY_INNER_W / 2 - 5]:
        for dy in [-EBAY_INNER_D / 2 + 5, EBAY_INNER_D / 2 - 5]:
            hole = (
                cq.Workplane("XY")
                .workplane(offset=-1)
                .center(dx, dy)
                .circle(EBAY_LID_SCREW / 2 + 0.2)
                .extrude(lid_h + 3)
            )
            lid = lid.cut(hole)
    return lid


# --- Standalone preview for cadquery-server ---
if _cq_server and not os.environ.get('_CQ_ASSEMBLY'):
    bay = build_electronics_bay()
    show_object(bay, name="Electronics Bay",
                options={"color": (0.3, 0.3, 0.3, 0.9)})
    lid = build_electronics_bay_lid().translate((0, 0, EBAY_INNER_H + EBAY_WALL + 5))
    show_object(lid, name="Bay Lid",
                options={"color": (0.5, 0.5, 0.5, 0.8)})
