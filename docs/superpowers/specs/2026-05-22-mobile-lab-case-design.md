# Mobile Lab Case — Design Spec

## Overview

A rugged, portable, three-panel notebook-style case housing a complete mobile workstation. 3D printed hard shell (PETG) with custom foam inserts for device protection. Opens like a book — three rigid pages connected by hinges, each page containing dedicated foam cutouts for specific devices. Latches on the front edge, carry handle on the spine. Somni Labs logo debossed on the cover.

Designed for field use: camping, car, travel, on-the-go work. Fits in a large backpack or carries standalone by handle.

## Device Inventory

| Device | Dimensions (mm) | Thickness (mm) | Weight |
|--------|-----------------|----------------|--------|
| Starlink Mini | 299 × 259 | 39 | 1.16kg |
| Starlink PSU | 91 × 44 | 51 | ~200g |
| GL-iNet Mudi 7 (GL-E5800) | 157 × 75 | 23 | ~300g |
| Framework Laptop 12 | 287 × 214 | 18 | 1.30kg |
| iPad 13" (generic) | 280 × 215 | 7 | ~680g |
| 17" Portable Monitor | 400 × 250 | 15 | ~800g |
| Turtle Beach Vulcan II TKL | 366 × 137 | 32 | ~700g |
| Turtle Beach Burst II Air | 120 × 60 | 40 | 47g |
| Flipper Zero | 100 × 40 | 26 | 102g |
| Portable Battery Bank | ~180 × 80 | 25 (generic) | ~500g |
| Charging Block | ~80 × 80 | 30 (generic) | ~300g |

**Total estimated weight (devices only):** ~6.1kg
**Total estimated weight (with case):** ~8-9kg

## Case Dimensions

- **Footprint (closed):** ~440 × 320mm
- **Thickness (closed):** ~180-200mm (three pages, each ~55-65mm)
- **Wall thickness:** 3mm outer shell, 2mm internal dividers
- **Corner radius:** 5mm fillets for comfort and strength
- **Material:** PETG (impact resistant, heat tolerant for car interiors)

## Three-Page Notebook Layout

### Page 1 — Bottom (Power & Connectivity)
~55mm usable depth

```
┌──────────────────────────────────────────┐
│                              │ Starlink  │
│  Starlink Mini               │ PSU       │
│  (299×259×39)                │ (91×44×51)│
│  [foam cutout, snug fit]     │           │
│                              ├───────────┤
│                              │ Battery   │
│                              │ Bank      │
│                              │ (generic) │
└──────────────────────────────┴───────────┘
```

- Starlink Mini sits flat in its foam pocket (39mm thick — fits in 55mm depth with foam base/top)
- Starlink PSU and portable battery bank fill the remaining space to the right
- All power-related items in one layer

### Page 2 — Middle (Screens & Compute)
~30mm usable depth

```
┌──────────────────────────────────────────┐
│                                          │
│  17" Portable Monitor (400×250×15)       │
│  [full width, foam cutout]               │
│                                          │
├──────────────────────────────────────────┤
│  Framework 12 + iPad 13"                 │
│  [stacked with foam divider, ~25mm]      │
│  (287×214 footprint)                     │
│                                          │
└──────────────────────────────────────────┘
```

- Monitor gets the full width of the case (400mm monitor in 430mm internal width)
- Laptop and iPad share a pocket, stacked with a thin foam divider sheet (~25mm combined)
- This is the thinnest page — all flat devices

### Page 3 — Top / Cover (Accessories)
~45mm usable depth

```
┌──────────────────────────────────────────┐
│                                          │
│  Turtle Beach Keyboard (366×137×32)      │
│  [foam cutout, full width]               │
│                                          │
├────────────┬──────────┬──────────────────┤
│  Mudi 7    │ Mouse    │  Misc pocket     │
│(157×75×23) │(120×60×40)│ (Flipper Zero,  │
│            │          │  chargers,       │
│            │          │  cables, USBs)   │
└────────────┴──────────┴──────────────────┘
```

- Keyboard runs full width along the top half
- Mudi 7, mouse, and misc compartment arranged below
- Misc pocket: Flipper Zero, charging block, cables, adapters, USB drives, etc.
- Pick-and-pluck foam in the misc pocket for flexibility

## Construction

### Panel Assembly
Each page is a 3D-printed rigid shell (bottom half + rim) with foam insert:
- **Outer shell:** 3mm PETG walls, reinforced corners
- **Print tiles:** Each panel splits into 2-3 sections to fit QIDI Q2 bed (275×295mm)
- **Tile joining:** M3 heat-set inserts + M3 bolts, with alignment pins for rigidity
- **Seam reinforcement:** Tongue-and-groove joints along tile seams

### Hinges
- Piano-style hinge along one long edge (440mm side)
- Printed hinge knuckles integrated into panel edges
- 3mm steel rod through knuckle loops (hardware store piano hinge rod)
- Pages fold flat when fully open (~540° total rotation for 3 pages)

### Latches
- 2 snap latches on the front edge (opposite hinge side)
- Printed cantilever snap-fit latches with positive click
- Optional padlock loop holes for security

### Handle
- Integrated carry handle on the spine (hinge side)
- Printed as part of the outer shell, reinforced with thicker walls
- Ergonomic grip, centered on the spine

### Foam
- **Primary:** Custom-cut EVA foam inserts (density: 2lb/ft³)
- **Misc pocket:** Pick-and-pluck EVA grid for flexible layout
- **Divider sheets:** 3mm EVA foam between stacked items (laptop/iPad)
- **Generation:** CadQuery model exports 2D cutout templates for laser cutting or manual cutting

### Logo
- Somni Labs logo debossed into the outer face of Page 3 (visible when case is closed)
- Same style as the wearable charging dock

## Print Strategy

### Tile Layout (per page)
Each ~440×320mm panel splits into tiles:
- **Option A:** 2 tiles per panel (220×320mm each) — fits QIDI Q2 bed
- **Option B:** 4 tiles per panel (220×160mm each) — faster prints, easier reprints if one fails

Recommend Option A (2 tiles) to minimize seams.

### Print Settings
- **Material:** PETG
- **Layer height:** 0.2mm
- **Infill:** 20% gyroid (strength + weight balance)
- **Walls:** 4 perimeters (structural rigidity)
- **Supports:** Minimal — design for printability (no overhangs > 45°)

### Estimated Print Time
- 6 panels (3 pages × 2 halves) = ~6 prints
- Hinge knuckles, latches, handle = ~3-4 small prints
- **Total:** ~10 prints, estimated 40-60 hours total print time

## Parametric Design

All dimensions parametric in CadQuery:
- Device dimensions as named constants with tolerance (`TOL = 1.0mm` per side, learned from wearable dock)
- Wall thickness, corner radius, foam depth as parameters
- Panel tile split positions calculated from bed size
- Hinge knuckle spacing and diameter parametric
- Foam cutout depth = device thickness + 5mm (base foam) + 3mm (top clearance)

## File Structure

```
designs/
  mobile-lab-case.py          # Main CadQuery parametric design
  foam-templates.py           # 2D cutout templates for foam cutting
export_mobile_lab.py          # STL/STEP export script
k8s/
  slice-mobile-lab.yaml       # K8s slicer job template
output/
  *.stl, *.step               # Generated files
```
