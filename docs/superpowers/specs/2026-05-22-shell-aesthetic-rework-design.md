# Shell Aesthetic Rework — Chamfered Slab + Armor Panels

**Date:** 2026-05-22
**Status:** Design
**Scope:** Visual rework of all three page shells and Page 3 armor panel treatment

## Problem

The V2 "Exosuit" shells are plain rectangular boxes with small corner fillets. `build_sculpted_shell()` produces a flat-walled open box with no visual character. The `TAPER` constant is defined but never used. Page 3 — the primary visual surface when the case is closed — has ridges and LED channels but they sit on a flat plane with no depth or panel articulation. The result looks like a toolbox, not the cyberpunk exosuit the spec envisions.

## Design Decisions

Decisions made during brainstorming:

- **Surface complexity level:** Panel armor plating — recessed panel lines, raised border trim, beveled transitions. Support-free, ~25-30% more print time. (Not full sculpted contours or hex cutouts.)
- **Profile shape:** Chamfered slab — flat top/bottom with 15mm 45-degree chamfers on all horizontal edges. Chamfer faces host LED channels. (Not wedge taper or barrel/pillow.)
- **Panel layout:** Symmetric grid — 3 spine + 2 lateral ridges creating 6 rectangular armor panel zones with beveled recessed surfaces. (Not asymmetric or radial.)
- **Visual intensity:** Bold — 15mm chamfers, 1.5mm panel grooves, 1mm beveled edges. Visible from across the room but not eating interior volume.

## Chamfered Slab Shell

### Form

Every page shell starts as the current rectangular box (corner-filleted at CORNER_R = 15mm on vertical edges). After the box is formed and hollowed, 15mm 45-degree chamfers are applied to all horizontal edges:

- **Top rim:** 4 edges where the top face meets the side walls
- **Bottom perimeter:** 4 edges where the bottom face meets the side walls

This transforms the box cross-section from a rectangle into a beveled slab. When three pages are stacked, the adjacent chamfers create a layered look — each page reads as a distinct armored plate.

### Chamfer Implementation Strategy

CadQuery's `.chamfer()` on the filleted box is the preferred approach. If it fails due to edge-length conflicts between the 15mm chamfer and 15mm corner fillet, the fallback is a constructive approach:

1. Create a full-height box with corner fillets (current approach)
2. Create chamfer-cutting solids — wedge prisms along each top/bottom edge
3. Subtract the wedge prisms from the box

This is more verbose but geometrically reliable.

### Interior

Unchanged. Flat inner walls, flat floor. All device pockets, mounting bosses, and subsystem attachment points remain in their current positions. The chamfer is purely an exterior treatment that removes material from outer corners.

### LED Channels on Chamfer Faces

The current LED channels run along the flat inner rim (top perimeter). These move to the chamfer faces — the angled 45-degree surfaces around the top of each page. Each of the 4 chamfer faces gets one continuous LED channel running its full length.

The channel is cut perpendicular to the chamfer face surface (not vertically). This means the channel entry is angled at 45 degrees when viewed from the side, which naturally retains the LED strip and diffuser without additional snap features.

### New Constants

```
CHAMFER_SIZE = 15          # edge chamfer dimension (mm)
PANEL_GROOVE_DEPTH = 1.5   # armor panel recess depth below ridge surface
PANEL_GROOVE_WIDTH = 2     # groove cut width between panels
PANEL_BEVEL = 1            # bevel transition at groove edges
```

## Armor Panel Treatment (Page 3 Only)

### Concept

The ridges are not raised features on a flat surface. Instead, the ridges are the *high surface* and the panels between them are *recessed*. The ridge grid forms a structural frame, and each panel zone is an inset plate sitting 1.5mm below the frame surface.

### Layout

The existing ridge positions divide Page 3's outer face into a symmetric grid:

- **3 spine ridges** running along Y at X = {-W/3, 0, +W/3}, inset 10mm from edges
- **2 lateral ridges** running along X at Y = {-D/3, +D/3}, inset 10mm from edges
- This creates a grid of panel zones: 4 interior panels (between ridge intersections) + 8 edge/corner panels (between outermost ridges and the chamfer perimeter)

The 4 interior panels are the primary visual zones — they're the largest and most prominent. The edge panels are narrower accent zones that frame the interior panels.

### Panel Construction

For each panel zone:

1. A rectangular area is identified between adjacent ridges (or between a ridge and the chamfer edge)
2. The area is recessed 1.5mm (PANEL_GROOVE_DEPTH) below the ridge surface
3. A 1mm bevel (PANEL_BEVEL) transitions from the ridge surface down to the recessed panel
4. The panel floor is flat

### Ridge Intersection Diamonds

The existing chamfered diamond accents at ridge intersections remain. In the new scheme they read as armor bolt heads or rivets at the frame joints — a natural complement to the armor plating metaphor. They sit at the ridge surface height (the high point), not recessed.

### LED Channels

LED channels run alongside each ridge on the panel surface (recessed side), offset by RIDGE_W/2 + 2mm from the ridge centerline. Since the panel surface is 1.5mm below the ridge, the LED channel (3mm deep) cuts into the panel floor. The recessed position naturally shadows the LED strip, reducing direct glare.

### Logo

The Somni Labs geometric logo sits in the center panel of the grid (the largest interior panel, at the intersection of X=0 and Y=0). The deboss cuts 1mm into the already-recessed panel surface, giving two levels of depth: ridge surface → panel surface (1.5mm) → logo deboss (2.5mm total from ridge height).

### Touch Pads

Capacitive touch pad recesses sit in panel zones near the left-column ridge intersections, as currently positioned. The recessed panel surface means the touch pad recess is shallower (0.5mm below an already-recessed surface) which improves capacitive sensitivity through the thinner shell.

## Pages 1 and 2

Pages 1 and 2 get the chamfered slab profile and chamfer-face LED channels only. No armor panel grid — their outer surfaces face inward when the case is open, so the armor treatment on Page 3 alone is sufficient for the closed-case aesthetic.

The existing features on Pages 1 and 2 are preserved:
- **Page 1:** All device pockets, pedestal bosses, hinge servo bosses, latch catch bosses, cable pass-through
- **Page 2:** All device pockets, carry handle, electronics bay cutout, e-bay bosses, cam lift bosses, spine ridge

The Page 1 rim LED channels and Page 2 spine ridge LED channels move to chamfer faces.

## Files Changed

### Modified

| File | Change |
|------|--------|
| `designs/common/constants.py` | Add CHAMFER_SIZE, PANEL_GROOVE_DEPTH, PANEL_GROOVE_WIDTH, PANEL_BEVEL |
| `designs/common/mounting.py` | Rework `build_sculpted_shell()` for chamfered form; add `cut_armor_panels()` and `add_chamfer_led_channels()` helpers |
| `designs/shell/page1_shell.py` | Use chamfered shell, replace rim LEDs with chamfer LEDs |
| `designs/shell/page2_shell.py` | Use chamfered shell, replace rim LEDs with chamfer LEDs |
| `designs/shell/page3_shell.py` | Chamfered shell + armor panels + repositioned ridges/diamonds/logo/touch pads |

### Unchanged

All subsystem files: hinge_knuckles.py, latch_mechanism.py, hinge_servo_mount.py, pedestal_base.py, pedestal_platform.py, tilt_linkage.py, cam_lift.py, lift_plate.py, electronics_bay.py, button_mount.py, diffuser_strip.py, assembly_preview.py, export_v2.py.

M3 boss mounting positions are unchanged. All subsystem mechanical interfaces are preserved.

## Risks

1. **CadQuery chamfer on filleted edges:** The 15mm chamfer applied after 15mm corner fillets may fail if adjacent chamfer/fillet operations conflict geometrically. Mitigation: constructive wedge-subtraction fallback documented above.

2. **Interior volume loss:** The 15mm chamfer removes material from the outer shell corners. At the corners, the interior pocket edges may approach the chamfered outer wall. Mitigation: pockets already have 2mm clearance from inner walls; the chamfer only affects the outer surface at the top/bottom edges, not the mid-height walls where pockets are deepest.

3. **Print orientation:** The chamfered bottom edges mean the first layer is smaller than the widest cross-section. This is fine for bed adhesion (the flat bottom face is still the full footprint minus the chamfer perimeter — plenty of contact area).
