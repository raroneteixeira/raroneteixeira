"""Parametric box with a friction-fit lid.

Change LENGTH / WIDTH / HEIGHT and re-run to get a box for anything —
SD cards, screws, resistors. LID_CLEARANCE controls how tight the lid
fits: use the "snug" value from your clearance_test print (~0.2 mm) for
a lid that stays on, or the free value (~0.3 mm) for one that lifts off
easily.

Print both parts as-is: box open side up, lid flat side down. No supports.
"""

from pathlib import Path

from build123d import (
    BuildPart,
    BuildSketch,
    Mode,
    Plane,
    RectangleRounded,
    export_stl,
    extrude,
)

# ---------------------------------------------------------------- parameters
LENGTH = 60.0          # mm, outer
WIDTH = 40.0           # mm, outer
HEIGHT = 25.0          # mm, outer (without lid)
WALL = 1.6             # 4 perimeters at 0.4 mm nozzle
FLOOR = 1.2
CORNER_RADIUS = 4.0
LID_THICKNESS = 1.6
LIP_HEIGHT = 4.0
LIP_WALL = 1.6
LID_CLEARANCE = 0.2    # mm per side — from your clearance_test print

STL_DIR = Path(__file__).resolve().parent.parent / "stl"

# ------------------------------------------------------------------- box
with BuildPart() as box:
    with BuildSketch():
        RectangleRounded(LENGTH, WIDTH, radius=CORNER_RADIUS)
    extrude(amount=HEIGHT)
    with BuildSketch(Plane.XY.offset(FLOOR)):
        RectangleRounded(
            LENGTH - 2 * WALL, WIDTH - 2 * WALL, radius=CORNER_RADIUS - WALL
        )
    extrude(amount=HEIGHT, mode=Mode.SUBTRACT)

# ------------------------------------------------------------------- lid
lip_l = LENGTH - 2 * WALL - 2 * LID_CLEARANCE
lip_w = WIDTH - 2 * WALL - 2 * LID_CLEARANCE

with BuildPart() as lid:
    with BuildSketch():
        RectangleRounded(LENGTH, WIDTH, radius=CORNER_RADIUS)
    extrude(amount=LID_THICKNESS)
    with BuildSketch(Plane.XY.offset(LID_THICKNESS)):
        RectangleRounded(lip_l, lip_w, radius=CORNER_RADIUS - WALL - LID_CLEARANCE)
    extrude(amount=LIP_HEIGHT)
    # hollow the lip so it flexes and saves plastic
    with BuildSketch(Plane.XY.offset(LID_THICKNESS)):
        RectangleRounded(
            lip_l - 2 * LIP_WALL,
            lip_w - 2 * LIP_WALL,
            radius=max(CORNER_RADIUS - WALL - LID_CLEARANCE - LIP_WALL, 0.5),
        )
    extrude(amount=LIP_HEIGHT, mode=Mode.SUBTRACT)

if __name__ == "__main__":
    STL_DIR.mkdir(exist_ok=True)
    export_stl(box.part, str(STL_DIR / "box.stl"))
    export_stl(lid.part, str(STL_DIR / "box_lid.stl"))
    print(f"exported {STL_DIR / 'box.stl'} and {STL_DIR / 'box_lid.stl'}")
