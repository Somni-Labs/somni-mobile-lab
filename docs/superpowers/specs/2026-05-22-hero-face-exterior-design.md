# Exosuit Exterior Design — Hero Face + Structural Ribs

## Problem

The case exterior looks like a plain rectangular toolbox despite having chamfers, side ribs, and a logo deboss. The changes are geometrically present but visually too subtle at the case's scale (~412×271mm). The uniform treatment on all four walls reads as "industrial storage" rather than "cyberpunk exosuit."

## Design

All changes are exterior-only. Zero interior volume loss.

### Hero Face (Front Wall, +Y)

Three-layer depth treatment creating 5mm total depth variation:

1. **Raised center logo plate** — ~120mm wide × 50mm tall, centered on the front wall, protruding 3mm proud of the wall surface. The plate surface is recessed 1.5mm everywhere EXCEPT the logo shapes (nameplate rectangle, accent bar, flanking chevrons), which remain at the full 3mm proud height. This creates a "raised logo from recessed background" effect with strong shadow lines.

2. **Recessed hex panels** — Two panel zones, one above and one below the logo plate. Each panel is recessed 1.5mm into the wall surface and filled with a grid of 15mm-across hexagonal pockets cut an additional 0.5mm deeper (2mm total from outer wall). Hex walls between pockets are ~2mm thick.

3. **Frame grooves** — 2mm wide, 1mm deep grooves separating the three zones (upper hex panel, logo plate, lower hex panel), creating visible shadow-line transitions between armor segments.

### Secondary Sides (Back, Left, Right)

- **Back wall (-Y):** 3 bold vertical ribs, 4mm wide, 3mm proud, evenly spaced. Reads as structural reinforcement.
- **Short sides (±X):** 1-2 bold vertical ribs each (same dimensions), placed toward center to avoid hinge/latch zones near the edges.
- **All sides** keep the 10mm top/bottom chamfers — the consistent slab profile that ties the case together.

### Removed Features

- Uniform 2mm ribs every 40mm on all four walls (replaced by hero face + structural ribs)
- Old logo deboss into front wall (replaced by raised logo plate)
- Constants: `SIDE_RIB_W=6`, `SIDE_RIB_H=2`, `SIDE_RIB_SPACING=40` replaced

### Per-Page Treatment

All 3 pages (78mm, 53mm, 51mm) get the same exterior treatment. When stacked, the armor plates and hex panels align vertically across pages.

## CadQuery Implementation

### Hex Grid Strategy

Build hex panels using an additive approach (faster than subtractive):
1. Cut the recessed panel rectangle into the wall (single boolean)
2. Build the hex wall grid as a compound of thin ridges and union onto the recessed surface
3. This inverts "cut 50 hexes" into "add hex walls" — fewer booleans, cleaner topology

### New Functions

- `build_hero_face(body, width, depth, height)` — Full front-wall treatment: logo plate, hex panels, frame grooves
- `add_structural_ribs(body, width, depth, height)` — Fewer/bolder ribs on back and short sides only (not front)

### Replaced Functions

- `add_side_ribs()` → `add_structural_ribs()`
- `add_logo_deboss()` → absorbed into `build_hero_face()`

### Dimensions

| Feature | Dimension |
|---|---|
| Logo plate size | ~120 × 50mm |
| Logo plate proud height | 3mm |
| Logo recess into plate | 1.5mm |
| Hex panel recess from wall | 1.5mm |
| Hex pocket additional depth | 0.5mm |
| Hex size (across flats) | 15mm |
| Hex wall thickness | ~2mm |
| Frame groove width | 2mm |
| Frame groove depth | 1mm |
| Structural rib width | 4mm |
| Structural rib proud height | 3mm |
| Back wall ribs | 3 |
| Short side ribs | 1-2 each |
| Total depth variation (hero face) | 5mm |

### Build Time

Expecting ~5-8 seconds per page (up from ~3s). Assembly preview under 30 seconds.
