# Somni Mobile Lab

Portable three-page notebook-style case for a complete mobile workstation. 3D printed hard shell (PETG) with custom foam inserts, designed in CadQuery and printed on a QIDI Q2 via Klipper/Moonraker.

## Architecture

- **`designs/mobile-lab-case.py`** — Main CadQuery parametric design (3 pages + hinges + latches + handle)
- **`designs/foam-templates.py`** — 2D foam cutout templates for laser/manual cutting
- **`export_mobile_lab.py`** — STL/STEP export script
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
