"""
Mobile Lab Case V2 — Shared CadQuery Helpers

Mounting bosses, bolt holes, wire channels, LED channels,
sculpted shell builder, side ribs, and pocket cutter.
"""

import math
import os
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
    # Auto-cap chamfer to 20% of page height so shorter pages aren't eaten alive.
    # Also cap rim_band proportionally.
    max_chamfer = height * 0.20
    chamfer = min(chamfer, max_chamfer)
    max_rim = height * 0.15
    rim_band = min(rim_band, max_rim)

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
    chamfer = min(chamfer, height * 0.20)  # match shell auto-cap
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


def _build_letter_solid(letter, letter_w, letter_h, stroke):
    """
    Build a single block letter as a 2D CadQuery Wire on the XZ plane.

    Each letter is constructed from rectangular blocks (union of rects).
    Returns a CadQuery Workplane solid extruded 1mm in Y, centered at origin.
    The caller scales/positions it.
    """
    parts = []

    def _rect(cx, cz, w, h):
        """Create a rectangle solid centered at (cx, cz) on XZ plane."""
        return (
            cq.Workplane("XZ")
            .center(cx, cz)
            .rect(w, h)
            .extrude(1)
        )

    hw = letter_w / 2
    hh = letter_h / 2
    s = stroke

    if letter == 'S':
        # Top bar
        parts.append(_rect(0, hh - s/2, letter_w, s))
        # Middle bar
        parts.append(_rect(0, 0, letter_w, s))
        # Bottom bar
        parts.append(_rect(0, -hh + s/2, letter_w, s))
        # Left top leg
        parts.append(_rect(-hw + s/2, hh/2, s, hh))
        # Right bottom leg
        parts.append(_rect(hw - s/2, -hh/2, s, hh))

    elif letter == 'O':
        # Four sides of the O
        parts.append(_rect(0, hh - s/2, letter_w, s))       # top
        parts.append(_rect(0, -hh + s/2, letter_w, s))      # bottom
        parts.append(_rect(-hw + s/2, 0, s, letter_h))      # left
        parts.append(_rect(hw - s/2, 0, s, letter_h))       # right

    elif letter == 'M':
        # M: two outer legs, two inner legs spread wide, top bar connecting all
        # Key: big gaps between the legs at the bottom
        parts.append(_rect(-hw + s/2, 0, s, letter_h))      # left outer leg
        parts.append(_rect(hw - s/2, 0, s, letter_h))       # right outer leg
        parts.append(_rect(-hw * 0.35, hh * 0.3, s, hh * 1.1))  # left inner (starts high, shorter)
        parts.append(_rect(hw * 0.35, hh * 0.3, s, hh * 1.1))   # right inner (starts high, shorter)
        parts.append(_rect(0, hh - s/2, letter_w, s))       # top bar

    elif letter == 'N':
        # N: two legs with a thin diagonal bar — keep open space visible
        parts.append(_rect(-hw + s/2, 0, s, letter_h))      # left leg
        parts.append(_rect(hw - s/2, 0, s, letter_h))       # right leg
        # Diagonal simplified as a narrow angled bar from top-left to bottom-right
        parts.append(_rect(-hw * 0.2, hh * 0.3, s, hh * 0.5))   # upper-left piece
        parts.append(_rect(hw * 0.2, -hh * 0.3, s, hh * 0.5))   # lower-right piece

    elif letter == 'I':
        parts.append(_rect(0, 0, s, letter_h))              # vertical bar
        parts.append(_rect(0, hh - s/2, letter_w * 0.6, s)) # top serif
        parts.append(_rect(0, -hh + s/2, letter_w * 0.6, s))# bottom serif

    elif letter == 'L':
        parts.append(_rect(-hw + s/2, 0, s, letter_h))      # vertical bar
        parts.append(_rect(0, -hh + s/2, letter_w, s))      # bottom bar

    elif letter == 'A':
        # A: two legs, top bar, crossbar at ⅓ height — big counter gap above
        parts.append(_rect(-hw + s/2, 0, s, letter_h))      # left leg
        parts.append(_rect(hw - s/2, 0, s, letter_h))       # right leg
        parts.append(_rect(0, hh - s/2, letter_w, s))       # top bar
        parts.append(_rect(0, -hh/3, letter_w - s * 2, s))  # crossbar at ⅓ height

    elif letter == 'B':
        parts.append(_rect(-hw + s/2, 0, s, letter_h))      # left vertical
        parts.append(_rect(0, hh - s/2, letter_w, s))       # top bar
        parts.append(_rect(0, 0, letter_w, s))              # middle bar
        parts.append(_rect(0, -hh + s/2, letter_w, s))      # bottom bar
        parts.append(_rect(hw - s/2, hh/4, s, hh))          # right top (full height to connect bars)
        parts.append(_rect(hw - s/2, -hh/4, s, hh))         # right bottom (full height to connect bars)

    # Union all parts
    result = parts[0]
    for p in parts[1:]:
        result = result.union(p)
    return result


def _font_path():
    """Resolve the bundled DejaVu Sans Bold font path."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "fonts", "DejaVuSans-Bold.ttf")


def build_hero_face(body, width, depth, height, wall=WALL, chamfer=CHAMFER_SIZE,
                    plate_w=HERO_PLATE_W, plate_h=HERO_PLATE_H,
                    plate_proud=HERO_PLATE_PROUD, plate_recess=HERO_PLATE_RECESS,
                    hex_panel_recess=HEX_PANEL_RECESS,
                    groove_w=FRAME_GROOVE_W, groove_d=FRAME_GROOVE_D):
    """
    Build the hero face on the front wall (+Y face).

    Features:
    1. "SOMNI LABS" cut all the way THROUGH the front wall as letter-shaped
       holes using a real font (DejaVu Sans Bold) — proper M/N diagonals,
       visible from any angle, backlit by LED channel behind
    2. LED channel on the inside of the front wall behind the text cutout
       to illuminate the letters from behind
    3. Structural ribs are handled separately by add_structural_ribs()
    """
    hd = depth / 2
    face_y = hd  # outer surface of front wall
    chamfer = min(chamfer, height * 0.20)  # match shell auto-cap

    z_lo = chamfer
    z_hi = height - chamfer
    face_z_center = (z_lo + z_hi) / 2
    face_z_extent = z_hi - z_lo

    # --- 1. Raised plate on front wall (breaks silhouette) ---
    effective_plate_h = min(plate_h, face_z_extent * 0.65)
    logo_plate = (
        cq.Workplane("XZ")
        .center(0, face_z_center)
        .rect(plate_w, effective_plate_h)
        .extrude(plate_proud)
        .translate((0, face_y + plate_proud, 0))
    )
    body = body.union(logo_plate)

    # --- 2. Text sizing ---
    # Letters should be BIG — at least 15mm tall to be visible on a 412mm case.
    font_size = min(face_z_extent * 0.45, 30)
    font_size = max(font_size, 15)  # minimum 15mm

    # --- 3. Build text cutter using real font ---
    # CadQuery text() on XZ plane extrudes in -Y direction.
    # We mirror X (halve=True not available, so we negate X after) so the text
    # reads correctly from the +Y outside looking in.
    cut_through_depth = wall + plate_proud + 2  # through plate + wall

    font_file = _font_path()
    text_kwargs = {}
    if os.path.isfile(font_file):
        text_kwargs["fontPath"] = font_file
        text_kwargs["font"] = "DejaVu Sans"

    try:
        # Build text solid on XZ plane centered at origin
        text_solid = (
            cq.Workplane("XZ")
            .center(0, face_z_center)
            .text("SOMNI LABS", font_size, cut_through_depth,
                  kind="bold", **text_kwargs)
        )
        # Mirror X so text reads correctly from outside (+Y)
        text_solid = text_solid.mirror("YZ")
        # Position: start just outside the plate and cut inward
        text_solid = text_solid.translate((0, face_y + plate_proud + 0.01, 0))
        body = body.cut(text_solid)

        # Estimate total text width for LED channel sizing
        text_bb = text_solid.val().BoundingBox()
        total_text_w = text_bb.xlen
    except Exception:
        # Fallback: use block letter rectangles if text() fails
        body, total_text_w = _cut_block_letters_on_body(
            body, face_z_center, face_z_extent, face_y,
            plate_proud, plate_w, wall,
        )

    # --- 4. LED channel behind the text (inside of front wall) ---
    # Shallow channel for LED strip to backlight the letter cutouts
    led_channel_w = total_text_w + 20
    led_channel_h = font_size + 10
    led_depth = LED_CHANNEL_D
    led_channel = (
        cq.Workplane("XZ")
        .center(0, face_z_center)
        .rect(led_channel_w, led_channel_h)
        .extrude(led_depth)
        .translate((0, face_y - wall + 0.01, 0))
    )
    body = body.cut(led_channel)

    return body


def _cut_block_letters_on_body(body, face_z_center, face_z_extent, face_y,
                                plate_proud, plate_w, wall):
    """Fallback: cut SOMNI LABS as block-letter rectangles through the wall."""
    letter_h = min(face_z_extent * 0.45, 30)
    letter_h = max(letter_h, 15)
    letter_w = letter_h * 0.65
    stroke = max(letter_h * 0.25, 3.0)
    gap = letter_h * 0.3
    space_w = letter_h * 0.5

    total_text_w = 9 * letter_w + 8 * gap + space_w
    max_text_w = plate_w * 0.9
    if total_text_w > max_text_w:
        scale = max_text_w / total_text_w
        letter_h *= scale
        letter_w *= scale
        stroke *= scale
        gap *= scale
        space_w *= scale
        total_text_w = max_text_w

    cut_through_depth = wall + plate_proud + 2
    text = "SOMNILABS"
    x_cursor = -total_text_w / 2

    for i, ch in enumerate(text):
        if i == 5:
            x_cursor += space_w
        rects = _get_letter_rects(ch, letter_w, letter_h, stroke)
        for (rcx, rcz, rw, rh) in rects:
            abs_cx = -(x_cursor + letter_w / 2 + rcx)
            abs_cz = face_z_center + rcz
            cutter = (
                cq.Workplane("XZ")
                .center(abs_cx, abs_cz)
                .rect(rw, rh)
                .extrude(cut_through_depth)
                .translate((0, face_y + plate_proud + 0.01, 0))
            )
            body = body.cut(cutter)
        x_cursor += letter_w + gap

    return body, total_text_w


def _get_letter_rects(letter, letter_w, letter_h, stroke):
    """
    Return list of (cx, cz, w, h) rectangles that make up a letter.

    Coordinates are relative to the letter center (0, 0).
    These are the SOLID parts of the letter — we cut these through the wall.
    """
    hw = letter_w / 2
    hh = letter_h / 2
    s = stroke
    rects = []

    if letter == 'S':
        rects.append((0, hh - s/2, letter_w, s))           # top bar
        rects.append((0, 0, letter_w, s))                   # middle bar
        rects.append((0, -hh + s/2, letter_w, s))           # bottom bar
        rects.append((-hw + s/2, hh/4, s, hh - s))         # left upper
        rects.append((hw - s/2, -hh/4, s, hh - s))         # right lower

    elif letter == 'O':
        rects.append((0, hh - s/2, letter_w, s))           # top
        rects.append((0, -hh + s/2, letter_w, s))          # bottom
        rects.append((-hw + s/2, 0, s, letter_h))          # left
        rects.append((hw - s/2, 0, s, letter_h))           # right

    elif letter == 'M':
        # M: two outer legs, two inner legs spread wide, top bar
        # Inner legs start higher and are shorter — big gaps at bottom
        rects.append((-hw + s/2, 0, s, letter_h))                   # left outer leg
        rects.append((hw - s/2, 0, s, letter_h))                    # right outer leg
        rects.append((-hw * 0.35, hh * 0.3, s, hh * 1.1))          # left inner (high)
        rects.append((hw * 0.35, hh * 0.3, s, hh * 1.1))           # right inner (high)
        rects.append((0, hh - s/2, letter_w, s))                    # top bar

    elif letter == 'N':
        # N: two legs with diagonal suggested by two offset bars
        # Open space visible between them
        rects.append((-hw + s/2, 0, s, letter_h))                   # left leg
        rects.append((hw - s/2, 0, s, letter_h))                    # right leg
        rects.append((-hw * 0.2, hh * 0.3, s, hh * 0.5))           # upper-left piece
        rects.append((hw * 0.2, -hh * 0.3, s, hh * 0.5))           # lower-right piece

    elif letter == 'I':
        rects.append((0, 0, s, letter_h))                  # vertical bar
        rects.append((0, hh - s/2, letter_w * 0.6, s))     # top serif
        rects.append((0, -hh + s/2, letter_w * 0.6, s))    # bottom serif

    elif letter == 'L':
        rects.append((-hw + s/2, 0, s, letter_h))          # vertical bar
        rects.append((0, -hh + s/2, letter_w, s))          # bottom bar

    elif letter == 'A':
        # A: two legs, top bar, crossbar low (⅓ up) so counter gap is prominent
        rects.append((-hw + s/2, 0, s, letter_h))                   # left leg
        rects.append((hw - s/2, 0, s, letter_h))                    # right leg
        rects.append((0, hh - s/2, letter_w, s))                    # top bar
        rects.append((0, -hh/3, letter_w - s * 2, s))               # crossbar at ⅓ height

    elif letter == 'B':
        rects.append((-hw + s/2, 0, s, letter_h))          # left vertical
        rects.append((0, hh - s/2, letter_w, s))           # top bar
        rects.append((0, 0, letter_w, s))                   # middle bar
        rects.append((0, -hh + s/2, letter_w, s))          # bottom bar
        rects.append((hw - s/2, hh/4, s, hh))              # right top (connects bars)
        rects.append((hw - s/2, -hh/4, s, hh))             # right bottom (connects bars)

    return rects


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
