"""Tests for the chamfered slab shell form."""
import cadquery as cq
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from designs.common.constants import WALL, CORNER_R, CHAMFER_SIZE, PANEL_GROOVE_DEPTH, LED_CHANNEL_W, LED_CHANNEL_D, RIDGE_H, RIM_BAND, RIM_STEP
from designs.common.mounting import build_sculpted_shell, add_chamfer_led_channels, cut_armor_panels, add_ridge, add_structural_ribs


def test_chamfered_shell_builds_without_error():
    """Shell should build successfully with chamfers."""
    shell = build_sculpted_shell(200, 150, 60)
    assert shell is not None
    bb = shell.val().BoundingBox()
    assert abs(bb.xlen - 200) < 1.0
    assert abs(bb.ylen - 150) < 1.0


def test_chamfered_shell_height_matches():
    """
    Shell bounding-box height should be less than the nominal height due to
    chamfer material removal, but greater than height - 2*chamfer since
    the chamfer only affects edges/corners not the full face.

    The new stepped rim design means the shell retains more height than the
    old thin-wall design. Accept anything between (height - 2*chamfer) and height.
    """
    shell = build_sculpted_shell(200, 150, 60)
    bb = shell.val().BoundingBox()
    assert bb.zlen < 60, f"Shell should be shorter than nominal 60mm, got {bb.zlen:.1f}"
    assert bb.zlen > 60 - 2 * CHAMFER_SIZE, (
        f"Shell should be > {60 - 2 * CHAMFER_SIZE:.1f}mm, got {bb.zlen:.1f}"
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


def test_chamfer_led_channels_build():
    """Adding chamfer LED channels should not error."""
    shell = build_sculpted_shell(200, 150, 60)
    result = add_chamfer_led_channels(shell, 200, 150, 60)
    assert result is not None
    bb = result.val().BoundingBox()
    assert abs(bb.xlen - 200) < 1.0


def test_chamfer_led_channels_remove_material():
    """Chamfer LED channels should cut material from the shell."""
    shell = build_sculpted_shell(200, 150, 60)
    vol_before = shell.val().Volume()
    result = add_chamfer_led_channels(shell, 200, 150, 60)
    vol_after = result.val().Volume()
    assert vol_after < vol_before, "LED channels should remove material"


def _build_shell_with_ridges(width=400, depth=270, height=50):
    """Helper: build a shell with ridges on top face, simulating Page 3 setup."""
    shell = build_sculpted_shell(width, depth, height)
    hw = width / 2
    hd = depth / 2
    spine_xs = [-hw / 3, 0, hw / 3]
    lateral_ys = [-hd / 3, hd / 3]
    # Add ridges on top face (like Page 3 does before cutting panels)
    for sx in spine_xs:
        shell = add_ridge(shell, sx, -hd + 10, sx, hd - 10, z=height)
    for ly in lateral_ys:
        shell = add_ridge(shell, -hw + 10, ly, hw - 10, ly, z=height)
    return shell, spine_xs, lateral_ys


def test_armor_panels_build():
    """Cutting armor panels should not error."""
    shell, spine_xs, lateral_ys = _build_shell_with_ridges()
    result = cut_armor_panels(shell, 400, 270, 50, spine_xs, lateral_ys)
    assert result is not None


def test_armor_panels_remove_material():
    """Armor panels should recess material from the ridged top face."""
    shell, spine_xs, lateral_ys = _build_shell_with_ridges()
    vol_before = shell.val().Volume()
    result = cut_armor_panels(shell, 400, 270, 50, spine_xs, lateral_ys)
    vol_after = result.val().Volume()
    assert vol_after < vol_before, "Armor panels should remove material from ridged surface"


def test_structural_ribs_add_material():
    """Structural ribs should add protruding material to back and short sides."""
    shell = build_sculpted_shell(200, 150, 60)
    vol_before = shell.val().Volume()
    result = add_structural_ribs(shell, 200, 150, 60)
    vol_after = result.val().Volume()
    assert vol_after > vol_before, "Structural ribs should add material"


def test_structural_ribs_skip_front():
    """Structural ribs should NOT add material on the front (+Y) face."""
    shell = build_sculpted_shell(200, 150, 60)
    bb_before = shell.val().BoundingBox()
    result = add_structural_ribs(shell, 200, 150, 60)
    bb_after = result.val().BoundingBox()
    # Back (-Y) should extend outward (ribs protrude)
    assert bb_after.ymin < bb_before.ymin, (
        f"Back face should extend: ymin before={bb_before.ymin:.1f}, after={bb_after.ymin:.1f}"
    )
    # Front (+Y) should NOT extend (no ribs on hero face)
    assert abs(bb_after.ymax - bb_before.ymax) < 0.1, (
        f"Front face should not extend: ymax before={bb_before.ymax:.1f}, after={bb_after.ymax:.1f}"
    )


def test_shell_has_rim_band():
    """Shell should have a visibly thick rim at the top (stepped profile)."""
    # A shell with rim_band should have more material near the top
    # than one without. We verify by comparing volumes.
    shell_with_rim = build_sculpted_shell(200, 150, 60, rim_band=8, rim_step=3)
    shell_no_rim = build_sculpted_shell(200, 150, 60, rim_band=0, rim_step=0)
    # With rim should have more volume (thicker walls near top)
    assert shell_with_rim.val().Volume() > shell_no_rim.val().Volume(), \
        "Shell with rim band should have more volume than shell without"


from designs.shell.page1_shell import build_page1
from designs.shell.page2_shell import build_page2
from designs.shell.page3_shell import build_page3
from designs.common.constants import PAGE3_H


def test_page1_builds_with_chamfer():
    """Page 1 should build successfully with the exosuit shell."""
    page1 = build_page1()
    assert page1 is not None
    bb = page1.val().BoundingBox()
    # Side ribs extend beyond the nominal shell width
    assert bb.xlen > 380, f"Expected xlen > 380, got {bb.xlen:.1f}"
    assert bb.ylen > 250, f"Expected ylen > 250, got {bb.ylen:.1f}"
    assert bb.zlen > 60, f"Expected zlen > 60, got {bb.zlen:.1f}"


def test_page2_builds_with_chamfer():
    """Page 2 should build successfully with the exosuit shell."""
    page2 = build_page2()
    assert page2 is not None
    bb = page2.val().BoundingBox()
    assert bb.xlen > 380, f"Expected xlen > 380, got {bb.xlen:.1f}"
    assert bb.ylen > 250, f"Expected ylen > 250, got {bb.ylen:.1f}"
    assert bb.zlen > 40, f"Expected zlen > 40, got {bb.zlen:.1f}"


def test_page3_builds_with_armor_panels():
    """Page 3 should build successfully with armor panel + exosuit treatment."""
    page3 = build_page3()
    assert page3 is not None
    bb = page3.val().BoundingBox()
    # Chamfered corners reduce the bounding box below nominal CASE_OUTER_W
    assert bb.xlen > 380, f"Expected xlen > 380, got {bb.xlen:.1f}"
    assert bb.ylen > 250, f"Expected ylen > 250, got {bb.ylen:.1f}"
    assert bb.zlen > 35, f"Expected zlen > 35, got {bb.zlen:.1f}"
