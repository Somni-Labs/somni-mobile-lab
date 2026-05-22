"""
Servo Latch Mechanism

SG90 servo-driven hook/cam latch. Default state: engaged (locked).
90-degree servo rotation disengages hook.

Returns:
  - Latch housing (bolts to shell, contains SG90 servo)
  - Latch hook (driven by servo)
  - Latch catch (mounted on opposing page)
  - Physical override finger tab on hook

All centered at origin; caller translates to final position.
"""

import cadquery as cq
from designs.common.constants import (
    SG90_W, SG90_D, SG90_H, SG90_FLANGE_W, SG90_FLANGE_H,
    LATCH_HOUSING_W, LATCH_HOUSING_D, LATCH_HOUSING_H,
    LATCH_HOOK_W, LATCH_HOOK_TRAVEL,
    WALL,
    M3_INSERT_DIA, M3_INSERT_DEPTH,
)


def build_latch_housing():
    """
    Build the latch housing that contains an SG90 servo.
    Open-top box with servo pocket, mounting holes on the bottom face.
    """
    housing_wall = 2
    # Outer box
    outer = (
        cq.Workplane("XY")
        .rect(LATCH_HOUSING_W, LATCH_HOUSING_D)
        .extrude(LATCH_HOUSING_H)
    )
    try:
        outer = outer.edges("|Z").fillet(1.5)
    except Exception:
        pass
    # Inner cavity for SG90
    inner = (
        cq.Workplane("XY")
        .workplane(offset=housing_wall)
        .rect(SG90_W + 1, SG90_D + 1)
        .extrude(LATCH_HOUSING_H)
    )
    housing = outer.cut(inner)
    # Servo flange ledge
    ledge = (
        cq.Workplane("XY")
        .workplane(offset=housing_wall + SG90_H - SG90_FLANGE_H)
        .rect(SG90_FLANGE_W + 1, SG90_D + 1)
        .extrude(SG90_FLANGE_H)
    )
    ledge_cut = (
        cq.Workplane("XY")
        .workplane(offset=housing_wall + SG90_H - SG90_FLANGE_H)
        .rect(SG90_FLANGE_W + 1, SG90_D - 1)
        .extrude(SG90_FLANGE_H)
    )
    housing = housing.cut(ledge_cut)
    # Mounting holes (2x M3 on bottom)
    for dx in [-LATCH_HOUSING_W / 2 + 5, LATCH_HOUSING_W / 2 - 5]:
        hole = (
            cq.Workplane("XY")
            .center(dx, 0)
            .circle(M3_INSERT_DIA / 2)
            .extrude(housing_wall + 1)
        )
        housing = housing.cut(hole)
    return housing


def build_latch_hook():
    """
    Build the latch hook arm that the servo drives.
    Includes a finger tab for manual override.
    """
    arm_thick = 3
    arm_h = 15
    # Main arm
    arm = (
        cq.Workplane("XY")
        .rect(LATCH_HOOK_W, arm_thick)
        .extrude(arm_h)
    )
    # Hook at bottom
    hook = (
        cq.Workplane("XY")
        .center(0, arm_thick / 2)
        .rect(LATCH_HOOK_W, LATCH_HOOK_TRAVEL + arm_thick)
        .extrude(arm_thick)
    )
    arm = arm.union(hook)
    # Finger tab (extends outward for manual release)
    tab = (
        cq.Workplane("XY")
        .workplane(offset=arm_h - 3)
        .center(0, -arm_thick)
        .rect(LATCH_HOOK_W - 4, 5)
        .extrude(3)
    )
    try:
        tab = tab.edges(">Z").fillet(1)
    except Exception:
        pass
    arm = arm.union(tab)
    # Servo shaft hole at top
    shaft_hole = (
        cq.Workplane("XY")
        .workplane(offset=arm_h - 5)
        .circle(1.5)  # servo horn shaft
        .extrude(6)
    )
    arm = arm.cut(shaft_hole)
    return arm


def build_latch_catch():
    """Build the catch ledge that the hook engages with on the opposing page."""
    catch = (
        cq.Workplane("XY")
        .rect(LATCH_HOOK_W, LATCH_HOOK_TRAVEL + 4)
        .extrude(WALL)
    )
    # Mounting holes
    for dx in [-LATCH_HOOK_W / 2 + 4, LATCH_HOOK_W / 2 - 4]:
        hole = (
            cq.Workplane("XY")
            .center(dx, 0)
            .circle(M3_INSERT_DIA / 2)
            .extrude(WALL + 1)
        )
        catch = catch.cut(hole)
    return catch


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    housing = build_latch_housing()
    show_object(housing, name="Latch Housing",
                options={"color": (0.4, 0.4, 0.4, 0.9)})
    hook = build_latch_hook().translate((0, 30, 0))
    show_object(hook, name="Latch Hook",
                options={"color": (0.8, 0.3, 0.3, 0.9)})
    catch = build_latch_catch().translate((0, 60, 0))
    show_object(catch, name="Latch Catch",
                options={"color": (0.3, 0.3, 0.8, 0.9)})
except ImportError:
    pass
