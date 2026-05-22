"""
Page 3 Shell — Top / Cover (Accessories)

Sculpted organic shell with device pockets for:
  - Keyboard (top, full width)
  - Mudi 7 (bottom-left)
  - Mouse (bottom-center)
  - Misc pocket (bottom-right: Flipper Zero, charging block, cables)

Includes:
  - Full exosuit ridge treatment (3 spine + 2 lateral ridges)
  - LED channels alongside all ridges
  - 2x mounting bosses for latch servo housings
  - 2x mounting bosses for keyboard cam lift
  - 2x capacitive touch pad recesses at ridge intersections
  - Somni Labs geometric logo deboss on outer face

Loadable by cadquery-server via show_object().
"""

import os
import cadquery as cq
from designs.common.constants import (
    WALL, DIVIDER, CORNER_R,
    CASE_OUTER_W, CASE_OUTER_D, CASE_INNER_W, CASE_INNER_D,
    PAGE3_H, PAGE3_DEPTH,
    KB_W, KB_D, KB_H,
    MOUSE_W, MOUSE_D, MOUSE_H,
    MUDI_W, MUDI_D, MUDI_H,
    FLIPPER_H, CHARGER_H,
    FOAM_BASE,
    MOUNT_BOSS_OD,
    LATCH_HOUSING_W,
    RIDGE_H, RIDGE_W, RIDGE_DIAMOND,
    TOUCH_PAD_W, TOUCH_PAD_D, TOUCH_PAD_RECESS,
)
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_ridge, cut_led_channel,
)


def build_page3():
    """Build the complete Page 3 shell with pockets, ridges, LEDs, and mounts."""
    shell = build_sculpted_shell(CASE_OUTER_W, CASE_OUTER_D, PAGE3_H)

    # --- Device pockets ---

    # Keyboard (top, full width)
    kb_cx = 0
    kb_cy = CASE_INNER_D / 2 - DIVIDER - KB_D / 2
    shell = cut_pocket(shell, kb_cx, kb_cy,
        KB_W, KB_D, KB_H + FOAM_BASE, floor_z=WALL, corner_r=3)

    # Bottom row
    bottom_row_cy_start = kb_cy - KB_D / 2 - DIVIDER

    # Mudi 7 (bottom-left)
    mudi_cx = -CASE_INNER_W / 2 + DIVIDER + MUDI_W / 2
    mudi_cy = bottom_row_cy_start - MUDI_D / 2
    shell = cut_pocket(shell, mudi_cx, mudi_cy,
        MUDI_W, MUDI_D, MUDI_H + FOAM_BASE, floor_z=WALL, corner_r=2)

    # Mouse (bottom-center)
    mouse_cx = mudi_cx + MUDI_W / 2 + DIVIDER + MOUSE_W / 2
    mouse_cy = mudi_cy
    shell = cut_pocket(shell, mouse_cx, mouse_cy,
        MOUSE_W, MOUSE_D, MOUSE_H + FOAM_BASE, floor_z=WALL, corner_r=2)

    # Misc pocket (bottom-right)
    misc_left = mouse_cx + MOUSE_W / 2 + DIVIDER
    misc_right = CASE_INNER_W / 2 - DIVIDER
    misc_w = misc_right - misc_left
    misc_cx = (misc_left + misc_right) / 2
    misc_cy = mudi_cy
    misc_d = max(MUDI_D, MOUSE_D)
    shell = cut_pocket(shell, misc_cx, misc_cy,
        misc_w, misc_d, max(FLIPPER_H, CHARGER_H) + FOAM_BASE,
        floor_z=WALL, corner_r=2)

    # --- Exosuit ridges on outer face (Z=0, which is the exterior when closed) ---
    # 3 spine ridges running along Y (lengthwise on the cover)
    ridge_z = PAGE3_H  # top face (exterior when assembled)
    hw = CASE_OUTER_W / 2
    hd = CASE_OUTER_D / 2
    spine_positions = [-hw / 3, 0, hw / 3]  # three evenly spaced
    for sx in spine_positions:
        shell = add_ridge(shell, sx, -hd + 10, sx, hd - 10, z=ridge_z)

    # 2 lateral ridges running along X
    lateral_positions = [-hd / 3, hd / 3]
    for ly in lateral_positions:
        shell = add_ridge(shell, -hw + 10, ly, hw - 10, ly, z=ridge_z)

    # LED channels alongside each spine ridge
    led_offset = RIDGE_W / 2 + 2  # offset from ridge centerline
    for sx in spine_positions:
        shell = cut_led_channel(shell, sx + led_offset, -hd + 12, sx + led_offset, hd - 12, z=ridge_z)
    # LED channels alongside lateral ridges
    for ly in lateral_positions:
        shell = cut_led_channel(shell, -hw + 12, ly + led_offset, hw - 12, ly + led_offset, z=ridge_z)

    # --- Ridge intersection diamonds ---
    for sx in spine_positions:
        for ly in lateral_positions:
            diamond = (
                cq.Workplane("XY")
                .workplane(offset=ridge_z)
                .center(sx, ly)
                .rect(RIDGE_DIAMOND, RIDGE_DIAMOND)
                .extrude(RIDGE_H + 0.5)
            )
            try:
                diamond = diamond.edges(">Z").chamfer(0.8)
            except Exception:
                pass
            shell = shell.union(diamond)

    # --- Mounting bosses: latch servo housings (2x on +X front edge) ---
    latch_spacing = CASE_OUTER_D / 3
    for i in range(2):
        ly = -CASE_OUTER_D / 3 + i * latch_spacing
        shell = add_mounting_boss(shell,
            x=CASE_OUTER_W / 2 - WALL - MOUNT_BOSS_OD / 2,
            y=ly, z=0, height=8)

    # --- Mounting bosses: keyboard cam lift (2x in pocket floor) ---
    shell = add_mounting_boss(shell, kb_cx - KB_W / 4, kb_cy, z=0, height=WALL)
    shell = add_mounting_boss(shell, kb_cx + KB_W / 4, kb_cy, z=0, height=WALL)

    # --- Capacitive touch pad recesses (2x at lateral ridge intersections) ---
    for ly in lateral_positions:
        pad_recess = (
            cq.Workplane("XY")
            .workplane(offset=PAGE3_H - TOUCH_PAD_RECESS)
            .center(spine_positions[0], ly)  # left intersection
            .rect(TOUCH_PAD_W, TOUCH_PAD_D)
            .extrude(TOUCH_PAD_RECESS + 0.1)
        )
        shell = shell.cut(pad_recess)

    # --- Somni Labs logo deboss (geometric, no text/fontconfig) ---
    logo_depth = 1.0
    logo_rect = (
        cq.Workplane("XY")
        .workplane(offset=PAGE3_H + RIDGE_H - logo_depth)
        .center(0, 0)
        .rect(60, 20)
        .extrude(logo_depth + 0.1)
    )
    logo_bar = (
        cq.Workplane("XY")
        .workplane(offset=PAGE3_H + RIDGE_H - logo_depth)
        .center(0, -18)
        .rect(80, 3)
        .extrude(logo_depth + 0.1)
    )
    shell = shell.cut(logo_rect).cut(logo_bar)

    return shell


# --- Standalone preview for cadquery-server ---
if not os.environ.get('_CQ_ASSEMBLY'):
    try:
        from cq_server.ui import ui, show_object
        page3 = build_page3()
        show_object(page3, name="Page 3 - Top (Accessories)",
                    options={"color": (1.0, 0.63, 0.48, 0.7)})
    except ImportError:
        pass
