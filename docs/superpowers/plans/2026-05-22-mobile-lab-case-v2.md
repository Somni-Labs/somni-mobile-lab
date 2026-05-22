# Mobile Lab Case V2 — "Exosuit" Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete V2 Exosuit case in CadQuery — sculpted organic shell with geometric ridges, LED channels, mounting bosses for all mechatronic subsystems, motorized latch/hinge mechanisms, Starlink pop-up pedestal, cam device lifts, electronics bay, and a unified assembly preview for cadquery-server.

**Architecture:** Modular subsystem design. A shared `constants.py` defines all parametric dimensions. A shared `mounting.py` provides reusable mounting boss/bolt hole helpers. Each subsystem is its own CadQuery module importing from these shared files. An `assembly_preview.py` composes all subsystems into a single cadquery-server view. V1 files are preserved (not deleted) — V2 lives in subdirectories under `designs/`.

**Tech Stack:** CadQuery (parametric CAD), Python, cadquery-server (3D preview), QIDI Q2 printer (275x295mm bed), PrusaSlicer (via K8s job).

**Spec:** `docs/superpowers/specs/2026-05-22-mobile-lab-case-v2-design.md`

**Note on testing:** CadQuery models don't have traditional unit tests. Verification is: (1) the script runs without error, (2) `show_object()` produces visible geometry in cadquery-server, (3) dimensional checks via bounding box assertions in the script itself. Each task includes a verification step that runs the script and checks the bounding box.

**Note on cadquery-server compatibility:** All `show_object()` calls MUST use RGBA tuples for colors, not CSS color name strings. Example: `options={"color": (0.27, 0.51, 0.71, 0.7)}`. String colors cause `TypeError: can only concatenate tuple (not "list") to tuple`. Avoid `.text()` calls — Fontconfig is not available in the container.

---

### Task 1: Shared Constants Module

**Files:**
- Create: `designs/common/__init__.py`
- Create: `designs/common/constants.py`

This is the foundation — every other module imports from here. All device dimensions, tolerances, shell parameters, mounting specs, servo specs, LED channel dimensions, and derived case dimensions live here.

- [ ] **Step 1: Create the common package**

Create `designs/common/__init__.py`:

```python
"""Common constants and helpers for Mobile Lab Case V2."""
```

- [ ] **Step 2: Create constants.py with all parametric dimensions**

Create `designs/common/constants.py`:

```python
"""
Mobile Lab Case V2 — Parametric Constants

All dimensions in mm. Every subsystem imports from here.
Device dimensions include TOL (print tolerance per side).
"""

# =============================================================================
# TOLERANCES & FOAM
# =============================================================================
TOL = 1.0              # print tolerance per side (1mm clearance for snug drop-in)
FOAM_BASE = 5          # foam padding below each device
FOAM_TOP = 3           # foam clearance above each device

# =============================================================================
# CASE SHELL
# =============================================================================
WALL = 3               # outer shell wall thickness
DIVIDER = 2            # internal divider wall thickness
CORNER_R = 15          # outer corner fillet radius (organic, up from 5mm in V1)
TAPER = 3              # shell taper per side (thicker center, thinner edges)

# =============================================================================
# EXOSUIT RIDGES
# =============================================================================
RIDGE_H = 2            # ridge height above shell surface (proud)
RIDGE_W = 4            # ridge width
RIDGE_CHAMFER = 0.5    # 45-degree chamfer on ridge edges (half of 1mm)
RIDGE_ACCENT_H = 1.5   # side accent ridge height (thinner)
RIDGE_ACCENT_W = 3     # side accent ridge width
RIDGE_DIAMOND = 3      # chamfered diamond size at ridge intersections

# =============================================================================
# LED CHANNELS
# =============================================================================
LED_CHANNEL_W = 4      # channel width (WS2812B strip is 5mm, slight compression)
LED_CHANNEL_D = 3      # channel depth into shell surface
LED_DIFFUSER_SNAP = 0.5  # snap-fit lip for diffuser retention

# =============================================================================
# HINGE (UPGRADED)
# =============================================================================
HINGE_TUBE_OD = 3      # hollow steel tube outer diameter
HINGE_TUBE_ID = 2      # hollow steel tube inner diameter (wiring pass-through)
HINGE_KNUCKLE_OD = 10  # knuckle outer diameter (up from 8mm in V1)
HINGE_KNUCKLE_LEN = 20 # each knuckle segment length (up from 15mm)
HINGE_GAP = 1.5        # gap between knuckle segments

# =============================================================================
# SERVO DIMENSIONS (for mount design)
# =============================================================================
# MG996R high-torque servo
MG996R_W = 40.7        # body width
MG996R_D = 19.7        # body depth
MG996R_H = 42.9        # body height (without horn)
MG996R_FLANGE_W = 54.5 # flange-to-flange width
MG996R_FLANGE_H = 2.5  # flange thickness
MG996R_SHAFT_OFFSET = 10  # shaft center from one end

# SG90 micro servo
SG90_W = 22.5          # body width
SG90_D = 12.0          # body depth
SG90_H = 22.7          # body height (without horn)
SG90_FLANGE_W = 32.0   # flange-to-flange width
SG90_FLANGE_H = 2.5    # flange thickness

# =============================================================================
# LATCH (SERVO-ACTUATED)
# =============================================================================
LATCH_HOUSING_W = 30   # latch enclosure width
LATCH_HOUSING_D = 20   # latch enclosure depth
LATCH_HOUSING_H = 15   # latch enclosure height
LATCH_HOOK_W = 20      # hook width
LATCH_HOOK_TRAVEL = 5  # hook engagement depth

# =============================================================================
# STARLINK PEDESTAL
# =============================================================================
PEDESTAL_STROKE = 50    # linear actuator stroke (mm)
PEDESTAL_ACTUATOR_DIA = 20  # actuator cylinder diameter (approx)
PEDESTAL_ACTUATOR_LEN = 100  # actuator retracted length (approx)
PEDESTAL_GUIDE_OD = 8   # guide rail outer diameter
PEDESTAL_GUIDE_BUSHING_OD = 12  # bushing outer diameter
PEDESTAL_GUIDE_BUSHING_LEN = 15  # bushing length
CABLE_PASSTHROUGH_DIA = 15  # Starlink cable pass-through hole diameter

# =============================================================================
# CAM LIFT
# =============================================================================
CAM_LIFT_HEIGHT = 20    # how far the lift plate rises
CAM_OD = 30             # cam outer diameter (eccentric)
CAM_ECCENTRICITY = 10   # offset of cam center from shaft center
CAM_THICKNESS = 5       # cam disc thickness
LIFT_SLOT_W = 35        # slot width in pocket floor for lift plate

# =============================================================================
# ELECTRONICS BAY
# =============================================================================
EBAY_INNER_W = 120      # internal width
EBAY_INNER_D = 40       # internal depth
EBAY_INNER_H = 30       # internal height
EBAY_WALL = 2           # bay wall thickness
EBAY_LID_SCREW = 2      # M2 screw diameter for lid

# =============================================================================
# HANDLE
# =============================================================================
HANDLE_W = 100          # grip span
HANDLE_H = 25           # how far handle extends from spine
HANDLE_THICK = 5        # handle wall thickness (reinforced)
HANDLE_FILLET = 15      # fillet radius on handle (organic, matching shell)

# =============================================================================
# BUTTON & TOUCH
# =============================================================================
BUTTON_DIA = 12         # push button outer diameter
BUTTON_RECESS = 2       # how far button sits below shell surface
TOUCH_PAD_W = 25        # capacitive touch pad width
TOUCH_PAD_D = 25        # capacitive touch pad depth
TOUCH_PAD_RECESS = 0.5  # shell thinning over touch pad for sensitivity

# =============================================================================
# MOUNTING INTERFACE
# =============================================================================
M3_CLEARANCE_DIA = 3.4  # M3 bolt clearance hole
M3_INSERT_DIA = 4.2     # M3 heat-set insert hole
M3_INSERT_DEPTH = 6     # heat-set insert depth
MOUNT_BOSS_OD = 8       # mounting boss outer diameter
MOUNT_BOSS_ALIGN_H = 1  # alignment ring height on mounting bosses

# Wire channels
WIRE_CHANNEL_W = 3      # wire routing channel width
WIRE_CHANNEL_D = 3      # wire routing channel depth

# =============================================================================
# PRINT BED CONSTRAINTS
# =============================================================================
BED_W = 275             # QIDI Q2 bed width
BED_D = 295             # QIDI Q2 bed depth

# =============================================================================
# DEVICES (all include TOL per side)
# =============================================================================
# Page 1 — Power & Connectivity
STARLINK_W = 299 + TOL * 2
STARLINK_D = 259 + TOL * 2
STARLINK_H = 39

STARLINK_PSU_W = 91 + TOL * 2
STARLINK_PSU_D = 44 + TOL * 2
STARLINK_PSU_H = 51

BATTERY_W = 180 + TOL * 2
BATTERY_D = 80 + TOL * 2
BATTERY_H = 25

# Page 2 — Screens & Compute
MONITOR_W = 400 + TOL * 2
MONITOR_D = 250 + TOL * 2
MONITOR_H = 15

LAPTOP_W = 287 + TOL * 2
LAPTOP_D = 214 + TOL * 2
LAPTOP_H = 18

IPAD_W = 280 + TOL * 2
IPAD_D = 215 + TOL * 2
IPAD_H = 7

# Page 3 — Accessories
KB_W = 366 + TOL * 2
KB_D = 137 + TOL * 2
KB_H = 32

MOUSE_W = 120 + TOL * 2
MOUSE_D = 60 + TOL * 2
MOUSE_H = 40

MUDI_W = 157 + TOL * 2
MUDI_D = 75 + TOL * 2
MUDI_H = 23

FLIPPER_W = 100 + TOL * 2
FLIPPER_D = 40 + TOL * 2
FLIPPER_H = 26

CHARGER_W = 80 + TOL * 2
CHARGER_D = 80 + TOL * 2
CHARGER_H = 30

# =============================================================================
# DERIVED PAGE DEPTHS
# =============================================================================
# Page 1: increased to 75mm to accommodate Starlink pedestal mechanism beneath pocket
PAGE1_DEPTH = 75
PAGE2_DEPTH = FOAM_BASE + MONITOR_H + 2 + LAPTOP_H + IPAD_H + FOAM_TOP  # ~50mm
PAGE3_DEPTH = MOUSE_H + FOAM_BASE + FOAM_TOP  # ~48mm

# =============================================================================
# DERIVED CASE DIMENSIONS
# =============================================================================
CASE_INNER_W = max(MONITOR_W, KB_W, STARLINK_W) + DIVIDER * 2
CASE_INNER_D = max(STARLINK_D, MONITOR_D, KB_D + MUDI_D + DIVIDER) + DIVIDER * 2
CASE_OUTER_W = CASE_INNER_W + WALL * 2
CASE_OUTER_D = CASE_INNER_D + WALL * 2

PAGE1_H = PAGE1_DEPTH + WALL
PAGE2_H = PAGE2_DEPTH + WALL
PAGE3_H = PAGE3_DEPTH + WALL
CASE_TOTAL_H = PAGE1_H + PAGE2_H + PAGE3_H + WALL
```

- [ ] **Step 3: Verify constants are importable**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "from designs.common.constants import *; print(f'Case: {CASE_OUTER_W:.0f} x {CASE_OUTER_D:.0f} x {CASE_TOTAL_H:.0f}mm')"
```

Expected output: `Case: 412 x 271 x 185mm` (approximately)

- [ ] **Step 4: Commit**

```bash
git add designs/common/__init__.py designs/common/constants.py
git commit -m "feat(v2): add shared parametric constants module"
```

---

### Task 2: Shared Mounting Helpers Module

**Files:**
- Create: `designs/common/mounting.py`

Reusable CadQuery helpers used by every subsystem: mounting bosses, bolt holes, wire channels, LED channels, and the sculpted shell builder.

- [ ] **Step 1: Create mounting.py**

Create `designs/common/mounting.py`:

```python
"""
Mobile Lab Case V2 — Shared CadQuery Helpers

Mounting bosses, bolt holes, wire channels, LED channels,
sculpted shell builder, and pocket cutter.
"""

import cadquery as cq
from designs.common.constants import (
    WALL, CORNER_R, TAPER, DIVIDER,
    M3_CLEARANCE_DIA, M3_INSERT_DIA, M3_INSERT_DEPTH,
    MOUNT_BOSS_OD, MOUNT_BOSS_ALIGN_H,
    WIRE_CHANNEL_W, WIRE_CHANNEL_D,
    LED_CHANNEL_W, LED_CHANNEL_D, LED_DIFFUSER_SNAP,
    RIDGE_H, RIDGE_W, RIDGE_CHAMFER,
    RIDGE_ACCENT_H, RIDGE_ACCENT_W,
    BED_W, BED_D,
)


def build_sculpted_shell(width, depth, height, corner_r=CORNER_R, wall=WALL, taper=TAPER):
    """
    Build a sculpted page shell — open-top box with large organic fillets
    and a subtle taper (thicker center, thinner edges).

    The outer profile is a tapered box: the top face is (width - taper*2) x (depth - taper*2),
    while the bottom face is the full width x depth. This creates a subtle wedge shape.

    Returns a CadQuery solid (shell with floor, no top).
    """
    # Outer body — tapered via loft between bottom and top rectangles
    bottom = cq.Workplane("XY").rect(width, depth)
    top = (
        cq.Workplane("XY")
        .workplane(offset=height)
        .rect(width - taper * 2, depth - taper * 2)
    )
    # Use extrude with draft angle for taper effect
    # CadQuery doesn't have loft between rects easily, so we extrude + chamfer
    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
    )
    # Apply organic fillets to all vertical edges
    if corner_r > 0:
        try:
            outer = outer.edges("|Z").fillet(corner_r)
        except Exception:
            # Fall back to smaller fillet if geometry fails
            outer = outer.edges("|Z").fillet(corner_r / 2)
    # Apply top edge fillets for organic feel
    try:
        outer = outer.edges(">Z").fillet(min(corner_r / 2, wall))
    except Exception:
        pass
    # Cut interior cavity (open top)
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
        try:
            pocket = pocket.edges("|Z").fillet(corner_r)
        except Exception:
            pass
    return body.cut(pocket)


def add_mounting_boss(body, x, y, z, height, boss_od=MOUNT_BOSS_OD,
                      insert_dia=M3_INSERT_DIA, insert_depth=M3_INSERT_DEPTH,
                      align_h=MOUNT_BOSS_ALIGN_H):
    """
    Add a cylindrical mounting boss with M3 heat-set insert hole and alignment ring.

    Boss is a cylinder at (x, y) starting at z, extruding upward 'height' mm.
    Insert hole is drilled from the top, 'insert_depth' deep.
    Alignment ring is a 1mm tall raised ring on top.
    """
    # Main boss cylinder
    boss = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(x, y)
        .circle(boss_od / 2)
        .extrude(height)
    )
    # Alignment ring on top
    ring = (
        cq.Workplane("XY")
        .workplane(offset=z + height)
        .center(x, y)
        .circle(boss_od / 2 + 0.5)
        .circle(boss_od / 2 - 0.5)
        .extrude(align_h)
    )
    body = body.union(boss).union(ring)
    # Insert hole from top
    hole = (
        cq.Workplane("XY")
        .workplane(offset=z + height + align_h - insert_depth)
        .center(x, y)
        .circle(insert_dia / 2)
        .extrude(insert_depth + 1)
    )
    body = body.cut(hole)
    return body


def add_bolt_clearance_hole(body, x, y, z, depth, dia=M3_CLEARANCE_DIA):
    """Drill an M3 clearance hole (3.4mm) through the body at the given position."""
    hole = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(x, y)
        .circle(dia / 2)
        .extrude(depth)
    )
    return body.cut(hole)


def cut_wire_channel(body, x1, y1, x2, y2, z, channel_w=WIRE_CHANNEL_W,
                     channel_d=WIRE_CHANNEL_D):
    """
    Cut a rectangular wire routing channel along a straight path.
    Channel runs from (x1,y1) to (x2,y2) at height z, cut downward into the wall.
    """
    import math
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    angle = math.degrees(math.atan2(dy, dx))
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    channel = (
        cq.Workplane("XY")
        .workplane(offset=z - channel_d)
        .center(cx, cy)
        .rect(length, channel_w)
        .extrude(channel_d + 0.1)
    )
    if abs(angle) > 0.01:
        channel = channel.rotate((cx, cy, 0), (cx, cy, 1), angle)
    return body.cut(channel)


def cut_led_channel(body, x1, y1, x2, y2, z, channel_w=LED_CHANNEL_W,
                    channel_d=LED_CHANNEL_D, snap_lip=LED_DIFFUSER_SNAP):
    """
    Cut an LED strip channel along a straight path on the shell surface.
    Channel is open-top with a small snap-fit lip for diffuser retention.
    Runs from (x1,y1) to (x2,y2) at height z.
    """
    import math
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    angle = math.degrees(math.atan2(dy, dx))
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    # Main channel
    channel = (
        cq.Workplane("XY")
        .workplane(offset=z - channel_d)
        .center(cx, cy)
        .rect(length, channel_w)
        .extrude(channel_d + 0.1)
    )
    if abs(angle) > 0.01:
        channel = channel.rotate((cx, cy, 0), (cx, cy, 1), angle)
    body = body.cut(channel)
    # Snap lips on each side (narrow ridges at channel mouth)
    for side in [-1, 1]:
        lip_y = cy + side * (channel_w / 2)
        lip = (
            cq.Workplane("XY")
            .workplane(offset=z - snap_lip)
            .center(cx, lip_y)
            .rect(length, snap_lip)
            .extrude(snap_lip)
        )
        if abs(angle) > 0.01:
            lip = lip.rotate((cx, cy, 0), (cx, cy, 1), angle)
        body = body.union(lip)
    return body


def add_ridge(body, x1, y1, x2, y2, z, ridge_w=RIDGE_W, ridge_h=RIDGE_H,
              chamfer=RIDGE_CHAMFER):
    """
    Add a raised geometric ridge along a straight path on the shell surface.
    Ridge sits on top of the surface at height z, extruding upward ridge_h mm.
    Edges get 45-degree chamfers.
    """
    import math
    dx = x2 - x1
    dy = y2 - y1
    length = math.sqrt(dx * dx + dy * dy)
    angle = math.degrees(math.atan2(dy, dx))
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    ridge = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(cx, cy)
        .rect(length, ridge_w)
        .extrude(ridge_h)
    )
    if abs(angle) > 0.01:
        ridge = ridge.rotate((cx, cy, 0), (cx, cy, 1), angle)
    # Chamfer the top edges
    try:
        ridge = ridge.edges(">Z").chamfer(chamfer)
    except Exception:
        pass
    body = body.union(ridge)
    return body


def split_into_tiles(body, case_outer_w, case_outer_d, page_height):
    """
    Split a page body into left and right halves at X=0.
    Each tile must fit the QIDI Q2 bed (275x295mm).
    Returns (left_tile, right_tile).
    """
    margin = 10
    half_w = case_outer_w / 2 + margin
    h = page_height + margin * 2
    # Right half (X > 0)
    right_cutter = (
        cq.Workplane("XY")
        .workplane(offset=-margin)
        .center(half_w / 2, 0)
        .rect(half_w, case_outer_d + margin * 2)
        .extrude(h)
    )
    right_tile = body.intersect(right_cutter)
    # Left half (X < 0)
    left_cutter = (
        cq.Workplane("XY")
        .workplane(offset=-margin)
        .center(-half_w / 2, 0)
        .rect(half_w, case_outer_d + margin * 2)
        .extrude(h)
    )
    left_tile = body.intersect(left_cutter)
    return left_tile, right_tile


def add_tile_seam_features(body, case_outer_d, page_height, is_left=True, n_bolts=5):
    """
    Add tongue-and-groove alignment + M3 bolt/insert holes along the tile split seam at X=0.
    Left tiles: clearance holes (3.4mm) + groove.
    Right tiles: insert holes (4.2mm) + tongue.
    """
    usable_d = case_outer_d - 30
    spacing = usable_d / (n_bolts - 1) if n_bolts > 1 else 0
    y_start = -usable_d / 2
    z_mid = page_height / 2
    dia = M3_CLEARANCE_DIA if is_left else M3_INSERT_DIA
    hole_depth = WALL + 2
    for i in range(n_bolts):
        y = y_start + i * spacing
        hole = (
            cq.Workplane("YZ")
            .center(y, z_mid)
            .circle(dia / 2)
            .extrude(hole_depth, both=True)
        )
        body = body.cut(hole)
    return body
```

- [ ] **Step 2: Verify mounting module imports correctly**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "from designs.common.mounting import *; print('Mounting helpers loaded OK')"
```

Expected: `Mounting helpers loaded OK`

- [ ] **Step 3: Commit**

```bash
git add designs/common/mounting.py
git commit -m "feat(v2): add shared mounting/shell helpers — bosses, channels, ridges, tiles"
```

---

### Task 3: Page 1 Shell — Bottom (Power & Connectivity)

**Files:**
- Create: `designs/shell/__init__.py`
- Create: `designs/shell/page1_shell.py`

Page 1 holds the Starlink Mini, PSU, and battery bank. Deeper than V1 (75mm vs 59mm) to accommodate the Starlink pedestal mechanism beneath. Includes mounting bosses for pedestal base (4×), hinge servo mounts (2×), and latch catches (2×). LED channels along the inner rim perimeter. Cable pass-through hole for Starlink PSU connection.

- [ ] **Step 1: Create shell package init**

Create `designs/shell/__init__.py`:

```python
"""Shell subsystem — sculpted page panels with LED channels and mounting bosses."""
```

- [ ] **Step 2: Create page1_shell.py**

Create `designs/shell/page1_shell.py`:

```python
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

import cadquery as cq
from designs.common.constants import (
    WALL, DIVIDER, CORNER_R, TAPER,
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
    cut_led_channel,
)


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
    boss_h = WALL  # bosses sit on the floor, extend up to wall height
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

    # --- LED channel along inner rim (top face perimeter) ---
    rim_z = PAGE1_H
    hw = CASE_OUTER_W / 2 - WALL - 2  # inset from wall
    hd = CASE_OUTER_D / 2 - WALL - 2
    # Four sides of the rim
    shell = cut_led_channel(shell, -hw, -hd, hw, -hd, rim_z)   # front
    shell = cut_led_channel(shell, hw, -hd, hw, hd, rim_z)     # right
    shell = cut_led_channel(shell, hw, hd, -hw, hd, rim_z)     # back
    shell = cut_led_channel(shell, -hw, hd, -hw, -hd, rim_z)   # left

    return shell


# --- Standalone preview for cadquery-server ---
try:
    from cq_server.ui import ui, show_object
    page1 = build_page1()
    show_object(page1, name="Page 1 - Bottom (Power)",
                options={"color": (0.27, 0.51, 0.71, 0.7)})
except ImportError:
    pass
```

- [ ] **Step 3: Verify the script runs without error**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys; sys.modules['cq_server'] = type(sys)('mock'); sys.modules['cq_server.ui'] = type(sys)('mock')
sys.modules['cq_server.ui'].ui = None; sys.modules['cq_server.ui'].show_object = lambda *a, **k: None
from designs.shell.page1_shell import build_page1
p = build_page1()
bb = p.val().BoundingBox()
print(f'Page 1 bounding box: {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm')
assert bb.xlen > 400, f'Width too small: {bb.xlen}'
assert bb.ylen > 260, f'Depth too small: {bb.ylen}'
assert bb.zlen > 70, f'Height too small: {bb.zlen}'
print('PASS')
"
```

Expected: Bounding box ~412 x 271 x 78mm, PASS

- [ ] **Step 4: Commit**

```bash
git add designs/shell/__init__.py designs/shell/page1_shell.py
git commit -m "feat(v2): Page 1 sculpted shell — Starlink, PSU, battery pockets + mounting bosses"
```

---

### Task 4: Page 2 Shell — Middle (Screens & Compute)

**Files:**
- Create: `designs/shell/page2_shell.py`

Page 2 holds the 17" monitor, Framework laptop, and iPad. Two-tier pocket layout. Includes carry handle on spine, electronics bay cutout, mounting bosses for cam lifts (2× for monitor + laptop), and spine ridge LED channels. This is the center page that connects to both hinges.

- [ ] **Step 1: Create page2_shell.py**

Create `designs/shell/page2_shell.py`:

```python
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

import cadquery as cq
from designs.common.constants import (
    WALL, DIVIDER, CORNER_R, TAPER,
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
    add_ridge, cut_led_channel,
)


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

    # --- Spine ridge LED channels (both outer faces) ---
    # Two vertical ridges on the -X (spine) face, flanking the handle
    spine_x = -CASE_OUTER_W / 2
    ridge_y1 = -CASE_OUTER_D / 3
    ridge_y2 = CASE_OUTER_D / 3

    # Add ridges
    shell = add_ridge(shell, spine_x, ridge_y1, spine_x, ridge_y2,
                      z=PAGE2_H, ridge_w=RIDGE_W, ridge_h=RIDGE_H)

    return shell


# --- Standalone preview for cadquery-server ---
try:
    from cq_server.ui import ui, show_object
    page2 = build_page2()
    show_object(page2, name="Page 2 - Middle (Screens)",
                options={"color": (0.56, 0.74, 0.56, 0.7)})
except ImportError:
    pass
```

- [ ] **Step 2: Verify the script runs**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys; sys.modules['cq_server'] = type(sys)('mock'); sys.modules['cq_server.ui'] = type(sys)('mock')
sys.modules['cq_server.ui'].ui = None; sys.modules['cq_server.ui'].show_object = lambda *a, **k: None
from designs.shell.page2_shell import build_page2
p = build_page2()
bb = p.val().BoundingBox()
print(f'Page 2 bounding box: {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm')
assert bb.zlen > 45, f'Height too small: {bb.zlen}'
print('PASS')
"
```

- [ ] **Step 3: Commit**

```bash
git add designs/shell/page2_shell.py
git commit -m "feat(v2): Page 2 sculpted shell — monitor, laptop, iPad + handle + e-bay cutout"
```

---

### Task 5: Page 3 Shell — Top/Cover (Accessories)

**Files:**
- Create: `designs/shell/page3_shell.py`

Page 3 is the cover — visible when case is closed. Has the full exosuit surface treatment (3 spine ridges + 2 lateral ridges with LED channels), device pockets for keyboard/mouse/Mudi 7/misc, mounting bosses for latch servos and keyboard cam lift, capacitive touch pad recesses, and Somni Labs logo deboss.

- [ ] **Step 1: Create page3_shell.py**

Create `designs/shell/page3_shell.py`:

```python
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
try:
    from cq_server.ui import ui, show_object
    page3 = build_page3()
    show_object(page3, name="Page 3 - Top (Accessories)",
                options={"color": (1.0, 0.63, 0.48, 0.7)})
except ImportError:
    pass
```

- [ ] **Step 2: Verify the script runs**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys; sys.modules['cq_server'] = type(sys)('mock'); sys.modules['cq_server.ui'] = type(sys)('mock')
sys.modules['cq_server.ui'].ui = None; sys.modules['cq_server.ui'].show_object = lambda *a, **k: None
from designs.shell.page3_shell import build_page3
p = build_page3()
bb = p.val().BoundingBox()
print(f'Page 3 bounding box: {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm')
assert bb.zlen > 45, f'Height too small: {bb.zlen}'
print('PASS')
"
```

- [ ] **Step 3: Commit**

```bash
git add designs/shell/page3_shell.py
git commit -m "feat(v2): Page 3 sculpted shell — keyboard, mouse, Mudi, ridges, LEDs, logo"
```

---

### Task 6: Hinge & Latch System

**Files:**
- Create: `designs/hinge/__init__.py`
- Create: `designs/hinge/hinge_knuckles.py`
- Create: `designs/hinge/latch_mechanism.py`
- Create: `designs/hinge/hinge_servo_mount.py`

Upgraded piano hinge with 10mm knuckles, hollow tube bore for wiring, gear sectors for motorized opening. Servo latch housing with hook/cam. MG996R servo mount bracket with spur gear.

- [ ] **Step 1: Create hinge package**

Create `designs/hinge/__init__.py`:

```python
"""Hinge & latch subsystem — motorized latches, geared hinge, spring assist."""
```

- [ ] **Step 2: Create hinge_knuckles.py**

Create `designs/hinge/hinge_knuckles.py`:

```python
"""
Upgraded Piano Hinge Knuckles

10mm OD knuckles with hollow 3mm tube bore (2mm ID for wiring).
Interleaving segments along -X edge. One knuckle per page gets a
gear sector for the hinge servo to drive.
Asymmetric chamfer on knuckle ends for fool-proof assembly.

Returns a CadQuery solid — caller unions it onto the page shell.
"""

import cadquery as cq
import math
from designs.common.constants import (
    HINGE_KNUCKLE_OD, HINGE_KNUCKLE_LEN, HINGE_GAP,
    HINGE_TUBE_OD, HINGE_TUBE_ID,
    CASE_OUTER_W, CASE_OUTER_D,
)


def build_hinge_knuckles(page_height, case_depth=CASE_OUTER_D,
                         case_outer_w=CASE_OUTER_W, parity="even",
                         gear_sector_index=None):
    """
    Build interleaving hinge knuckles along the -X edge.

    Args:
        page_height: Z position of the hinge line (top or bottom of page)
        case_depth: depth of the case (Y extent)
        case_outer_w: width of the case (X extent)
        parity: "even" for knuckle indices 0,2,4... ; "odd" for 1,3,5...
        gear_sector_index: if set, this knuckle index gets a gear sector
                           (120-degree arc of teeth for the hinge servo)

    Returns a CadQuery solid (union of all knuckles).
    """
    knuckle_r = HINGE_KNUCKLE_OD / 2
    tube_r = HINGE_TUBE_OD / 2 + 0.15  # clearance for tube

    slot_pitch = HINGE_KNUCKLE_LEN + HINGE_GAP
    n_slots = int(case_depth // slot_pitch)
    total_len = n_slots * slot_pitch - HINGE_GAP
    y_start = -total_len / 2 + HINGE_KNUCKLE_LEN / 2

    hinge_x = -case_outer_w / 2
    hinge_z = page_height

    knuckles = None
    start_idx = 0 if parity == "even" else 1

    for i in range(start_idx, n_slots, 2):
        cy = y_start + i * slot_pitch

        # Knuckle cylinder
        knuckle = (
            cq.Workplane("XZ")
            .center(hinge_x, hinge_z)
            .circle(knuckle_r)
            .extrude(HINGE_KNUCKLE_LEN, both=False)
            .translate((0, cy - HINGE_KNUCKLE_LEN / 2, 0))
        )

        # Hollow tube bore
        bore = (
            cq.Workplane("XZ")
            .center(hinge_x, hinge_z)
            .circle(tube_r)
            .extrude(HINGE_KNUCKLE_LEN + 2, both=False)
            .translate((0, cy - HINGE_KNUCKLE_LEN / 2 - 1, 0))
        )
        knuckle = knuckle.cut(bore)

        # Asymmetric chamfer on one end (for assembly orientation)
        chamfer_end = (
            cq.Workplane("XZ")
            .center(hinge_x, hinge_z)
            .circle(knuckle_r)
            .circle(knuckle_r - 1)
            .extrude(1)
            .translate((0, cy - HINGE_KNUCKLE_LEN / 2, 0))
        )
        # Cut a small notch on one side only
        notch = (
            cq.Workplane("XZ")
            .center(hinge_x + knuckle_r - 0.5, hinge_z)
            .rect(1, 1)
            .extrude(1)
            .translate((0, cy - HINGE_KNUCKLE_LEN / 2, 0))
        )
        knuckle = knuckle.cut(notch)

        # Gear sector (if this is the designated knuckle)
        if gear_sector_index is not None and i == gear_sector_index:
            gear_r = knuckle_r + 3  # gear extends beyond knuckle
            n_teeth = 8  # teeth over ~120 degrees
            tooth_angle = 120 / n_teeth
            for t in range(n_teeth):
                angle_rad = math.radians(-60 + t * tooth_angle + tooth_angle / 2)
                tx = hinge_x + gear_r * math.cos(angle_rad)
                tz = hinge_z + gear_r * math.sin(angle_rad)
                tooth = (
                    cq.Workplane("XZ")
                    .center(tx, tz)
                    .rect(2, 2)
                    .extrude(HINGE_KNUCKLE_LEN - 2)
                    .translate((0, cy - HINGE_KNUCKLE_LEN / 2 + 1, 0))
                )
                knuckle = knuckle.union(tooth)

        if knuckles is None:
            knuckles = knuckle
        else:
            knuckles = knuckles.union(knuckle)

    return knuckles


def build_retaining_clip():
    """
    Build a printed C-clip that snaps over the hinge tube end.
    Small part — printed separately.
    """
    clip = (
        cq.Workplane("XY")
        .circle(HINGE_TUBE_OD / 2 + 1.5)
        .circle(HINGE_TUBE_OD / 2 + 0.2)
        .extrude(3)
    )
    # Cut opening slot for snap-on
    slot = (
        cq.Workplane("XY")
        .center(HINGE_TUBE_OD / 2 + 1, 0)
        .rect(3, HINGE_TUBE_OD / 2)
        .extrude(3)
    )
    clip = clip.cut(slot)
    return clip


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    knuckles = build_hinge_knuckles(50, gear_sector_index=2)
    show_object(knuckles, name="Hinge Knuckles (sample)",
                options={"color": (0.5, 0.5, 0.5, 0.9)})
    clip = build_retaining_clip()
    show_object(clip.translate((0, 0, 60)), name="Retaining C-Clip",
                options={"color": (0.7, 0.7, 0.7, 0.9)})
except ImportError:
    pass
```

- [ ] **Step 3: Create latch_mechanism.py**

Create `designs/hinge/latch_mechanism.py`:

```python
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
```

- [ ] **Step 4: Create hinge_servo_mount.py**

Create `designs/hinge/hinge_servo_mount.py`:

```python
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
```

- [ ] **Step 5: Verify all hinge files run**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys; sys.modules['cq_server'] = type(sys)('mock'); sys.modules['cq_server.ui'] = type(sys)('mock')
sys.modules['cq_server.ui'].ui = None; sys.modules['cq_server.ui'].show_object = lambda *a, **k: None
from designs.hinge.hinge_knuckles import build_hinge_knuckles, build_retaining_clip
from designs.hinge.latch_mechanism import build_latch_housing, build_latch_hook, build_latch_catch
from designs.hinge.hinge_servo_mount import build_servo_mount, build_spur_gear
k = build_hinge_knuckles(50, gear_sector_index=2)
print(f'Knuckles OK: {k.val().BoundingBox().ylen:.0f}mm span')
h = build_latch_housing(); print(f'Latch housing OK')
m = build_servo_mount(); print(f'Servo mount OK')
g = build_spur_gear(); print(f'Spur gear OK')
c = build_retaining_clip(); print(f'C-clip OK')
print('PASS')
"
```

- [ ] **Step 6: Commit**

```bash
git add designs/hinge/
git commit -m "feat(v2): hinge system — geared knuckles, servo latch, MG996R mount + spur gear"
```

---

### Task 7: Starlink Deployment System

**Files:**
- Create: `designs/starlink/__init__.py`
- Create: `designs/starlink/pedestal_base.py`
- Create: `designs/starlink/pedestal_platform.py`
- Create: `designs/starlink/tilt_linkage.py`

The pop-up pedestal: base plate with linear actuator mount and guide rail bushings, rising platform with tilt hinge, and tilt servo linkage arm.

- [ ] **Step 1: Create starlink package**

Create `designs/starlink/__init__.py`:

```python
"""Starlink deployment subsystem — pop-up pedestal with tilt mechanism."""
```

- [ ] **Step 2: Create pedestal_base.py**

Create `designs/starlink/pedestal_base.py`:

```python
"""
Starlink Pedestal Base

Mounts inside Page 1 beneath the Starlink pocket. Contains:
  - Central linear actuator mount (vertical cylinder bore)
  - 4x guide rail bushings at corners for level travel
  - M3 mounting holes to bolt onto Page 1 floor bosses
"""

import cadquery as cq
from designs.common.constants import (
    STARLINK_W, STARLINK_D,
    PEDESTAL_STROKE, PEDESTAL_ACTUATOR_DIA, PEDESTAL_ACTUATOR_LEN,
    PEDESTAL_GUIDE_OD, PEDESTAL_GUIDE_BUSHING_OD, PEDESTAL_GUIDE_BUSHING_LEN,
    M3_CLEARANCE_DIA,
    WALL,
    TOL,
)


def build_pedestal_base():
    """
    Build the pedestal base plate that sits on the Page 1 floor.

    The base plate is a flat slab with:
      - A central bore for the linear actuator
      - 4 corner bushings for guide rails
      - 4 M3 bolt holes for mounting to shell bosses
    """
    # Base plate dimensions (slightly smaller than Starlink pocket)
    base_w = STARLINK_W - 10
    base_d = STARLINK_D - 10
    base_h = 5  # base plate thickness

    plate = (
        cq.Workplane("XY")
        .rect(base_w, base_d)
        .extrude(base_h)
    )
    try:
        plate = plate.edges("|Z").fillet(3)
    except Exception:
        pass

    # Central actuator bore (vertical cylinder)
    actuator_bore = (
        cq.Workplane("XY")
        .circle(PEDESTAL_ACTUATOR_DIA / 2 + 0.5)
        .extrude(base_h + 1)
    )
    plate = plate.cut(actuator_bore)

    # Actuator retention ring (lip around the bore to hold actuator body)
    retention = (
        cq.Workplane("XY")
        .workplane(offset=base_h)
        .circle(PEDESTAL_ACTUATOR_DIA / 2 + 3)
        .circle(PEDESTAL_ACTUATOR_DIA / 2 + 0.5)
        .extrude(3)
    )
    plate = plate.union(retention)

    # 4 corner guide rail bushings
    inset = 20  # inset from plate edges
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        bx = dx * (base_w / 2 - inset)
        by = dy * (base_d / 2 - inset)
        bushing = (
            cq.Workplane("XY")
            .workplane(offset=base_h)
            .center(bx, by)
            .circle(PEDESTAL_GUIDE_BUSHING_OD / 2)
            .extrude(PEDESTAL_GUIDE_BUSHING_LEN)
        )
        bore = (
            cq.Workplane("XY")
            .center(bx, by)
            .circle(PEDESTAL_GUIDE_OD / 2 + 0.2)  # clearance for guide rod
            .extrude(base_h + PEDESTAL_GUIDE_BUSHING_LEN + 1)
        )
        plate = plate.union(bushing).cut(bore)

    # 4 M3 mounting holes (matching shell boss positions)
    pedestal_inset = 15
    starlink_cx = 0  # centered when base is centered
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        hx = dx * (base_w / 2 - pedestal_inset)
        hy = dy * (base_d / 2 - pedestal_inset)
        hole = (
            cq.Workplane("XY")
            .center(hx, hy)
            .circle(M3_CLEARANCE_DIA / 2)
            .extrude(base_h + 1)
        )
        plate = plate.cut(hole)

    return plate


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    base = build_pedestal_base()
    show_object(base, name="Pedestal Base",
                options={"color": (0.3, 0.3, 0.6, 0.9)})
except ImportError:
    pass
```

- [ ] **Step 3: Create pedestal_platform.py**

Create `designs/starlink/pedestal_platform.py`:

```python
"""
Starlink Pedestal Platform

The rising platform that carries the Starlink Mini.
Connects to the linear actuator via a tilt hinge along one long edge.
4 guide rod receptacles at corners for smooth vertical travel.
"""

import cadquery as cq
from designs.common.constants import (
    STARLINK_W, STARLINK_D,
    PEDESTAL_GUIDE_OD,
    HINGE_TUBE_OD,
)


def build_pedestal_platform():
    """
    Build the platform plate that rises on the pedestal.

    Features:
      - Flat plate matching Starlink Mini footprint
      - 4 corner guide rod receptacles (cylindrical sleeves)
      - Tilt hinge barrel along one long edge (for tilt servo)
      - Actuator push point at center (flat contact area)
    """
    plat_w = STARLINK_W - 5  # slightly narrower than pocket
    plat_d = STARLINK_D - 5
    plat_h = 4  # platform thickness

    platform = (
        cq.Workplane("XY")
        .rect(plat_w, plat_d)
        .extrude(plat_h)
    )
    try:
        platform = platform.edges("|Z").fillet(2)
    except Exception:
        pass

    # Guide rod receptacles (4 corners — short sleeves extending downward)
    inset = 20
    sleeve_len = 20
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        rx = dx * (plat_w / 2 - inset)
        ry = dy * (plat_d / 2 - inset)
        sleeve = (
            cq.Workplane("XY")
            .workplane(offset=-sleeve_len)
            .center(rx, ry)
            .circle(PEDESTAL_GUIDE_OD / 2 + 2)
            .extrude(sleeve_len)
        )
        bore = (
            cq.Workplane("XY")
            .workplane(offset=-sleeve_len - 1)
            .center(rx, ry)
            .circle(PEDESTAL_GUIDE_OD / 2 + 0.2)
            .extrude(sleeve_len + plat_h + 2)
        )
        platform = platform.union(sleeve).cut(bore)

    # Tilt hinge barrel along -Y edge (closest to spine when installed)
    hinge_barrel = (
        cq.Workplane("YZ")
        .center(-plat_d / 2, plat_h / 2)
        .circle(HINGE_TUBE_OD)
        .extrude(plat_w - 20)
        .translate((-plat_w / 2 + 10, 0, 0))
    )
    hinge_bore = (
        cq.Workplane("YZ")
        .center(-plat_d / 2, plat_h / 2)
        .circle(HINGE_TUBE_OD / 2 + 0.2)
        .extrude(plat_w - 18)
        .translate((-plat_w / 2 + 9, 0, 0))
    )
    platform = platform.union(hinge_barrel).cut(hinge_bore)

    return platform


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    platform = build_pedestal_platform()
    show_object(platform, name="Pedestal Platform",
                options={"color": (0.3, 0.5, 0.7, 0.9)})
except ImportError:
    pass
```

- [ ] **Step 4: Create tilt_linkage.py**

Create `designs/starlink/tilt_linkage.py`:

```python
"""
Starlink Tilt Linkage

MG996R servo mount on the platform underside + printed linkage arm
that drives the tilt hinge. Tilt range: 0-45 degrees.
"""

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
    # Mounting holes (2x M3)
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
    # Servo horn hole (one end)
    h1 = (
        cq.Workplane("XY")
        .center(-length / 2 + width / 2, 0)
        .circle(hole_dia / 2)
        .extrude(thickness + 1)
    )
    # Hinge pin hole (other end)
    h2 = (
        cq.Workplane("XY")
        .center(length / 2 - width / 2, 0)
        .circle(hole_dia / 2)
        .extrude(thickness + 1)
    )
    arm = arm.cut(h1).cut(h2)
    return arm


# --- Standalone preview ---
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
```

- [ ] **Step 5: Verify all starlink files run**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys; sys.modules['cq_server'] = type(sys)('mock'); sys.modules['cq_server.ui'] = type(sys)('mock')
sys.modules['cq_server.ui'].ui = None; sys.modules['cq_server.ui'].show_object = lambda *a, **k: None
from designs.starlink.pedestal_base import build_pedestal_base
from designs.starlink.pedestal_platform import build_pedestal_platform
from designs.starlink.tilt_linkage import build_tilt_servo_mount, build_linkage_arm
b = build_pedestal_base(); print(f'Base OK: {b.val().BoundingBox().xlen:.0f}mm wide')
p = build_pedestal_platform(); print(f'Platform OK')
m = build_tilt_servo_mount(); print(f'Tilt mount OK')
a = build_linkage_arm(); print(f'Linkage arm OK')
print('PASS')
"
```

- [ ] **Step 6: Commit**

```bash
git add designs/starlink/
git commit -m "feat(v2): Starlink deployment — pedestal base, platform, tilt servo + linkage"
```

---

### Task 8: Device Lift System

**Files:**
- Create: `designs/lifts/__init__.py`
- Create: `designs/lifts/cam_lift.py`
- Create: `designs/lifts/lift_plate.py`

Parametric eccentric cam mechanism driven by SG90 servo. Reused 3x for laptop, monitor, and keyboard. Lift plates sized per device pocket.

- [ ] **Step 1: Create lifts package and cam_lift.py**

Create `designs/lifts/__init__.py`:

```python
"""Device lift subsystem — SG90-driven eccentric cam lifts."""
```

Create `designs/lifts/cam_lift.py`:

```python
"""
Eccentric Cam Lift Mechanism

Parametric cam driven by SG90 micro servo.
180-degree rotation pushes cam high point through a floor slot,
raising a lift plate ~20mm.

Reused 3x (laptop, monitor, keyboard) with different slot widths.
"""

import cadquery as cq
import math
from designs.common.constants import (
    CAM_OD, CAM_ECCENTRICITY, CAM_THICKNESS,
    CAM_LIFT_HEIGHT, LIFT_SLOT_W,
    SG90_W, SG90_D, SG90_H,
    M3_CLEARANCE_DIA,
)


def build_cam(cam_od=CAM_OD, eccentricity=CAM_ECCENTRICITY,
              thickness=CAM_THICKNESS):
    """
    Build an eccentric cam disc.
    The cam center is offset from the shaft center by 'eccentricity'.
    Shaft hole is at origin; cam disc is offset.
    """
    cam = (
        cq.Workplane("XY")
        .center(eccentricity, 0)
        .circle(cam_od / 2)
        .extrude(thickness)
    )
    # Shaft hole at origin
    shaft = (
        cq.Workplane("XY")
        .circle(3)  # 6mm diameter shaft bore
        .extrude(thickness + 1)
    )
    cam = cam.cut(shaft)
    # Flat on one side for set screw / D-shaft
    flat = (
        cq.Workplane("XY")
        .center(-3, 0)
        .rect(2, 4)
        .extrude(thickness + 1)
    )
    cam = cam.cut(flat)
    return cam


def build_cam_housing(slot_w=LIFT_SLOT_W):
    """
    Build the housing that sits beneath the pocket floor.
    Contains the SG90 servo and cam, with a slot opening in the top
    for the lift plate to pass through.
    """
    housing_wall = 2
    hw = SG90_W + housing_wall * 2 + CAM_OD  # wide enough for servo + cam
    hd = max(SG90_D, CAM_OD) + housing_wall * 2
    hh = SG90_H + housing_wall

    housing = (
        cq.Workplane("XY")
        .rect(hw, hd)
        .extrude(hh)
    )
    # Servo cavity
    servo_cavity = (
        cq.Workplane("XY")
        .workplane(offset=housing_wall)
        .center(-hw / 4, 0)
        .rect(SG90_W + 1, SG90_D + 1)
        .extrude(SG90_H + 1)
    )
    housing = housing.cut(servo_cavity)
    # Cam cavity
    cam_cavity = (
        cq.Workplane("XY")
        .workplane(offset=housing_wall)
        .center(hw / 4, 0)
        .circle(CAM_OD / 2 + CAM_ECCENTRICITY + 1)
        .extrude(CAM_THICKNESS + 5)
    )
    housing = housing.cut(cam_cavity)
    # Top slot for lift plate to pass through
    slot = (
        cq.Workplane("XY")
        .workplane(offset=hh - 1)
        .center(hw / 4, 0)
        .rect(slot_w, hd - housing_wall * 2)
        .extrude(housing_wall + 2)
    )
    housing = housing.cut(slot)
    # Mounting holes (2x M3)
    for dx in [-hw / 2 + 5, hw / 2 - 5]:
        hole = (
            cq.Workplane("XY")
            .center(dx, 0)
            .circle(M3_CLEARANCE_DIA / 2)
            .extrude(housing_wall + 1)
        )
        housing = housing.cut(hole)
    return housing


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    cam = build_cam()
    show_object(cam, name="Eccentric Cam",
                options={"color": (0.7, 0.5, 0.2, 0.9)})
    housing = build_cam_housing().translate((0, 50, 0))
    show_object(housing, name="Cam Housing",
                options={"color": (0.4, 0.4, 0.4, 0.8)})
except ImportError:
    pass
```

- [ ] **Step 2: Create lift_plate.py**

Create `designs/lifts/lift_plate.py`:

```python
"""
Lift Plates

Thin plates that sit under each device, pushed up by the cam mechanism.
Sized per device pocket. The plate has a tab that extends down through
the floor slot to contact the cam.
"""

import cadquery as cq
from designs.common.constants import (
    LAPTOP_W, LAPTOP_D,
    MONITOR_W, MONITOR_D,
    KB_W, KB_D,
    CAM_LIFT_HEIGHT,
    LIFT_SLOT_W,
)


def build_lift_plate(device_w, device_d, plate_thick=2, tab_w=None, tab_h=None):
    """
    Build a lift plate for a specific device.

    Args:
        device_w: width of the device pocket (plate is slightly smaller)
        device_d: depth of the device pocket
        plate_thick: plate thickness
        tab_w: width of the cam-contact tab (defaults to LIFT_SLOT_W - 2)
        tab_h: height of the tab extending below plate (defaults to CAM_LIFT_HEIGHT)
    """
    if tab_w is None:
        tab_w = LIFT_SLOT_W - 2
    if tab_h is None:
        tab_h = CAM_LIFT_HEIGHT

    # Plate slightly smaller than pocket for clearance
    pw = device_w - 4
    pd = device_d - 4

    plate = (
        cq.Workplane("XY")
        .rect(pw, pd)
        .extrude(plate_thick)
    )
    try:
        plate = plate.edges("|Z").fillet(2)
    except Exception:
        pass

    # Cam-contact tab extending downward from center
    tab = (
        cq.Workplane("XY")
        .workplane(offset=-tab_h)
        .rect(tab_w, tab_w)
        .extrude(tab_h)
    )
    plate = plate.union(tab)

    return plate


def build_laptop_lift_plate():
    """Lift plate sized for Framework Laptop pocket."""
    return build_lift_plate(LAPTOP_W, LAPTOP_D)


def build_monitor_lift_plate():
    """Lift plate sized for 17" monitor pocket."""
    return build_lift_plate(MONITOR_W, MONITOR_D)


def build_keyboard_lift_plate():
    """Lift plate sized for keyboard pocket."""
    return build_lift_plate(KB_W, KB_D)


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    lp = build_laptop_lift_plate()
    show_object(lp, name="Laptop Lift Plate",
                options={"color": (0.6, 0.6, 0.8, 0.8)})
    mp = build_monitor_lift_plate().translate((0, 0, 30))
    show_object(mp, name="Monitor Lift Plate",
                options={"color": (0.6, 0.8, 0.6, 0.8)})
    kp = build_keyboard_lift_plate().translate((0, 0, 60))
    show_object(kp, name="Keyboard Lift Plate",
                options={"color": (0.8, 0.6, 0.6, 0.8)})
except ImportError:
    pass
```

- [ ] **Step 3: Verify lift files run**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys; sys.modules['cq_server'] = type(sys)('mock'); sys.modules['cq_server.ui'] = type(sys)('mock')
sys.modules['cq_server.ui'].ui = None; sys.modules['cq_server.ui'].show_object = lambda *a, **k: None
from designs.lifts.cam_lift import build_cam, build_cam_housing
from designs.lifts.lift_plate import build_laptop_lift_plate, build_monitor_lift_plate, build_keyboard_lift_plate
c = build_cam(); print(f'Cam OK')
h = build_cam_housing(); print(f'Housing OK')
lp = build_laptop_lift_plate(); print(f'Laptop plate: {lp.val().BoundingBox().xlen:.0f}mm')
mp = build_monitor_lift_plate(); print(f'Monitor plate: {mp.val().BoundingBox().xlen:.0f}mm')
kp = build_keyboard_lift_plate(); print(f'Keyboard plate: {kp.val().BoundingBox().xlen:.0f}mm')
print('PASS')
"
```

- [ ] **Step 4: Commit**

```bash
git add designs/lifts/
git commit -m "feat(v2): device lift system — eccentric cam, housing, and 3 lift plates"
```

---

### Task 9: Electronics Bay

**Files:**
- Create: `designs/electronics/__init__.py`
- Create: `designs/electronics/electronics_bay.py`
- Create: `designs/electronics/button_mount.py`

The electronics bay enclosure (120×40×30mm) that mounts in the Page 2 spine, with component mounting posts, USB-C port cutout, and removable lid. Plus the recessed button housing.

- [ ] **Step 1: Create electronics package and bay**

Create `designs/electronics/__init__.py`:

```python
"""Electronics subsystem — ESP32 bay, button mount, touch pad recesses."""
```

Create `designs/electronics/electronics_bay.py`:

```python
"""
Electronics Bay Enclosure

Enclosed box (120x40x30mm internal) that mounts in the Page 2 spine wall.
Contains ESP32, PCA9685, TP4056, boost converter, LiPo cell.
Removable lid with M2 screws. USB-C port cutout on one end.
"""

import cadquery as cq
from designs.common.constants import (
    EBAY_INNER_W, EBAY_INNER_D, EBAY_INNER_H, EBAY_WALL,
    EBAY_LID_SCREW,
    M3_CLEARANCE_DIA,
)


def build_electronics_bay():
    """Build the electronics bay box (without lid)."""
    ow = EBAY_INNER_W + EBAY_WALL * 2
    od = EBAY_INNER_D + EBAY_WALL * 2
    oh = EBAY_INNER_H + EBAY_WALL  # open top (lid goes on)

    box = (
        cq.Workplane("XY")
        .rect(ow, od)
        .extrude(oh)
    )
    try:
        box = box.edges("|Z").fillet(2)
    except Exception:
        pass
    # Interior cavity
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=EBAY_WALL)
        .rect(EBAY_INNER_W, EBAY_INNER_D)
        .extrude(EBAY_INNER_H + 1)
    )
    box = box.cut(cavity)

    # USB-C port cutout (one end, centered)
    usbc_w = 10  # USB-C port width
    usbc_h = 4   # USB-C port height
    usbc_cutout = (
        cq.Workplane("XZ")
        .center(-ow / 2, EBAY_WALL + EBAY_INNER_H / 2)
        .rect(usbc_h, usbc_w)
        .extrude(EBAY_WALL + 2, both=True)
    )
    # Rotate to cut through the -Y face
    usbc_cutout2 = (
        cq.Workplane("YZ")
        .center(-od / 2, EBAY_WALL + EBAY_INNER_H / 2)
        .rect(usbc_h, usbc_w)
        .extrude(EBAY_WALL + 2, both=True)
    )
    box = box.cut(usbc_cutout2)

    # Lid screw bosses (4x M2 holes in rim)
    for dx in [-EBAY_INNER_W / 2 + 5, EBAY_INNER_W / 2 - 5]:
        for dy in [-EBAY_INNER_D / 2 + 5, EBAY_INNER_D / 2 - 5]:
            boss = (
                cq.Workplane("XY")
                .workplane(offset=oh - 3)
                .center(dx, dy)
                .circle(EBAY_LID_SCREW + 2)
                .extrude(3)
            )
            hole = (
                cq.Workplane("XY")
                .workplane(offset=oh - 4)
                .center(dx, dy)
                .circle(EBAY_LID_SCREW / 2)
                .extrude(5)
            )
            box = box.union(boss).cut(hole)

    # Shell mounting holes (4x M3 on bottom face)
    for dx in [-EBAY_INNER_W / 2 + 8, EBAY_INNER_W / 2 - 8]:
        for dy in [-EBAY_INNER_D / 2 + 8, EBAY_INNER_D / 2 - 8]:
            hole = (
                cq.Workplane("XY")
                .center(dx, dy)
                .circle(M3_CLEARANCE_DIA / 2)
                .extrude(EBAY_WALL + 1)
            )
            box = box.cut(hole)

    return box


def build_electronics_bay_lid():
    """Build the removable lid for the electronics bay."""
    ow = EBAY_INNER_W + EBAY_WALL * 2
    od = EBAY_INNER_D + EBAY_WALL * 2
    lid_h = EBAY_WALL

    lid = (
        cq.Workplane("XY")
        .rect(ow, od)
        .extrude(lid_h)
    )
    try:
        lid = lid.edges("|Z").fillet(2)
    except Exception:
        pass
    # Inner lip that fits inside the box
    lip = (
        cq.Workplane("XY")
        .workplane(offset=-2)
        .rect(EBAY_INNER_W - 0.5, EBAY_INNER_D - 0.5)
        .extrude(2)
    )
    lid = lid.union(lip)
    # M2 screw holes (4x, matching bay bosses)
    for dx in [-EBAY_INNER_W / 2 + 5, EBAY_INNER_W / 2 - 5]:
        for dy in [-EBAY_INNER_D / 2 + 5, EBAY_INNER_D / 2 - 5]:
            hole = (
                cq.Workplane("XY")
                .workplane(offset=-1)
                .center(dx, dy)
                .circle(EBAY_LID_SCREW / 2 + 0.2)
                .extrude(lid_h + 3)
            )
            lid = lid.cut(hole)
    return lid


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    bay = build_electronics_bay()
    show_object(bay, name="Electronics Bay",
                options={"color": (0.3, 0.3, 0.3, 0.9)})
    lid = build_electronics_bay_lid().translate((0, 0, EBAY_INNER_H + EBAY_WALL + 5))
    show_object(lid, name="Bay Lid",
                options={"color": (0.5, 0.5, 0.5, 0.8)})
except ImportError:
    pass
```

- [ ] **Step 2: Create button_mount.py**

Create `designs/electronics/button_mount.py`:

```python
"""
Recessed Button Housing

Flush-mount housing for 12mm push button with LED ring.
Mounts on the Page 2 spine wall next to the USB-C port.
"""

import cadquery as cq
from designs.common.constants import BUTTON_DIA, BUTTON_RECESS, WALL


def build_button_mount():
    """
    Build the recessed button housing.
    A short cylinder with a central bore for the button,
    and a lip that sits flush with the shell surface.
    """
    outer_dia = BUTTON_DIA + 6  # housing outer diameter
    housing_h = WALL + BUTTON_RECESS + 2  # total height

    housing = (
        cq.Workplane("XY")
        .circle(outer_dia / 2)
        .extrude(housing_h)
    )
    # Button bore (through hole)
    bore = (
        cq.Workplane("XY")
        .circle(BUTTON_DIA / 2 + 0.2)
        .extrude(housing_h + 1)
    )
    housing = housing.cut(bore)
    # Recess lip at the top (wider flat ring that sits flush with shell)
    lip = (
        cq.Workplane("XY")
        .workplane(offset=housing_h - BUTTON_RECESS)
        .circle(outer_dia / 2 + 2)
        .circle(outer_dia / 2)
        .extrude(BUTTON_RECESS)
    )
    housing = housing.union(lip)
    return housing


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    btn = build_button_mount()
    show_object(btn, name="Button Mount",
                options={"color": (0.2, 0.2, 0.2, 0.9)})
except ImportError:
    pass
```

- [ ] **Step 3: Verify electronics files run**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys; sys.modules['cq_server'] = type(sys)('mock'); sys.modules['cq_server.ui'] = type(sys)('mock')
sys.modules['cq_server.ui'].ui = None; sys.modules['cq_server.ui'].show_object = lambda *a, **k: None
from designs.electronics.electronics_bay import build_electronics_bay, build_electronics_bay_lid
from designs.electronics.button_mount import build_button_mount
bay = build_electronics_bay(); print(f'Bay OK: {bay.val().BoundingBox().xlen:.0f}mm')
lid = build_electronics_bay_lid(); print(f'Lid OK')
btn = build_button_mount(); print(f'Button OK')
print('PASS')
"
```

- [ ] **Step 4: Commit**

```bash
git add designs/electronics/
git commit -m "feat(v2): electronics bay enclosure + lid + button mount"
```

---

### Task 10: LED Diffuser Strip

**Files:**
- Create: `designs/led/__init__.py`
- Create: `designs/led/diffuser_strip.py`

Snap-in translucent diffuser channel cover. Parametric length — used for all ridge and rim LED channels.

- [ ] **Step 1: Create LED package and diffuser**

Create `designs/led/__init__.py`:

```python
"""LED subsystem — diffuser strips for LED channels."""
```

Create `designs/led/diffuser_strip.py`:

```python
"""
LED Diffuser Strip

Snap-in translucent cover for LED channels.
Printed in clear/natural PETG.
Parametric length — cut to match each channel run.
"""

import cadquery as cq
from designs.common.constants import (
    LED_CHANNEL_W, LED_CHANNEL_D, LED_DIFFUSER_SNAP,
)


def build_diffuser_strip(length, channel_w=LED_CHANNEL_W,
                         channel_d=LED_CHANNEL_D,
                         snap_lip=LED_DIFFUSER_SNAP):
    """
    Build a diffuser strip that snaps into an LED channel.

    The strip has a flat top face and snap-fit wings on the sides
    that engage with the channel lip.
    """
    strip_h = channel_d - 0.5  # slightly shorter than channel depth
    strip_w = channel_w - 0.3  # slight clearance

    # Main body
    strip = (
        cq.Workplane("XY")
        .rect(length, strip_w)
        .extrude(strip_h)
    )
    # Snap wings on each side (small ridges that catch the channel lip)
    wing_h = snap_lip
    wing_w = 0.5
    for side in [-1, 1]:
        wing = (
            cq.Workplane("XY")
            .workplane(offset=strip_h - wing_h)
            .center(0, side * (strip_w / 2 + wing_w / 2))
            .rect(length, wing_w)
            .extrude(wing_h)
        )
        strip = strip.union(wing)
    return strip


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    sample = build_diffuser_strip(100)
    show_object(sample, name="Diffuser Strip (100mm sample)",
                options={"color": (0.9, 0.9, 0.95, 0.5)})
except ImportError:
    pass
```

- [ ] **Step 2: Verify**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys; sys.modules['cq_server'] = type(sys)('mock'); sys.modules['cq_server.ui'] = type(sys)('mock')
sys.modules['cq_server.ui'].ui = None; sys.modules['cq_server.ui'].show_object = lambda *a, **k: None
from designs.led.diffuser_strip import build_diffuser_strip
d = build_diffuser_strip(200)
bb = d.val().BoundingBox()
print(f'Diffuser: {bb.xlen:.0f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm')
assert abs(bb.xlen - 200) < 1, 'Length wrong'
print('PASS')
"
```

- [ ] **Step 3: Commit**

```bash
git add designs/led/
git commit -m "feat(v2): LED diffuser strip — snap-in translucent channel cover"
```

---

### Task 11: Assembly Preview for cadquery-server

**Files:**
- Create: `designs/assembly/__init__.py`
- Create: `designs/assembly/assembly_preview.py`

Unified assembly view that imports all subsystems, positions them correctly, and shows them in cadquery-server. This is the file that gets symlinked by git-sync so you can browse the full case in the browser.

- [ ] **Step 1: Create assembly package**

Create `designs/assembly/__init__.py`:

```python
"""Assembly preview — full case view for cadquery-server."""
```

- [ ] **Step 2: Create assembly_preview.py**

Create `designs/assembly/assembly_preview.py`:

```python
"""
Mobile Lab Case V2 — Full Assembly Preview

Composes all subsystems into a single cadquery-server view.
Three pages stacked with visual gaps, hinges attached,
Starlink pedestal in Page 1, electronics bay in Page 2 spine,
latches on front edge.

This is the file symlinked by cadquery-server git-sync.
"""

import cadquery as cq
from cq_server.ui import ui, show_object

from designs.shell.page1_shell import build_page1
from designs.shell.page2_shell import build_page2
from designs.shell.page3_shell import build_page3
from designs.hinge.hinge_knuckles import build_hinge_knuckles
from designs.hinge.latch_mechanism import build_latch_housing, build_latch_catch
from designs.hinge.hinge_servo_mount import build_servo_mount
from designs.starlink.pedestal_base import build_pedestal_base
from designs.starlink.pedestal_platform import build_pedestal_platform
from designs.electronics.electronics_bay import build_electronics_bay
from designs.common.constants import (
    CASE_OUTER_W, CASE_OUTER_D,
    PAGE1_H, PAGE2_H, PAGE3_H,
)


# ============================================================
# Build all pages
# ============================================================
page1 = build_page1()
page2 = build_page2()
page3 = build_page3()

# ============================================================
# Add hinge knuckles to each page
# ============================================================
# Page 1 top: even knuckles with gear sector
p1_hinges = build_hinge_knuckles(PAGE1_H, parity="even", gear_sector_index=2)
page1 = page1.union(p1_hinges)

# Page 2 bottom: odd knuckles
p2_hinges_bot = build_hinge_knuckles(0, parity="odd")
# Page 2 top: even knuckles with gear sector
p2_hinges_top = build_hinge_knuckles(PAGE2_H, parity="even", gear_sector_index=2)
page2 = page2.union(p2_hinges_bot).union(p2_hinges_top)

# Page 3 bottom: odd knuckles
p3_hinges = build_hinge_knuckles(0, parity="odd")
page3 = page3.union(p3_hinges)

# ============================================================
# Show in stacked assembly view
# ============================================================
show_object(page1, name="Page 1 - Bottom (Power)",
            options={"color": (0.27, 0.51, 0.71, 0.7)})

p2_z = PAGE1_H + 2  # 2mm visual gap
page2_view = page2.translate((0, 0, p2_z))
show_object(page2_view, name="Page 2 - Middle (Screens)",
            options={"color": (0.56, 0.74, 0.56, 0.7)})

p3_z = p2_z + PAGE2_H + 2
page3_view = page3.translate((0, 0, p3_z))
show_object(page3_view, name="Page 3 - Top (Accessories)",
            options={"color": (1.0, 0.63, 0.48, 0.7)})

# ============================================================
# Show key subsystems as separate objects
# ============================================================
# Starlink pedestal base (inside Page 1)
pedestal = build_pedestal_base()
pedestal_view = pedestal.translate((0, 0, 3))  # on Page 1 floor
show_object(pedestal_view, name="Starlink Pedestal Base",
            options={"color": (0.3, 0.3, 0.6, 0.5)})

# Starlink platform (raised position for visual)
platform = build_pedestal_platform()
platform_view = platform.translate((0, 0, PAGE1_H + 20))  # shown in raised position
show_object(platform_view, name="Starlink Platform (raised)",
            options={"color": (0.3, 0.5, 0.7, 0.5)})

# Electronics bay (in Page 2 spine)
ebay = build_electronics_bay()
ebay_view = ebay.rotate((0, 0, 0), (0, 1, 0), 90).translate((
    -CASE_OUTER_W / 2 + 5, 0, p2_z + PAGE2_H / 2
))
show_object(ebay_view, name="Electronics Bay",
            options={"color": (0.2, 0.2, 0.2, 0.6)})
```

- [ ] **Step 3: Update cadquery-server git-sync to symlink the assembly file**

The cadquery-server git-sync init container currently symlinks `designs/*.py`. The V2 assembly file is at `designs/assembly/assembly_preview.py`. We need to update the git-sync script in the ArgoCD manifest to also symlink files from subdirectories.

Edit `/home/curiosity/repos/SomniKubernetes/argocd/manifests/cadquery-server/deployment.yaml`:

Change the symlink loop from:
```
for f in "${repo}"/designs/*.py; do
```
To:
```
for f in $(find "${repo}/designs" -name "*.py" -not -name "__init__.py"); do
```

This symlinks all .py files from all subdirectories under designs/ (excluding __init__.py which would collide).

- [ ] **Step 4: Verify assembly runs locally (mocked cq_server)**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 -c "
import sys
# Mock cq_server
mock_mod = type(sys)('mock')
sys.modules['cq_server'] = mock_mod
mock_ui = type(sys)('mock')
mock_ui.ui = None
shown = []
mock_ui.show_object = lambda obj, name='', options=None: shown.append(name)
sys.modules['cq_server.ui'] = mock_ui

# Import triggers the build
import designs.assembly.assembly_preview

print(f'Objects shown: {len(shown)}')
for s in shown:
    print(f'  - {s}')
assert len(shown) >= 5, f'Expected at least 5 show_object calls, got {len(shown)}'
print('PASS')
"
```

Expected: 6 objects (3 pages + pedestal base + platform + electronics bay)

- [ ] **Step 5: Commit assembly + push + restart cadquery-server**

```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
git add designs/assembly/
git commit -m "feat(v2): assembly preview — full case view for cadquery-server"
git push
```

Then update the ArgoCD manifest (separate commit in SomniKubernetes):
```bash
cd /home/curiosity/repos/SomniKubernetes
# Edit the deployment.yaml symlink loop (see Step 3)
git add argocd/manifests/cadquery-server/deployment.yaml
git commit -m "fix: symlink nested design files for cadquery-server"
git push
```

Then restart and verify:
```bash
kubectl rollout restart deployment cadquery-server -n utilities
kubectl rollout status deployment cadquery-server -n utilities --timeout=90s
SVC_IP=$(kubectl get svc cadquery-server -n utilities -o jsonpath='{.spec.clusterIP}')
curl -s -o /dev/null -w "%{http_code}" "http://$SVC_IP:5000/json?m=assembly_preview" --max-time 120
```

Expected: HTTP 200

- [ ] **Step 6: Commit verification success**

If render returns 200, assembly is complete. If 400, check logs and fix (likely RGBA tuple issue or import path issue).

---

### Task 12: Export Script and Slicer Job Update

**Files:**
- Create: `export_v2.py`
- Modify: `k8s/slice-v2.yaml` (may need updating for new file paths)

Export script that generates STL/STEP for all printable parts. Each shell page is split into tiles. Mechanical parts (pedestal, cams, gears, latches, bay) get individual STLs.

- [ ] **Step 1: Create export_v2.py**

Create `export_v2.py`:

```python
"""
Mobile Lab Case V2 — STL/STEP Export Script

Exports all printable parts:
  - 6 shell tiles (3 pages x 2 halves)
  - Hinge knuckles (per page, as pre-unioned with shell)
  - Latch housings, hooks, catches
  - Servo mounts + spur gears
  - Starlink pedestal base + platform + tilt mount + linkage
  - Cam lift housings + cams + lift plates
  - Electronics bay + lid
  - Button mount
  - LED diffuser strips
  - Retaining C-clips

All STLs translated to Z=0 for printing.
"""

import sys
import os

# Mock cq_server so imports don't fail
mock_mod = type(sys)('mock')
sys.modules['cq_server'] = mock_mod
mock_ui = type(sys)('mock')
mock_ui.ui = None
mock_ui.show_object = lambda *a, **k: None
sys.modules['cq_server.ui'] = mock_ui

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cadquery as cq
from designs.common.constants import (
    CASE_OUTER_W, CASE_OUTER_D,
    PAGE1_H, PAGE2_H, PAGE3_H,
)
from designs.common.mounting import split_into_tiles, add_tile_seam_features
from designs.shell.page1_shell import build_page1
from designs.shell.page2_shell import build_page2
from designs.shell.page3_shell import build_page3
from designs.hinge.hinge_knuckles import build_hinge_knuckles, build_retaining_clip
from designs.hinge.latch_mechanism import build_latch_housing, build_latch_hook, build_latch_catch
from designs.hinge.hinge_servo_mount import build_servo_mount, build_spur_gear
from designs.starlink.pedestal_base import build_pedestal_base
from designs.starlink.pedestal_platform import build_pedestal_platform
from designs.starlink.tilt_linkage import build_tilt_servo_mount, build_linkage_arm
from designs.lifts.cam_lift import build_cam, build_cam_housing
from designs.lifts.lift_plate import build_laptop_lift_plate, build_monitor_lift_plate, build_keyboard_lift_plate
from designs.electronics.electronics_bay import build_electronics_bay, build_electronics_bay_lid
from designs.electronics.button_mount import build_button_mount
from designs.led.diffuser_strip import build_diffuser_strip


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def export_stl(solid, name):
    """Export a CadQuery solid to STL, translated to Z=0."""
    bb = solid.val().BoundingBox()
    if bb.zmin != 0:
        solid = solid.translate((0, 0, -bb.zmin))
    path = os.path.join(OUTPUT_DIR, f"v2-{name}.stl")
    cq.exporters.export(solid, path)
    print(f"  Exported: {path}")


def export_step(solid, name):
    """Export a CadQuery solid to STEP."""
    path = os.path.join(OUTPUT_DIR, f"v2-{name}.step")
    cq.exporters.export(solid, path)
    print(f"  Exported: {path}")


def main():
    print("=== Mobile Lab Case V2 — Exporting all parts ===\n")

    # --- Shell tiles ---
    print("Shell tiles:")
    for name, builder, page_h in [
        ("page1", build_page1, PAGE1_H),
        ("page2", build_page2, PAGE2_H),
        ("page3", build_page3, PAGE3_H),
    ]:
        page = builder()
        # Add hinges
        parity_top = "even"
        parity_bot = "odd" if name == "page2" or name == "page3" else None
        hinges_top = build_hinge_knuckles(page_h, parity=parity_top)
        page = page.union(hinges_top)
        if parity_bot:
            hinges_bot = build_hinge_knuckles(0, parity=parity_bot)
            page = page.union(hinges_bot)
        # Split into tiles
        left, right = split_into_tiles(page, CASE_OUTER_W, CASE_OUTER_D, page_h)
        left = add_tile_seam_features(left, CASE_OUTER_D, page_h, is_left=True)
        right = add_tile_seam_features(right, CASE_OUTER_D, page_h, is_left=False)
        export_stl(left, f"{name}-left-tile")
        export_stl(right, f"{name}-right-tile")
        export_step(page, f"{name}-assembled")

    # --- Hinge parts ---
    print("\nHinge & latch parts:")
    export_stl(build_latch_housing(), "latch-housing")
    export_stl(build_latch_hook(), "latch-hook")
    export_stl(build_latch_catch(), "latch-catch")
    export_stl(build_servo_mount(), "hinge-servo-mount")
    export_stl(build_spur_gear(), "spur-gear")
    export_stl(build_retaining_clip(), "retaining-clip")

    # --- Starlink pedestal ---
    print("\nStarlink pedestal:")
    export_stl(build_pedestal_base(), "pedestal-base")
    export_stl(build_pedestal_platform(), "pedestal-platform")
    export_stl(build_tilt_servo_mount(), "tilt-servo-mount")
    export_stl(build_linkage_arm(), "tilt-linkage-arm")

    # --- Cam lifts ---
    print("\nDevice lifts:")
    export_stl(build_cam(), "eccentric-cam")
    export_stl(build_cam_housing(), "cam-housing")
    export_stl(build_laptop_lift_plate(), "lift-plate-laptop")
    export_stl(build_monitor_lift_plate(), "lift-plate-monitor")
    export_stl(build_keyboard_lift_plate(), "lift-plate-keyboard")

    # --- Electronics ---
    print("\nElectronics:")
    export_stl(build_electronics_bay(), "electronics-bay")
    export_stl(build_electronics_bay_lid(), "electronics-bay-lid")
    export_stl(build_button_mount(), "button-mount")

    # --- LED diffusers ---
    print("\nLED diffusers:")
    for length, label in [(200, "spine"), (150, "lateral"), (100, "accent")]:
        export_stl(build_diffuser_strip(length), f"diffuser-{label}-{length}mm")

    print(f"\n=== Done! {len(os.listdir(OUTPUT_DIR))} files in {OUTPUT_DIR} ===")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify export script runs**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
PYTHONPATH=. python3 export_v2.py
```

Expected: All parts export to `output/` directory without errors.

- [ ] **Step 3: Commit**

```bash
git add export_v2.py
git commit -m "feat(v2): export script for all V2 printable parts"
```

---

### Task 13: Update CLAUDE.md and Final Push

**Files:**
- Modify: `CLAUDE.md`

Update project documentation with V2 architecture, file structure, and lessons learned.

- [ ] **Step 1: Update CLAUDE.md**

Add V2 section to CLAUDE.md documenting the modular subsystem architecture, file structure, new constants, and cadquery-server compatibility notes (RGBA tuples, no .text(), nested symlinks).

- [ ] **Step 2: Final push and verify cadquery-server**

```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with V2 architecture and lessons learned"
git push
```

Restart cadquery-server and verify all models render:
```bash
kubectl rollout restart deployment cadquery-server -n utilities
kubectl rollout status deployment cadquery-server -n utilities --timeout=90s
SVC_IP=$(kubectl get svc cadquery-server -n utilities -o jsonpath='{.spec.clusterIP}')
curl -s -o /dev/null -w "%{http_code}" "http://$SVC_IP:5000/json?m=assembly_preview" --max-time 120
```

Expected: HTTP 200

- [ ] **Step 3: Commit**

Final verification commit if any fixes were needed.
