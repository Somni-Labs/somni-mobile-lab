"""
Hero Face Demo — Isolated front wall preview for visual review.

Shows just a single page shell with the hero face treatment,
no other subsystems. Makes the "SOMNI LABS" through-cuts and
vent slots clearly visible without the complexity of the full assembly.

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
from designs.common.mounting import build_sculpted_shell, build_hero_face, add_structural_ribs

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False


def build_hero_demo():
    """Build a single shell with hero face — no pockets, no subsystems."""
    shell = build_sculpted_shell(CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)
    shell = build_hero_face(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)
    shell = add_structural_ribs(shell, CASE_OUTER_W, CASE_OUTER_D, PAGE1_H)
    return shell


if _cq_server:
    demo = build_hero_demo()
    show_object(demo, name="Hero Face Demo (Page 1 shell)",
                options={"color": (0.27, 0.51, 0.71, 1.0)})  # fully opaque
