"""
Mobile Lab Case V2 — Shared CadQuery Helpers

Mounting bosses, bolt holes, wire channels, LED channels,
sculpted shell builder, and pocket cutter.
"""

import cadquery as cq
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


def build_sculpted_shell(width, depth, height, corner_r=CORNER_R, wall=WALL,
                         taper=TAPER, chamfer=CHAMFER_SIZE):
    """
    Build a chamfered slab page shell — open-top box with large organic fillets
    on vertical edges and 45-degree chamfers on all horizontal edges.

    The chamfer transforms the rectangular profile into a beveled slab.
    Interior is flat-walled (chamfer is exterior only).

    Returns a CadQuery solid (shell with floor, no top).
    """
    outer = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(height)
    )
    if corner_r > 0:
        try:
            outer = outer.edges("|Z").fillet(corner_r)
        except Exception:
            outer = outer.edges("|Z").fillet(corner_r / 2)

    if chamfer > 0:
        try:
            outer = outer.edges(">Z").chamfer(chamfer)
        except Exception:
            try:
                outer = outer.edges(">Z").chamfer(chamfer * 0.6)
            except Exception:
                pass
        try:
            outer = outer.edges("<Z").chamfer(chamfer)
        except Exception:
            try:
                outer = outer.edges("<Z").chamfer(chamfer * 0.6)
            except Exception:
                pass

    inner = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .rect(width - wall * 2, depth - wall * 2)
        .extrude(height)
    )
    shell = outer.cut(inner)
    return shell


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
    import math
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
    import math
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
    import math
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
    import math
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
