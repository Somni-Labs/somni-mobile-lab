# Hero Face + Structural Ribs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the uniform side ribs and flat logo deboss with a dramatic hero face (layered armor plates + hex grid + raised logo) on the front wall and fewer/bolder structural ribs on secondary sides.

**Architecture:** Two new functions in `designs/common/mounting.py` replace the existing `add_side_ribs()` and `add_logo_deboss()`. The hex grid uses an additive approach (union hex walls onto a recessed surface) instead of subtractive (cutting individual hexes). All three page shells update their imports and calls. Constants are replaced in-place.

**Tech Stack:** CadQuery 2.7.0, Python 3.13, pytest

---

### Task 1: Update Constants

**Files:**
- Modify: `designs/common/constants.py:38-40` (replace SIDE_RIB constants)
- Modify: `designs/common/mounting.py:20` (update import)

- [ ] **Step 1: Replace the three SIDE_RIB constants with hero face and structural rib constants**

In `designs/common/constants.py`, replace lines 38-40:

```python
SIDE_RIB_W = 6         # bold vertical ribs on exterior side walls
SIDE_RIB_H = 2         # how far side ribs protrude from wall surface
SIDE_RIB_SPACING = 40  # spacing between side ribs (along long axis)
```

with:

```python
# Hero face (front wall armor plate treatment)
HERO_PLATE_W = 120     # raised logo plate width
HERO_PLATE_H = 50      # raised logo plate height (Z extent on front wall)
HERO_PLATE_PROUD = 3   # how far logo plate protrudes from wall surface
HERO_PLATE_RECESS = 1.5  # recess depth into the plate for logo background
HEX_SIZE = 15          # hex pocket size across flats (mm)
HEX_WALL = 2           # wall thickness between hex pockets (mm)
HEX_PANEL_RECESS = 1.5 # how deep hex panel is recessed into wall
HEX_POCKET_EXTRA = 0.5 # additional depth of hex pockets below panel surface
FRAME_GROOVE_W = 2     # groove width between armor zones
FRAME_GROOVE_D = 1     # groove depth

# Structural ribs (back + short sides only)
STRUCT_RIB_W = 4       # structural rib width
STRUCT_RIB_H = 3       # how far structural ribs protrude from wall
STRUCT_RIB_BACK_N = 3  # number of ribs on back wall
STRUCT_RIB_SIDE_N = 1  # number of ribs per short side
```

- [ ] **Step 2: Update the import in mounting.py**

In `designs/common/mounting.py`, replace the import line:

```python
    SIDE_RIB_W, SIDE_RIB_H, SIDE_RIB_SPACING,
```

with:

```python
    HERO_PLATE_W, HERO_PLATE_H, HERO_PLATE_PROUD, HERO_PLATE_RECESS,
    HEX_SIZE, HEX_WALL, HEX_PANEL_RECESS, HEX_POCKET_EXTRA,
    FRAME_GROOVE_W, FRAME_GROOVE_D,
    STRUCT_RIB_W, STRUCT_RIB_H, STRUCT_RIB_BACK_N, STRUCT_RIB_SIDE_N,
```

- [ ] **Step 3: Verify imports work**

Run: `cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab && python3 -c "from designs.common.mounting import build_sculpted_shell; print('OK')"`

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add designs/common/constants.py designs/common/mounting.py
git commit -m "feat(v2): replace side rib constants with hero face + structural rib constants"
```

---

### Task 2: Implement `add_structural_ribs()`

**Files:**
- Modify: `designs/common/mounting.py` (replace `add_side_ribs` function)
- Test: `tests/test_shell_chamfer.py`

- [ ] **Step 1: Write failing tests for structural ribs**

In `tests/test_shell_chamfer.py`, replace `test_side_ribs_add_material` (lines 106-116) and `test_logo_deboss_removes_material` (lines 119-125) with:

```python
def test_structural_ribs_add_material():
    """Structural ribs should add protruding material to back and short sides."""
    shell = build_sculpted_shell(200, 150, 60)
    vol_before = shell.val().Volume()
    result = add_structural_ribs(shell, 200, 150, 60)
    vol_after = result.val().Volume()
    assert vol_after > vol_before, "Structural ribs should add material"


def test_structural_ribs_skip_front():
    """Structural ribs should NOT add material on the front (+Y) face.

    We verify by checking that the +Y bounding box extent doesn't grow,
    while the -Y (back) extent does grow outward.
    """
    shell = build_sculpted_shell(200, 150, 60)
    bb_before = shell.val().BoundingBox()
    result = add_structural_ribs(shell, 200, 150, 60)
    bb_after = result.val().BoundingBox()
    # Back (-Y) should extend outward (ribs protrude)
    assert bb_after.ymin < bb_before.ymin, (
        f"Back face should extend: ymin before={bb_before.ymin:.1f}, after={bb_after.ymin:.1f}"
    )
    # Front (+Y) should NOT extend (no ribs on hero face)
    assert abs(bb_after.ymax - bb_before.ymax) < 0.1, (
        f"Front face should not extend: ymax before={bb_before.ymax:.1f}, after={bb_after.ymax:.1f}"
    )
```

Also update the import line at the top of the test file — replace `add_side_ribs, add_logo_deboss` with `add_structural_ribs, build_hero_face`.

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_shell_chamfer.py::test_structural_ribs_add_material tests/test_shell_chamfer.py::test_structural_ribs_skip_front -v`

Expected: FAIL (functions not defined yet)

- [ ] **Step 3: Implement `add_structural_ribs()` — replace `add_side_ribs()` in mounting.py**

Replace the entire `add_side_ribs` function (lines 100-165) with:

```python
def add_structural_ribs(body, width, depth, height, chamfer=CHAMFER_SIZE,
                        rib_w=STRUCT_RIB_W, rib_h=STRUCT_RIB_H,
                        n_back=STRUCT_RIB_BACK_N, n_side=STRUCT_RIB_SIDE_N,
                        corner_r=CORNER_R):
    """
    Add bold vertical ribs on the back wall and short sides of a shell.

    The front wall (+Y) is left clean for the hero face treatment.
    Back wall (-Y) gets n_back evenly spaced ribs.
    Short sides (±X) get n_side ribs each, centered to avoid hinge zones.

    Ribs run vertically from just above the bottom chamfer to just below
    the top chamfer. Each rib is rectangular, protruding rib_h outward.
    """
    hw = width / 2
    hd = depth / 2
    z_lo = chamfer + 2
    z_hi = height - chamfer - 2
    rib_z_height = z_hi - z_lo
    if rib_z_height < 5:
        return body

    # Back wall (-Y): n_back ribs evenly spaced along X
    if n_back > 0:
        usable_x = width - corner_r * 4
        if n_back == 1:
            back_xs = [0]
        else:
            spacing = usable_x / (n_back - 1)
            back_xs = [-(n_back - 1) * spacing / 2 + i * spacing for i in range(n_back)]
        for x in back_xs:
            rib = (
                cq.Workplane("XY")
                .workplane(offset=z_lo)
                .center(x, -hd - rib_h / 2)
                .rect(rib_w, rib_h)
                .extrude(rib_z_height)
            )
            try:
                rib = rib.edges(">Z").chamfer(min(1.0, rib_h * 0.4))
            except Exception:
                pass
            body = body.union(rib)

    # Short sides (±X): n_side ribs each, centered along Y
    if n_side > 0:
        usable_y = depth - corner_r * 4
        if n_side == 1:
            side_ys = [0]
        else:
            spacing = usable_y / (n_side - 1)
            side_ys = [-(n_side - 1) * spacing / 2 + i * spacing for i in range(n_side)]
        for y in side_ys:
            for sign in [-1, 1]:  # both ±X sides
                rib = (
                    cq.Workplane("XY")
                    .workplane(offset=z_lo)
                    .center(sign * (hw + rib_h / 2), y)
                    .rect(rib_h, rib_w)
                    .extrude(rib_z_height)
                )
                try:
                    rib = rib.edges(">Z").chamfer(min(1.0, rib_h * 0.4))
                except Exception:
                    pass
                body = body.union(rib)

    return body
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_shell_chamfer.py::test_structural_ribs_add_material tests/test_shell_chamfer.py::test_structural_ribs_skip_front -v`

Expected: both PASS

- [ ] **Step 5: Commit**

```bash
git add designs/common/mounting.py tests/test_shell_chamfer.py
git commit -m "feat(v2): add add_structural_ribs() — bold ribs on back + short sides only"
```

---

### Task 3: Implement `build_hero_face()`

This is the largest task — the full hero face with raised logo plate, recessed hex panels, and frame grooves.

**Files:**
- Modify: `designs/common/mounting.py` (replace `add_logo_deboss` with `build_hero_face`)
- Test: `tests/test_shell_chamfer.py`

- [ ] **Step 1: Write failing tests for hero face**

Add to `tests/test_shell_chamfer.py`, replacing the old `test_logo_deboss_removes_material`:

```python
def test_hero_face_builds_without_error():
    """Hero face should build on a standard shell without errors."""
    shell = build_sculpted_shell(200, 150, 60)
    result = build_hero_face(shell, 200, 150, 60)
    assert result is not None


def test_hero_face_adds_material():
    """Hero face should add net material (raised logo plate protrudes 3mm)."""
    shell = build_sculpted_shell(200, 150, 60)
    vol_before = shell.val().Volume()
    result = build_hero_face(shell, 200, 150, 60)
    vol_after = result.val().Volume()
    # The 3mm proud plate adds more volume than the hex panel recesses remove
    assert vol_after > vol_before, (
        f"Hero face should add net material: before={vol_before:.0f}, after={vol_after:.0f}"
    )


def test_hero_face_extends_front():
    """Hero face logo plate should extend the +Y bounding box by ~3mm."""
    shell = build_sculpted_shell(200, 150, 60)
    bb_before = shell.val().BoundingBox()
    result = build_hero_face(shell, 200, 150, 60)
    bb_after = result.val().BoundingBox()
    extension = bb_after.ymax - bb_before.ymax
    assert extension > 2.0, f"Logo plate should extend +Y by ~3mm, got {extension:.1f}"
    assert extension < 5.0, f"Logo plate should not extend +Y by more than 5mm, got {extension:.1f}"


def test_hero_face_has_hex_grid():
    """Hero face should have more faces than just the logo plate (hex grid adds geometry)."""
    shell = build_sculpted_shell(200, 150, 60)
    faces_before = len(shell.val().Faces())
    result = build_hero_face(shell, 200, 150, 60)
    faces_after = len(result.val().Faces())
    # Hex grid adds many faces — expect at least 20 more
    assert faces_after > faces_before + 20, (
        f"Hex grid should add many faces: before={faces_before}, after={faces_after}"
    )
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m pytest tests/test_shell_chamfer.py::test_hero_face_builds_without_error tests/test_shell_chamfer.py::test_hero_face_adds_material tests/test_shell_chamfer.py::test_hero_face_extends_front tests/test_shell_chamfer.py::test_hero_face_has_hex_grid -v`

Expected: FAIL (function not defined)

- [ ] **Step 3: Implement `build_hero_face()` — replace `add_logo_deboss()` in mounting.py**

Replace the entire `add_logo_deboss` function (lines 168-214) with:

```python
def _build_hex_wall_grid(panel_w, panel_h, hex_size=HEX_SIZE, hex_wall=HEX_WALL):
    """
    Build a grid of hexagonal wall ridges that fill a rectangular region.

    Instead of cutting individual hexes (expensive), we build the WALLS
    between hexes as thin ridges and return them as a single compound.
    The caller unions this onto a recessed panel surface.

    The hex grid is oriented with flat tops (pointy sides left/right).
    Hex center-to-center spacing: hex_size + hex_wall.

    Returns a CadQuery Workplane with the wall grid, centered at origin,
    extruded to wall_height (= HEX_POCKET_EXTRA) on the XZ plane.
    """
    wall_height = HEX_POCKET_EXTRA + 0.01  # slightly taller to ensure clean union
    pitch = hex_size + hex_wall
    row_h = pitch * math.sqrt(3) / 2  # vertical spacing between hex rows

    n_cols = int(panel_w / pitch) + 1
    n_rows = int(panel_h / row_h) + 1

    # Center the grid
    x_offset = -(n_cols - 1) * pitch / 2
    z_offset = -(n_rows - 1) * row_h / 2

    walls = cq.Workplane("XZ")

    # Build horizontal wall strips between hex rows
    for row in range(n_rows + 1):
        z = z_offset + row * row_h - row_h / 2
        if abs(z) > panel_h / 2:
            continue
        strip = (
            cq.Workplane("XZ")
            .center(0, z)
            .rect(panel_w, hex_wall)
            .extrude(wall_height)
        )
        walls = walls.union(strip)

    # Build vertical wall strips between hex columns
    for col in range(n_cols + 1):
        x = x_offset + col * pitch - pitch / 2
        if abs(x) > panel_w / 2:
            continue
        strip = (
            cq.Workplane("XZ")
            .center(x, 0)
            .rect(hex_wall, panel_h)
            .extrude(wall_height)
        )
        walls = walls.union(strip)

    # Add angled connecting walls to create hex pattern
    # Each hex has 6 sides — the horizontal strips handle top/bottom,
    # vertical strips handle the straight sides. We add short angled
    # segments at each hex vertex to create the hex shape.
    half_hex = hex_size / 2
    for row in range(n_rows):
        for col in range(n_cols):
            cx = x_offset + col * pitch + (row % 2) * pitch / 2
            cz = z_offset + row * row_h
            if abs(cx) > panel_w / 2 + pitch or abs(cz) > panel_h / 2 + row_h:
                continue
            # Upper-left and upper-right angled walls
            for dx_sign in [-1, 1]:
                x1 = cx + dx_sign * half_hex
                z1 = cz + row_h / 3
                x2 = cx + dx_sign * (half_hex + hex_wall)
                z2 = cz + row_h * 2 / 3
                seg_cx = (x1 + x2) / 2
                seg_cz = (z1 + z2) / 2
                seg_len = math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2) + hex_wall
                seg_angle = math.degrees(math.atan2(z2 - z1, x2 - x1))
                seg = (
                    cq.Workplane("XZ")
                    .center(seg_cx, seg_cz)
                    .rect(seg_len, hex_wall)
                    .extrude(wall_height)
                )
                if abs(seg_angle) > 0.01:
                    seg = seg.rotate((seg_cx, 0, seg_cz), (seg_cx, 1, seg_cz), seg_angle)
                walls = walls.union(seg)

    return walls


def build_hero_face(body, width, depth, height, wall=WALL, chamfer=CHAMFER_SIZE,
                    plate_w=HERO_PLATE_W, plate_h=HERO_PLATE_H,
                    plate_proud=HERO_PLATE_PROUD, plate_recess=HERO_PLATE_RECESS,
                    hex_panel_recess=HEX_PANEL_RECESS,
                    groove_w=FRAME_GROOVE_W, groove_d=FRAME_GROOVE_D):
    """
    Build the full hero face treatment on the front wall (+Y face).

    Three-layer depth treatment:
    1. Raised center logo plate (plate_proud mm above wall surface)
       with recessed background and raised logo shapes
    2. Two hex-grid panels (above and below logo plate), recessed into wall
    3. Frame grooves separating the three zones

    All geometry is on the +Y face. The front face center Y = depth/2.
    The Z center of the face = height/2 (between chamfer zones).
    """
    hd = depth / 2
    face_y = hd  # outer surface of front wall

    # Usable Z range on the front face (between chamfer zones)
    z_lo = chamfer + 2
    z_hi = height - chamfer - 2
    face_z_center = (z_lo + z_hi) / 2
    face_z_extent = z_hi - z_lo

    # Clamp plate_h to available face height
    effective_plate_h = min(plate_h, face_z_extent * 0.4)

    # --- 1. Raised logo plate ---
    # A solid block protruding plate_proud from the front wall
    logo_plate = (
        cq.Workplane("XZ")
        .center(0, face_z_center)
        .rect(plate_w, effective_plate_h)
        .extrude(plate_proud)
        .translate((0, face_y, 0))
    )
    body = body.union(logo_plate)

    # Recess the plate surface (except logo shapes which stay proud)
    plate_recess_cut = (
        cq.Workplane("XZ")
        .center(0, face_z_center)
        .rect(plate_w - 4, effective_plate_h - 4)  # 2mm frame inside plate
        .extrude(plate_recess)
        .translate((0, face_y + plate_proud - plate_recess, 0))
    )
    body = body.cut(plate_recess_cut)

    # Logo shapes stay at full proud height (not recessed):
    # Main nameplate rectangle
    nameplate = (
        cq.Workplane("XZ")
        .center(0, face_z_center)
        .rect(80, 16)
        .extrude(plate_recess + 0.01)
        .translate((0, face_y + plate_proud - plate_recess, 0))
    )
    body = body.union(nameplate)

    # Accent bar below
    accent_bar = (
        cq.Workplane("XZ")
        .center(0, face_z_center - 14)
        .rect(100, 2.5)
        .extrude(plate_recess + 0.01)
        .translate((0, face_y + plate_proud - plate_recess, 0))
    )
    body = body.union(accent_bar)

    # Flanking chevrons
    for dx in [-55, 55]:
        chevron = (
            cq.Workplane("XZ")
            .center(dx, face_z_center)
            .rect(6, 20)
            .extrude(plate_recess + 0.01)
            .translate((0, face_y + plate_proud - plate_recess, 0))
        )
        body = body.union(chevron)

    # --- 2. Hex panels (above and below logo plate) ---
    # Upper hex panel: from top of logo plate to z_hi
    upper_panel_z_lo = face_z_center + effective_plate_h / 2 + groove_w + 1
    upper_panel_z_hi = z_hi
    upper_panel_h = upper_panel_z_hi - upper_panel_z_lo
    upper_panel_cz = (upper_panel_z_lo + upper_panel_z_hi) / 2
    hex_panel_w = plate_w + 20  # slightly wider than logo plate

    # Lower hex panel: from z_lo to bottom of logo plate
    lower_panel_z_lo = z_lo
    lower_panel_z_hi = face_z_center - effective_plate_h / 2 - groove_w - 1
    lower_panel_h = lower_panel_z_hi - lower_panel_z_lo
    lower_panel_cz = (lower_panel_z_lo + lower_panel_z_hi) / 2

    for panel_cz, panel_h in [(upper_panel_cz, upper_panel_h),
                               (lower_panel_cz, lower_panel_h)]:
        if panel_h < 10:
            continue  # skip if panel zone is too small

        # Cut the recessed panel into the front wall
        panel_recess_box = (
            cq.Workplane("XZ")
            .center(0, panel_cz)
            .rect(hex_panel_w, panel_h)
            .extrude(hex_panel_recess)
            .translate((0, face_y - hex_panel_recess, 0))
        )
        body = body.cut(panel_recess_box)

        # Build hex wall grid and position it on the recessed surface
        hex_walls = _build_hex_wall_grid(hex_panel_w, panel_h)
        # Translate to the correct position on the front face
        hex_walls = hex_walls.translate((0, face_y - hex_panel_recess, panel_cz))
        body = body.union(hex_walls)

    # --- 3. Frame grooves ---
    # Horizontal grooves separating logo plate from hex panels
    for groove_z in [face_z_center + effective_plate_h / 2 + groove_w / 2,
                     face_z_center - effective_plate_h / 2 - groove_w / 2]:
        groove = (
            cq.Workplane("XZ")
            .center(0, groove_z)
            .rect(hex_panel_w + 10, groove_w)
            .extrude(groove_d)
            .translate((0, face_y - groove_d, 0))
        )
        body = body.cut(groove)

    return body
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m pytest tests/test_shell_chamfer.py::test_hero_face_builds_without_error tests/test_shell_chamfer.py::test_hero_face_adds_material tests/test_shell_chamfer.py::test_hero_face_extends_front tests/test_shell_chamfer.py::test_hero_face_has_hex_grid -v`

Expected: all PASS

- [ ] **Step 5: If hex grid approach is too slow or produces bad topology, simplify**

The `_build_hex_wall_grid` function uses many union operations. If build time exceeds ~10 seconds for a single face, simplify by replacing the hex grid with a rectangular grid (simpler geometry, fewer booleans):

```python
# Fallback: rectangular grid instead of hex
for row in range(n_rows):
    z = z_offset + row * row_h
    strip = cq.Workplane("XZ").center(0, z).rect(panel_w, hex_wall).extrude(wall_height)
    walls = walls.union(strip)
for col in range(n_cols):
    x = x_offset + col * pitch
    strip = cq.Workplane("XZ").center(x, 0).rect(hex_wall, panel_h).extrude(wall_height)
    walls = walls.union(strip)
```

This still creates a visible grid pattern and is much faster.

- [ ] **Step 6: Commit**

```bash
git add designs/common/mounting.py tests/test_shell_chamfer.py
git commit -m "feat(v2): add build_hero_face() — armor plates, hex grid, raised logo"
```

---

### Task 4: Update Page Shells

**Files:**
- Modify: `designs/shell/page1_shell.py:42-44` (imports) and `122-126` (calls)
- Modify: `designs/shell/page2_shell.py:42-43` (imports) and `132-137` (calls)
- Modify: `designs/shell/page3_shell.py:48-50` (imports) and `157-161` (calls)
- Test: `tests/test_shell_chamfer.py` (page build tests)

- [ ] **Step 1: Update page1_shell.py imports and calls**

In `designs/shell/page1_shell.py`, change the import:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_chamfer_led_channels, add_side_ribs, add_logo_deboss,
)
```

to:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_chamfer_led_channels, add_structural_ribs, build_hero_face,
)
```

Replace the exterior feature calls (lines 122-126):

```python
    # --- Exterior side ribs (bold vertical lines on all 4 walls) ---
    shell = add_side_ribs(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)

    # --- Logo deboss on front face ---
    shell = add_logo_deboss(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)
```

with:

```python
    # --- Hero face (front wall armor plate treatment) ---
    shell = build_hero_face(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)

    # --- Structural ribs (back + short sides) ---
    shell = add_structural_ribs(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)
```

- [ ] **Step 2: Update page2_shell.py imports and calls**

In `designs/shell/page2_shell.py`, change the import:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_ridge, add_chamfer_led_channels, add_side_ribs, add_logo_deboss,
)
```

to:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_ridge, add_chamfer_led_channels, add_structural_ribs, build_hero_face,
)
```

Replace the exterior feature calls (lines 133-137):

```python
    # --- Exterior side ribs (bold vertical lines on all 4 walls) ---
    shell = add_side_ribs(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE2_H)

    # --- Logo deboss on front face ---
    shell = add_logo_deboss(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE2_H)
```

with:

```python
    # --- Hero face (front wall armor plate treatment) ---
    shell = build_hero_face(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE2_H)

    # --- Structural ribs (back + short sides) ---
    shell = add_structural_ribs(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE2_H)
```

- [ ] **Step 3: Update page3_shell.py imports and calls**

In `designs/shell/page3_shell.py`, change the import:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_ridge, cut_led_channel, cut_armor_panels,
    add_chamfer_led_channels, add_side_ribs, add_logo_deboss,
)
```

to:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_ridge, cut_led_channel, cut_armor_panels,
    add_chamfer_led_channels, add_structural_ribs, build_hero_face,
)
```

Replace lines 157-161:

```python
    # --- Exterior side ribs (bold vertical lines on all 4 walls) ---
    shell = add_side_ribs(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE3_H)

    # --- Somni Labs logo deboss on front wall ---
    shell = add_logo_deboss(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE3_H)
```

with:

```python
    # --- Hero face (front wall armor plate treatment) ---
    shell = build_hero_face(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE3_H)

    # --- Structural ribs (back + short sides) ---
    shell = add_structural_ribs(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE3_H)
```

- [ ] **Step 4: Run all tests**

Run: `python3 -m pytest tests/test_shell_chamfer.py -v`

Expected: all tests PASS (including page build tests)

- [ ] **Step 5: Commit**

```bash
git add designs/shell/page1_shell.py designs/shell/page2_shell.py designs/shell/page3_shell.py
git commit -m "feat(v2): update all page shells — hero face + structural ribs"
```

---

### Task 5: Clean Up Dead Code and Deploy

**Files:**
- Modify: `designs/common/mounting.py` (remove old `add_side_ribs` and `add_logo_deboss` if not already replaced)
- Test: full test suite

- [ ] **Step 1: Verify no remaining references to old functions**

Run: `grep -rn "add_side_ribs\|add_logo_deboss" designs/ tests/`

Expected: no matches. If any remain, update them to use the new functions.

- [ ] **Step 2: Remove old function bodies if they still exist as dead code**

If `add_side_ribs()` and `add_logo_deboss()` still exist alongside the new functions in `mounting.py`, delete them. The new functions (`add_structural_ribs`, `build_hero_face`) fully replace them.

Also remove `SIDE_TAPER_ANGLE` from the constants import in mounting.py if it's no longer used by any function.

- [ ] **Step 3: Run full test suite**

Run: `python3 -m pytest tests/test_shell_chamfer.py -v`

Expected: all tests PASS

- [ ] **Step 4: Verify all 3 pages build and check geometry**

Run:
```python
python3 -c "
import sys; sys.path.insert(0, '.')
import os; os.environ['_CQ_ASSEMBLY'] = '1'
from designs.shell.page1_shell import build_page1
from designs.shell.page2_shell import build_page2
from designs.shell.page3_shell import build_page3
del os.environ['_CQ_ASSEMBLY']
for name, builder in [('Page 1', build_page1), ('Page 2', build_page2), ('Page 3', build_page3)]:
    result = builder()
    bb = result.val().BoundingBox()
    print(f'{name}: {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f}mm, faces={len(result.val().Faces())}')
print('All pages build successfully!')
"
```

Expected: all 3 pages build, front (+Y) bounding box extends ~3mm beyond the back (-Y), each page has noticeably more faces than before.

- [ ] **Step 5: Commit**

```bash
git add designs/common/mounting.py designs/common/constants.py
git commit -m "refactor(v2): remove dead add_side_ribs/add_logo_deboss code"
```

- [ ] **Step 6: Push and restart cadquery-server**

```bash
git push origin main
kubectl rollout restart deployment cadquery-server -n utilities
kubectl rollout status deployment cadquery-server -n utilities --timeout=120s
```

- [ ] **Step 7: Verify cadquery-server renders all modules**

```bash
POD_IP=$(kubectl get pods -n utilities -l app=cadquery-server -o jsonpath='{.items[0].status.podIP}')
for module in page1_shell page2_shell page3_shell assembly_preview; do
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 120 "http://${POD_IP}:5000/json?m=${module}")
    echo "$module: HTTP $code"
done
```

Expected: all HTTP 200

- [ ] **Step 8: Commit any deployment fixes if needed**

If any module returns errors, check server logs, fix import issues, re-push.
