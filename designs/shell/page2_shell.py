"""
Page 2 Shell — Middle (Screens & Compute)

Sculpted organic shell with device pockets for:
  - 17" Portable Monitor (full width, shallow tier)
  - Framework Laptop + iPad (stacked sub-pocket, deeper tier)

Includes:
  - Carry handle on -X (spine) edge
  - Electronics bay cutout in spine wall
  - 2x mounting bosses for cam lifts (monitor + laptop)
  - 4x mounting bosses for electronics bay
  - Spine ridge LED channels on both outer faces

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
    PAGE2_H, PAGE2_DEPTH,
    MONITOR_W, MONITOR_D, MONITOR_H,
    LAPTOP_W, LAPTOP_D, LAPTOP_H,
    IPAD_W, IPAD_D, IPAD_H,
    FOAM_BASE,
    HANDLE_W, HANDLE_H, HANDLE_THICK, HANDLE_FILLET,
    EBAY_INNER_W, EBAY_INNER_D, EBAY_INNER_H, EBAY_WALL,
    MOUNT_BOSS_OD,
    RIDGE_H, RIDGE_W,
)
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_ridge, add_chamfer_led_channels,
)

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False


def build_carry_handle():
    """Build the ergonomic U-shaped carry handle for the spine."""
    outer = (
        cq.Workplane("XY")
        .rect(HANDLE_H, HANDLE_W + HANDLE_THICK * 2)
        .extrude(HANDLE_THICK)
    )
    try:
        outer = outer.edges("|Z").fillet(min(HANDLE_FILLET, HANDLE_THICK - 0.1))
    except Exception:
        pass
    inner = (
        cq.Workplane("XY")
        .rect(HANDLE_H - HANDLE_THICK * 2, HANDLE_W)
        .extrude(HANDLE_THICK)
    )
    handle = outer.cut(inner)
    return handle


def build_page2():
    """Build the complete Page 2 shell with pockets, handle, and mounting features."""
    shell = build_sculpted_shell(CASE_OUTER_W, CASE_OUTER_D, PAGE2_H)

    # --- Device pockets ---

    # Tier 1: 17" Monitor (full page, shallow)
    mon_pocket_h = FOAM_BASE + MONITOR_H
    shell = cut_pocket(shell, 0, 0,
        MONITOR_W, MONITOR_D, mon_pocket_h, floor_z=WALL, corner_r=3)

    # Tier 2: Laptop + iPad stacked (centered, deeper)
    stack_w = max(LAPTOP_W, IPAD_W)
    stack_d = max(LAPTOP_D, IPAD_D)
    stack_h = FOAM_BASE + MONITOR_H + 2 + LAPTOP_H + IPAD_H
    shell = cut_pocket(shell, 0, 0,
        stack_w, stack_d, stack_h, floor_z=WALL, corner_r=3)

    # --- Carry handle on -X spine ---
    handle = build_carry_handle()
    handle = (
        handle
        .rotate((0, 0, 0), (0, 1, 0), 90)
        .translate((-CASE_OUTER_W / 2 - HANDLE_H / 2, 0, PAGE2_H / 2))
    )
    shell = shell.union(handle)

    # --- Electronics bay cutout in spine wall ---
    ebay_cutout = (
        cq.Workplane("XY")
        .workplane(offset=WALL)
        .center(-CASE_OUTER_W / 2 + WALL / 2, 0)
        .rect(WALL + 2, EBAY_INNER_W + EBAY_WALL * 2)
        .extrude(EBAY_INNER_H + EBAY_WALL * 2)
    )
    shell = shell.cut(ebay_cutout)

    # --- Mounting bosses: electronics bay (4x in spine) ---
    ebay_half_w = (EBAY_INNER_W + EBAY_WALL * 2) / 2
    ebay_x = -CASE_OUTER_W / 2 + WALL + MOUNT_BOSS_OD / 2
    for dy in [-ebay_half_w + 5, ebay_half_w - 5]:
        for dz in [WALL + 3, WALL + EBAY_INNER_H]:
            shell = add_mounting_boss(shell, ebay_x, dy, z=dz, height=4)

    # --- Mounting bosses: cam lifts (2x — monitor center + laptop center) ---
    # Monitor lift: center of monitor pocket floor
    shell = add_mounting_boss(shell, 0, CASE_INNER_D / 4, z=0, height=WALL)
    # Laptop lift: center of laptop sub-pocket floor
    shell = add_mounting_boss(shell, 0, -CASE_INNER_D / 4, z=0, height=WALL)

    # --- Spine ridge (structural/visual, flanking handle) ---
    spine_x = -CASE_OUTER_W / 2
    ridge_y1 = -CASE_OUTER_D / 3
    ridge_y2 = CASE_OUTER_D / 3
    shell = add_ridge(shell, spine_x, ridge_y1, spine_x, ridge_y2,
                      z=PAGE2_H, ridge_w=RIDGE_W, ridge_h=RIDGE_H)

    # --- LED channels on chamfer faces (top perimeter) ---
    shell = add_chamfer_led_channels(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE2_H)

    return shell


# --- Standalone preview for cadquery-server ---
if _cq_server and not os.environ.get('_CQ_ASSEMBLY'):
    page2 = build_page2()
    show_object(page2, name="Page 2 - Middle (Screens)",
                options={"color": (0.56, 0.74, 0.56, 0.7)})
