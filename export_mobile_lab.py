#!/usr/bin/env python3
"""
Export STL/STEP files from mobile-lab-case.py for 3D printing.

Exports each tile at Z=0 for slicing. Also exports assembled
pages as STEP files for reference.
"""

import sys
import os
import re
from pathlib import Path


def export_files():
    try:
        import cadquery as cq
        print("✅ CadQuery available")
    except ImportError:
        print("❌ CadQuery not available. Install with: pip install cadquery")
        return False

    sys.path.insert(0, str(Path(__file__).parent / "designs"))

    try:
        with open("designs/mobile-lab-case.py", "r") as f:
            code = f.read()

        code = code.replace("from cq_server.ui import ui, show_object", "# cq_server removed")

        # Stub out show_object so cq_server preview calls are silently ignored
        g = {"show_object": lambda *a, **kw: None, "ui": None}
        exec(code, g)

        tiles = {
            "page1-left":  g["page1_left"],
            "page1-right": g["page1_right"],
            "page2-left":  g["page2_left"],
            "page2-right": g["page2_right"],
            "page3-left":  g["page3_left"],
            "page3-right": g["page3_right"],
        }

        pages = {
            "page1-assembled": g["page1"],
            "page2-assembled": g["page2"],
            "page3-assembled": g["page3"],
        }

        print("✅ Design objects loaded")

    except Exception as e:
        print(f"❌ Failed to load design: {e}")
        import traceback
        traceback.print_exc()
        return False

    os.makedirs("output", exist_ok=True)

    # Export tiles as STL (translated to Z=0 for printing)
    for name, solid in tiles.items():
        bb = solid.val().BoundingBox()
        z_offset = -bb.zmin  # translate to Z=0
        printable = solid.translate((0, 0, z_offset))

        stl_path = f"output/mobile-lab-{name}.stl"
        cq.exporters.export(printable, stl_path)
        print(f"✅ {stl_path}")

    # Export assembled pages as STEP (for reference)
    for name, solid in pages.items():
        step_path = f"output/mobile-lab-{name}.step"
        cq.exporters.export(solid, step_path)
        print(f"✅ {step_path}")

    print(f"\n🖨️  Print tiles on QIDI Q2 (275×295mm bed)")
    print(f"   Material: PETG | Layer: 0.2mm | Infill: 20% gyroid | Walls: 4")
    print(f"   Join tiles with M3 heat-set inserts + M3×8 bolts")
    return True


if __name__ == "__main__":
    export_files()
