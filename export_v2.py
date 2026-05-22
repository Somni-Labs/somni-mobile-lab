"""
Mobile Lab Case V2 — STL/STEP Export Script

Exports all printable parts:
  - 6 shell tiles (3 pages x 2 halves)
  - Hinge knuckles (per page, as pre-unioned with shell)
  - Latch housings, hooks, catches
  - Servo mounts + spur gears
  - Starlink pedestal base + platform + tilt mount + linkage
  - Cam lift housings + cams + lift plates
  - Electronics bay + lid
  - Button mount
  - LED diffuser strips
  - Retaining C-clips

All STLs translated to Z=0 for printing.
"""

import sys
import os

# Mock cq_server so imports don't fail
mock_mod = type(sys)('mock')
sys.modules['cq_server'] = mock_mod
mock_ui = type(sys)('mock')
mock_ui.ui = None
mock_ui.show_object = lambda *a, **k: None
sys.modules['cq_server.ui'] = mock_ui

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import cadquery as cq
from designs.common.constants import (
    CASE_OUTER_W, CASE_OUTER_D,
    PAGE1_H, PAGE2_H, PAGE3_H,
)
from designs.common.mounting import split_into_tiles, add_tile_seam_features
from designs.shell.page1_shell import build_page1
from designs.shell.page2_shell import build_page2
from designs.shell.page3_shell import build_page3
from designs.hinge.hinge_knuckles import build_hinge_knuckles, build_retaining_clip
from designs.hinge.latch_mechanism import build_latch_housing, build_latch_hook, build_latch_catch
from designs.hinge.hinge_servo_mount import build_servo_mount, build_spur_gear
from designs.starlink.pedestal_base import build_pedestal_base
from designs.starlink.pedestal_platform import build_pedestal_platform
from designs.starlink.tilt_linkage import build_tilt_servo_mount, build_linkage_arm
from designs.lifts.cam_lift import build_cam, build_cam_housing
from designs.lifts.lift_plate import build_laptop_lift_plate, build_monitor_lift_plate, build_keyboard_lift_plate
from designs.electronics.electronics_bay import build_electronics_bay, build_electronics_bay_lid
from designs.electronics.button_mount import build_button_mount
from designs.led.diffuser_strip import build_diffuser_strip


OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def export_stl(solid, name):
    """Export a CadQuery solid to STL, translated to Z=0."""
    bb = solid.val().BoundingBox()
    if bb.zmin != 0:
        solid = solid.translate((0, 0, -bb.zmin))
    path = os.path.join(OUTPUT_DIR, f"v2-{name}.stl")
    cq.exporters.export(solid, path)
    print(f"  Exported: {path}")


def export_step(solid, name):
    """Export a CadQuery solid to STEP."""
    path = os.path.join(OUTPUT_DIR, f"v2-{name}.step")
    cq.exporters.export(solid, path)
    print(f"  Exported: {path}")


def main():
    print("=== Mobile Lab Case V2 — Exporting all parts ===\n")

    # --- Shell tiles ---
    print("Shell tiles:")
    for name, builder, page_h in [
        ("page1", build_page1, PAGE1_H),
        ("page2", build_page2, PAGE2_H),
        ("page3", build_page3, PAGE3_H),
    ]:
        page = builder()
        # Add hinges
        parity_top = "even"
        parity_bot = "odd" if name == "page2" or name == "page3" else None
        hinges_top = build_hinge_knuckles(page_h, parity=parity_top)
        page = page.union(hinges_top)
        if parity_bot:
            hinges_bot = build_hinge_knuckles(0, parity=parity_bot)
            page = page.union(hinges_bot)
        # Split into tiles
        left, right = split_into_tiles(page, CASE_OUTER_W, CASE_OUTER_D, page_h)
        left = add_tile_seam_features(left, CASE_OUTER_D, page_h, is_left=True)
        right = add_tile_seam_features(right, CASE_OUTER_D, page_h, is_left=False)
        export_stl(left, f"{name}-left-tile")
        export_stl(right, f"{name}-right-tile")
        export_step(page, f"{name}-assembled")

    # --- Hinge parts ---
    print("\nHinge & latch parts:")
    export_stl(build_latch_housing(), "latch-housing")
    export_stl(build_latch_hook(), "latch-hook")
    export_stl(build_latch_catch(), "latch-catch")
    export_stl(build_servo_mount(), "hinge-servo-mount")
    export_stl(build_spur_gear(), "spur-gear")
    export_stl(build_retaining_clip(), "retaining-clip")

    # --- Starlink pedestal ---
    print("\nStarlink pedestal:")
    export_stl(build_pedestal_base(), "pedestal-base")
    export_stl(build_pedestal_platform(), "pedestal-platform")
    export_stl(build_tilt_servo_mount(), "tilt-servo-mount")
    export_stl(build_linkage_arm(), "tilt-linkage-arm")

    # --- Cam lifts ---
    print("\nDevice lifts:")
    export_stl(build_cam(), "eccentric-cam")
    export_stl(build_cam_housing(), "cam-housing")
    export_stl(build_laptop_lift_plate(), "lift-plate-laptop")
    export_stl(build_monitor_lift_plate(), "lift-plate-monitor")
    export_stl(build_keyboard_lift_plate(), "lift-plate-keyboard")

    # --- Electronics ---
    print("\nElectronics:")
    export_stl(build_electronics_bay(), "electronics-bay")
    export_stl(build_electronics_bay_lid(), "electronics-bay-lid")
    export_stl(build_button_mount(), "button-mount")

    # --- LED diffusers ---
    print("\nLED diffusers:")
    for length, label in [(200, "spine"), (150, "lateral"), (100, "accent")]:
        export_stl(build_diffuser_strip(length), f"diffuser-{label}-{length}mm")

    print(f"\n=== Done! {len(os.listdir(OUTPUT_DIR))} files in {OUTPUT_DIR} ===")


if __name__ == "__main__":
    main()
