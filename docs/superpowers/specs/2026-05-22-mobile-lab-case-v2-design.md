# Mobile Lab Case V2 — "Exosuit" Design Spec

## Overview

A futuristic, motorized, three-panel notebook-style case housing a complete mobile workstation. Sculpted organic shell (PETG) with raised geometric ridge lines, integrated addressable RGB LED channels, motorized latches, motorized lid opening, a pop-up Starlink deployment pedestal, cam-driven device lifts, and an ESP32 brain with Wi-Fi/BLE phone control. Over-engineered. Deliberately.

Same device inventory as V1. Same three-page notebook layout. Completely redesigned shell, hinge, latch, and accessory systems.

Modular subsystem architecture — each subsystem is independently designed, printed, tested, and bolted together via standardized M3 heat-set insert mounting points.

## Device Inventory

| Device | Dimensions (mm) | Thickness (mm) | Weight |
|--------|-----------------|----------------|--------|
| Starlink Mini | 299 x 259 | 39 | 1.16kg |
| Starlink PSU | 91 x 44 | 51 | ~200g |
| GL-iNet Mudi 7 (GL-E5800) | 157 x 75 | 23 | ~300g |
| Framework Laptop 12 | 287 x 214 | 18 | 1.30kg |
| iPad 13" (generic) | 280 x 215 | 7 | ~680g |
| 17" Portable Monitor | 400 x 250 | 15 | ~800g |
| Turtle Beach Vulcan II TKL | 366 x 137 | 32 | ~700g |
| Turtle Beach Burst II Air | 120 x 60 | 40 | 47g |
| Flipper Zero | 100 x 40 | 26 | 102g |
| Portable Battery Bank | ~180 x 80 | 25 (generic) | ~500g |
| Charging Block | ~80 x 80 | 30 (generic) | ~300g |

**Total estimated weight (devices only):** ~6.1kg
**Total estimated weight (with case + mechatronics):** ~9-11kg

## Subsystem Architecture

Six independently designed, printed, and testable subsystems bolted to a common shell via M3 heat-set inserts:

```
 Shell System (sculpted panels, LED channels, mounting bosses)
    |
    +-- Hinge & Latch System (motorized latches, spring-assisted hinge, lid servos)
    +-- Starlink Deployment System (linear actuator pedestal, tilt servo)
    +-- Device Lift System (3x cam lifts for laptop, monitor, keyboard)
    +-- Electronics Bay (ESP32, PCA9685, LiPo, power management)
    +-- LED System (WS2812B strips, diffusers, daisy chain)
```

---

## Subsystem 1: Shell System — The Exosuit

### Organic Base Form

- All outer edges get 15-20mm fillets — no sharp corners anywhere on the outside
- Profile tapers slightly: thicker in the center, thinner toward edges (~3mm taper per side)
- Overall footprint: ~440 x 320mm closed (driven by 17" monitor and keyboard)
- Wall thickness: 3mm outer shell, 2mm internal dividers
- Material: PETG (impact resistant, heat tolerant for car interiors)
- Total closed thickness: ~185mm (75 + 50 + 48 + walls)

### Carry Handle

- Integrated into Page 2 spine wall (-X edge), centered along the depth
- Printed as part of the Page 2 shell tile, reinforced with 5mm thick walls
- Ergonomic U-shape with 15-20mm fillets matching the organic shell aesthetic
- 100mm grip span, extends 25mm outward from spine surface
- LED channel runs along the handle spine for accent lighting

### Exosuit Surface Detail

- Three raised spine ridges running lengthwise along Page 3 outer face: 2mm proud, 4mm wide, 45-degree chamfered edges. Double duty as structural ribs and LED channel guides.
- Two lateral ridges running across the width, intersecting the spines. Creates a geometric grid pattern — the "armor panel" look.
- Ridge intersections have small 3mm chamfered diamonds where they cross.
- Ridge accent lines continue down the sides of each page (thinner, 1.5mm proud).

### LED Channels

- 4mm wide x 3mm deep channels run alongside every ridge line, recessed into the shell surface
- Sized for WS2812B strips (5mm wide, slight compression press-fit for retention)
- Translucent PETG diffuser strips (printed separately in clear filament) snap over each channel
- Channels connect through hinge side via pass-through slots for continuous wiring

### Standardized Mounting Interface

All subsystems attach via M3 heat-set inserts in the shell walls. Pre-positioned mounting boss patterns:

| Mount Point | Count | Location | Subsystem |
|-------------|-------|----------|-----------|
| Spine electronics | 4 | Page 2 spine (-X wall) | Electronics bay |
| Latch mounts | 2 per latch (4 total) | Page 1 + Page 3 front (+X) edge | Servo latches |
| Pedestal base | 4 | Page 1 floor, Starlink pocket area | Starlink pedestal |
| Cam lift pivots | 2 per lift (6 total) | Page 2 + Page 3 pocket floors | Device lifts |
| Hinge servos | 2 per servo (4 total) | Page 1 spine, near hinge line | Lid opening servos |

All mounting bosses: 8mm OD cylindrical posts molded into inner wall, 6mm deep for heat-set inserts.

### Tile Printing

- Each page splits into left/right tiles at centerline (same as V1)
- Tongue-and-groove alignment along seam + M3 bolts through heat-set inserts
- Organic fillets and ridges designed printable: no overhangs beyond 45 degrees
- Ridges print upward, LED channels are open-top (diffuser snaps in post-print)
- Each tile fits QIDI Q2 bed (275 x 295mm)

### Three-Page Layout (Internal Pockets)

Same device arrangement as V1:

**Page 1 — Bottom (Power & Connectivity), ~75mm depth (increased from 59mm to accommodate Starlink pedestal mechanism):**
- Starlink Mini (left, large pocket)
- Starlink PSU (top-right)
- Battery Bank (bottom-right, rotated 90 degrees)

**Page 2 — Middle (Screens & Compute), ~50mm depth:**
- 17" Portable Monitor (full width, shallow shelf)
- Framework Laptop + iPad (stacked sub-pocket with foam divider)

**Page 3 — Top/Cover (Accessories), ~48mm depth:**
- Keyboard (top, full width)
- Mudi 7 (bottom-left), Mouse (bottom-center), Misc pocket (bottom-right)

---

## Subsystem 2: Hinge & Motorized Latch System

### Upgraded Piano Hinge

- Interleaving knuckles along -X edge with hollow steel tubes (3mm OD, 2mm ID) as hinge rod
- Hollow tubes allow wiring harness to pass through (replaces solid 3mm rod from V1)
- Knuckle OD: 10mm (increased from 8mm for added weight)
- Knuckle segments: 20mm with 1.5mm gaps
- Retaining C-clips (printed) snap over grooves at each end of the tube
- Page 2 gets a torsion spring assist (off-the-shelf, ~0.5mm wire, 10mm OD) wrapping the hinge tube at center-span — biases Page 2 to crack open when latches release

### Motorized Lid Opening

- 2x MG996R high-torque servos (~10kg-cm), one per hinge joint
- Servo 1: mounted in Page 1 spine, drives Page 2 open via spur gear meshing with gear sector on Page 2 hinge knuckle
- Servo 2: mounted in Page 2 spine, drives Page 3 open via same gear mechanism
- Target open angle: ~110 degrees per page
- Closing is manual — servos backdrive when pushed
- Latch auto-engage: a small reed switch + magnet pair at each latch position detects when pages are fully closed; ESP32 fires latch servos to engage hooks automatically

### Motorized Latches

- 2x SG90 micro servos (9g each), one per latch position on +X front edge
- Each drives a printed hook/cam mechanism
- Default state: hook engaged (locked). 90-degree rotation to disengage.
- Latch housing: printed enclosure 30 x 20 x 15mm, bolts to shell mounting bosses
- Physical override: finger tab on hook for manual release if electronics are dead

### Open Sequence

1. User triggers open (button, phone, or capacitive touch)
2. ESP32 fires 2x latch servos — hooks release
3. Torsion spring cracks case open ~5 degrees
4. Hinge servos open Page 2 to 110 degrees, then Page 3 to 110 degrees
5. LED chase animation runs along ridge lines
6. Device lifts activate after 2-second delay

---

## Subsystem 3: Starlink Deployment System — Pop-Up Pedestal

### Pedestal Mechanism

- 12V linear actuator (50mm stroke, ~50N force) mounted vertically beneath Starlink pocket in Page 1
- Pushes a printed platform plate (300 x 260mm) straight up through the pocket opening
- 4x printed guide rails (8mm OD rods in printed bushings with PTFE sleeves) at corners for level travel
- At full extension: Starlink sits ~50mm above Page 1 rim, fully clear of case walls

### Tilt Mechanism

- Platform connects to actuator via a tilt hinge along one long edge (closest to case spine)
- MG996R high-torque servo on platform underside drives tilt via printed linkage arm
- Tilt range: 0 degrees (flat/stowed) to 45 degrees (angled toward sky)
- Tilt axis along 300mm edge — dish tilts away from user when deployed
- Default tilt: 35 degrees (optimal for most latitudes), adjustable via phone app slider

### Deployment Sequence

1. ESP32 signals "deploy Starlink"
2. Linear actuator extends — platform rises 50mm (~3 seconds)
3. Tilt servo rotates dish to 35 degrees
4. Page 1 rim LEDs pulse blue during deployment, steady cyan when complete
5. Tilt angle adjustable via web UI slider

### Stow Sequence

1. Tilt servo returns to 0 degrees
2. Linear actuator retracts — platform descends flush into pocket
3. Starlink rests in foam pocket, no visible mechanism when stowed

### Power

- Actuator needs 12V via boost converter (5V to 12V) from battery bank pass-through
- Draw: ~1A for ~3 seconds per deployment — negligible total energy
- Feature disabled when battery bank not present (ESP32 checks voltage sense pin)

### Cable Pass-Through

- The Starlink Mini connects to its PSU via a proprietary cable
- A 15mm diameter cable pass-through hole in the Page 1 side wall (+X edge, near the PSU pocket) allows the Starlink cable to reach the PSU while the dish is deployed on the pedestal
- The pass-through has a printed rubber grommet channel for strain relief
- When stowed, the cable coils in the gap between the Starlink pocket wall and the pedestal guide rails

### Structural

- Pedestal base bolts to 4x M3 mounting bosses in Page 1 floor
- Guide rails printed as part of base plate with replaceable PTFE bushing sleeves
- Adds ~15mm to Page 1 depth (59mm to 75mm) to accommodate actuator beneath pocket

---

## Subsystem 4: Device Lift System

### Cam Lift Mechanism

- Each lift: 1x SG90 micro servo (9g) driving a printed eccentric cam
- Cam sits beneath foam pocket floor in a recessed cavity in the shell wall
- 180-degree servo rotation pushes cam high point through a slot in pocket floor, raising a printed lift plate
- Lift height: ~20mm — enough to get fingers under device edge
- Return: servo back to 0 degrees, device settles into foam under own weight

### Why Cams

- Light (9g servo vs 100g+ actuator)
- Cheap ($2 SG90 vs $15 actuator)
- Small — fits in shell wall thickness plus inner wall boss
- Sufficient force: SG90 produces ~1.8kg-cm, cam mechanical advantage multiplies this

### Devices with Lifts

| Device | Weight | Page | Cam Position |
|--------|--------|------|-------------|
| Framework Laptop | 1.3kg | Page 2 | Center of laptop sub-pocket |
| 17" Monitor | 800g | Page 2 | Center of monitor pocket |
| Keyboard | 700g | Page 3 | Center of keyboard pocket |

### Activation

- Auto-activate 2 seconds after page reaches full open (hinge servo target angle as trigger)
- Individually controllable from phone app
- No manual override needed — cam rests in low position when unpowered, doesn't obstruct

### Wiring

- 3 wires per SG90 (5V, GND, signal) routed through printed wire channels (3mm x 3mm grooves with snap-on covers)
- Page-to-page routing through hollow hinge tubes

---

## Subsystem 5: Electronics Bay

### Location

- Built into -X (hinge side) wall of Page 2, center page
- Enclosed printed box: 120 x 40 x 30mm internal
- Bolts to 4x spine mounting bosses
- Removable lid (2x M2 screws) for board access
- Center-span of case depth, between hinge knuckles

### Components

| Component | Purpose | Size (approx) |
|-----------|---------|---------------|
| ESP32-S3 DevKitC | Main controller (Wi-Fi, BLE, GPIO) | 55 x 26mm |
| PCA9685 PWM driver | 16-channel servo driver over I2C | 62 x 26mm |
| TP4056 module | LiPo charge controller, USB-C input | 26 x 17mm |
| 5V-to-12V boost converter | Powers Starlink linear actuator | 22 x 17mm |
| LiPo cell (3.7V 2000mAh) | Backup power for LEDs + latches | 60 x 35 x 8mm |
| Voltage divider + MOSFET | Battery bank detection + pass-through | 20 x 20mm perfboard |

### Power Architecture

```
Battery Bank (5V USB) ---+--- Boost to 12V ---> Linear actuator (Starlink)
                         +--- 5V rail ---> PCA9685 ---> All servos (5x SG90 + 2x MG996R)
                         +--- 5V rail ---> ESP32 + WS2812B LED strips

Built-in LiPo (3.7V) ---> TP4056 ---> 3.3V/5V regulator
                           +--- ESP32 (always-on, deep sleep when closed)
                           +--- Latch servos (2x SG90, must always work)
                           +--- LED strips (reduced brightness)
```

### Power Modes

- **Full power** (battery bank present): All features available — servos, actuator, LEDs at full brightness, phone app
- **LiPo-only** (battery bank absent): Latches + LEDs + phone control only. Lid servos, lifts, and Starlink pedestal disabled.
- **Deep sleep** (case latched closed): ~10 microamps draw. LiPo lasts months. Wake via button GPIO interrupt, BLE connection, or capacitive touch.

### Servo Allocation (PCA9685 Channels)

| Channel | Servo | Type |
|---------|-------|------|
| 0 | Latch 1 (front-left) | SG90 |
| 1 | Latch 2 (front-right) | SG90 |
| 2 | Hinge servo Page 1-2 | MG996R |
| 3 | Hinge servo Page 2-3 | MG996R |
| 4 | Starlink tilt | MG996R |
| 5 | Laptop cam lift | SG90 |
| 6 | Monitor cam lift | SG90 |
| 7 | Keyboard cam lift | SG90 |
| 8-15 | Reserved / spare | — |

### External Connectors

- 1x USB-C port on spine exterior (LiPo charging via TP4056)
- 1x internal JST-PH 2-pin for battery bank pass-through cable
- Servo connectors: standard 3-pin DuPont headers on PCA9685
- LED data: 1x 3-pin JST-SM connector

---

## Subsystem 6: LED System

### Strip Specification

- WS2812B addressable RGB, 60 LEDs/meter
- 5V logic, single data pin from ESP32
- One continuous daisy chain: Page 1 -> Page 2 -> Page 3 through hollow hinge tubes

### Layout

| Page | Location | Strip Length | LED Count | Purpose |
|------|----------|-------------|-----------|---------|
| Page 1 | Rim perimeter (inner edge, top face) | ~1.4m | ~84 | Underlighting, Starlink deploy status |
| Page 2 | Spine ridge channels (both outer faces) | ~0.6m | ~36 | Spine accent, visible closed or open |
| Page 3 | All 5 ridge channels (3 spine + 2 lateral) | ~1.2m | ~72 | Cover art — main visual when closed |
| All | Side wall edge accent | ~0.5m | ~30 | Table underglow |

**Total: ~3.7m, ~222 LEDs. Peak draw ~13A full white (never used). Typical animated patterns: 2-3A.**

### Diffusion

- Ridge channels: snap-in translucent PETG diffuser strips (printed in clear/natural PETG)
- Rim perimeter: no diffuser, LEDs face inward/upward for interior wash
- Side wall edges: LEDs face downward for table underglow

### Animation Profiles

| Event | Animation | Duration |
|-------|-----------|----------|
| Wake / unlock | White flash, fade to accent color | 0.5s |
| Latch release | Blue pulse at latch positions, ripple outward | 1s |
| Page opening | Chase following page swing | 2s |
| Starlink deploying | Page 1 rim blue pulse, accelerating | 3s |
| Starlink online | Page 1 rim steady cyan | continuous |
| Device lift | White pulse under lifted device | 0.5s |
| Idle (open) | Slow breathing in accent color | continuous |
| Low LiPo | Red pulse on spine, 5s interval | until charged |
| Closing | Reverse chase, fade to off | 2s |
| Sleep | All off | — |

### User Customization (via phone/web UI)

- Accent color picker (HSV)
- Brightness slider (10-100%)
- Animation speed
- Toggle individual zones on/off
- Stealth mode — all LEDs off

---

## Control Interface

### Physical Button

- 12mm metal push button with blue LED ring, recessed into Page 2 spine wall next to USB-C port
- Flush mount — does not protrude past shell surface
- Short press: unlatch + open sequence
- Long press (2s): deploy Starlink
- Double press: close sequence (retract lifts, wind down LEDs — manual push to close pages, latches auto-engage)
- Triple press: stealth mode toggle

### Capacitive Touch Zones

- 2x touch pads on Page 3 outer cover, integrated at lateral ridge intersections
- Copper tape under shell surface, wired to ESP32 touch GPIO pins
- Left pad tap: wake + unlock (same as button short press)
- Right pad swipe: cycle LED color profiles
- 1-second hold requirement to prevent accidental triggers in backpack
- Auto-calibrates on boot via ESP32 touch API

### Phone App (ESP32 Web Server)

Responsive web UI served by ESP32 over Wi-Fi. Not a native app.

ESP32 creates soft AP (`SomniLab-XXXX`) or joins known network (Mudi 7 / Starlink).

**Web UI pages:**
- **Dashboard**: Case status (open/closed, battery levels, Starlink state), quick-action buttons
- **Controls**: Individual subsystem buttons — open/close, deploy Starlink, raise/lower lifts, LED zones
- **Starlink**: Tilt angle slider (0-45 degrees), deploy/stow, signal status
- **LEDs**: Color picker, brightness, animation profile, zone toggles, stealth mode
- **Settings**: Wi-Fi config, button behavior, auto-deploy preferences, OTA firmware update

### Auto-Behaviors (all off by default, configurable)

- Auto-deploy Starlink on open
- Auto-lift devices when page fully opens
- Auto-stow all on close
- Auto-sleep after 30 min idle with case closed

---

## Assembly & Wiring Harness

### Wiring Harness

- All inter-page wiring through hollow hinge tubes (2mm ID)
- Flat flex ribbon per hinge tube: 8 conductors (5V, GND, 12V, servo signal x3, LED data, sense)
- Labeled JST-PH connectors at each end, color-coded heat shrink:
  - Red = power
  - Blue = servo
  - Green = LED
  - Yellow = sensor
- Intra-page wiring in printed channels (3mm x 3mm grooves) with snap-on covers

### Assembly Order

| Step | Action | Verification |
|------|--------|-------------|
| 1 | Print all shell tiles, join left/right halves per page (M3 bolts + heat-set inserts) | Tiles flush, no rocking |
| 2 | Install heat-set inserts in all mounting bosses (30 total) | Each insert flush with surface |
| 3 | Mount electronics bay in Page 2 spine, connect USB-C port | USB-C accessible from outside |
| 4 | Install ESP32 + PCA9685 + LiPo + TP4056 in bay, wire power bus | TP4056 LED lights on USB-C |
| 5 | Mount latch servo housings (2x) on Page 3, catches on Page 1 | Hooks engage/disengage by hand |
| 6 | Mount hinge servos (2x) in Page 1 spine, gear sectors on knuckles | Gears mesh, <0.5mm backlash |
| 7 | Install Starlink pedestal in Page 1 — actuator, rails, tilt servo | Platform rises/lowers without binding |
| 8 | Install cam lifts (3x) in Page 2 and Page 3 pockets | Lift plates move freely in floor slots |
| 9 | Press-fit LED strips into channels, connect daisy chain | All LEDs flash test pattern |
| 10 | Thread hinge tube wiring harness, connect JST per color code | Continuity test each conductor |
| 11 | Assemble hinges — slide tubes through knuckles, install C-clips | Pages swing freely |
| 12 | Flash ESP32 firmware, run self-test routine | Self-test passes on web UI |
| 13 | Install foam inserts, snap LED diffuser strips into channels | Foam flush, diffusers click in |
| 14 | Install button and capacitive touch pads, final check | Button LED lights, touch responds |

### Self-Test Routine (Firmware)

On first boot or triggered from web UI:
- Blink each LED zone individually
- Pulse each servo to 45 degrees and back
- Extend/retract Starlink actuator 10mm
- Read battery bank voltage, LiPo voltage, touch pad baseline
- Report pass/fail per subsystem on web UI dashboard
- Failed subsystem flagged red with description (e.g., "Page 1 lift servo: no PWM response")

### Alignment & Fool-Proofing

- Every mounting boss has a raised alignment ring (1mm tall) — subsystems only fit one way
- Hinge knuckles have asymmetric chamfers — only assemble in correct orientation
- JST connectors use different pin counts per subsystem — physically impossible to cross-connect

---

## Bill of Materials — Electronics & Hardware

| Item | Qty | Approx Cost |
|------|-----|-------------|
| ESP32-S3 DevKitC | 1 | $8 |
| PCA9685 16-ch PWM driver | 1 | $4 |
| SG90 micro servo (9g) | 5 | $10 |
| MG996R high-torque servo | 3 | $18 |
| 12V linear actuator (50mm stroke) | 1 | $15 |
| WS2812B LED strip (60/m, 5m roll) | 1 | $12 |
| TP4056 USB-C LiPo charger | 1 | $2 |
| 3.7V 2000mAh LiPo cell | 1 | $8 |
| 5V-to-12V boost converter | 1 | $3 |
| 12mm metal push button (LED ring) | 1 | $4 |
| Copper tape (capacitive touch) | 1 roll | $5 |
| Hollow steel tubes 3mm OD x 2mm ID (320mm) | 2 | $3 |
| Torsion spring (0.5mm wire, 10mm OD) | 1 | $2 |
| M3 heat-set inserts | 30 | $5 |
| M3 x 6mm bolts | 30 | $3 |
| M2 x 4mm screws (electronics bay lid) | 2 | $1 |
| JST-PH connectors (assorted) | 10 | $4 |
| 8-conductor flat flex ribbon (1m) | 1 | $3 |
| PTFE bushing sleeves (8mm ID) | 4 | $3 |
| Retaining C-clips (printed) | 4 | printed |
| Color-coded heat shrink | assorted | $3 |
| Reed switches (N/O) | 2 | $2 |
| Small neodymium magnets (5mm disc) | 2 | $2 |

**Electronics total: ~$118**
**PETG filament (estimated 2-3kg): ~$50-75**
**Grand total: ~$170-195**

---

## Print Strategy

### Per Page

Each page splits into left/right tiles at centerline (2 tiles per page, 6 total). Plus:
- Hinge knuckle inserts (printed with gear sectors)
- Latch housings (2x)
- Electronics bay box + lid
- Starlink pedestal platform + guide rail bushings
- Cam lift mechanisms (3x)
- LED diffuser strips (clear PETG)
- Carry handle
- Retaining C-clips

### Print Settings

- Material: PETG (shell, mechanisms) + clear/natural PETG (diffusers)
- Layer height: 0.2mm
- Infill: 20% gyroid
- Walls: 4 perimeters
- Supports: minimal (designed for printability, no overhangs > 45 degrees)

### Estimated Print Time

- 6 shell tiles: ~40-50 hours
- Mechanical parts (pedestal, cams, gears, latches, bay): ~15-20 hours
- Diffuser strips + small parts: ~5-8 hours
- **Total: ~60-80 hours across ~15-20 prints**

---

## File Structure

```
designs/
  shell/
    page1_shell.py           # Page 1 sculpted shell with LED channels and mounting bosses
    page2_shell.py           # Page 2 shell + electronics bay cutout
    page3_shell.py           # Page 3 shell with ridge lines and logo
    shell_common.py          # Shared helpers: build_sculpted_shell(), cut_pocket(), ridge_lines()
  hinge/
    hinge_knuckles.py        # Upgraded knuckles with gear sectors, hollow tube bore
    latch_mechanism.py       # Servo latch housing + hook/cam + catch
    hinge_servo_mount.py     # MG996R mount bracket + spur gear
  starlink/
    pedestal_base.py         # Base plate with actuator mount + guide rail bushings
    pedestal_platform.py     # Rising platform with tilt hinge
    tilt_linkage.py          # Tilt servo mount + linkage arm
  lifts/
    cam_lift.py              # Parametric cam lift mechanism (reused 3x)
    lift_plate.py            # Lift plate sized per device pocket
  electronics/
    electronics_bay.py       # Bay enclosure + lid
    button_mount.py          # Recessed button housing
    touch_pad_recess.py      # Shell cutout for copper tape touch pads
  led/
    diffuser_strip.py        # Snap-in translucent diffuser channel cover
  assembly/
    assembly_preview.py      # Full assembly view for cadquery-server (all subsystems positioned)
  common/
    constants.py             # All parametric dimensions, tolerances, device specs
    mounting.py              # Mounting boss, bolt hole, heat-set insert helpers
firmware/
  src/
    main.cpp                 # ESP32 Arduino/PlatformIO main
    servos.cpp               # PCA9685 servo control
    leds.cpp                 # WS2812B animations (FastLED)
    web_server.cpp           # ESP32 web UI
    power.cpp                # Battery monitoring, power mode switching
    touch.cpp                # Capacitive touch handling
  platformio.ini             # PlatformIO config for ESP32-S3
  data/                      # SPIFFS web UI files (HTML/CSS/JS)
export_v2.py                 # STL/STEP export for all printable parts
k8s/
  slice-v2.yaml              # K8s slicer job template
output/
  *.stl, *.step              # Generated files
docs/
  assembly-guide.md          # Step-by-step assembly with verification checks
  wiring-diagram.md          # Connector pinouts, harness routing
```

---

## Parametric Design Principles

All dimensions parametric in CadQuery:
- Device dimensions as named constants in `constants.py` with `TOL = 1.0mm` per side
- Shell fillet radii, ridge dimensions, taper angles as parameters
- Mounting boss positions calculated from device pocket locations
- Tile split at centerline, calculated from bed size
- Cam lift geometry parametric on device weight and desired lift height
- Starlink pedestal stroke, guide rail spacing, tilt range as parameters
- LED channel dimensions derived from WS2812B strip spec (5mm width)
