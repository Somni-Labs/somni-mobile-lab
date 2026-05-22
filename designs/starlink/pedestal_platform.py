"""
Starlink Pedestal Platform

The rising platform that carries the Starlink Mini.
Connects to the linear actuator via a tilt hinge along one long edge.
4 guide rod receptacles at corners for smooth vertical travel.
"""

import cadquery as cq
from designs.common.constants import (
    STARLINK_W, STARLINK_D,
    PEDESTAL_GUIDE_OD,
    HINGE_TUBE_OD,
)


def build_pedestal_platform():
    """
    Build the platform plate that rises on the pedestal.

    Features:
      - Flat plate matching Starlink Mini footprint
      - 4 corner guide rod receptacles (cylindrical sleeves)
      - Tilt hinge barrel along one long edge (for tilt servo)
      - Actuator push point at center (flat contact area)
    """
    plat_w = STARLINK_W - 5
    plat_d = STARLINK_D - 5
    plat_h = 4

    platform = (
        cq.Workplane("XY")
        .rect(plat_w, plat_d)
        .extrude(plat_h)
    )
    try:
        platform = platform.edges("|Z").fillet(2)
    except Exception:
        pass

    inset = 20
    sleeve_len = 20
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        rx = dx * (plat_w / 2 - inset)
        ry = dy * (plat_d / 2 - inset)
        sleeve = (
            cq.Workplane("XY")
            .workplane(offset=-sleeve_len)
            .center(rx, ry)
            .circle(PEDESTAL_GUIDE_OD / 2 + 2)
            .extrude(sleeve_len)
        )
        bore = (
            cq.Workplane("XY")
            .workplane(offset=-sleeve_len - 1)
            .center(rx, ry)
            .circle(PEDESTAL_GUIDE_OD / 2 + 0.2)
            .extrude(sleeve_len + plat_h + 2)
        )
        platform = platform.union(sleeve).cut(bore)

    hinge_barrel = (
        cq.Workplane("YZ")
        .center(-plat_d / 2, plat_h / 2)
        .circle(HINGE_TUBE_OD)
        .extrude(plat_w - 20)
        .translate((-plat_w / 2 + 10, 0, 0))
    )
    hinge_bore = (
        cq.Workplane("YZ")
        .center(-plat_d / 2, plat_h / 2)
        .circle(HINGE_TUBE_OD / 2 + 0.2)
        .extrude(plat_w - 18)
        .translate((-plat_w / 2 + 9, 0, 0))
    )
    platform = platform.union(hinge_barrel).cut(hinge_bore)

    return platform


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    platform = build_pedestal_platform()
    show_object(platform, name="Pedestal Platform",
                options={"color": (0.3, 0.5, 0.7, 0.9)})
except ImportError:
    pass
