"""
Starlink Pedestal Base

Mounts inside Page 1 beneath the Starlink pocket. Contains:
  - Central linear actuator mount (vertical cylinder bore)
  - 4x guide rail bushings at corners for level travel
  - M3 mounting holes to bolt onto Page 1 floor bosses
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
    STARLINK_W, STARLINK_D,
    PEDESTAL_STROKE, PEDESTAL_ACTUATOR_DIA, PEDESTAL_ACTUATOR_LEN,
    PEDESTAL_GUIDE_OD, PEDESTAL_GUIDE_BUSHING_OD, PEDESTAL_GUIDE_BUSHING_LEN,
    M3_CLEARANCE_DIA,
    WALL,
    TOL,
)

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False


def build_pedestal_base():
    """
    Build the pedestal base plate that sits on the Page 1 floor.

    The base plate is a flat slab with:
      - A central bore for the linear actuator
      - 4 corner bushings for guide rails
      - 4 M3 bolt holes for mounting to shell bosses
    """
    base_w = STARLINK_W - 10
    base_d = STARLINK_D - 10
    base_h = 5

    plate = (
        cq.Workplane("XY")
        .rect(base_w, base_d)
        .extrude(base_h)
    )
    try:
        plate = plate.edges("|Z").fillet(3)
    except Exception:
        pass

    actuator_bore = (
        cq.Workplane("XY")
        .circle(PEDESTAL_ACTUATOR_DIA / 2 + 0.5)
        .extrude(base_h + 1)
    )
    plate = plate.cut(actuator_bore)

    retention = (
        cq.Workplane("XY")
        .workplane(offset=base_h)
        .circle(PEDESTAL_ACTUATOR_DIA / 2 + 3)
        .circle(PEDESTAL_ACTUATOR_DIA / 2 + 0.5)
        .extrude(3)
    )
    plate = plate.union(retention)

    inset = 20
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        bx = dx * (base_w / 2 - inset)
        by = dy * (base_d / 2 - inset)
        bushing = (
            cq.Workplane("XY")
            .workplane(offset=base_h)
            .center(bx, by)
            .circle(PEDESTAL_GUIDE_BUSHING_OD / 2)
            .extrude(PEDESTAL_GUIDE_BUSHING_LEN)
        )
        bore = (
            cq.Workplane("XY")
            .center(bx, by)
            .circle(PEDESTAL_GUIDE_OD / 2 + 0.2)
            .extrude(base_h + PEDESTAL_GUIDE_BUSHING_LEN + 1)
        )
        plate = plate.union(bushing).cut(bore)

    pedestal_inset = 15
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        hx = dx * (base_w / 2 - pedestal_inset)
        hy = dy * (base_d / 2 - pedestal_inset)
        hole = (
            cq.Workplane("XY")
            .center(hx, hy)
            .circle(M3_CLEARANCE_DIA / 2)
            .extrude(base_h + 1)
        )
        plate = plate.cut(hole)

    return plate


# --- Standalone preview for cadquery-server ---
if _cq_server and not os.environ.get('_CQ_ASSEMBLY'):
    base = build_pedestal_base()
    show_object(base, name="Pedestal Base",
                options={"color": (0.3, 0.3, 0.6, 0.9)})
