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
PAGE2_DEPTH = LAPTOP_H + IPAD_H + FOAM_BASE + FOAM_TOP + 3  # ~36mm (stacked laptop+iPad+divider)
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
