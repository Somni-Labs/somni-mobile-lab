# Somni Mobile Lab

Portable three-page notebook-style case for a complete mobile workstation. 3D printed hard shell (PETG) with custom foam inserts, designed in CadQuery and printed on a QIDI Q2 via Klipper/Moonraker.

## Architecture

### V2 "Exosuit" (Active)

Modular subsystem design with motorized mechanisms, LED lighting, and ESP32 brain. Each subsystem is a CadQuery Python module importing from shared constants and helpers.

```
designs/
  common/
    __init__.py
    constants.py          # All parametric dimensions, tolerances, device specs
    mounting.py           # Shared helpers: sculpted shell, pockets, bosses, channels, ridges, tiles
  shell/
    __init__.py
    page1_shell.py        # Page 1 — Bottom (Starlink, PSU, battery)
    page2_shell.py        # Page 2 — Middle (monitor, laptop, iPad, carry handle)
    page3_shell.py        # Page 3 — Top/cover (keyboard, mouse, Mudi, ridges, LEDs, logo)
  hinge/
    __init__.py
    hinge_knuckles.py     # 10mm geared knuckles with hollow tube bore for wiring
    latch_mechanism.py    # SG90 servo latch housing + hook + catch
    hinge_servo_mount.py  # MG996R bracket + spur gear for motorized opening
  starlink/
    __init__.py
    pedestal_base.py      # Linear actuator mount + guide rail bushings
    pedestal_platform.py  # Rising platform with tilt hinge barrel
    tilt_linkage.py       # MG996R tilt servo mount + linkage arm
  lifts/
    __init__.py
    cam_lift.py           # Eccentric cam + SG90 housing (reused 3x)
    lift_plate.py         # Per-device lift plates (laptop, monitor, keyboard)
  electronics/
    __init__.py
    electronics_bay.py    # ESP32/PCA9685 enclosure (120x40x30mm) + lid
    button_mount.py       # Recessed 12mm push button housing
  led/
    __init__.py
    diffuser_strip.py     # Snap-in translucent LED channel covers
  assembly/
    __init__.py
    assembly_preview.py   # Full case assembly view for cadquery-server
export_v2.py              # STL/STEP export for all V2 printable parts
docs/
  superpowers/
    specs/2026-05-22-mobile-lab-case-v2-design.md   # Full design spec
    plans/2026-05-22-mobile-lab-case-v2.md           # Implementation plan
```

**Key dimensions (derived):** Case outer: ~412 × 271 × 185mm, ~9-11kg total weight

**Subsystem interfaces:** All subsystems connect via M3 heat-set insert mounting bosses (8mm OD, 4.2mm insert hole, 1mm alignment ring). JST connectors with different pin counts per subsystem for fool-proof wiring.

**Motors:** 3x MG996R high-torque servos (hinge opening, Starlink tilt), 5x SG90 micro servos (2 latches, 3 cam lifts), 1x 12V linear actuator (Starlink pop-up pedestal, 50mm stroke)

**Electronics:** ESP32-S3 brain, PCA9685 16-ch PWM servo driver (I2C), WS2812B addressable RGB LEDs (~222 total), TP4056 LiPo charger + boost converter, dual power (3.7V LiPo always-on + 5V battery bank pass-through)

### V1 (Preserved)

- **`designs/mobile-lab-case.py`** — V1 single-file parametric design (3 pages + hinges + latches + handle)
- **`designs/foam-templates.py`** — 2D foam cutout templates for laser/manual cutting
- **`export_mobile_lab.py`** — V1 STL/STEP export script
- **`k8s/slice-mobile-lab.yaml`** — K8s Job template for PrusaSlicer slicing + Moonraker upload
- **`output/`** — Generated STL/STEP files
- Live preview via `cadquery-server` deployment in K8s (`utilities` namespace)

## Device Inventory

| Device | Dimensions (mm) | Page |
|--------|-----------------|------|
| Starlink Mini | 299×259×39 | 1 (Bottom) |
| Starlink PSU | 91×44×51 | 1 (Bottom) |
| Portable Battery Bank | ~180×80×25 | 1 (Bottom) |
| 17" Portable Monitor | 400×250×15 | 2 (Middle) |
| Framework Laptop 12 | 287×214×18 | 2 (Middle) |
| iPad 13" | 280×215×7 | 2 (Middle) |
| Turtle Beach Vulcan II TKL | 366×137×32 | 3 (Top) |
| Turtle Beach Burst II Air | 120×60×40 | 3 (Top) |
| GL-iNet Mudi 7 | 157×75×23 | 3 (Top) |
| Flipper Zero | 100×40×26 | 3 (Top/Misc) |
| Charging Block | ~80×80×30 | 3 (Top/Misc) |

## QIDI Q2 Printer

- **Moonraker API**: `http://192.168.1.15:7125`
- **Actual build volume**: X: 0-275, Y: 0-295, Z: 0-265
- **Bed shape for PrusaSlicer**: `0x0,275x0,275x295,0x295`, center `137,147`
- **Klipper gcode flavor** in all slicer profiles

## Design Principles (from Wearable Dock)

- **Tolerance**: `TOL = 1.0mm` per side for device pockets (snug but removable)
- **PrusaSlicer temp bug**: Post-process gcode with `sed` to fix M104/M109/M140/M190 temperatures
- **Filament sensor**: Always enable `filament_switch_sensor` via `ENABLE_ALL_SENSOR` macro before printing
- **Moonraker upload race**: Add `sleep 2` between delete and upload operations
- **Node selector**: Use `kubernetes.io/arch: amd64` for slicer jobs (image is amd64-only)
- **INI whitespace**: Strip leading whitespace from heredoc-generated INI files with `sed`

## V2 Lessons Learned

### cadquery-server compatibility

- **RGBA tuples only**: `show_object()` colors MUST use RGBA tuples like `(0.27, 0.51, 0.71, 0.7)`, NOT CSS color name strings. String colors cause `TypeError: can only concatenate tuple (not "list") to tuple`.
- **No `.text()` calls**: Fontconfig is not available in the cadquery-server container. Use geometric shapes (rectangles, etc.) for logos instead.
- **Nested file discovery**: cadquery-server git-sync uses `find "${repo}/designs" -name "*.py" -not -name "__init__.py"` to symlink all design files from subdirectories (updated in SomniKubernetes ArgoCD manifest).
- **sys.path bootstrap**: V2 assembly_preview.py uses `os.path.realpath(__file__)` to resolve the symlink back to the repo root and adds it to `sys.path` before package imports. This is required for `from designs.shell.page1_shell import ...` to work when the file is loaded via a symlink in `/projects/`.

### Modular CadQuery package structure

- Each subsystem is its own Python package under `designs/` with an `__init__.py`.
- All parametric dimensions live in `designs/common/constants.py` — no magic numbers in subsystem files.
- Shared CadQuery helpers (shell builder, pocket cutter, mounting boss, wire/LED channel, ridge, tile splitter) live in `designs/common/mounting.py`.
- Every module has a `try/except ImportError` guard for standalone cadquery-server preview.
- The export script (`export_v2.py`) mocks `cq_server` before importing modules so their standalone preview blocks don't fire.

### Print strategy

- Shell pages split into left/right tiles at X=0 to fit QIDI Q2 bed (275×295mm).
- Tile seam features: tongue-and-groove alignment + M3 bolt holes along the split.
- Separate STL per printable part, all translated to Z=0 for direct slicing.
- STEP exports for assembled views (pre-split) for CAD interchange.
