"""
Mobile Lab Case — V1
Three-page notebook-style portable case for a complete mobile workstation.

Page 1 (Bottom): Starlink Mini + PSU + Battery Bank
Page 2 (Middle): 17" Monitor + Framework Laptop + iPad
Page 3 (Top):    Keyboard + Mouse + Mudi 7 + Flipper Zero + Misc

Design goals:
  - Rugged portable case, fits in large backpack or carries by handle
  - 3D printed PETG shell with custom EVA foam inserts
  - Three rigid pages connected by piano hinge, latches on front
  - Each device gets a dedicated foam cutout pocket
  - Somni Labs logo debossed on cover
  - Printable on QIDI Q2 (275x295mm bed) in tile sections

Loadable by cadquery-server via show_object().
"""

import cadquery as cq
import math
from cq_server.ui import ui, show_object

# =============================================================================
# PARAMETRIC DIMENSIONS (all in mm)
# =============================================================================

# --- Tolerances ---
TOL = 1.0              # print tolerance per side (1mm clearance for snug drop-in)
FOAM_BASE = 5          # foam padding below each device
FOAM_TOP = 3           # foam clearance above each device

# --- Case shell ---
WALL = 3               # outer shell wall thickness
DIVIDER = 2            # internal divider wall thickness
CORNER_R = 5           # corner fillet radius
HINGE_ROD_DIA = 3      # piano hinge rod diameter (3mm steel rod)
HINGE_KNUCKLE_OD = 8   # hinge knuckle outer diameter
HINGE_KNUCKLE_LEN = 15 # each knuckle segment length
HINGE_GAP = 1          # gap between knuckle segments

# --- Print tile constraints ---
BED_W = 275            # QIDI Q2 bed width
BED_D = 295            # QIDI Q2 bed depth

# --- Device 1: Starlink Mini (Page 1) ---
STARLINK_W = 299 + TOL * 2   # width
STARLINK_D = 259 + TOL * 2   # depth
STARLINK_H = 39               # thickness

# --- Device 2: Starlink PSU (Page 1) ---
STARLINK_PSU_W = 91 + TOL * 2
STARLINK_PSU_D = 44 + TOL * 2
STARLINK_PSU_H = 51

# --- Device 3: Portable Battery Bank (Page 1, generic) ---
BATTERY_W = 180 + TOL * 2
BATTERY_D = 80 + TOL * 2
BATTERY_H = 25

# --- Device 4: 17" Portable Monitor (Page 2) ---
MONITOR_W = 400 + TOL * 2
MONITOR_D = 250 + TOL * 2
MONITOR_H = 15

# --- Device 5: Framework Laptop 12 (Page 2) ---
LAPTOP_W = 287 + TOL * 2
LAPTOP_D = 214 + TOL * 2
LAPTOP_H = 18

# --- Device 6: iPad 13" generic (Page 2) ---
IPAD_W = 280 + TOL * 2
IPAD_D = 215 + TOL * 2
IPAD_H = 7

# --- Device 7: Turtle Beach Vulcan II TKL Keyboard (Page 3) ---
KB_W = 366 + TOL * 2
KB_D = 137 + TOL * 2
KB_H = 32

# --- Device 8: Turtle Beach Burst II Air Mouse (Page 3) ---
MOUSE_W = 120 + TOL * 2
MOUSE_D = 60 + TOL * 2
MOUSE_H = 40

# --- Device 9: GL-iNet Mudi 7 (Page 3) ---
MUDI_W = 157 + TOL * 2
MUDI_D = 75 + TOL * 2
MUDI_H = 23

# --- Device 10: Flipper Zero (Page 3, misc pocket) ---
FLIPPER_W = 100 + TOL * 2
FLIPPER_D = 40 + TOL * 2
FLIPPER_H = 26

# --- Device 11: Charging Block (Page 3, misc pocket) ---
CHARGER_W = 80 + TOL * 2
CHARGER_D = 80 + TOL * 2
CHARGER_H = 30

# --- Page depths (usable internal depth for foam + device) ---
PAGE1_DEPTH = STARLINK_PSU_H + FOAM_BASE + FOAM_TOP  # ~59mm (PSU is tallest at 51mm)
PAGE2_DEPTH = FOAM_BASE + MONITOR_H + 2 + LAPTOP_H + IPAD_H + FOAM_TOP  # ~50mm (two-tier: monitor shelf over laptop+iPad stack)
PAGE3_DEPTH = MOUSE_H + FOAM_BASE + FOAM_TOP           # ~48mm (mouse is tallest at 40mm)

# --- Internal case dimensions (driven by largest items) ---
CASE_INNER_W = max(MONITOR_W, KB_W, STARLINK_W) + DIVIDER * 2
CASE_INNER_D = max(STARLINK_D, MONITOR_D, KB_D + MUDI_D + DIVIDER) + DIVIDER * 2
CASE_OUTER_W = CASE_INNER_W + WALL * 2
CASE_OUTER_D = CASE_INNER_D + WALL * 2
CASE_TOTAL_H = PAGE1_DEPTH + PAGE2_DEPTH + PAGE3_DEPTH + WALL * 4

# --- Latch positions ---
LATCH_COUNT = 2
LATCH_W = 20
LATCH_H = 12
LATCH_HOOK = 2

# --- Handle ---
HANDLE_W = 100
HANDLE_H = 25
HANDLE_THICK = 8


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_page_shell(width, depth, height, corner_r=CORNER_R, wall=WALL):
    """Build a single page shell -- open-top box with rounded corners."""
    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
    )
    if corner_r > 0:
        outer = outer.edges("|Z").fillet(corner_r)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .rect(width - wall * 2, depth - wall * 2)
        .extrude(height)
    )
    shell = outer.cut(inner)
    return shell


def cut_pocket(body, cx, cy, pocket_w, pocket_d, pocket_h, floor_z, corner_r=2):
    """Cut a rectangular pocket (foam cutout) into a page shell."""
    pocket = (
        cq.Workplane("XY")
        .workplane(offset=floor_z)
        .center(cx, cy)
        .rect(pocket_w, pocket_d)
        .extrude(pocket_h + 1)
    )
    if corner_r > 0:
        pocket = pocket.edges("|Z").fillet(corner_r)
    return body.cut(pocket)


# =============================================================================
# PAGE 1 — BOTTOM (Power & Connectivity)
# =============================================================================
_p1_h = PAGE1_DEPTH + WALL

page1 = build_page_shell(CASE_OUTER_W, CASE_OUTER_D, _p1_h)

# Starlink Mini pocket (left side, spanning nearly full depth)
_starlink_cx = -CASE_INNER_W / 2 + DIVIDER + STARLINK_W / 2
_starlink_cy = 0
page1 = cut_pocket(page1, _starlink_cx, _starlink_cy,
    STARLINK_W, STARLINK_D, STARLINK_H + FOAM_BASE, floor_z=WALL, corner_r=3)

# Right column: space to the right of the Starlink Mini
_right_col_left = _starlink_cx + STARLINK_W / 2 + DIVIDER
_right_col_w = CASE_INNER_W / 2 - DIVIDER - _right_col_left

# Starlink PSU pocket (top-right)
_psu_cx = _right_col_left + STARLINK_PSU_W / 2
_psu_cy = CASE_INNER_D / 2 - DIVIDER - STARLINK_PSU_D / 2
page1 = cut_pocket(page1, _psu_cx, _psu_cy,
    STARLINK_PSU_W, STARLINK_PSU_D, STARLINK_PSU_H + FOAM_BASE, floor_z=WALL, corner_r=2)

# Battery Bank pocket (bottom-right, rotated 90deg to fit the narrow column)
# Physical battery is 182x82, placed as 82(W) x 182(D) in the right column
_bat_pocket_w = BATTERY_D   # 82mm (rotated: depth becomes width)
_bat_pocket_d = BATTERY_W   # 182mm (rotated: width becomes depth)
_bat_cx = _right_col_left + _bat_pocket_w / 2
_bat_cy = _psu_cy - STARLINK_PSU_D / 2 - DIVIDER - _bat_pocket_d / 2
page1 = cut_pocket(page1, _bat_cx, _bat_cy,
    _bat_pocket_w, _bat_pocket_d, BATTERY_H + FOAM_BASE, floor_z=WALL, corner_r=2)


# =============================================================================
# PAGE 2 — MIDDLE (Screens & Compute)
# =============================================================================
# Two-tier pocket layout: shallow monitor pocket over deeper laptop+iPad sub-pocket.
# The monitor rests on a foam shelf formed by the larger pocket perimeter.
_p2_h = PAGE2_DEPTH + WALL

page2 = build_page_shell(CASE_OUTER_W, CASE_OUTER_D, _p2_h)

# Tier 1: 17" Portable Monitor pocket (full page, shallow)
_mon_cx = 0
_mon_cy = 0
_mon_pocket_h = FOAM_BASE + MONITOR_H  # 20mm from floor
page2 = cut_pocket(page2, _mon_cx, _mon_cy,
    MONITOR_W, MONITOR_D, _mon_pocket_h, floor_z=WALL, corner_r=3)

# Tier 2: Framework Laptop + iPad stacked sub-pocket (centered within monitor pocket, deeper)
_stack_w = max(LAPTOP_W, IPAD_W)   # 289mm
_stack_d = max(LAPTOP_D, IPAD_D)   # 217mm
_stack_h = FOAM_BASE + MONITOR_H + 2 + LAPTOP_H + IPAD_H  # 47mm from floor
_stack_cx = 0
_stack_cy = 0
page2 = cut_pocket(page2, _stack_cx, _stack_cy,
    _stack_w, _stack_d, _stack_h, floor_z=WALL, corner_r=3)


# =============================================================================
# PAGE 3 — TOP / COVER (Accessories)
# =============================================================================
_p3_h = PAGE3_DEPTH + WALL

page3 = build_page_shell(CASE_OUTER_W, CASE_OUTER_D, _p3_h)

# Keyboard pocket (top, full width)
_kb_cx = 0
_kb_cy = CASE_INNER_D / 2 - DIVIDER - KB_D / 2
page3 = cut_pocket(page3, _kb_cx, _kb_cy,
    KB_W, KB_D, KB_H + FOAM_BASE, floor_z=WALL, corner_r=3)

# Bottom row: Mudi 7, Mouse, Misc
_bottom_row_cy_start = _kb_cy - KB_D / 2 - DIVIDER

# Mudi 7 (bottom-left)
_mudi_cx = -CASE_INNER_W / 2 + DIVIDER + MUDI_W / 2
_mudi_cy = _bottom_row_cy_start - MUDI_D / 2
page3 = cut_pocket(page3, _mudi_cx, _mudi_cy,
    MUDI_W, MUDI_D, MUDI_H + FOAM_BASE, floor_z=WALL, corner_r=2)

# Mouse (bottom-center)
_mouse_cx = _mudi_cx + MUDI_W / 2 + DIVIDER + MOUSE_W / 2
_mouse_cy = _mudi_cy
page3 = cut_pocket(page3, _mouse_cx, _mouse_cy,
    MOUSE_W, MOUSE_D, MOUSE_H + FOAM_BASE, floor_z=WALL, corner_r=2)

# Misc pocket (bottom-right, remaining space for Flipper Zero + Charging Block)
_misc_left = _mouse_cx + MOUSE_W / 2 + DIVIDER
_misc_right = CASE_INNER_W / 2 - DIVIDER
_misc_w = _misc_right - _misc_left
_misc_cx = (_misc_left + _misc_right) / 2
_misc_cy = _mudi_cy
_misc_d = max(MUDI_D, MOUSE_D)
page3 = cut_pocket(page3, _misc_cx, _misc_cy,
    _misc_w, _misc_d, max(FLIPPER_H, CHARGER_H) + FOAM_BASE, floor_z=WALL, corner_r=2)

# --- Somni Labs logo deboss on cover (top face of page 3) ---
try:
    _logo_depth = 1.0
    logo = (
        cq.Workplane("XY")
        .workplane(offset=_p3_h)
        .text("SOMNI", fontsize=30, distance=_logo_depth, combine=False,
              halign="center", valign="center")
        .translate((0, 0, -_logo_depth))
    )
    page3 = page3.cut(logo)
except Exception:
    # Fallback: simple rectangular deboss placeholder
    logo_rect = (
        cq.Workplane("XY")
        .workplane(offset=_p3_h - 1.0)
        .rect(80, 15)
        .extrude(1.0 + 0.1)
    )
    page3 = page3.cut(logo_rect)


# =============================================================================
# CADQUERY-SERVER PREVIEW
# =============================================================================
show_object(page1, name="Page 1 - Bottom (Power)", options={"color": "steelblue", "alpha": 0.7})

_p2_assembly_z = _p1_h + 2
page2_view = page2.translate((0, 0, _p2_assembly_z))
show_object(page2_view, name="Page 2 - Middle (Screens)", options={"color": "darkseagreen", "alpha": 0.7})

_p3_assembly_z = _p2_assembly_z + _p2_h + 2
page3_view = page3.translate((0, 0, _p3_assembly_z))
show_object(page3_view, name="Page 3 - Top (Accessories)", options={"color": "lightsalmon", "alpha": 0.7})
