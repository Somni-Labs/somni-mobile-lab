"""
Hinge Servo Mount

MG996R servo mount bracket that bolts to the Page 1 spine wall.
Includes a spur gear that meshes with the gear sector on the hinge knuckle.
"""

import cadquery as cq
import math
from designs.common.constants import (
    MG996R_W, MG996R_D, MG996R_H, MG996R_FLANGE_W, MG996R_FLANGE_H,
    MG996R_SHAFT_OFFSET,
    WALL,
    M3_INSERT_DIA,
    HINGE_KNUCKLE_OD,
)


def build_servo_mount():
    """
    Build the MG996R servo mount bracket.
    The bracket holds the servo body and provides mounting tabs with M3 holes.
    """
    bracket_wall = 3
    # Outer box sized to hold MG996R
    bw = MG996R_W + bracket_wall * 2
    bd = MG996R_D + bracket_wall * 2
    bh = MG996R_H + bracket_wall
    outer = (
        cq.Workplane("XY")
        .rect(bw, bd)
        .extrude(bh)
    )
    # Servo cavity
    inner = (
        cq.Workplane("XY")
        .workplane(offset=bracket_wall)
        .rect(MG996R_W + 0.5, MG996R_D + 0.5)
        .extrude(MG996R_H + 1)
    )
    bracket = outer.cut(inner)
    # Flange slots
    flange_slot = (
        cq.Workplane("XY")
        .workplane(offset=bracket_wall + MG996R_H - MG996R_FLANGE_H - 1)
        .rect(MG996R_FLANGE_W + 1, MG996R_D - 2)
        .extrude(MG996R_FLANGE_H + 1)
    )
    bracket = bracket.cut(flange_slot)
    # Shaft hole through top
    shaft_hole = (
        cq.Workplane("XY")
        .workplane(offset=bh - 1)
        .center(-MG996R_W / 2 + MG996R_SHAFT_OFFSET, 0)
        .circle(5)  # clearance for servo horn
        .extrude(bracket_wall + 2)
    )
    bracket = bracket.cut(shaft_hole)
    # Mounting tabs with M3 holes (2x, extending from sides)
    for side in [-1, 1]:
        tab = (
            cq.Workplane("XY")
            .center(side * (bw / 2 + 8), 0)
            .rect(16, bd)
            .extrude(bracket_wall)
        )
        bracket = bracket.union(tab)
        hole = (
            cq.Workplane("XY")
            .center(side * (bw / 2 + 8), 0)
            .circle(M3_INSERT_DIA / 2)
            .extrude(bracket_wall + 1)
        )
        bracket = bracket.cut(hole)
    return bracket


def build_spur_gear(n_teeth=12, module_mm=1.5, thickness=8, bore_dia=6):
    """
    Build a simple spur gear for the hinge servo.
    Approximate gear teeth as rectangular profiles (good enough for 3D printing).
    """
    pitch_r = n_teeth * module_mm / 2
    tooth_h = module_mm * 2.25
    outer_r = pitch_r + module_mm
    inner_r = pitch_r - module_mm * 1.25
    # Base disc
    gear = (
        cq.Workplane("XY")
        .circle(inner_r)
        .extrude(thickness)
    )
    # Teeth
    tooth_w = module_mm * 1.4  # approximate
    for i in range(n_teeth):
        angle = i * 360 / n_teeth
        angle_rad = math.radians(angle)
        tx = pitch_r * math.cos(angle_rad)
        ty = pitch_r * math.sin(angle_rad)
        tooth = (
            cq.Workplane("XY")
            .center(tx, ty)
            .rect(tooth_w, tooth_h)
            .extrude(thickness)
        )
        tooth = tooth.rotate((tx, ty, 0), (tx, ty, 1), math.degrees(math.atan2(ty, tx)) + 90)
        gear = gear.union(tooth)
    # Bore hole
    bore = (
        cq.Workplane("XY")
        .circle(bore_dia / 2)
        .extrude(thickness + 1)
    )
    gear = gear.cut(bore)
    return gear


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    mount = build_servo_mount()
    show_object(mount, name="Hinge Servo Mount (MG996R)",
                options={"color": (0.4, 0.4, 0.4, 0.9)})
    gear = build_spur_gear().translate((60, 0, 0))
    show_object(gear, name="Spur Gear",
                options={"color": (0.6, 0.6, 0.3, 0.9)})
except ImportError:
    pass
