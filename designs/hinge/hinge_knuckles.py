"""
Upgraded Piano Hinge Knuckles

10mm OD knuckles with hollow 3mm tube bore (2mm ID for wiring).
Interleaving segments along -X edge. One knuckle per page gets a
gear sector for the hinge servo to drive.
Asymmetric chamfer on knuckle ends for fool-proof assembly.

Returns a CadQuery solid — caller unions it onto the page shell.
"""

import cadquery as cq
import math
from designs.common.constants import (
    HINGE_KNUCKLE_OD, HINGE_KNUCKLE_LEN, HINGE_GAP,
    HINGE_TUBE_OD, HINGE_TUBE_ID,
    CASE_OUTER_W, CASE_OUTER_D,
)


def build_hinge_knuckles(page_height, case_depth=CASE_OUTER_D,
                         case_outer_w=CASE_OUTER_W, parity="even",
                         gear_sector_index=None):
    """
    Build interleaving hinge knuckles along the -X edge.

    Args:
        page_height: Z position of the hinge line (top or bottom of page)
        case_depth: depth of the case (Y extent)
        case_outer_w: width of the case (X extent)
        parity: "even" for knuckle indices 0,2,4... ; "odd" for 1,3,5...
        gear_sector_index: if set, this knuckle index gets a gear sector
                           (120-degree arc of teeth for the hinge servo)

    Returns a CadQuery solid (union of all knuckles).
    """
    knuckle_r = HINGE_KNUCKLE_OD / 2
    tube_r = HINGE_TUBE_OD / 2 + 0.15  # clearance for tube

    slot_pitch = HINGE_KNUCKLE_LEN + HINGE_GAP
    n_slots = int(case_depth // slot_pitch)
    total_len = n_slots * slot_pitch - HINGE_GAP
    y_start = -total_len / 2 + HINGE_KNUCKLE_LEN / 2

    hinge_x = -case_outer_w / 2
    hinge_z = page_height

    knuckles = None
    start_idx = 0 if parity == "even" else 1

    for i in range(start_idx, n_slots, 2):
        cy = y_start + i * slot_pitch

        # Knuckle cylinder
        knuckle = (
            cq.Workplane("XZ")
            .center(hinge_x, hinge_z)
            .circle(knuckle_r)
            .extrude(HINGE_KNUCKLE_LEN, both=False)
            .translate((0, cy - HINGE_KNUCKLE_LEN / 2, 0))
        )

        # Hollow tube bore
        bore = (
            cq.Workplane("XZ")
            .center(hinge_x, hinge_z)
            .circle(tube_r)
            .extrude(HINGE_KNUCKLE_LEN + 2, both=False)
            .translate((0, cy - HINGE_KNUCKLE_LEN / 2 - 1, 0))
        )
        knuckle = knuckle.cut(bore)

        # Asymmetric chamfer on one end (for assembly orientation)
        chamfer_end = (
            cq.Workplane("XZ")
            .center(hinge_x, hinge_z)
            .circle(knuckle_r)
            .circle(knuckle_r - 1)
            .extrude(1)
            .translate((0, cy - HINGE_KNUCKLE_LEN / 2, 0))
        )
        # Cut a small notch on one side only
        notch = (
            cq.Workplane("XZ")
            .center(hinge_x + knuckle_r - 0.5, hinge_z)
            .rect(1, 1)
            .extrude(1)
            .translate((0, cy - HINGE_KNUCKLE_LEN / 2, 0))
        )
        knuckle = knuckle.cut(notch)

        # Gear sector (if this is the designated knuckle)
        if gear_sector_index is not None and i == gear_sector_index:
            gear_r = knuckle_r + 3  # gear extends beyond knuckle
            n_teeth = 8  # teeth over ~120 degrees
            tooth_angle = 120 / n_teeth
            for t in range(n_teeth):
                angle_rad = math.radians(-60 + t * tooth_angle + tooth_angle / 2)
                tx = hinge_x + gear_r * math.cos(angle_rad)
                tz = hinge_z + gear_r * math.sin(angle_rad)
                tooth = (
                    cq.Workplane("XZ")
                    .center(tx, tz)
                    .rect(2, 2)
                    .extrude(HINGE_KNUCKLE_LEN - 2)
                    .translate((0, cy - HINGE_KNUCKLE_LEN / 2 + 1, 0))
                )
                knuckle = knuckle.union(tooth)

        if knuckles is None:
            knuckles = knuckle
        else:
            knuckles = knuckles.union(knuckle)

    return knuckles


def build_retaining_clip():
    """
    Build a printed C-clip that snaps over the hinge tube end.
    Small part — printed separately.
    """
    clip = (
        cq.Workplane("XY")
        .circle(HINGE_TUBE_OD / 2 + 1.5)
        .circle(HINGE_TUBE_OD / 2 + 0.2)
        .extrude(3)
    )
    # Cut opening slot for snap-on
    slot = (
        cq.Workplane("XY")
        .center(HINGE_TUBE_OD / 2 + 1, 0)
        .rect(3, HINGE_TUBE_OD / 2)
        .extrude(3)
    )
    clip = clip.cut(slot)
    return clip


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    knuckles = build_hinge_knuckles(50, gear_sector_index=2)
    show_object(knuckles, name="Hinge Knuckles (sample)",
                options={"color": (0.5, 0.5, 0.5, 0.9)})
    clip = build_retaining_clip()
    show_object(clip.translate((0, 0, 60)), name="Retaining C-Clip",
                options={"color": (0.7, 0.7, 0.7, 0.9)})
except ImportError:
    pass
