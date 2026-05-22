"""
LED Diffuser Strip

Snap-in translucent cover for LED channels.
Printed in clear/natural PETG.
Parametric length — cut to match each channel run.
"""

import os
import sys
import cadquery as cq

# Bootstrap sys.path for cadquery-server symlink loading
_this_dir = os.path.dirname(os.path.realpath(__file__))
_repo_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from designs.common.constants import (
    LED_CHANNEL_W, LED_CHANNEL_D, LED_DIFFUSER_SNAP,
)

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False


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


# --- Standalone preview for cadquery-server ---
if _cq_server and not os.environ.get('_CQ_ASSEMBLY'):
    sample = build_diffuser_strip(100)
    show_object(sample, name="Diffuser Strip (100mm sample)",
                options={"color": (0.9, 0.9, 0.95, 0.5)})
