"""
Starlink Tilt Linkage

MG996R servo mount on the platform underside + printed linkage arm
that drives the tilt hinge. Tilt range: 0-45 degrees.
"""

import os
import cadquery as cq
from designs.common.constants import (
    MG996R_W, MG996R_D, MG996R_H,
    M3_CLEARANCE_DIA,
)


def build_tilt_servo_mount():
    """
    Build the MG996R tilt servo mount bracket.
    Mounts on the underside of the pedestal platform.
    """
    bracket_wall = 2.5
    bw = MG996R_W + bracket_wall * 2
    bd = MG996R_D + bracket_wall * 2
    bh = MG996R_H + bracket_wall

    mount = (
        cq.Workplane("XY")
        .rect(bw, bd)
        .extrude(bh)
    )
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=bracket_wall)
        .rect(MG996R_W + 0.5, MG996R_D + 0.5)
        .extrude(MG996R_H + 1)
    )
    mount = mount.cut(cavity)
    for dx in [-bw / 2 + 5, bw / 2 - 5]:
        hole = (
            cq.Workplane("XY")
            .center(dx, 0)
            .circle(M3_CLEARANCE_DIA / 2)
            .extrude(bracket_wall + 1)
        )
        mount = mount.cut(hole)
    return mount


def build_linkage_arm(length=40, width=10, thickness=5, hole_dia=3):
    """
    Build a simple linkage arm connecting the tilt servo horn to the platform hinge.
    Two holes: one for servo horn, one for hinge pin.
    """
    arm = (
        cq.Workplane("XY")
        .rect(length, width)
        .extrude(thickness)
    )
    try:
        arm = arm.edges("|Z").fillet(width / 2 - 0.5)
    except Exception:
        pass
    h1 = (
        cq.Workplane("XY")
        .center(-length / 2 + width / 2, 0)
        .circle(hole_dia / 2)
        .extrude(thickness + 1)
    )
    h2 = (
        cq.Workplane("XY")
        .center(length / 2 - width / 2, 0)
        .circle(hole_dia / 2)
        .extrude(thickness + 1)
    )
    arm = arm.cut(h1).cut(h2)
    return arm


# --- Standalone preview ---
if not os.environ.get('_CQ_ASSEMBLY'):
    try:
        from cq_server.ui import ui, show_object
        mount = build_tilt_servo_mount()
        show_object(mount, name="Tilt Servo Mount",
                    options={"color": (0.4, 0.4, 0.5, 0.9)})
        arm = build_linkage_arm().translate((0, 40, 0))
        show_object(arm, name="Tilt Linkage Arm",
                    options={"color": (0.6, 0.4, 0.3, 0.9)})
    except ImportError:
        pass
