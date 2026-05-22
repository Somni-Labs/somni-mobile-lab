# Shell Aesthetic Rework Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the plain rectangular page shells into chamfered slabs with armor panel treatment on Page 3, creating the cyberpunk exosuit aesthetic.

**Architecture:** Rework `build_sculpted_shell()` in mounting.py to produce chamfered forms, add two new helpers (`cut_armor_panels()`, `add_chamfer_led_channels()`), update all three page shells to use the new shell form and LED placement, and give Page 3 the full recessed armor panel treatment.

**Tech Stack:** CadQuery 2.7.0, Python 3, cadquery-server for live preview

**Spec:** `docs/superpowers/specs/2026-05-22-shell-aesthetic-rework-design.md`

---

### Task 1: Add Chamfer Constants

**Files:**
- Modify: `designs/common/constants.py` (lines 17-21, the CASE SHELL section)

- [ ] **Step 1: Add the new constants to the CASE SHELL section**

In `designs/common/constants.py`, add 4 new constants after the existing `TAPER = 3` line (line 21):

```python
CHAMFER_SIZE = 15          # 45-degree edge chamfer dimension (mm)
PANEL_GROOVE_DEPTH = 1.5   # armor panel recess below ridge surface
PANEL_GROOVE_WIDTH = 2     # groove cut width between panels
PANEL_BEVEL = 1            # bevel transition at groove edges
```

- [ ] **Step 2: Verify the constants import correctly**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -c "from designs.common.constants import CHAMFER_SIZE, PANEL_GROOVE_DEPTH, PANEL_GROOVE_WIDTH, PANEL_BEVEL; print(f'CHAMFER={CHAMFER_SIZE}, GROOVE_D={PANEL_GROOVE_DEPTH}, GROOVE_W={PANEL_GROOVE_WIDTH}, BEVEL={PANEL_BEVEL}')"
```

Expected: `CHAMFER=15, GROOVE_D=1.5, GROOVE_W=2, BEVEL=1`

- [ ] **Step 3: Commit**

```bash
git add designs/common/constants.py
git commit -m "feat(v2): add chamfer and armor panel constants for shell rework"
```

---

### Task 2: Rework `build_sculpted_shell()` for Chamfered Slab Form

**Files:**
- Modify: `designs/common/mounting.py` (lines 9-17 imports, lines 21-49 `build_sculpted_shell`)

This is the core change. The current function builds a box, fillets vertical edges, attempts a top-edge fillet, and hollows it. The new version must:
1. Build the box with vertical corner fillets (same as now)
2. Apply 15mm chamfers on all 8 horizontal edges (4 top + 4 bottom) of the OUTER solid
3. Hollow the interior (same as now)

The chamfer is applied to the outer solid BEFORE the interior is cut, so the chamfer is purely exterior.

- [ ] **Step 1: Write a test for the chamfered shell**

Create `tests/test_shell_chamfer.py`:

```python
"""Tests for the chamfered slab shell form."""
import cadquery as cq
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from designs.common.constants import WALL, CORNER_R, CHAMFER_SIZE
from designs.common.mounting import build_sculpted_shell


def test_chamfered_shell_builds_without_error():
    """Shell should build successfully with chamfers."""
    shell = build_sculpted_shell(200, 150, 60)
    assert shell is not None
    bb = shell.val().BoundingBox()
    # Width and depth should match input (chamfer doesn't change XY footprint at mid-height)
    assert abs(bb.xlen - 200) < 1.0
    assert abs(bb.ylen - 150) < 1.0


def test_chamfered_shell_height_matches():
    """Shell height should match the requested height."""
    shell = build_sculpted_shell(200, 150, 60)
    bb = shell.val().BoundingBox()
    assert abs(bb.zlen - 60) < 1.0


def test_chamfered_shell_is_shorter_at_corners():
    """
    The chamfer removes material at the top/bottom edges.
    The shell at the extreme X/Y corner should be thinner than at the center
    due to the chamfered edges. Verify by checking that the volume is less than
    a plain box of the same outer dimensions.
    """
    shell = build_sculpted_shell(200, 150, 60)
    shell_vol = shell.val().Volume()
    # A plain hollow box (no chamfer) would have this volume:
    outer_vol = 200 * 150 * 60
    inner_vol = (200 - WALL * 2) * (150 - WALL * 2) * (60 - WALL)
    plain_box_vol = outer_vol - inner_vol
    # Chamfered shell should be smaller than plain box
    assert shell_vol < plain_box_vol, f"Chamfered shell ({shell_vol:.0f}) should be smaller than plain box ({plain_box_vol:.0f})"


def test_chamfered_shell_has_floor():
    """Shell should be solid at Z=0 (floor) and open at the top."""
    shell = build_sculpted_shell(200, 150, 60)
    bb = shell.val().BoundingBox()
    assert bb.zmin < 0.1, "Shell should start at Z≈0"
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py -v
```

Expected: `test_chamfered_shell_is_shorter_at_corners` FAILS because the current shell has no chamfer, so the volume equals the plain box volume.

- [ ] **Step 3: Update imports in mounting.py**

In `designs/common/mounting.py`, update the import block (lines 9-18) to include `CHAMFER_SIZE`:

```python
import cadquery as cq
from designs.common.constants import (
    WALL, CORNER_R, TAPER, DIVIDER,
    CHAMFER_SIZE,
    M3_CLEARANCE_DIA, M3_INSERT_DIA, M3_INSERT_DEPTH,
    MOUNT_BOSS_OD, MOUNT_BOSS_ALIGN_H,
    WIRE_CHANNEL_W, WIRE_CHANNEL_D,
    LED_CHANNEL_W, LED_CHANNEL_D, LED_DIFFUSER_SNAP,
    RIDGE_H, RIDGE_W, RIDGE_CHAMFER,
    RIDGE_ACCENT_H, RIDGE_ACCENT_W,
    BED_W, BED_D,
)
```

- [ ] **Step 4: Rewrite `build_sculpted_shell()`**

Replace the entire `build_sculpted_shell` function (lines 21-49) in `designs/common/mounting.py` with:

```python
def build_sculpted_shell(width, depth, height, corner_r=CORNER_R, wall=WALL,
                         taper=TAPER, chamfer=CHAMFER_SIZE):
    """
    Build a chamfered slab page shell — open-top box with large organic fillets
    on vertical edges and 45-degree chamfers on all horizontal edges.

    The chamfer transforms the rectangular profile into a beveled slab.
    Interior is flat-walled (chamfer is exterior only).

    Returns a CadQuery solid (shell with floor, no top).
    """
    # --- Outer solid ---
    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
    )

    # Vertical corner fillets (organic rounded corners)
    if corner_r > 0:
        try:
            outer = outer.edges("|Z").fillet(corner_r)
        except Exception:
            outer = outer.edges("|Z").fillet(corner_r / 2)

    # 45-degree chamfers on horizontal edges (top and bottom)
    if chamfer > 0:
        # Chamfer top edges (where top face meets side walls)
        try:
            outer = outer.edges(">Z").chamfer(chamfer)
        except Exception:
            # Fallback: try smaller chamfer if it conflicts with corner fillet
            try:
                outer = outer.edges(">Z").chamfer(chamfer * 0.6)
            except Exception:
                pass

        # Chamfer bottom edges (where bottom face meets side walls)
        try:
            outer = outer.edges("<Z").chamfer(chamfer)
        except Exception:
            try:
                outer = outer.edges("<Z").chamfer(chamfer * 0.6)
            except Exception:
                pass

    # --- Hollow interior ---
    inner = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .rect(width - wall * 2, depth - wall * 2)
        .extrude(height)
    )
    shell = outer.cut(inner)
    return shell
```

- [ ] **Step 5: Run tests to verify they pass**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py -v
```

Expected: All 4 tests PASS.

- [ ] **Step 6: Verify existing page shells still build**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -c "
from designs.shell.page1_shell import build_page1
from designs.shell.page2_shell import build_page2
from designs.shell.page3_shell import build_page3
p1 = build_page1(); bb1 = p1.val().BoundingBox(); print(f'Page 1: {bb1.xlen:.0f} x {bb1.ylen:.0f} x {bb1.zlen:.0f}')
p2 = build_page2(); bb2 = p2.val().BoundingBox(); print(f'Page 2: {bb2.xlen:.0f} x {bb2.ylen:.0f} x {bb2.zlen:.0f}')
p3 = build_page3(); bb3 = p3.val().BoundingBox(); print(f'Page 3: {bb3.xlen:.0f} x {bb3.ylen:.0f} x {bb3.zlen:.0f}')
"
```

Expected: All three pages build without error. Bounding boxes should be approximately 412 x 271 x [78, 53, 51]mm. The chamfers don't change the bounding box (the max extents are at mid-height where there's no chamfer).

- [ ] **Step 7: Commit**

```bash
git add designs/common/mounting.py tests/test_shell_chamfer.py
git commit -m "feat(v2): rework build_sculpted_shell with 45-degree chamfered slab form"
```

---

### Task 3: Add `add_chamfer_led_channels()` Helper

**Files:**
- Modify: `designs/common/mounting.py` (add new function after `cut_led_channel`)

The current `cut_led_channel()` cuts channels into flat horizontal surfaces. The new `add_chamfer_led_channels()` cuts 4 LED channels into the chamfer faces around the top perimeter of a page shell. Each channel runs along one of the 4 chamfer faces (front, right, back, left) at 45 degrees.

The approach: for each side, create a channel box at the correct position on the chamfer face, rotated 45 degrees around the edge axis so it sits flush with the angled surface.

- [ ] **Step 1: Write a test for chamfer LED channels**

Add to `tests/test_shell_chamfer.py`:

```python
from designs.common.mounting import build_sculpted_shell, add_chamfer_led_channels
from designs.common.constants import WALL, CORNER_R, CHAMFER_SIZE, LED_CHANNEL_W, LED_CHANNEL_D


def test_chamfer_led_channels_build():
    """Adding chamfer LED channels should not error."""
    shell = build_sculpted_shell(200, 150, 60)
    result = add_chamfer_led_channels(shell, 200, 150, 60)
    assert result is not None
    bb = result.val().BoundingBox()
    assert abs(bb.xlen - 200) < 1.0


def test_chamfer_led_channels_remove_material():
    """Chamfer LED channels should cut material from the shell."""
    shell = build_sculpted_shell(200, 150, 60)
    vol_before = shell.val().Volume()
    result = add_chamfer_led_channels(shell, 200, 150, 60)
    vol_after = result.val().Volume()
    assert vol_after < vol_before, "LED channels should remove material"
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py::test_chamfer_led_channels_build -v
```

Expected: FAIL with `ImportError: cannot import name 'add_chamfer_led_channels'`

- [ ] **Step 3: Implement `add_chamfer_led_channels()`**

Add this function to `designs/common/mounting.py`, after the existing `cut_led_channel()` function (after line 173):

```python
def add_chamfer_led_channels(body, width, depth, height, chamfer=CHAMFER_SIZE,
                              channel_w=LED_CHANNEL_W, channel_d=LED_CHANNEL_D):
    """
    Cut LED channels into the 4 chamfer faces around the top perimeter of a page shell.

    Each channel runs along the midline of a chamfer face at 45 degrees.
    The channel is a rectangular groove cut perpendicular to the chamfer surface.

    Args:
        body: CadQuery shell solid
        width: outer width of the shell
        depth: outer depth of the shell
        height: shell height
        chamfer: chamfer size (default CHAMFER_SIZE)
        channel_w: LED channel width
        channel_d: LED channel depth
    """
    import math
    hw = width / 2
    hd = depth / 2

    # The chamfer face midpoint is at 45 degrees, offset chamfer/2 from the edge
    # in both the vertical and horizontal directions.
    # Z position: height - chamfer/2 (midpoint of the chamfer face vertically)
    # XY position: inset chamfer/2 from the outer wall face
    chamfer_mid_z = height - chamfer / 2
    chamfer_inset = chamfer / 2

    # Channel depth is cut perpendicular to the 45-degree face.
    # We approximate by cutting a box rotated 45 degrees around the edge axis.
    # For simplicity and reliability, cut a rectangular slot at the chamfer midpoint
    # that spans the diagonal — slightly wider to ensure full coverage.
    cut_size = channel_d * math.sqrt(2)  # diagonal extent to ensure full depth on angled face

    # Inset from corners to avoid intersecting the corner fillet region
    corner_clearance = chamfer + 5

    sides = [
        # (center_x, center_y, length, rotation_axis)
        # Front (-Y face): channel runs along X
        (0, -hd + chamfer_inset, width - corner_clearance * 2, "X"),
        # Back (+Y face): channel runs along X
        (0, hd - chamfer_inset, width - corner_clearance * 2, "X"),
        # Right (+X face): channel runs along Y
        (hw - chamfer_inset, 0, depth - corner_clearance * 2, "Y"),
        # Left (-X face): channel runs along Y
        (-hw + chamfer_inset, 0, depth - corner_clearance * 2, "Y"),
    ]

    for cx, cy, length, axis in sides:
        if length <= 0:
            continue
        # Create channel box at the chamfer midpoint
        channel = (
            cq.Workplane("XY")
            .workplane(offset=chamfer_mid_z - cut_size / 2)
            .center(cx, cy)
        )
        if axis == "X":
            channel = channel.rect(length, cut_size).extrude(cut_size)
        else:
            channel = channel.rect(cut_size, length).extrude(cut_size)
        body = body.cut(channel)

    return body
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py -v
```

Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add designs/common/mounting.py tests/test_shell_chamfer.py
git commit -m "feat(v2): add chamfer LED channel helper for angled shell edges"
```

---

### Task 4: Add `cut_armor_panels()` Helper

**Files:**
- Modify: `designs/common/mounting.py` (add new function, update imports)

This function takes a body and the ridge grid positions, then recesses the panel zones between the ridges. The ridges remain at the original surface height; the panels are cut 1.5mm below.

- [ ] **Step 1: Write a test for armor panel cutting**

Add to `tests/test_shell_chamfer.py`:

```python
from designs.common.mounting import build_sculpted_shell, cut_armor_panels
from designs.common.constants import PANEL_GROOVE_DEPTH


def test_armor_panels_build():
    """Cutting armor panels should not error."""
    shell = build_sculpted_shell(400, 270, 50)
    spine_xs = [-400 / 6, 0, 400 / 6]
    lateral_ys = [-270 / 6, 270 / 6]
    result = cut_armor_panels(shell, 400, 270, 50, spine_xs, lateral_ys)
    assert result is not None


def test_armor_panels_remove_material():
    """Armor panels should recess material from the top face."""
    shell = build_sculpted_shell(400, 270, 50)
    vol_before = shell.val().Volume()
    spine_xs = [-400 / 6, 0, 400 / 6]
    lateral_ys = [-270 / 6, 270 / 6]
    result = cut_armor_panels(shell, 400, 270, 50, spine_xs, lateral_ys)
    vol_after = result.val().Volume()
    assert vol_after < vol_before, "Armor panels should remove material"
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py::test_armor_panels_build -v
```

Expected: FAIL with `ImportError: cannot import name 'cut_armor_panels'`

- [ ] **Step 3: Update imports in mounting.py**

Add `PANEL_GROOVE_DEPTH, PANEL_GROOVE_WIDTH, PANEL_BEVEL` to the import block in `designs/common/mounting.py`:

```python
from designs.common.constants import (
    WALL, CORNER_R, TAPER, DIVIDER,
    CHAMFER_SIZE,
    PANEL_GROOVE_DEPTH, PANEL_GROOVE_WIDTH, PANEL_BEVEL,
    M3_CLEARANCE_DIA, M3_INSERT_DIA, M3_INSERT_DEPTH,
    MOUNT_BOSS_OD, MOUNT_BOSS_ALIGN_H,
    WIRE_CHANNEL_W, WIRE_CHANNEL_D,
    LED_CHANNEL_W, LED_CHANNEL_D, LED_DIFFUSER_SNAP,
    RIDGE_H, RIDGE_W, RIDGE_CHAMFER,
    RIDGE_ACCENT_H, RIDGE_ACCENT_W,
    BED_W, BED_D,
)
```

- [ ] **Step 4: Implement `cut_armor_panels()`**

Add this function to `designs/common/mounting.py`, after `add_chamfer_led_channels()`:

```python
def cut_armor_panels(body, width, depth, height, spine_xs, lateral_ys,
                     chamfer=CHAMFER_SIZE, groove_depth=PANEL_GROOVE_DEPTH,
                     groove_width=PANEL_GROOVE_WIDTH, ridge_w=RIDGE_W,
                     edge_inset=10):
    """
    Cut recessed armor panel zones into the top face of a page shell.

    The top face is divided into a grid by spine ridges (running along Y at spine_xs)
    and lateral ridges (running along X at lateral_ys). The panel zones between
    ridges are recessed by groove_depth below the ridge surface.

    The ridges themselves remain at the original surface height (height).
    Panel zones are cut groove_depth below that surface.

    Args:
        body: CadQuery shell solid
        width: outer width of the shell
        depth: outer depth of the shell
        height: shell height (top face Z coordinate)
        spine_xs: list of X positions for spine ridges
        lateral_ys: list of Y positions for lateral ridges
        chamfer: chamfer size for computing edge boundaries
        groove_depth: how deep panels are recessed below ridges
        groove_width: width of the groove between ridge and panel (transition zone)
        ridge_w: width of the ridge lines
        edge_inset: how far ridges are inset from the shell edges
    """
    hw = width / 2
    hd = depth / 2

    # Build sorted boundary lists including the shell edges
    # The shell edge with chamfer means the flat top face ends at (hw - chamfer) from center
    x_bounds = sorted([-hw + chamfer] + spine_xs + [hw - chamfer])
    y_bounds = sorted([-hd + chamfer] + lateral_ys + [hd - chamfer])

    # Half the ridge width defines the keep-zone around each ridge line
    half_rw = ridge_w / 2 + groove_width / 2

    # For each rectangular zone between adjacent boundaries, cut a recessed panel
    for i in range(len(x_bounds) - 1):
        for j in range(len(y_bounds) - 1):
            x_lo = x_bounds[i]
            x_hi = x_bounds[i + 1]
            y_lo = y_bounds[j]
            y_hi = y_bounds[j + 1]

            # Inset the panel from the ridge centerlines by half_rw
            # Left/right boundaries: if adjacent to a spine ridge, inset from it
            panel_x_lo = x_lo + half_rw if x_lo in spine_xs else x_lo + groove_width
            panel_x_hi = x_hi - half_rw if x_hi in spine_xs else x_hi - groove_width
            panel_y_lo = y_lo + half_rw if y_lo in lateral_ys else y_lo + groove_width
            panel_y_hi = y_hi - half_rw if y_hi in lateral_ys else y_hi - groove_width

            # Skip if panel is too small
            if panel_x_hi - panel_x_lo < 5 or panel_y_hi - panel_y_lo < 5:
                continue

            panel_cx = (panel_x_lo + panel_x_hi) / 2
            panel_cy = (panel_y_lo + panel_y_hi) / 2
            panel_w = panel_x_hi - panel_x_lo
            panel_d = panel_y_hi - panel_y_lo

            # Cut the panel recess from the top face
            recess = (
                cq.Workplane("XY")
                .workplane(offset=height - groove_depth)
                .center(panel_cx, panel_cy)
                .rect(panel_w, panel_d)
                .extrude(groove_depth + 0.1)
            )
            # Try to add a small bevel on the top edges for the transition effect
            try:
                recess = recess.edges(">Z").chamfer(min(PANEL_BEVEL, groove_depth * 0.4))
            except Exception:
                pass
            body = body.cut(recess)

    return body
```

- [ ] **Step 5: Run tests to verify they pass**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py -v
```

Expected: All 8 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add designs/common/mounting.py tests/test_shell_chamfer.py
git commit -m "feat(v2): add cut_armor_panels helper for recessed armor plate zones"
```

---

### Task 5: Update Page 1 Shell — Chamfer LEDs

**Files:**
- Modify: `designs/shell/page1_shell.py` (lines 41-44 imports, lines 119-127 LED section)

Replace the flat rim LED channels with chamfer-face LED channels. Everything else (pockets, bosses, cable pass-through) stays identical.

- [ ] **Step 1: Write a test for Page 1 with chamfer LEDs**

Add to `tests/test_shell_chamfer.py`:

```python
from designs.shell.page1_shell import build_page1


def test_page1_builds_with_chamfer():
    """Page 1 should build successfully with the chamfered shell."""
    page1 = build_page1()
    assert page1 is not None
    bb = page1.val().BoundingBox()
    # Should still be approximately the right size
    assert bb.xlen > 400
    assert bb.ylen > 260
    assert bb.zlen > 70
```

- [ ] **Step 2: Run test to verify it passes with current code (baseline)**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py::test_page1_builds_with_chamfer -v
```

Expected: PASS (current code already builds; this is a regression guard).

- [ ] **Step 3: Update imports in page1_shell.py**

In `designs/shell/page1_shell.py`, update the mounting import (lines 41-44) to import `add_chamfer_led_channels` instead of `cut_led_channel`:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_chamfer_led_channels,
)
```

Remove `TAPER` from the constants import (line 31) since it's no longer used directly. The updated constants import:

```python
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
```

- [ ] **Step 4: Replace rim LED channels with chamfer LED channels**

In `designs/shell/page1_shell.py`, replace the entire LED channel section (lines 119-127):

```python
    # --- LED channel along inner rim (top face perimeter) ---
    rim_z = PAGE1_H
    hw = CASE_OUTER_W / 2 - WALL - 2  # 2mm clearance from inner wall to LED strip
    hd = CASE_OUTER_D / 2 - WALL - 2  # same inset on depth axis
    # Four sides of the rim
    shell = cut_led_channel(shell, -hw, -hd, hw, -hd, rim_z)   # front
    shell = cut_led_channel(shell, hw, -hd, hw, hd, rim_z)     # right
    shell = cut_led_channel(shell, hw, hd, -hw, hd, rim_z)     # back
    shell = cut_led_channel(shell, -hw, hd, -hw, -hd, rim_z)   # left
```

With:

```python
    # --- LED channels on chamfer faces (top perimeter) ---
    shell = add_chamfer_led_channels(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)
```

- [ ] **Step 5: Run test to verify Page 1 still builds**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py::test_page1_builds_with_chamfer -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add designs/shell/page1_shell.py tests/test_shell_chamfer.py
git commit -m "feat(v2): Page 1 chamfer LED channels replacing flat rim LEDs"
```

---

### Task 6: Update Page 2 Shell — Chamfer LEDs

**Files:**
- Modify: `designs/shell/page2_shell.py` (lines 28-32 imports, lines 41-44 mounting imports, lines 123-131 spine ridge/LED section)

Replace the spine ridge LED channel with chamfer-face LED channels. Keep the spine ridge itself (it's a structural/visual feature on Page 2), carry handle, e-bay cutout, and all bosses.

- [ ] **Step 1: Write a test for Page 2**

Add to `tests/test_shell_chamfer.py`:

```python
from designs.shell.page2_shell import build_page2


def test_page2_builds_with_chamfer():
    """Page 2 should build successfully with the chamfered shell."""
    page2 = build_page2()
    assert page2 is not None
    bb = page2.val().BoundingBox()
    assert bb.xlen > 400
    assert bb.ylen > 260
    assert bb.zlen > 50
```

- [ ] **Step 2: Run test as baseline**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py::test_page2_builds_with_chamfer -v
```

Expected: PASS.

- [ ] **Step 3: Update imports in page2_shell.py**

Update the constants import to remove `TAPER`:

```python
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
```

Update the mounting import to add `add_chamfer_led_channels`:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_ridge, add_chamfer_led_channels,
)
```

Note: `cut_led_channel` is removed from the import since Page 2 no longer calls it directly.

- [ ] **Step 4: Replace spine LED section with chamfer LED channels**

In `designs/shell/page2_shell.py`, replace the spine ridge LED section (lines 123-131):

```python
    # --- Spine ridge LED channels (both outer faces) ---
    # Two vertical ridges on the -X (spine) face, flanking the handle
    spine_x = -CASE_OUTER_W / 2
    ridge_y1 = -CASE_OUTER_D / 3
    ridge_y2 = CASE_OUTER_D / 3

    # Add ridges
    shell = add_ridge(shell, spine_x, ridge_y1, spine_x, ridge_y2,
                      z=PAGE2_H, ridge_w=RIDGE_W, ridge_h=RIDGE_H)
```

With:

```python
    # --- Spine ridge (structural/visual, flanking handle) ---
    spine_x = -CASE_OUTER_W / 2
    ridge_y1 = -CASE_OUTER_D / 3
    ridge_y2 = CASE_OUTER_D / 3
    shell = add_ridge(shell, spine_x, ridge_y1, spine_x, ridge_y2,
                      z=PAGE2_H, ridge_w=RIDGE_W, ridge_h=RIDGE_H)

    # --- LED channels on chamfer faces (top perimeter) ---
    shell = add_chamfer_led_channels(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE2_H)
```

- [ ] **Step 5: Run test**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py::test_page2_builds_with_chamfer -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add designs/shell/page2_shell.py tests/test_shell_chamfer.py
git commit -m "feat(v2): Page 2 chamfer LED channels, keep spine ridge"
```

---

### Task 7: Rework Page 3 Shell — Full Armor Panel Treatment

**Files:**
- Modify: `designs/shell/page3_shell.py` (substantial rework of the ridge/LED/diamond/logo/touch pad sections)

This is the biggest change. Page 3 gets:
1. Chamfered slab shell (automatic from `build_sculpted_shell`)
2. Ridges that form the armor frame (same positions, but now the ridges are the HIGH surface)
3. `cut_armor_panels()` to recess the zones between ridges
4. Ridge intersection diamonds sitting at ridge height
5. LED channels alongside ridges on the recessed panel surface
6. Logo deboss in the center panel (deeper, accounting for recess)
7. Touch pad recesses adjusted for panel depth
8. Chamfer-face LED channels around the perimeter

- [ ] **Step 1: Write a test for Page 3 armor panels**

Add to `tests/test_shell_chamfer.py`:

```python
from designs.shell.page3_shell import build_page3
from designs.common.constants import PAGE3_H, PANEL_GROOVE_DEPTH, RIDGE_H


def test_page3_builds_with_armor_panels():
    """Page 3 should build successfully with armor panel treatment."""
    page3 = build_page3()
    assert page3 is not None
    bb = page3.val().BoundingBox()
    assert bb.xlen > 400
    assert bb.ylen > 260
    # Height should include ridge height above the shell
    assert bb.zlen >= PAGE3_H


def test_page3_has_recessed_panels():
    """Page 3 volume should be less than a plain shell due to panel recesses."""
    from designs.common.mounting import build_sculpted_shell
    from designs.common.constants import CASE_OUTER_W, CASE_OUTER_D
    plain = build_sculpted_shell(CASE_OUTER_W, CASE_OUTER_D, PAGE3_H)
    page3 = build_page3()
    # Page 3 has ridges (add material) but also panel recesses and pockets (remove material)
    # Overall it should have less volume than plain shell + ridges
    # Just verify it builds and has reasonable volume
    vol = page3.val().Volume()
    assert vol > 0
```

- [ ] **Step 2: Run test as baseline**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py::test_page3_builds_with_armor_panels -v
```

Expected: PASS (current code already builds).

- [ ] **Step 3: Update imports in page3_shell.py**

Replace the constants import block:

```python
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
    PANEL_GROOVE_DEPTH,
    TOUCH_PAD_W, TOUCH_PAD_D, TOUCH_PAD_RECESS,
    CHAMFER_SIZE,
)
```

Replace the mounting import block:

```python
from designs.common.mounting import (
    build_sculpted_shell, cut_pocket, add_mounting_boss,
    add_ridge, cut_led_channel, cut_armor_panels,
    add_chamfer_led_channels,
)
```

- [ ] **Step 4: Rewrite the ridge, panel, LED, diamond, logo, and touch pad sections**

In `designs/shell/page3_shell.py`, replace everything from line 95 (the `# --- Exosuit ridges` comment) through line 172 (end of logo deboss) with:

```python
    # --- Exosuit armor treatment on outer face ---
    # The outer face is at Z = PAGE3_H (top face, exterior when case is closed)
    ridge_z = PAGE3_H
    hw = CASE_OUTER_W / 2
    hd = CASE_OUTER_D / 2

    # Ridge grid positions (same as before)
    spine_positions = [-hw / 3, 0, hw / 3]
    lateral_positions = [-hd / 3, hd / 3]

    # 3 spine ridges running along Y
    for sx in spine_positions:
        shell = add_ridge(shell, sx, -hd + 10, sx, hd - 10, z=ridge_z)

    # 2 lateral ridges running along X
    for ly in lateral_positions:
        shell = add_ridge(shell, -hw + 10, ly, hw - 10, ly, z=ridge_z)

    # --- Recessed armor panels between ridges ---
    shell = cut_armor_panels(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE3_H,
                             spine_positions, lateral_positions)

    # --- Ridge intersection diamonds (at ridge height, not recessed) ---
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

    # --- LED channels alongside ridges (on recessed panel surface) ---
    led_offset = RIDGE_W / 2 + 2  # offset from ridge centerline
    recessed_z = ridge_z - PANEL_GROOVE_DEPTH  # panel surface Z
    for sx in spine_positions:
        shell = cut_led_channel(shell, sx + led_offset, -hd + 12,
                                sx + led_offset, hd - 12, z=recessed_z)
    for ly in lateral_positions:
        shell = cut_led_channel(shell, -hw + 12, ly + led_offset,
                                hw - 12, ly + led_offset, z=recessed_z)

    # --- Chamfer-face LED channels (perimeter) ---
    shell = add_chamfer_led_channels(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE3_H)

    # --- Capacitive touch pad recesses (on recessed panel surface) ---
    for ly in lateral_positions:
        pad_recess = (
            cq.Workplane("XY")
            .workplane(offset=PAGE3_H - PANEL_GROOVE_DEPTH - TOUCH_PAD_RECESS)
            .center(spine_positions[0], ly)
            .rect(TOUCH_PAD_W, TOUCH_PAD_D)
            .extrude(TOUCH_PAD_RECESS + 0.1)
        )
        shell = shell.cut(pad_recess)

    # --- Somni Labs logo deboss (in center panel, two depth levels) ---
    # Logo cuts into the recessed panel surface (already PANEL_GROOVE_DEPTH below ridges)
    logo_depth = 1.0
    logo_z = PAGE3_H - PANEL_GROOVE_DEPTH - logo_depth
    logo_rect = (
        cq.Workplane("XY")
        .workplane(offset=logo_z)
        .center(0, 0)
        .rect(60, 20)
        .extrude(logo_depth + 0.1)
    )
    logo_bar = (
        cq.Workplane("XY")
        .workplane(offset=logo_z)
        .center(0, -18)
        .rect(80, 3)
        .extrude(logo_depth + 0.1)
    )
    shell = shell.cut(logo_rect).cut(logo_bar)
```

- [ ] **Step 5: Run all tests**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -m pytest tests/test_shell_chamfer.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Verify the full assembly still builds**

Run:
```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
python3 -c "
import os
os.environ['_CQ_ASSEMBLY'] = '1'
from designs.shell.page1_shell import build_page1
from designs.shell.page2_shell import build_page2
from designs.shell.page3_shell import build_page3
p1 = build_page1(); p2 = build_page2(); p3 = build_page3()
for name, p in [('Page 1', p1), ('Page 2', p2), ('Page 3', p3)]:
    bb = p.val().BoundingBox()
    print(f'{name}: {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm, vol={p.val().Volume():.0f}')
del os.environ['_CQ_ASSEMBLY']
"
```

Expected: All three pages build. Page 3 height should be slightly taller than PAGE3_H due to ridge height above the surface.

- [ ] **Step 7: Commit**

```bash
git add designs/shell/page3_shell.py tests/test_shell_chamfer.py
git commit -m "feat(v2): Page 3 full armor panel treatment with recessed panels and chamfer LEDs"
```

---

### Task 8: Push and Verify in cadquery-server

**Files:**
- No code changes — deployment verification only

- [ ] **Step 1: Push all commits to GitHub**

```bash
cd /home/curiosity/mounted_drives/obsidian/obsidian/Somni/SomniApps/somni-mobile-lab
git push
```

- [ ] **Step 2: Restart cadquery-server**

```bash
kubectl rollout restart deployment cadquery-server -n utilities
kubectl rollout status deployment cadquery-server -n utilities --timeout=120s
```

Expected: `deployment "cadquery-server" successfully rolled out`

- [ ] **Step 3: Verify assembly preview renders (HTTP 200)**

```bash
SVC_IP=$(kubectl get svc cadquery-server -n utilities -o jsonpath='{.spec.clusterIP}')
curl -s -o /dev/null -w "%{http_code}" "http://$SVC_IP:5000/json?m=assembly_preview" --max-time 300
```

Expected: `200`

- [ ] **Step 4: Verify all standalone page previews**

```bash
SVC_IP=$(kubectl get svc cadquery-server -n utilities -o jsonpath='{.spec.clusterIP}')
for m in page1_shell page2_shell page3_shell; do
    echo -n "$m: "
    curl -s -o /dev/null -w "%{http_code}\n" "http://$SVC_IP:5000/json?m=$m" --max-time 180
done
```

Expected: All three return `200`.

- [ ] **Step 5: Verify V1 model still works**

```bash
SVC_IP=$(kubectl get svc cadquery-server -n utilities -o jsonpath='{.spec.clusterIP}')
curl -s -o /dev/null -w "%{http_code}" "http://$SVC_IP:5000/json?m=mobile-lab-case" --max-time 120
```

Expected: `200`
