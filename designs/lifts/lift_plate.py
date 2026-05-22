"""
Lift Plates

Thin plates that sit under each device, pushed up by the cam mechanism.
Sized per device pocket. The plate has a tab that extends down through
the floor slot to contact the cam.
"""

import cadquery as cq
from designs.common.constants import (
    LAPTOP_W, LAPTOP_D,
    MONITOR_W, MONITOR_D,
    KB_W, KB_D,
    CAM_LIFT_HEIGHT,
    LIFT_SLOT_W,
)


def build_lift_plate(device_w, device_d, plate_thick=2, tab_w=None, tab_h=None):
    """
    Build a lift plate for a specific device.

    Args:
        device_w: width of the device pocket (plate is slightly smaller)
        device_d: depth of the device pocket
        plate_thick: plate thickness
        tab_w: width of the cam-contact tab (defaults to LIFT_SLOT_W - 2)
        tab_h: height of the tab extending below plate (defaults to CAM_LIFT_HEIGHT)
    """
    if tab_w is None:
        tab_w = LIFT_SLOT_W - 2
    if tab_h is None:
        tab_h = CAM_LIFT_HEIGHT

    pw = device_w - 4
    pd = device_d - 4

    plate = (
        cq.Workplane("XY")
        .rect(pw, pd)
        .extrude(plate_thick)
    )
    try:
        plate = plate.edges("|Z").fillet(2)
    except Exception:
        pass

    tab = (
        cq.Workplane("XY")
        .workplane(offset=-tab_h)
        .rect(tab_w, tab_w)
        .extrude(tab_h)
    )
    plate = plate.union(tab)

    return plate


def build_laptop_lift_plate():
    """Lift plate sized for Framework Laptop pocket."""
    return build_lift_plate(LAPTOP_W, LAPTOP_D)


def build_monitor_lift_plate():
    """Lift plate sized for 17" monitor pocket."""
    return build_lift_plate(MONITOR_W, MONITOR_D)


def build_keyboard_lift_plate():
    """Lift plate sized for keyboard pocket."""
    return build_lift_plate(KB_W, KB_D)


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    lp = build_laptop_lift_plate()
    show_object(lp, name="Laptop Lift Plate",
                options={"color": (0.6, 0.6, 0.8, 0.8)})
    mp = build_monitor_lift_plate().translate((0, 0, 30))
    show_object(mp, name="Monitor Lift Plate",
                options={"color": (0.6, 0.8, 0.6, 0.8)})
    kp = build_keyboard_lift_plate().translate((0, 0, 60))
    show_object(kp, name="Keyboard Lift Plate",
                options={"color": (0.8, 0.6, 0.6, 0.8)})
except ImportError:
    pass
