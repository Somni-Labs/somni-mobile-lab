"""
Mobile Lab Case V2 — Shared CadQuery Helpers

Mounting bosses, bolt holes, wire channels, LED channels,
sculpted shell builder, side ribs, and pocket cutter.
"""

import math
import cadquery as cq
from designs.common.constants import (
    WALL, CORNER_R, TAPER, DIVIDER,
    CHAMFER_SIZE, RIM_BAND, RIM_STEP,
    PANEL_GROOVE_DEPTH, PANEL_GROOVE_WIDTH, PANEL_BEVEL,
    M3_CLEARANCE_DIA, M3_INSERT_DIA, M3_INSERT_DEPTH,
    MOUNT_BOSS_OD, MOUNT_BOSS_ALIGN_H,
    WIRE_CHANNEL_W, WIRE_CHANNEL_D,
    LED_CHANNEL_W, LED_CHANNEL_D, LED_DIFFUSER_SNAP,
    RIDGE_H, RIDGE_W, RIDGE_CHAMFER,
    RIDGE_ACCENT_H, RIDGE_ACCENT_W,
    HERO_PLATE_W, HERO_PLATE_H, HERO_PLATE_PROUD, HERO_PLATE_RECESS,
    HEX_SIZE, HEX_WALL, HEX_PANEL_RECESS, HEX_POCKET_EXTRA,
    FRAME_GROOVE_W, FRAME_GROOVE_D,
    STRUCT_RIB_W, STRUCT_RIB_H, STRUCT_RIB_BACK_N, STRUCT_RIB_SIDE_N,
    BED_W, BED_D,
)


def build_sculpted_shell(width, depth, height, corner_r=CORNER_R, wall=WALL,
                         taper=TAPER, chamfer=CHAMFER_SIZE,
                         rim_band=RIM_BAND, rim_step=RIM_STEP):
    """
    Build an exosuit-styled page shell with a dramatically non-rectangular profile.

    Key visual features:
    - 45-degree chamfers on ALL horizontal edges (top and bottom)
    - Thick solid rim band at top (rim_band mm) so chamfer is prominently visible
    - Inward step below the rim creating a layered/armored look
    - Large organic fillets on vertical edges
    - Open-top interior for device pockets

    The rim_band creates a solid zone at the top of the shell where the chamfer
    has full material to bite into, making the angled profile clearly visible
    instead of being eaten by the thin wall.

    Returns a CadQuery solid (shell with floor, no top).
    """
    # Step 1: Build the outer form — full solid box
    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
    )

    # Step 2: Fillet vertical edges (organic corners)
    if corner_r > 0:
        try:
            outer = outer.edges("|Z").fillet(corner_r)
        except Exception:
            try:
                outer = outer.edges("|Z").fillet(corner_r / 2)
            except Exception:
                pass

    # Step 3: Chamfer horizontal edges — this is the signature "slab" profile
    if chamfer > 0:
        for selector in [">Z", "<Z"]:
            try:
                outer = outer.edges(selector).chamfer(chamfer)
            except Exception:
                try:
                    outer = outer.edges(selector).chamfer(chamfer * 0.6)
                except Exception:
                    pass

    # Step 4: Cut the main interior cavity
    # Cavity stops short of the top by rim_band, leaving a thick solid rim
    cavity_height = height - wall - rim_band
    if cavity_height > 0:
        inner_main = (
            cq.Workplane("XY")
            .workplane(offset=wall)
            .rect(width - wall * 2, depth - wall * 2)
            .extrude(cavity_height)
        )
        outer = outer.cut(inner_main)

    # Step 5: Cut a SECOND cavity in the rim zone — stepped inward
    # This creates the layered armored look: thick rim with chamfer visible,
    # then an inward step where the shell walls are thicker
    if rim_band > 0 and rim_step > 0:
        rim_cavity = (
            cq.Workplane("XY")
            .workplane(offset=height - rim_band)
            .rect(width - wall * 2 - rim_step * 2,
                  depth - wall * 2 - rim_step * 2)
            .extrude(rim_band + 1)
        )
        outer = outer.cut(rim_cavity)

    return outer


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
    z_lo = chamfer
    z_hi = height - chamfer
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


def _build_grid_panel(panel_w, panel_h, grid_size=HEX_SIZE, grid_wall=HEX_WALL,
                      pocket_depth=HEX_POCKET_EXTRA):
    """
    Build a rectangular grid of wall ridges filling a panel region.

    Creates a "waffle" pattern: horizontal + vertical wall strips with
    rectangular pockets between them. Reads as technical/sci-fi at scale.

    Built on the XZ plane, centered at origin, extruded in +Y.
    Returns a CadQuery Workplane ready to be translated into position.
    """
    wall_height = pocket_depth + 0.01
    pitch = grid_size + grid_wall

    n_cols = max(1, int(panel_w / pitch))
    n_rows = max(1, int(panel_h / pitch))

    # Build all horizontal strips as a single compound
    result = None
    for row in range(n_rows + 1):
        z = -panel_h / 2 + row * pitch
        if abs(z) > panel_h / 2 + grid_wall:
            continue
        strip = (
            cq.Workplane("XZ")
            .center(0, z)
            .rect(panel_w, grid_wall)
            .extrude(wall_height)
        )
        result = strip if result is None else result.union(strip)

    # Build all vertical strips
    for col in range(n_cols + 1):
        x = -panel_w / 2 + col * pitch
        if abs(x) > panel_w / 2 + grid_wall:
            continue
        strip = (
            cq.Workplane("XZ")
            .center(x, 0)
            .rect(grid_wall, panel_h)
            .extrude(wall_height)
        )
        result = strip if result is None else result.union(strip)

    return result


def build_hero_face(body, width, depth, height, wall=WALL, chamfer=CHAMFER_SIZE,
                    plate_w=HERO_PLATE_W, plate_h=HERO_PLATE_H,
                    plate_proud=HERO_PLATE_PROUD, plate_recess=HERO_PLATE_RECESS,
                    hex_panel_recess=HEX_PANEL_RECESS,
                    groove_w=FRAME_GROOVE_W, groove_d=FRAME_GROOVE_D):
    """
    Build the full hero face treatment on the front wall (+Y face).

    Three-layer depth treatment:
    1. Raised center logo plate with recessed background + raised logo shapes
    2. Two grid panels (above and below logo plate), recessed into wall
    3. Frame grooves separating the three zones

    Total depth variation: ~5mm (deepest pocket to top of logo shapes).
    """
    hd = depth / 2
    face_y = hd  # outer surface of front wall

    # Usable Z range on the front face (between chamfer zones).
    # The chamfer itself defines the safe boundary — no extra margin needed
    # because the logo plate protrudes OUTWARD from the flat wall surface.
    z_lo = chamfer
    z_hi = height - chamfer
    face_z_center = (z_lo + z_hi) / 2
    face_z_extent = z_hi - z_lo

    # Allocate 65% of available height to the logo plate (was 60%);
    # the remaining 35% is split between upper/lower grid panels.
    # On shorter pages, this means the logo plate dominates the face.
    # On taller pages, grid panels get enough space to render.
    effective_plate_h = min(plate_h, face_z_extent * 0.65)

    # NOTE: CadQuery's XZ workplane extrudes in the -Y direction.
    # To place geometry spanning [y_lo, y_hi], extrude (y_hi - y_lo)
    # and translate to (0, y_hi, 0) so it extends backward from y_hi.

    # --- 1. Raised logo plate ---
    # Spans face_y to face_y + plate_proud (protrudes outward from wall)
    logo_plate = (
        cq.Workplane("XZ")
        .center(0, face_z_center)
        .rect(plate_w, effective_plate_h)
        .extrude(plate_proud)
        .translate((0, face_y + plate_proud, 0))
    )
    body = body.union(logo_plate)

    # Recess the plate surface (except logo shapes)
    # Cut from the plate outer surface inward by plate_recess
    plate_recess_cut = (
        cq.Workplane("XZ")
        .center(0, face_z_center)
        .rect(plate_w - 4, effective_plate_h - 4)
        .extrude(plate_recess)
        .translate((0, face_y + plate_proud, 0))
    )
    body = body.cut(plate_recess_cut)

    # Logo shapes stay at full proud height — they fill the recessed zone
    # back up to the plate's outer surface. Use a small overlap (0.1mm into
    # the recessed surface) to ensure the union has overlapping volume and
    # doesn't fail due to coincident faces.
    logo_overlap = 0.1
    # Logo shapes span from (plate top - recess - overlap) to (plate top + 0.01)
    logo_extrude = plate_recess + logo_overlap + 0.01
    logo_translate_y = face_y + plate_proud + 0.01  # top of logo shape

    # Main nameplate rectangle — scaled to 60% of plate width for prominence
    nameplate_w = min(plate_w * 0.6, effective_plate_h * 4)
    nameplate = (
        cq.Workplane("XZ")
        .center(0, face_z_center)
        .rect(nameplate_w, min(16, effective_plate_h * 0.5))
        .extrude(logo_extrude)
        .translate((0, logo_translate_y, 0))
    )
    body = body.union(nameplate)

    # Accent bar below nameplate — thin horizontal stripe
    accent_z = max(face_z_center - effective_plate_h * 0.35,
                   face_z_center - effective_plate_h / 2 + 2)
    accent_bar = (
        cq.Workplane("XZ")
        .center(0, accent_z)
        .rect(min(plate_w * 0.8, plate_w - 4), 2.5)
        .extrude(logo_extrude)
        .translate((0, logo_translate_y, 0))
    )
    body = body.union(accent_bar)

    # Flanking chevrons (scaled to plate width)
    chevron_dx = min(plate_w * 0.4, plate_w / 2 - 5)
    for dx in [-chevron_dx, chevron_dx]:
        chevron = (
            cq.Workplane("XZ")
            .center(dx, face_z_center)
            .rect(6, min(20, effective_plate_h - 2))
            .extrude(logo_extrude)
            .translate((0, logo_translate_y, 0))
        )
        body = body.union(chevron)

    # --- 2. Grid panels (above and below logo plate) ---
    hex_panel_w = plate_w + 20  # slightly wider than logo plate

    # Upper panel: from just above the groove to the top chamfer line
    upper_z_lo = face_z_center + effective_plate_h / 2 + groove_w + 0.5
    upper_z_hi = z_hi
    upper_h = upper_z_hi - upper_z_lo
    upper_cz = (upper_z_lo + upper_z_hi) / 2

    # Lower panel: from bottom chamfer line to just below the groove
    lower_z_lo = z_lo
    lower_z_hi = face_z_center - effective_plate_h / 2 - groove_w - 0.5
    lower_h = lower_z_hi - lower_z_lo
    lower_cz = (lower_z_lo + lower_z_hi) / 2

    for panel_cz, panel_h in [(upper_cz, upper_h), (lower_cz, lower_h)]:
        if panel_h < 5:
            continue

        # Cut the recessed panel into the front wall
        # Cuts from face_y inward by hex_panel_recess
        panel_recess_box = (
            cq.Workplane("XZ")
            .center(0, panel_cz)
            .rect(hex_panel_w, panel_h)
            .extrude(hex_panel_recess)
            .translate((0, face_y, 0))
        )
        body = body.cut(panel_recess_box)

        # Build grid walls on the recessed surface
        # Grid is built at origin extruding in -Y; translate so the grid
        # top surface sits at face_y - hex_panel_recess (the recessed surface)
        grid = _build_grid_panel(hex_panel_w, panel_h)
        if grid is not None:
            grid = grid.translate((0, face_y - hex_panel_recess, panel_cz))
            body = body.union(grid)

    # --- 3. Frame grooves ---
    # Cut into the front wall surface
    for groove_z in [face_z_center + effective_plate_h / 2 + groove_w / 2,
                     face_z_center - effective_plate_h / 2 - groove_w / 2]:
        groove = (
            cq.Workplane("XZ")
            .center(0, groove_z)
            .rect(hex_panel_w + 10, groove_w)
            .extrude(groove_d)
            .translate((0, face_y, 0))
        )
        body = body.cut(groove)

    return body


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
    """
    boss = (
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(x, y)
        .circle(boss_od / 2)
        .extrude(height)
    )
    ring = (
        cq.Workplane("XY")
        .workplane(offset=z + height)
        .center(x, y)
        .circle(boss_od / 2 + 0.5)
        .circle(boss_od / 2 - 0.5)
        .extrude(align_h)
    )
    body = body.union(boss).union(ring)
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
    """
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
    """
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
    body = body.cut(channel)
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


def add_chamfer_led_channels(body, width, depth, height, wall=WALL,
                              chamfer=CHAMFER_SIZE,
                              channel_w=LED_CHANNEL_W, channel_d=LED_CHANNEL_D):
    """
    Cut LED channels into the 4 chamfer faces around the top perimeter of a page shell.

    Each channel runs along the midline of a chamfer face. The channel groove is
    centered on the chamfer face, which occupies the Z range from
    (height - chamfer) to (height - chamfer + wall). The cut box spans across
    the face in both the normal and Z directions.
    """
    hw = width / 2
    hd = depth / 2
    # The chamfer face runs from z=(height-chamfer) to z=(height-chamfer+wall).
    # Center Z of the face: height - chamfer + wall/2
    chamfer_z_lo = height - chamfer
    cz = chamfer_z_lo + wall / 2
    # Half-size of the cut perpendicular to the chamfer face (45-deg projection).
    cut_half = channel_d / math.sqrt(2)
    corner_clearance = chamfer + 5

    # Each side: (center_x, center_y, length, axis_along_face)
    # Outer face center in the normal direction: hw - wall/2 (for ±X faces),
    # hd - wall/2 (for ±Y faces). Inner edge: hw - wall / hd - wall.
    # We center the cut between outer and inner, then extend ±cut_half.
    cy_front_outer = hd - (cz - chamfer_z_lo)   # outer Y at cz for ±Y faces
    cy_front_inner = hd - wall                   # inner Y for ±Y faces
    cy_front = (cy_front_outer + cy_front_inner) / 2

    cx_side_outer = hw - (cz - chamfer_z_lo)     # outer X at cz for ±X faces
    cx_side_inner = hw - wall                     # inner X for ±X faces
    cx_side = (cx_side_outer + cx_side_inner) / 2

    length_x = width - corner_clearance * 2
    length_y = depth - corner_clearance * 2

    sides = [
        (0, -cy_front, length_x, "X"),
        (0, +cy_front, length_x, "X"),
        (+cx_side, 0, length_y, "Y"),
        (-cx_side, 0, length_y, "Y"),
    ]

    for cx, cy, length, axis in sides:
        if length <= 0:
            continue
        channel = (
            cq.Workplane("XY")
            .workplane(offset=cz - cut_half)
            .center(cx, cy)
        )
        if axis == "X":
            channel = channel.rect(length, cut_half * 2).extrude(cut_half * 2)
        else:
            channel = channel.rect(cut_half * 2, length).extrude(cut_half * 2)
        body = body.cut(channel)

    return body


def cut_armor_panels(body, width, depth, height, spine_xs, lateral_ys,
                     chamfer=CHAMFER_SIZE, groove_depth=PANEL_GROOVE_DEPTH,
                     groove_width=PANEL_GROOVE_WIDTH, ridge_w=RIDGE_W,
                     edge_inset=10):
    """
    Cut groove lines along ridge edges to create the visual separation between
    raised ridges and recessed armor panel zones on the shell's top face.

    The ridges (already added via add_ridge) are the high surface. This function
    cuts narrow grooves alongside each ridge line to create a clean visual
    transition — a shadow line that makes each ridge stand out from the
    surrounding panel surface.

    For a shell with 2mm ridges and 1.5mm groove depth, the visual effect is:
    ridge surface → groove → panel surface, reading as armored plate segments.

    The groove cuts extend slightly below the top face of the shell to ensure
    they're visible even where the shell rim is thin.
    """
    hd = depth / 2
    hw = width / 2

    # Cut groove lines alongside spine ridges (running along Y)
    for sx in spine_xs:
        for side in [-1, 1]:
            gx = sx + side * (ridge_w / 2 + groove_width / 2)
            groove = (
                cq.Workplane("XY")
                .workplane(offset=height - groove_depth)
                .center(gx, 0)
                .rect(groove_width, depth - chamfer * 2 - edge_inset * 2)
                .extrude(groove_depth + RIDGE_H + 0.1)
            )
            body = body.cut(groove)

    # Cut groove lines alongside lateral ridges (running along X)
    for ly in lateral_ys:
        for side in [-1, 1]:
            gy = ly + side * (ridge_w / 2 + groove_width / 2)
            groove = (
                cq.Workplane("XY")
                .workplane(offset=height - groove_depth)
                .center(0, gy)
                .rect(width - chamfer * 2 - edge_inset * 2, groove_width)
                .extrude(groove_depth + RIDGE_H + 0.1)
            )
            body = body.cut(groove)

    return body


def add_ridge(body, x1, y1, x2, y2, z, ridge_w=RIDGE_W, ridge_h=RIDGE_H,
              chamfer=RIDGE_CHAMFER):
    """
    Add a raised geometric ridge along a straight path on the shell surface.
    """
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
    try:
        ridge = ridge.edges(">Z").chamfer(chamfer)
    except Exception:
        pass
    body = body.union(ridge)
    return body


def split_into_tiles(body, case_outer_w, case_outer_d, page_height):
    """
    Split a page body into left and right halves at X=0.
    Returns (left_tile, right_tile).
    """
    margin = 10
    half_w = case_outer_w / 2 + margin
    h = page_height + margin * 2
    right_cutter = (
        cq.Workplane("XY")
        .workplane(offset=-margin)
        .center(half_w / 2, 0)
        .rect(half_w, case_outer_d + margin * 2)
        .extrude(h)
    )
    right_tile = body.intersect(right_cutter)
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
