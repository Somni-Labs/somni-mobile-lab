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
CHAMFER_SIZE = 18      # 45-degree edge chamfer (dramatic bevel on 412mm case)
RIM_BAND = 12          # solid rim band at top — thick enough for chamfer to read
RIM_STEP = 5           # inward step below rim (layered armor look)
SIDE_TAPER_ANGLE = 3   # degrees of inward taper on side walls (0=vertical)
PANEL_GROOVE_DEPTH = 1.5  # armor panel recess below ridge surface
PANEL_GROOVE_WIDTH = 3    # groove cut width between panels (wider for visibility)
PANEL_BEVEL = 1           # bevel transition at groove edges

# =============================================================================
# EXOSUIT RIDGES
# =============================================================================
RIDGE_H = 4            # ridge height above shell surface (bold, was 2)
RIDGE_W = 6            # ridge width (was 4)
RIDGE_CHAMFER = 1.0    # 45-degree chamfer on ridge edges
RIDGE_ACCENT_H = 2.5   # side accent ridge height
RIDGE_ACCENT_W = 4     # side accent ridge width
# Hero face (front wall armor plate treatment)
HERO_PLATE_W = 280     # raised logo plate width — 68% of 412mm case face
HERO_PLATE_H = 50      # raised logo plate height (Z extent on front wall)
HERO_PLATE_PROUD = 8   # how far logo plate protrudes (was 3 — invisible at scale)
HERO_PLATE_RECESS = 3  # recess depth into the plate for logo background
HEX_SIZE = 12          # hex pocket size across flats (mm)
HEX_WALL = 2.5         # wall thickness between hex pockets
HEX_PANEL_RECESS = 3   # how deep hex panel is recessed into wall (was 1.5)
HEX_POCKET_EXTRA = 1.5 # additional depth of hex pockets below panel surface
FRAME_GROOVE_W = 3     # groove width between armor zones (was 2)
FRAME_GROOVE_D = 2     # groove depth (was 1)

# Structural ribs (back + short sides only)
STRUCT_RIB_W = 8       # structural rib width (bold greeble)
STRUCT_RIB_H = 10      # how far structural ribs protrude from wall (was 5)
STRUCT_RIB_BACK_N = 5  # number of ribs on back wall (was 3)
STRUCT_RIB_SIDE_N = 3  # number of ribs per short side (was 2)
RIDGE_DIAMOND = 5      # chamfered diamond size at ridge intersections

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
