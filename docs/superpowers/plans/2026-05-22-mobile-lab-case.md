# Mobile Lab Case Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a three-page notebook-style portable case in CadQuery with foam cutout pockets for all devices, printable on QIDI Q2 in tile sections.

**Architecture:** Single CadQuery design file builds three page panels (bottom/middle/top), each with device-specific foam pocket cutouts. Pages connect via piano-hinge knuckles along one long edge. Each panel splits into 2 print tiles joined by M3 heat-set inserts. Export script generates per-tile STLs + foam cutting templates. cadquery-server renders the assembled case via show_object().

**Tech Stack:** CadQuery, Python 3, cadquery-server (K8s), PrusaSlicer via K8s Jobs, Moonraker API

---

## File Structure

| File | Responsibility |
|------|---------------|
| `designs/mobile-lab-case.py` | Main parametric design — all three pages, hinges, latches, handle, logo. Loaded by cadquery-server via `show_object()`. |
| `export_mobile_lab.py` | STL/STEP export script — strips cq_server dependency, exports each tile at Z=0 for printing, exports foam templates as DXF. |
| `k8s/slice-mobile-lab.yaml` | K8s Job template for PrusaSlicer slicing + Moonraker upload with temp post-processing. |

---

### Task 1: Parametric Constants and Helper Functions

**Files:**
- Create: `designs/mobile-lab-case.py`

- [ ] **Step 1: Create the design file with module docstring, imports, and all parametric constants**

```python
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
  - Printable on QIDI Q2 (275×295mm bed) in tile sections

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
PAGE1_DEPTH = STARLINK_PSU_H + FOAM_BASE + FOAM_TOP  # ~61mm (PSU is tallest at 51mm)
PAGE2_DEPTH = LAPTOP_H + IPAD_H + FOAM_BASE + FOAM_TOP + 3  # ~36mm (stacked laptop+iPad+divider)
PAGE3_DEPTH = MOUSE_H + FOAM_BASE + FOAM_TOP           # ~48mm (mouse is tallest at 40mm)

# --- Internal case dimensions (driven by largest items) ---
# Width: 17" monitor at 402mm is widest
# Depth: Starlink Mini at 261mm is deepest; but monitor at 252mm close
CASE_INNER_W = max(MONITOR_W, KB_W, STARLINK_W) + DIVIDER * 2  # ~406mm
CASE_INNER_D = max(STARLINK_D, MONITOR_D, KB_D + MUDI_D + DIVIDER) + DIVIDER * 2  # ~265mm
CASE_OUTER_W = CASE_INNER_W + WALL * 2
CASE_OUTER_D = CASE_INNER_D + WALL * 2
CASE_TOTAL_H = PAGE1_DEPTH + PAGE2_DEPTH + PAGE3_DEPTH + WALL * 4  # top/bottom of each page

# --- Latch positions ---
LATCH_COUNT = 2
LATCH_W = 20           # latch body width
LATCH_H = 12           # latch hook height
LATCH_HOOK = 2         # hook overhang

# --- Handle ---
HANDLE_W = 100         # handle grip width
HANDLE_H = 25          # handle height above surface
HANDLE_THICK = 8       # handle grip cross-section thickness
```

- [ ] **Step 2: Add helper function for building a page shell (reused by all 3 pages)**

```python
# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_page_shell(width, depth, height, corner_r=CORNER_R, wall=WALL):
    """Build a single page shell — open-top box with rounded corners.

    Returns a CadQuery solid: outer walls + floor, no lid.
    The interior is the foam cavity to be cut with device pockets.

    Args:
        width: outer width (X)
        depth: outer depth (Y)
        height: outer height (Z) including floor
        corner_r: corner fillet radius
        wall: wall thickness
    """
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
        .extrude(height)  # cut through top
    )
    shell = outer.cut(inner)
    return shell


def cut_pocket(body, cx, cy, pocket_w, pocket_d, pocket_h, floor_z, corner_r=2):
    """Cut a rectangular pocket (foam cutout) into a page shell.

    Args:
        body: CadQuery solid to cut from
        cx, cy: pocket center (X, Y)
        pocket_w: pocket width (X)
        pocket_d: pocket depth (Y)
        pocket_h: pocket height (Z) — device thickness + foam base
        floor_z: Z offset of pocket floor (above shell floor)
        corner_r: pocket corner fillet radius
    """
    pocket = (
        cq.Workplane("XY")
        .workplane(offset=floor_z)
        .center(cx, cy)
        .rect(pocket_w, pocket_d)
        .extrude(pocket_h + 1)  # +1 to cut through top
    )
    if corner_r > 0:
        pocket = pocket.edges("|Z").fillet(corner_r)
    return body.cut(pocket)
```

- [ ] **Step 3: Verify the file loads without errors**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 -c "code = open('designs/mobile-lab-case.py').read(); code = code.replace('from cq_server.ui import ui, show_object', ''); exec(code, {'show_object': lambda *a,**k: None}); print('OK')"`

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add designs/mobile-lab-case.py
git commit -m "feat: add parametric constants and helper functions for mobile lab case"
```

---

### Task 2: Page 1 — Bottom (Power & Connectivity)

**Files:**
- Modify: `designs/mobile-lab-case.py`

- [ ] **Step 1: Build Page 1 shell and cut device pockets**

Add after the helper functions:

```python
# =============================================================================
# PAGE 1 — BOTTOM (Power & Connectivity)
# =============================================================================
# Layout: Starlink Mini (left), Starlink PSU (top-right), Battery Bank (bottom-right)

_p1_h = PAGE1_DEPTH + WALL  # total page height including floor

page1 = build_page_shell(CASE_OUTER_W, CASE_OUTER_D, _p1_h)

# --- Starlink Mini pocket (left side) ---
_starlink_cx = -CASE_INNER_W / 2 + DIVIDER + STARLINK_W / 2
_starlink_cy = 0  # centered vertically
page1 = cut_pocket(
    page1, _starlink_cx, _starlink_cy,
    STARLINK_W, STARLINK_D, STARLINK_H + FOAM_BASE,
    floor_z=WALL, corner_r=3
)

# --- Starlink PSU pocket (top-right) ---
_psu_cx = _starlink_cx + STARLINK_W / 2 + DIVIDER + STARLINK_PSU_W / 2
_psu_cy = CASE_INNER_D / 2 - DIVIDER - STARLINK_PSU_D / 2
page1 = cut_pocket(
    page1, _psu_cx, _psu_cy,
    STARLINK_PSU_W, STARLINK_PSU_D, STARLINK_PSU_H + FOAM_BASE,
    floor_z=WALL, corner_r=2
)

# --- Battery Bank pocket (bottom-right) ---
_bat_cx = _psu_cx  # same X column as PSU
_bat_cy = _psu_cy - STARLINK_PSU_D / 2 - DIVIDER - BATTERY_D / 2
page1 = cut_pocket(
    page1, _bat_cx, _bat_cy,
    BATTERY_W, BATTERY_D, BATTERY_H + FOAM_BASE,
    floor_z=WALL, corner_r=2
)
```

- [ ] **Step 2: Add show_object for cadquery-server preview**

```python
show_object(page1, name="Page 1 — Bottom (Power)", options={"color": "steelblue", "alpha": 0.7})
```

- [ ] **Step 3: Verify it builds and renders**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 -c "code = open('designs/mobile-lab-case.py').read(); code = code.replace('from cq_server.ui import ui, show_object', ''); exec(code, {'show_object': lambda *a,**k: None}); print('Page 1 OK')"`

Expected: `Page 1 OK`

- [ ] **Step 4: Commit**

```bash
git add designs/mobile-lab-case.py
git commit -m "feat: add Page 1 — Starlink Mini, PSU, and battery bank pockets"
```

---

### Task 3: Page 2 — Middle (Screens & Compute)

**Files:**
- Modify: `designs/mobile-lab-case.py`

- [ ] **Step 1: Build Page 2 shell and cut device pockets**

```python
# =============================================================================
# PAGE 2 — MIDDLE (Screens & Compute)
# =============================================================================
# Layout: 17" Monitor (top, full width), Framework + iPad stacked (bottom)

_p2_h = PAGE2_DEPTH + WALL

page2 = build_page_shell(CASE_OUTER_W, CASE_OUTER_D, _p2_h)

# --- 17" Portable Monitor pocket (top, full width) ---
_mon_cx = 0  # centered
_mon_cy = CASE_INNER_D / 2 - DIVIDER - MONITOR_D / 2
page2 = cut_pocket(
    page2, _mon_cx, _mon_cy,
    MONITOR_W, MONITOR_D, MONITOR_H + FOAM_BASE,
    floor_z=WALL, corner_r=3
)

# --- Framework Laptop + iPad stacked pocket (bottom) ---
# Combined pocket depth = laptop + iPad + 3mm foam divider
_stack_h = LAPTOP_H + IPAD_H + 3  # 3mm foam divider between them
_stack_w = max(LAPTOP_W, IPAD_W)  # use larger footprint
_stack_d = max(LAPTOP_D, IPAD_D)
_stack_cx = 0
_stack_cy = _mon_cy - MONITOR_D / 2 - DIVIDER - _stack_d / 2
page2 = cut_pocket(
    page2, _stack_cx, _stack_cy,
    _stack_w, _stack_d, _stack_h + FOAM_BASE,
    floor_z=WALL, corner_r=3
)
```

- [ ] **Step 2: Add show_object**

```python
# Offset Page 2 above Page 1 for assembly view
_p2_assembly_z = _p1_h + 2  # 2mm visual gap
page2_positioned = page2.translate((0, 0, _p2_assembly_z))
show_object(page2_positioned, name="Page 2 — Middle (Screens)", options={"color": "darkseagreen", "alpha": 0.7})
```

- [ ] **Step 3: Verify it builds**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 -c "code = open('designs/mobile-lab-case.py').read(); code = code.replace('from cq_server.ui import ui, show_object', ''); exec(code, {'show_object': lambda *a,**k: None}); print('Page 2 OK')"`

Expected: `Page 2 OK`

- [ ] **Step 4: Commit**

```bash
git add designs/mobile-lab-case.py
git commit -m "feat: add Page 2 — monitor, laptop, and iPad pockets"
```

---

### Task 4: Page 3 — Top / Cover (Accessories)

**Files:**
- Modify: `designs/mobile-lab-case.py`

- [ ] **Step 1: Build Page 3 shell and cut device pockets**

```python
# =============================================================================
# PAGE 3 — TOP / COVER (Accessories)
# =============================================================================
# Layout: Keyboard (top, full width), Mudi 7 (bottom-left),
#         Mouse (bottom-center), Misc pocket (bottom-right)

_p3_h = PAGE3_DEPTH + WALL

page3 = build_page_shell(CASE_OUTER_W, CASE_OUTER_D, _p3_h)

# --- Keyboard pocket (top, full width) ---
_kb_cx = 0
_kb_cy = CASE_INNER_D / 2 - DIVIDER - KB_D / 2
page3 = cut_pocket(
    page3, _kb_cx, _kb_cy,
    KB_W, KB_D, KB_H + FOAM_BASE,
    floor_z=WALL, corner_r=3
)

# --- Bottom row: Mudi 7, Mouse, Misc ---
_bottom_row_cy_start = _kb_cy - KB_D / 2 - DIVIDER
_bottom_row_h = _p3_h - WALL  # full remaining depth

# Mudi 7 (bottom-left)
_mudi_cx = -CASE_INNER_W / 2 + DIVIDER + MUDI_W / 2
_mudi_cy = _bottom_row_cy_start - MUDI_D / 2
page3 = cut_pocket(
    page3, _mudi_cx, _mudi_cy,
    MUDI_W, MUDI_D, MUDI_H + FOAM_BASE,
    floor_z=WALL, corner_r=2
)

# Mouse (bottom-center)
_mouse_cx = _mudi_cx + MUDI_W / 2 + DIVIDER + MOUSE_W / 2
_mouse_cy = _mudi_cy
page3 = cut_pocket(
    page3, _mouse_cx, _mouse_cy,
    MOUSE_W, MOUSE_D, MOUSE_H + FOAM_BASE,
    floor_z=WALL, corner_r=2
)

# Misc pocket (bottom-right, remaining space)
# Fits Flipper Zero, charging block, cables, adapters
_misc_left = _mouse_cx + MOUSE_W / 2 + DIVIDER
_misc_right = CASE_INNER_W / 2 - DIVIDER
_misc_w = _misc_right - _misc_left
_misc_cx = (_misc_left + _misc_right) / 2
_misc_cy = _mudi_cy
_misc_d = max(MUDI_D, MOUSE_D)  # same depth as other bottom-row items
page3 = cut_pocket(
    page3, _misc_cx, _misc_cy,
    _misc_w, _misc_d, max(FLIPPER_H, CHARGER_H) + FOAM_BASE,
    floor_z=WALL, corner_r=2
)
```

- [ ] **Step 2: Add Somni Labs logo debossed on outer face**

```python
# --- Somni Labs logo (debossed on outer bottom face of Page 3 = case cover) ---
# Simple "SOMNI" text centered on the cover exterior
_logo_depth = 1.0  # 1mm deboss depth
logo = (
    cq.Workplane("XY")
    .text("SOMNI", fontsize=30, distance=_logo_depth, combine=False, halign="center", valign="center")
    .translate((0, 0, -_logo_depth))  # deboss into bottom face
)
page3 = page3.cut(logo)
```

- [ ] **Step 3: Add show_object**

```python
_p3_assembly_z = _p2_assembly_z + _p2_h + 2
page3_positioned = page3.translate((0, 0, _p3_assembly_z))
show_object(page3_positioned, name="Page 3 — Top (Accessories)", options={"color": "lightsalmon", "alpha": 0.7})
```

- [ ] **Step 4: Verify it builds**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 -c "code = open('designs/mobile-lab-case.py').read(); code = code.replace('from cq_server.ui import ui, show_object', ''); exec(code, {'show_object': lambda *a,**k: None}); print('Page 3 OK')"`

Expected: `Page 3 OK`

- [ ] **Step 5: Commit**

```bash
git add designs/mobile-lab-case.py
git commit -m "feat: add Page 3 — keyboard, mouse, Mudi 7, misc pocket, and Somni logo"
```

---

### Task 5: Hinge System

**Files:**
- Modify: `designs/mobile-lab-case.py`

- [ ] **Step 1: Add hinge knuckle builder function**

```python
def build_hinge_knuckles(page_depth, rod_dia=HINGE_ROD_DIA, knuckle_od=HINGE_KNUCKLE_OD,
                         knuckle_len=HINGE_KNUCKLE_LEN, gap=HINGE_GAP, side="left"):
    """Build a row of hinge knuckles along one edge of a page.

    Knuckles alternate between pages: 'left' pages get knuckles at even
    positions, 'right' pages get odd positions. When assembled, they
    interleave and a rod slides through all of them.

    Args:
        page_depth: Y-dimension of the page (to position along back edge)
        rod_dia: hinge rod diameter
        knuckle_od: knuckle outer diameter
        knuckle_len: length of each knuckle segment
        gap: gap between segments
        side: 'left' (even positions) or 'right' (odd positions)

    Returns:
        CadQuery solid of all knuckle cylinders with rod hole
    """
    total_span = CASE_OUTER_D
    segment_pitch = knuckle_len + gap
    n_segments = int(total_span / segment_pitch)

    knuckles = None
    for i in range(n_segments):
        if (side == "left" and i % 2 == 0) or (side == "right" and i % 2 == 1):
            y_pos = -total_span / 2 + segment_pitch / 2 + i * segment_pitch
            knuckle = (
                cq.Workplane("XY")
                .center(0, y_pos)
                .circle(knuckle_od / 2)
                .extrude(knuckle_len)
                .translate((0, 0, 0))
            )
            # Subtract rod hole
            hole = (
                cq.Workplane("XY")
                .center(0, y_pos)
                .circle(rod_dia / 2 + 0.2)  # 0.2mm clearance
                .extrude(knuckle_len)
            )
            knuckle = knuckle.cut(hole)

            if knuckles is None:
                knuckles = knuckle
            else:
                knuckles = knuckles.union(knuckle)

    return knuckles
```

- [ ] **Step 2: Attach hinge knuckles to each page along the back edge (-X side)**

```python
# --- Hinge knuckles ---
# Pages hinge along the back (−X) edge. Page 1 and Page 3 get "left" knuckles,
# Page 2 gets "right" knuckles so they interleave.
_hinge_x = -CASE_OUTER_W / 2 - HINGE_KNUCKLE_OD / 2 + WALL  # just outside back wall

# Page 1 hinges (top edge, connecting to Page 2)
p1_hinges = build_hinge_knuckles(CASE_OUTER_D, side="left")
p1_hinges = p1_hinges.rotate((0, 0, 0), (0, 1, 0), 90)  # orient along X axis
p1_hinges = p1_hinges.translate((_hinge_x, 0, _p1_h))
page1 = page1.union(p1_hinges)

# Page 2 hinges (bottom edge, connecting to Page 1)
p2_hinges_bottom = build_hinge_knuckles(CASE_OUTER_D, side="right")
p2_hinges_bottom = p2_hinges_bottom.rotate((0, 0, 0), (0, 1, 0), 90)
p2_hinges_bottom = p2_hinges_bottom.translate((_hinge_x, 0, _p2_assembly_z))
page2_positioned = page2_positioned.union(p2_hinges_bottom)

# Page 2 hinges (top edge, connecting to Page 3)
p2_hinges_top = build_hinge_knuckles(CASE_OUTER_D, side="left")
p2_hinges_top = p2_hinges_top.rotate((0, 0, 0), (0, 1, 0), 90)
p2_hinges_top = p2_hinges_top.translate((_hinge_x, 0, _p2_assembly_z + _p2_h))
page2_positioned = page2_positioned.union(p2_hinges_top)

# Page 3 hinges (bottom edge, connecting to Page 2)
p3_hinges = build_hinge_knuckles(CASE_OUTER_D, side="right")
p3_hinges = p3_hinges.rotate((0, 0, 0), (0, 1, 0), 90)
p3_hinges = p3_hinges.translate((_hinge_x, 0, _p3_assembly_z))
page3_positioned = page3_positioned.union(p3_hinges)
```

- [ ] **Step 3: Verify it builds**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 -c "code = open('designs/mobile-lab-case.py').read(); code = code.replace('from cq_server.ui import ui, show_object', ''); exec(code, {'show_object': lambda *a,**k: None}); print('Hinges OK')"`

Expected: `Hinges OK`

- [ ] **Step 4: Commit**

```bash
git add designs/mobile-lab-case.py
git commit -m "feat: add piano hinge knuckles connecting all three pages"
```

---

### Task 6: Latches and Handle

**Files:**
- Modify: `designs/mobile-lab-case.py`

- [ ] **Step 1: Add latch builder function and attach latches to Page 1 and Page 3**

```python
def build_latch(width=LATCH_W, height=LATCH_H, hook=LATCH_HOOK, wall=WALL):
    """Build a cantilever snap latch.

    The latch body attaches to Page 3 (top/cover). The catch lip
    hooks onto Page 1 (bottom). When the case is closed, Page 3
    folds over onto Page 1 and the latches click shut.

    Returns: (latch_body, latch_catch) tuple of CadQuery solids
    """
    # Latch body — flexible cantilever arm with hook at end
    body = (
        cq.Workplane("XY")
        .rect(width, wall)
        .extrude(height)
    )
    # Hook at the tip
    hook_solid = (
        cq.Workplane("XY")
        .workplane(offset=height - hook)
        .center(0, -hook / 2)
        .rect(width, hook)
        .extrude(hook)
    )
    body = body.union(hook_solid)

    # Catch on Page 1 — a small ledge the hook grabs
    catch = (
        cq.Workplane("XY")
        .rect(width + 2, hook + 1)
        .extrude(hook)
    )

    return body, catch


# --- Latches ---
# 2 latches evenly spaced along the front (+X) edge
_latch_x = CASE_OUTER_W / 2 + WALL  # front edge
_latch_spacing = CASE_OUTER_D / (LATCH_COUNT + 1)

for i in range(LATCH_COUNT):
    _latch_y = -CASE_OUTER_D / 2 + _latch_spacing * (i + 1)
    latch_body, latch_catch = build_latch()

    # Latch body on Page 3 (cover, top)
    latch_body = latch_body.translate((_latch_x, _latch_y, _p3_assembly_z))
    page3_positioned = page3_positioned.union(latch_body)

    # Latch catch on Page 1 (bottom)
    latch_catch = latch_catch.translate((_latch_x, _latch_y, 0))
    page1 = page1.union(latch_catch)
```

- [ ] **Step 2: Add carry handle on the hinge spine**

```python
# --- Handle ---
# Centered on the hinge spine (−X edge), attached to Page 2 (middle page)
_handle_x = _hinge_x - HINGE_KNUCKLE_OD / 2
_handle_base_z = _p2_assembly_z + _p2_h / 2

# Handle bridge — arch shape
handle = (
    cq.Workplane("XZ")
    .center(_handle_x, _handle_base_z)
    .rect(HANDLE_THICK, HANDLE_W)
    .extrude(HANDLE_H)
)
# Round the grip
handle = handle.edges("|Y").fillet(HANDLE_THICK / 2 - 0.5)

page2_positioned = page2_positioned.union(handle)
```

- [ ] **Step 3: Verify it builds**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 -c "code = open('designs/mobile-lab-case.py').read(); code = code.replace('from cq_server.ui import ui, show_object', ''); exec(code, {'show_object': lambda *a,**k: None}); print('Latches+Handle OK')"`

Expected: `Latches+Handle OK`

- [ ] **Step 4: Commit**

```bash
git add designs/mobile-lab-case.py
git commit -m "feat: add snap latches and carry handle"
```

---

### Task 7: Tile Split Lines for Printing

**Files:**
- Modify: `designs/mobile-lab-case.py`

- [ ] **Step 1: Add tile split function and split each page into 2 printable tiles**

```python
def split_into_tiles(body, split_x=0):
    """Split a body into two tiles along the X axis at split_x.

    Returns: (left_tile, right_tile) tuple of CadQuery solids.
    Each tile fits within the QIDI Q2 bed (275×295mm).
    """
    bb = body.val().BoundingBox()

    # Left tile: everything at X <= split_x
    left_cutter = (
        cq.Workplane("XY")
        .workplane(offset=bb.zmin - 1)
        .center((split_x + bb.xmax) / 2 + 0.5, 0)
        .rect(bb.xmax - split_x + 2, bb.ymax - bb.ymin + 10)
        .extrude(bb.zmax - bb.zmin + 10)
    )
    left_tile = body.cut(left_cutter)

    # Right tile: everything at X >= split_x
    right_cutter = (
        cq.Workplane("XY")
        .workplane(offset=bb.zmin - 1)
        .center((split_x + bb.xmin) / 2 - 0.5, 0)
        .rect(split_x - bb.xmin + 2, bb.ymax - bb.ymin + 10)
        .extrude(bb.zmax - bb.zmin + 10)
    )
    right_tile = body.cut(right_cutter)

    return left_tile, right_tile


# --- Tile splits ---
# Split each page into 2 tiles at X=0 (center line)
# Each half is ~206mm wide × ~271mm deep — fits QIDI Q2 bed (275×295mm)

page1_left, page1_right = split_into_tiles(page1, split_x=0)
page2_left, page2_right = split_into_tiles(page2, split_x=0)
page3_left, page3_right = split_into_tiles(page3, split_x=0)
```

Note: The tiles are split from the un-positioned pages (at Z=0) for export. Hinges, latches, and handle are attached before tile splitting. The positioned versions (with Z offsets) are for assembly preview only in cadquery-server.

- [ ] **Step 2: Add bolt hole alignment features at the split seam**

```python
# --- Alignment features at tile seams ---
# M3 bolt holes along the split line for joining tiles
_bolt_spacing = 60  # mm between bolt holes along seam
_bolt_dia = 3.2     # M3 clearance hole
_insert_dia = 4.5   # M3 heat-set insert outer diameter

def add_bolt_holes(tile, split_x, page_h, case_d, side="left"):
    """Add M3 bolt holes along the tile split seam.

    Left tile gets clearance holes, right tile gets insert-sized holes.
    """
    n_bolts = int(case_d / _bolt_spacing)
    for i in range(n_bolts):
        y = -case_d / 2 + _bolt_spacing / 2 + i * _bolt_spacing
        dia = _bolt_dia if side == "left" else _insert_dia
        hole = (
            cq.Workplane("XY")
            .workplane(offset=WALL / 2)
            .center(split_x, y)
            .circle(dia / 2)
            .extrude(page_h)
        )
        tile = tile.cut(hole)
    return tile

page1_left = add_bolt_holes(page1_left, 0, _p1_h, CASE_OUTER_D, "left")
page1_right = add_bolt_holes(page1_right, 0, _p1_h, CASE_OUTER_D, "right")
page2_left = add_bolt_holes(page2_left, 0, _p2_h, CASE_OUTER_D, "left")
page2_right = add_bolt_holes(page2_right, 0, _p2_h, CASE_OUTER_D, "right")
page3_left = add_bolt_holes(page3_left, 0, _p3_h, CASE_OUTER_D, "left")
page3_right = add_bolt_holes(page3_right, 0, _p3_h, CASE_OUTER_D, "right")
```

- [ ] **Step 3: Verify it builds**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 -c "code = open('designs/mobile-lab-case.py').read(); code = code.replace('from cq_server.ui import ui, show_object', ''); exec(code, {'show_object': lambda *a,**k: None}); print('Tiles OK')"`

Expected: `Tiles OK`

- [ ] **Step 4: Commit**

```bash
git add designs/mobile-lab-case.py
git commit -m "feat: add tile split and M3 bolt holes for print-bed-sized panels"
```

---

### Task 8: Export Script

**Files:**
- Create: `export_mobile_lab.py`

- [ ] **Step 1: Write the export script**

```python
#!/usr/bin/env python3
"""
Export STL/STEP files from mobile-lab-case.py for 3D printing.

Exports each tile at Z=0 for slicing. Also exports assembled
pages as STEP files for reference.
"""

import sys
import os
import re
from pathlib import Path


def export_files():
    try:
        import cadquery as cq
        print("✅ CadQuery available")
    except ImportError:
        print("❌ CadQuery not available. Install with: pip install cadquery")
        return False

    sys.path.insert(0, str(Path(__file__).parent / "designs"))

    try:
        with open("designs/mobile-lab-case.py", "r") as f:
            code = f.read()

        code = code.replace("from cq_server.ui import ui, show_object", "# cq_server removed")
        code = re.sub(r'show_object\(.*?\)', '# show_object removed', code, flags=re.DOTALL)

        g = {}
        exec(code, g)

        tiles = {
            "page1-left":  g["page1_left"],
            "page1-right": g["page1_right"],
            "page2-left":  g["page2_left"],
            "page2-right": g["page2_right"],
            "page3-left":  g["page3_left"],
            "page3-right": g["page3_right"],
        }

        pages = {
            "page1-assembled": g["page1"],
            "page2-assembled": g["page2"],
            "page3-assembled": g["page3"],
        }

        print("✅ Design objects loaded")

    except Exception as e:
        print(f"❌ Failed to load design: {e}")
        import traceback
        traceback.print_exc()
        return False

    os.makedirs("output", exist_ok=True)

    # Export tiles as STL (translated to Z=0 for printing)
    for name, solid in tiles.items():
        bb = solid.val().BoundingBox()
        z_offset = -bb.zmin  # translate to Z=0
        printable = solid.translate((0, 0, z_offset))

        stl_path = f"output/mobile-lab-{name}.stl"
        cq.exporters.export(printable, stl_path)
        print(f"✅ {stl_path}")

    # Export assembled pages as STEP (for reference)
    for name, solid in pages.items():
        step_path = f"output/mobile-lab-{name}.step"
        cq.exporters.export(solid, step_path)
        print(f"✅ {step_path}")

    print(f"\n🖨️  Print tiles on QIDI Q2 (275×295mm bed)")
    print(f"   Material: PETG | Layer: 0.2mm | Infill: 20% gyroid | Walls: 4")
    print(f"   Join tiles with M3 heat-set inserts + M3×8 bolts")
    return True


if __name__ == "__main__":
    export_files()
```

- [ ] **Step 2: Run the export script to verify**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 export_mobile_lab.py`

Expected: All STL and STEP files exported to `output/`

- [ ] **Step 3: Commit**

```bash
git add export_mobile_lab.py
git commit -m "feat: add STL/STEP export script for all tiles and assembled pages"
```

---

### Task 9: cadquery-server Integration and Final Assembly View

**Files:**
- Modify: `designs/mobile-lab-case.py`

- [ ] **Step 1: Ensure all show_object calls are at the end of the file with proper assembly positioning**

Verify the file ends with:

```python
# =============================================================================
# CADQUERY-SERVER PREVIEW
# =============================================================================
# Show assembled case with all three pages stacked

show_object(page1, name="Page 1 — Bottom (Power)", options={"color": "steelblue", "alpha": 0.7})

_p2_z = _p1_h + 2
page2_view = page2.translate((0, 0, _p2_z))
show_object(page2_view, name="Page 2 — Middle (Screens)", options={"color": "darkseagreen", "alpha": 0.7})

_p3_z = _p2_z + _p2_h + 2
page3_view = page3.translate((0, 0, _p3_z))
show_object(page3_view, name="Page 3 — Top (Accessories)", options={"color": "lightsalmon", "alpha": 0.7})
```

- [ ] **Step 2: Push to GitHub and restart cadquery-server**

```bash
git push
kubectl rollout restart deployment cadquery-server -n utilities
kubectl rollout status deployment cadquery-server -n utilities --timeout=120s
```

- [ ] **Step 3: Verify it renders in cadquery-server**

```bash
# Get service IP and trigger render
SVC_IP=$(kubectl get svc cadquery-server -n utilities -o jsonpath='{.spec.clusterIP}')
curl -s -o /dev/null -w "%{http_code}" "http://$SVC_IP:5000/json?m=mobile-lab-case" --max-time 90
```

Expected: HTTP 200

- [ ] **Step 4: Check logs for any errors**

```bash
kubectl logs deployment/cadquery-server -n utilities --tail=10
```

Expected: `GET /json?m=mobile-lab-case HTTP/1.1" 200 -` (no errors)

- [ ] **Step 5: Commit any final adjustments**

```bash
git add designs/mobile-lab-case.py
git commit -m "feat: finalize cadquery-server preview with assembly view"
git push
```

---

### Task 10: K8s Slicer Job Template

**Files:**
- Create: `k8s/slice-mobile-lab.yaml`

- [ ] **Step 1: Create the slicer job template**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: slice-mobile-lab
  namespace: utilities
spec:
  ttlSecondsAfterFinished: 3600
  backoffLimit: 1
  template:
    spec:
      restartPolicy: Never
      nodeSelector:
        kubernetes.io/arch: amd64
      containers:
      - name: slicer
        image: cznewt/prusa-slicer:latest
        command: ["/bin/bash", "-c"]
        args:
        - |
          set -e
          echo "=== PrusaSlicer — Mobile Lab Case Tiles ==="

          SLICER=/prusa-slicer/prusa-slicer
          INI=/tmp/petg.ini
          MOONRAKER="http://192.168.1.15:7125"

          cat > "$INI" << 'PROFILE'
          [print:PETG]
          layer_height = 0.2
          first_layer_height = 0.25
          perimeters = 4
          top_solid_layers = 5
          bottom_solid_layers = 4
          fill_density = 20%
          fill_pattern = gyroid
          external_perimeter_speed = 35
          infill_speed = 50
          travel_speed = 150
          bridge_speed = 20
          support_material = 0
          skirts = 2
          skirt_distance = 5
          brim_width = 5

          [filament:PETG]
          temperature = 240
          first_layer_temperature = 245
          bed_temperature = 80
          first_layer_bed_temperature = 85
          fan_always_on = 1
          min_fan_speed = 30
          max_fan_speed = 50
          bridge_fan_speed = 100

          [printer:QIDI_Q2]
          gcode_flavor = klipper
          bed_shape = 0x0,275x0,275x295,0x295
          max_print_height = 265
          nozzle_diameter = 0.4
          retract_length = 1.0
          retract_speed = 35
          retract_lift = 0.2
          start_gcode = G28\nG1 Z5 F5000
          end_gcode = END_PRINT
          PROFILE

          sed -i 's/^[[:space:]]*//' "$INI"

          fix_temps() {
            local FILE="$1"
            echo "  Post-processing temps in $FILE"
            sed -i 's/^M104 S200 ; set temperature/M140 S85 ; bed temp (first layer)\nM104 S245 ; extruder temp (first layer)/' "$FILE"
            sed -i 's/^M109 S200 ; set temperature and wait for it to be reached/M190 S85 ; wait for bed temp\nM109 S245 ; wait for extruder temp (first layer)/' "$FILE"
            sed -i '30,$ s/^M104 S200$/M104 S240 ; print temp/' "$FILE"
          }

          for TILE in /tmp/input/*.stl; do
            BASENAME=$(basename "$TILE" .stl)
            GCODE="/tmp/${BASENAME}.gcode"
            echo "--- Slicing $BASENAME ---"
            $SLICER --load "$INI" --center 137,147 \
              --output "$GCODE" --export-gcode "$TILE"
            fix_temps "$GCODE"
            echo "--- Uploading $BASENAME ---"
            curl -s -X DELETE "$MOONRAKER/server/files/gcodes/${BASENAME}.gcode" || true
            sleep 2
            curl -s -X POST "$MOONRAKER/server/files/upload" \
              -F "file=@${GCODE};filename=${BASENAME}.gcode" \
              -F "root=gcodes"
            echo ""
          done

          echo "=== All tiles sliced and uploaded ==="
        volumeMounts:
        - name: stl-input
          mountPath: /tmp/input
      volumes:
      - name: stl-input
        configMap:
          name: mobile-lab-stl-tiles
```

- [ ] **Step 2: Commit**

```bash
git add k8s/slice-mobile-lab.yaml
git commit -m "feat: add K8s slicer job template for PETG tile printing"
git push
```
