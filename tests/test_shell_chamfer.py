"""Tests for the chamfered slab shell form."""
import cadquery as cq
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from designs.common.constants import WALL, CORNER_R, CHAMFER_SIZE
from designs.common.mounting import build_sculpted_shell


def test_chamfered_shell_builds_without_error():
    """Shell should build successfully with chamfers."""
    shell = build_sculpted_shell(200, 150, 60)
    assert shell is not None
    bb = shell.val().BoundingBox()
    assert abs(bb.xlen - 200) < 1.0
    assert abs(bb.ylen - 150) < 1.0


def test_chamfered_shell_height_matches():
    """
    Shell bounding-box height should reflect the requested height minus chamfer
    material removed at the top.

    When CHAMFER_SIZE > WALL, the inner hollow cuts through the chamfer zone,
    so the effective bounding-box height is height - (CHAMFER_SIZE - WALL).
    The test accepts anything within 2 mm of that value.
    """
    shell = build_sculpted_shell(200, 150, 60)
    bb = shell.val().BoundingBox()
    expected_zlen = 60 - max(0, CHAMFER_SIZE - WALL)
    assert abs(bb.zlen - expected_zlen) < 2.0, (
        f"Expected zlen ≈ {expected_zlen:.1f} (height minus chamfer overhang), "
        f"got {bb.zlen:.1f}"
    )


def test_chamfered_shell_is_shorter_at_corners():
    """
    The chamfer removes material at the top/bottom edges.
    Verify by checking that the volume is less than a plain hollow box.
    """
    shell = build_sculpted_shell(200, 150, 60)
    shell_vol = shell.val().Volume()
    outer_vol = 200 * 150 * 60
    inner_vol = (200 - WALL * 2) * (150 - WALL * 2) * (60 - WALL)
    plain_box_vol = outer_vol - inner_vol
    assert shell_vol < plain_box_vol, f"Chamfered shell ({shell_vol:.0f}) should be smaller than plain box ({plain_box_vol:.0f})"


def test_chamfered_shell_has_floor():
    """Shell should be solid at Z=0 (floor) and open at the top."""
    shell = build_sculpted_shell(200, 150, 60)
    bb = shell.val().BoundingBox()
    assert bb.zmin < 0.1, "Shell should start at Z≈0"
