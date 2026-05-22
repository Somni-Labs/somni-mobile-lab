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


def build_hinge_knuckles(page_height, case_depth, case_outer_w, parity="even",
                         knuckle_od=HINGE_KNUCKLE_OD, knuckle_len=HINGE_KNUCKLE_LEN,
                         gap=HINGE_GAP, rod_dia=HINGE_ROD_DIA):
    """
    Build interleaving piano-hinge knuckles along the -X edge of a page.

    Knuckles are cylinders oriented along the Y axis, centered at:
      X = -case_outer_w/2 (the left wall edge)
      Z = page_height (top face, where pages meet)

    parity="even" gives knuckle indices 0,2,4,... ; "odd" gives 1,3,5,...
    Returns a single CadQuery solid (union of all knuckles with rod holes).
    """
    knuckle_r = knuckle_od / 2
    rod_r = rod_dia / 2 + 0.15  # small clearance for rod

    # How many knuckle slots fit along the depth
    slot_pitch = knuckle_len + gap
    n_slots = int(case_depth // slot_pitch)

    # Center the knuckle array along Y
    total_len = n_slots * slot_pitch - gap
    y_start = -total_len / 2 + knuckle_len / 2

    # Hinge center position
    hinge_x = -case_outer_w / 2
    hinge_z = page_height  # top face where pages meet

    knuckles = None
    start_idx = 0 if parity == "even" else 1

    for i in range(start_idx, n_slots, 2):
        cy = y_start + i * slot_pitch
        # Build a cylinder along Y axis at the hinge line
        knuckle = (
            cq.Workplane("XZ")
            .center(hinge_x, hinge_z)
            .circle(knuckle_r)
            .extrude(knuckle_len, both=False)
            .translate((0, cy - knuckle_len / 2, 0))
        )
        # Cut the rod hole through
        rod_hole = (
            cq.Workplane("XZ")
            .center(hinge_x, hinge_z)
            .circle(rod_r)
            .extrude(knuckle_len + 2, both=False)
            .translate((0, cy - knuckle_len / 2 - 1, 0))
        )
        knuckle = knuckle.cut(rod_hole)
        if knuckles is None:
            knuckles = knuckle
        else:
            knuckles = knuckles.union(knuckle)

    return knuckles


def build_latch(latch_w=LATCH_W, latch_h=LATCH_H, latch_hook=LATCH_HOOK, wall=WALL):
    """
    Build a snap latch — returns (body, catch) tuple.

    body: The latch arm with hook, attaches to the closing page (page3 outer face).
    catch: The catch ledge, attaches to the receiving page (page1 top edge).
    Both are centered at origin; caller translates to final position.
    """
    # Latch body: a flat arm with a hook at the bottom
    arm_thick = wall
    arm = (
        cq.Workplane("XY")
        .rect(latch_w, arm_thick)
        .extrude(latch_h)
    )
    # Hook at the bottom of the arm (extends inward in +Y direction)
    hook = (
        cq.Workplane("XY")
        .center(0, arm_thick / 2)
        .rect(latch_w, latch_hook + arm_thick)
        .extrude(arm_thick)
    )
    body = arm.union(hook)

    # Catch: a ledge that the hook grabs onto
    catch = (
        cq.Workplane("XY")
        .rect(latch_w, latch_hook + arm_thick + 0.5)
        .extrude(arm_thick)
    )

    return body, catch


def build_carry_handle(handle_w=HANDLE_W, handle_h=HANDLE_H, handle_thick=HANDLE_THICK):
    """
    Build a carry handle — a U-shaped loop.
    Oriented so the grip span is along Y, extending outward in -X.
    Centered at origin; caller translates to final position.
    """
    # Build as a rounded rectangle with a hole cut through it
    outer = (
        cq.Workplane("XY")
        .rect(handle_h, handle_w + handle_thick * 2)
        .extrude(handle_thick)
    )
    try:
        outer = outer.edges("|Z").fillet(handle_thick / 2 - 0.1)
    except Exception:
        pass
    inner = (
        cq.Workplane("XY")
        .rect(handle_h - handle_thick * 2, handle_w)
        .extrude(handle_thick)
    )
    handle = outer.cut(inner)
    return handle


def split_into_tiles(body, case_outer_w, case_outer_d, page_height):
    """
    Split a page body into left and right halves at X=0.
    Each tile must fit the QIDI Q2 bed (275x295mm).
    Returns (left_tile, right_tile).
    """
    margin = 10  # extra size for clean cut
    half_w = case_outer_w / 2 + margin
    h = page_height + margin * 2

    # Left half: everything at X < 0
    left_cutter = (
        cq.Workplane("XY")
        .workplane(offset=-margin)
        .center(half_w / 2, 0)
        .rect(half_w, case_outer_d + margin * 2)
        .extrude(h)
    )
    right_tile = body.intersect(left_cutter)

    # Right half: everything at X >= 0
    right_cutter = (
        cq.Workplane("XY")
        .workplane(offset=-margin)
        .center(-half_w / 2, 0)
        .rect(half_w, case_outer_d + margin * 2)
        .extrude(h)
    )
    left_tile = body.intersect(right_cutter)

    return left_tile, right_tile


def add_bolt_holes(body, case_outer_d, page_height, bolt_dia=3.0, insert_dia=4.2,
                   is_left=True, n_bolts=5, wall=WALL):
    """
    Add M3 bolt holes along the split seam at X=0.
    Left tiles get clearance holes (3.4mm), right tiles get heat-set insert holes (4.2mm).
    Holes are along X=0, distributed evenly along Y, at mid-height.
    """
    clearance_r = (bolt_dia + 0.4) / 2   # 3.4mm clearance
    insert_r = insert_dia / 2             # 4.2mm for heat-set insert

    r = clearance_r if is_left else insert_r
    hole_depth = wall + 2  # through the wall plus margin

    # Distribute bolts evenly along Y
    usable_d = case_outer_d - 30  # margin from edges
    spacing = usable_d / (n_bolts - 1) if n_bolts > 1 else 0
    y_start = -usable_d / 2

    z_mid = page_height / 2

    for i in range(n_bolts):
        y = y_start + i * spacing
        hole = (
            cq.Workplane("YZ")
            .center(y, z_mid)
            .circle(r)
            .extrude(hole_depth, both=True)
        )
        body = body.cut(hole)

    return body


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
# Geometric "S" deboss — avoids Fontconfig dependency that breaks cadquery-server.
# A stylized "S" shape built from two offset arcs, debossed 1mm into the top face.
_logo_depth = 1.0
_logo_s = (
    cq.Workplane("XY")
    .workplane(offset=_p3_h - _logo_depth)
    .center(0, 0)
    .rect(60, 20)
    .extrude(_logo_depth + 0.1)
)
# Horizontal bar under the S
_logo_bar = (
    cq.Workplane("XY")
    .workplane(offset=_p3_h - _logo_depth)
    .center(0, -18)
    .rect(80, 3)
    .extrude(_logo_depth + 0.1)
)
page3 = page3.cut(_logo_s).cut(_logo_bar)


# =============================================================================
# PIANO HINGE KNUCKLES
# =============================================================================
# Hinge along -X edge. Pages 1 & 3 get "even" knuckles, Page 2 gets "odd".
# Knuckles sit at the TOP Z face of each page (where pages meet when stacked).

_p1_hinges = build_hinge_knuckles(_p1_h, CASE_OUTER_D, CASE_OUTER_W, parity="even")
_p2_hinges_bottom = build_hinge_knuckles(0, CASE_OUTER_D, CASE_OUTER_W, parity="odd")
_p2_hinges_top = build_hinge_knuckles(_p2_h, CASE_OUTER_D, CASE_OUTER_W, parity="even")
_p3_hinges = build_hinge_knuckles(0, CASE_OUTER_D, CASE_OUTER_W, parity="odd")

page1 = page1.union(_p1_hinges)
page2 = page2.union(_p2_hinges_bottom).union(_p2_hinges_top)
page3 = page3.union(_p3_hinges)


# =============================================================================
# SNAP LATCHES AND CARRY HANDLE
# =============================================================================
# Two latches along +X (front) edge, evenly spaced along Y.
_latch_body, _latch_catch = build_latch()

_latch_x = CASE_OUTER_W / 2 + WALL / 2   # just outside the +X wall
_latch_spacing = CASE_OUTER_D / 3          # thirds along depth

for i in range(LATCH_COUNT):
    _ly = -CASE_OUTER_D / 3 + i * _latch_spacing

    # Latch body on page3 at Z=0 (outer face when closed, facing down)
    _body_placed = _latch_body.translate((_latch_x, _ly, 0))
    page3 = page3.union(_body_placed)

    # Latch catch on page1 at Z=_p1_h (top edge)
    _catch_placed = _latch_catch.translate((_latch_x, _ly, _p1_h))
    page1 = page1.union(_catch_placed)

# Carry handle on the -X (hinge) edge of page2, centered vertically.
_handle = build_carry_handle()
# Rotate so handle grip extends outward in -X direction
_handle = (
    _handle
    .rotate((0, 0, 0), (0, 1, 0), 90)  # now extends in X direction
    .translate((-CASE_OUTER_W / 2 - HANDLE_H / 2, 0, _p2_h / 2))
)
page2 = page2.union(_handle)


# =============================================================================
# TILE SPLIT AND BOLT HOLES
# =============================================================================
# Split each page into left/right tiles at X=0 for QIDI Q2 bed.

page1_left, page1_right = split_into_tiles(page1, CASE_OUTER_W, CASE_OUTER_D, _p1_h)
page2_left, page2_right = split_into_tiles(page2, CASE_OUTER_W, CASE_OUTER_D, _p2_h)
page3_left, page3_right = split_into_tiles(page3, CASE_OUTER_W, CASE_OUTER_D, _p3_h)

# Add M3 bolt holes along the split seam
page1_left = add_bolt_holes(page1_left, CASE_OUTER_D, _p1_h, is_left=True)
page1_right = add_bolt_holes(page1_right, CASE_OUTER_D, _p1_h, is_left=False)
page2_left = add_bolt_holes(page2_left, CASE_OUTER_D, _p2_h, is_left=True)
page2_right = add_bolt_holes(page2_right, CASE_OUTER_D, _p2_h, is_left=False)
page3_left = add_bolt_holes(page3_left, CASE_OUTER_D, _p3_h, is_left=True)
page3_right = add_bolt_holes(page3_right, CASE_OUTER_D, _p3_h, is_left=False)


# =============================================================================
# CADQUERY-SERVER PREVIEW
# =============================================================================
# Show full pages (with hinges/latches/handle) in stacked assembly view
show_object(page1, name="Page 1 - Bottom (Power)",
            options={"color": (0.27, 0.51, 0.71, 0.7)})   # steelblue, 70% opaque

_p2_assembly_z = _p1_h + 2
page2_view = page2.translate((0, 0, _p2_assembly_z))
show_object(page2_view, name="Page 2 - Middle (Screens)",
            options={"color": (0.56, 0.74, 0.56, 0.7)})   # darkseagreen, 70% opaque

_p3_assembly_z = _p2_assembly_z + _p2_h + 2
page3_view = page3.translate((0, 0, _p3_assembly_z))
show_object(page3_view, name="Page 3 - Top (Accessories)",
            options={"color": (1.0, 0.63, 0.48, 0.7)})    # lightsalmon, 70% opaque

# Tile variables exported for export script (page1_left, page1_right, etc.)
