"""
Recessed Button Housing

Flush-mount housing for 12mm push button with LED ring.
Mounts on the Page 2 spine wall next to the USB-C port.
"""

import cadquery as cq
from designs.common.constants import BUTTON_DIA, BUTTON_RECESS, WALL


def build_button_mount():
    """
    Build the recessed button housing.
    A short cylinder with a central bore for the button,
    and a lip that sits flush with the shell surface.
    """
    outer_dia = BUTTON_DIA + 6
    housing_h = WALL + BUTTON_RECESS + 2

    housing = (
        cq.Workplane("XY")
        .circle(outer_dia / 2)
        .extrude(housing_h)
    )
    bore = (
        cq.Workplane("XY")
        .circle(BUTTON_DIA / 2 + 0.2)
        .extrude(housing_h + 1)
    )
    housing = housing.cut(bore)
    lip = (
        cq.Workplane("XY")
        .workplane(offset=housing_h - BUTTON_RECESS)
        .circle(outer_dia / 2 + 2)
        .circle(outer_dia / 2)
        .extrude(BUTTON_RECESS)
    )
    housing = housing.union(lip)
    return housing


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    btn = build_button_mount()
    show_object(btn, name="Button Mount",
                options={"color": (0.2, 0.2, 0.2, 0.9)})
except ImportError:
    pass
