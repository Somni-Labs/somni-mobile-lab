"""
Eccentric Cam Lift Mechanism

Parametric cam driven by SG90 micro servo.
180-degree rotation pushes cam high point through a floor slot,
raising a lift plate ~20mm.

Reused 3x (laptop, monitor, keyboard) with different slot widths.
"""

import os
import sys
import cadquery as cq
import math

# Bootstrap sys.path for cadquery-server symlink loading
_this_dir = os.path.dirname(os.path.realpath(__file__))
_repo_root = os.path.abspath(os.path.join(_this_dir, "..", ".."))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from designs.common.constants import (
    CAM_OD, CAM_ECCENTRICITY, CAM_THICKNESS,
    CAM_LIFT_HEIGHT, LIFT_SLOT_W,
    SG90_W, SG90_D, SG90_H,
    M3_CLEARANCE_DIA,
)

try:
    from cq_server.ui import ui, show_object
    _cq_server = True
except ImportError:
    _cq_server = False


def build_cam(cam_od=CAM_OD, eccentricity=CAM_ECCENTRICITY,
              thickness=CAM_THICKNESS):
    """
    Build an eccentric cam disc.
    The cam center is offset from the shaft center by 'eccentricity'.
    Shaft hole is at origin; cam disc is offset.
    """
    cam = (
        cq.Workplane("XY")
        .center(eccentricity, 0)
        .circle(cam_od / 2)
        .extrude(thickness)
    )
    shaft = (
        cq.Workplane("XY")
        .circle(3)
        .extrude(thickness + 1)
    )
    cam = cam.cut(shaft)
    flat = (
        cq.Workplane("XY")
        .center(-3, 0)
        .rect(2, 4)
        .extrude(thickness + 1)
    )
    cam = cam.cut(flat)
    return cam


def build_cam_housing(slot_w=LIFT_SLOT_W):
    """
    Build the housing that sits beneath the pocket floor.
    Contains the SG90 servo and cam, with a slot opening in the top
    for the lift plate to pass through.
    """
    housing_wall = 2
    hw = SG90_W + housing_wall * 2 + CAM_OD
    hd = max(SG90_D, CAM_OD) + housing_wall * 2
    hh = SG90_H + housing_wall

    housing = (
        cq.Workplane("XY")
        .rect(hw, hd)
        .extrude(hh)
    )
    servo_cavity = (
        cq.Workplane("XY")
        .workplane(offset=housing_wall)
        .center(-hw / 4, 0)
        .rect(SG90_W + 1, SG90_D + 1)
        .extrude(SG90_H + 1)
    )
    housing = housing.cut(servo_cavity)
    cam_cavity = (
        cq.Workplane("XY")
        .workplane(offset=housing_wall)
        .center(hw / 4, 0)
        .circle(CAM_OD / 2 + CAM_ECCENTRICITY + 1)
        .extrude(CAM_THICKNESS + 5)
    )
    housing = housing.cut(cam_cavity)
    slot = (
        cq.Workplane("XY")
        .workplane(offset=hh - 1)
        .center(hw / 4, 0)
        .rect(slot_w, hd - housing_wall * 2)
        .extrude(housing_wall + 2)
    )
    housing = housing.cut(slot)
    for dx in [-hw / 2 + 5, hw / 2 - 5]:
        hole = (
            cq.Workplane("XY")
            .center(dx, 0)
            .circle(M3_CLEARANCE_DIA / 2)
            .extrude(housing_wall + 1)
        )
        housing = housing.cut(hole)
    return housing


# --- Standalone preview for cadquery-server ---
if _cq_server and not os.environ.get('_CQ_ASSEMBLY'):
    cam = build_cam()
    show_object(cam, name="Eccentric Cam",
                options={"color": (0.7, 0.5, 0.2, 0.9)})
    housing = build_cam_housing().translate((0, 50, 0))
    show_object(housing, name="Cam Housing",
                options={"color": (0.4, 0.4, 0.4, 0.8)})
