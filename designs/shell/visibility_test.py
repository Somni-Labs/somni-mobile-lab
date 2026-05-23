"""
Visibility Test — Can you see geometry changes?

This module shows a plain shell next to a shell with a HUGE obvious
block stuck on the front face. If you can see the difference between
the two, the viewer is working. If they look identical, something is
fundamentally broken with how cq-server renders changes.

Loadable by cadquery-server via show_object().
"""

import os
import sys
import cadquery as cq

_this_dir = os.path.dirname(os.path.realpath(__file__))
_repo_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from designs.common.constants import CASE_OUTER_W, CASE_OUTER_D, PAGE1_H
from designs.common.mounting import build_sculpted_shell

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False


if _cq_server:
    # Object 1: Plain shell — no modifications
    plain = build_sculpted_shell(CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)
    show_object(plain, name="1 - PLAIN SHELL (no changes)",
                options={"color": (0.5, 0.5, 0.5, 0.8)})

    # Object 2: Shell with a HUGE block on front face + big text-like shapes
    modified = build_sculpted_shell(CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)

    # Giant 200x40x20mm block protruding from front wall
    hw = CASE_OUTER_W / 2
    hd = CASE_OUTER_D / 2
    big_block = (
        cq.Workplane("XZ")
        .center(0, PAGE1_H / 2)
        .rect(200, 40)
        .extrude(20)
        .translate((0, hd + 20, 0))
    )
    modified = modified.union(big_block)

    # Five big vertical fins on the back wall — impossible to miss
    for i in range(5):
        x = -100 + i * 50
        fin = (
            cq.Workplane("XY")
            .workplane(offset=15)
            .center(x, -hd - 15)
            .rect(8, 30)
            .extrude(PAGE1_H - 30)
        )
        modified = modified.union(fin)

    # Big cylinder on top — to prove geometry additions work
    cylinder = (
        cq.Workplane("XY")
        .workplane(offset=PAGE1_H)
        .center(0, 0)
        .circle(40)
        .extrude(30)
    )
    modified = modified.union(cylinder)

    # Show it offset to the right so both are visible
    modified_view = modified.translate((CASE_OUTER_W + 50, 0, 0))
    show_object(modified_view, name="2 - MODIFIED (block+fins+cylinder)",
                options={"color": (1.0, 0.3, 0.3, 1.0)})
