"""
Page 1 Shell — Bottom (Power & Connectivity)

Sculpted organic shell with device pockets for:
  - Starlink Mini (left)
  - Starlink PSU (top-right)
  - Battery Bank (bottom-right, rotated 90deg)

Includes:
  - 4x mounting bosses for Starlink pedestal base
  - 2x mounting bosses for hinge servo mounts
  - 2x mounting bosses for latch catch positions
  - LED channel along inner rim perimeter
  - Cable pass-through hole for Starlink PSU connection
  - 15mm cable pass-through in +X wall

Loadable by cadquery-server via show_object().
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
    WALL, DIVIDER, CORNER_R,
    CASE_OUTER_W, CASE_OUTER_D, CASE_INNER_W, CASE_INNER_D,
    PAGE1_H, PAGE1_DEPTH,
    STARLINK_W, STARLINK_D, STARLINK_H,
    STARLINK_PSU_W, STARLINK_PSU_D, STARLINK_PSU_H,
    BATTERY_W, BATTERY_D, BATTERY_H,
    FOAM_BASE,
    CABLE_PASSTHROUGH_DIA,
    MOUNT_BOSS_OD,
)
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_chamfer_led_channels, add_side_ribs, add_logo_deboss,
)

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False


def build_page1():
    """Build the complete Page 1 shell with pockets and mounting features."""
    shell = build_sculpted_shell(CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)

    # --- Device pockets ---

    # Starlink Mini (left side, spanning nearly full depth)
    starlink_cx = -CASE_INNER_W / 2 + DIVIDER + STARLINK_W / 2
    starlink_cy = 0
    shell = cut_pocket(shell, starlink_cx, starlink_cy,
        STARLINK_W, STARLINK_D, STARLINK_H + FOAM_BASE, floor_z=WALL, corner_r=3)

    # Right column
    right_col_left = starlink_cx + STARLINK_W / 2 + DIVIDER

    # Starlink PSU (top-right)
    psu_cx = right_col_left + STARLINK_PSU_W / 2
    psu_cy = CASE_INNER_D / 2 - DIVIDER - STARLINK_PSU_D / 2
    shell = cut_pocket(shell, psu_cx, psu_cy,
        STARLINK_PSU_W, STARLINK_PSU_D, STARLINK_PSU_H + FOAM_BASE,
        floor_z=WALL, corner_r=2)

    # Battery Bank (bottom-right, rotated 90deg)
    bat_pocket_w = BATTERY_D   # rotated
    bat_pocket_d = BATTERY_W   # rotated
    bat_cx = right_col_left + bat_pocket_w / 2
    bat_cy = psu_cy - STARLINK_PSU_D / 2 - DIVIDER - bat_pocket_d / 2
    shell = cut_pocket(shell, bat_cx, bat_cy,
        bat_pocket_w, bat_pocket_d, BATTERY_H + FOAM_BASE,
        floor_z=WALL, corner_r=2)

    # --- Mounting bosses: Starlink pedestal (4x in floor, around Starlink pocket) ---
    pedestal_inset = 15  # inset from pocket edges
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        bx = starlink_cx + dx * (STARLINK_W / 2 - pedestal_inset)
        by = starlink_cy + dy * (STARLINK_D / 2 - pedestal_inset)
        shell = add_mounting_boss(shell, bx, by, z=0, height=WALL)

    # --- Mounting bosses: hinge servos (2x on -X spine wall) ---
    for servo_y_offset in [-CASE_OUTER_D / 6, CASE_OUTER_D / 6]:
        shell = add_mounting_boss(shell,
            x=-CASE_OUTER_W / 2 + WALL + MOUNT_BOSS_OD / 2,
            y=servo_y_offset,
            z=0, height=PAGE1_H - 2)

    # --- Mounting bosses: latch catches (2x on +X front edge) ---
    latch_spacing = CASE_OUTER_D / 3
    for i in range(2):
        ly = -CASE_OUTER_D / 3 + i * latch_spacing
        shell = add_mounting_boss(shell,
            x=CASE_OUTER_W / 2 - WALL - MOUNT_BOSS_OD / 2,
            y=ly,
            z=PAGE1_H - 8, height=6)

    # --- Cable pass-through (Starlink to PSU) ---
    passthrough_x = CASE_OUTER_W / 2  # +X wall
    passthrough_y = (starlink_cy + STARLINK_D / 2 + psu_cy - STARLINK_PSU_D / 2) / 2
    passthrough_z = WALL + FOAM_BASE + STARLINK_H / 2
    cable_hole = (
        cq.Workplane("YZ")
        .center(passthrough_y, passthrough_z)
        .circle(CABLE_PASSTHROUGH_DIA / 2)
        .extrude(WALL + 2, both=True)
    )
    shell = shell.cut(cable_hole)

    # --- LED channels on chamfer faces (top perimeter) ---
    shell = add_chamfer_led_channels(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)

    # --- Exterior side ribs (bold vertical lines on all 4 walls) ---
    shell = add_side_ribs(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)

    # --- Logo deboss on front face ---
    shell = add_logo_deboss(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)

    return shell


# --- Standalone preview for cadquery-server ---
if _cq_server and not os.environ.get('_CQ_ASSEMBLY'):
    page1 = build_page1()
    show_object(page1, name="Page 1 - Bottom (Power)",
                options={"color": (0.27, 0.51, 0.71, 0.7)})
