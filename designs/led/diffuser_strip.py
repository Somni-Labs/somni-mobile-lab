"""
LED Diffuser Strip

Snap-in translucent cover for LED channels.
Printed in clear/natural PETG.
Parametric length — cut to match each channel run.
"""

import cadquery as cq
from designs.common.constants import (
    LED_CHANNEL_W, LED_CHANNEL_D, LED_DIFFUSER_SNAP,
)


def build_diffuser_strip(length, channel_w=LED_CHANNEL_W,
                         channel_d=LED_CHANNEL_D,
                         snap_lip=LED_DIFFUSER_SNAP):
    """
    Build a diffuser strip that snaps into an LED channel.

    The strip has a flat top face and snap-fit wings on the sides
    that engage with the channel lip.
    """
    strip_h = channel_d - 0.5
    strip_w = channel_w - 0.3

    strip = (
        cq.Workplane("XY")
        .rect(length, strip_w)
        .extrude(strip_h)
    )
    wing_h = snap_lip
    wing_w = 0.5
    for side in [-1, 1]:
        wing = (
            cq.Workplane("XY")
            .workplane(offset=strip_h - wing_h)
            .center(0, side * (strip_w / 2 + wing_w / 2))
            .rect(length, wing_w)
            .extrude(wing_h)
        )
        strip = strip.union(wing)
    return strip


# --- Standalone preview ---
try:
    from cq_server.ui import ui, show_object
    sample = build_diffuser_strip(100)
    show_object(sample, name="Diffuser Strip (100mm sample)",
                options={"color": (0.9, 0.9, 0.95, 0.5)})
except ImportError:
    pass
