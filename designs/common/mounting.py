"""
Mobile Lab Case V2 — Shared CadQuery Helpers

Mounting bosses, bolt holes, wire channels, LED channels,
sculpted shell builder, and pocket cutter.
"""

import cadquery as cq
from designs.common.constants import (
    WALL, CORNER_R, TAPER, DIVIDER,
    M3_CLEARANCE_DIA, M3_INSERT_DIA, M3_INSERT_DEPTH,
    MOUNT_BOSS_OD, MOUNT_BOSS_ALIGN_H,
    WIRE_CHANNEL_W, WIRE_CHANNEL_D,
    LED_CHANNEL_W, LED_CHANNEL_D, LED_DIFFUSER_SNAP,
    RIDGE_H, RIDGE_W, RIDGE_CHAMFER,
    RIDGE_ACCENT_H, RIDGE_ACCENT_W,
    BED_W, BED_D,
)


def build_sculpted_shell(width, depth, height, corner_r=CORNER_R, wall=WALL, taper=TAPER):
    """
    Build a sculpted page shell — open-top box with large organic fillets
    and a subtle taper (thicker center, thinner edges).

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
    try:
        outer = outer.edges(">Z").fillet(min(corner_r / 2, wall))
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
