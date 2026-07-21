"""Clearance test gauge — print this FIRST.

A plate with five holes and a bar with five 5.00 mm pegs. Each hole is
oversized by a different clearance (0.0 to 0.4 mm). Press the peg bar into
the plate after printing and note which pegs engage:

  - tightest hole a peg fully enters  -> your press-fit clearance
  - loosest hole with no wobble       -> your snug/sliding-fit clearance
  - anything looser                   -> free fit (lids, hinges)

Write those numbers down — every parametric part you design from now on
uses them. On a well-tuned Bambu with PLA, expect roughly 0.1 / 0.2 / 0.3.
"""

from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Cylinder,
    Hole,
    Locations,
    Mode,
    Plane,
    Text,
    export_stl,
    extrude,
)

# ---------------------------------------------------------------- parameters
PEG_DIAMETER = 5.0            # mm, nominal
CLEARANCES = [0.0, 0.1, 0.2, 0.3, 0.4]  # mm added to each hole diameter
SPACING = 13.0                # mm between hole centers
PLATE_THICKNESS = 4.0
PEG_HEIGHT = 8.0
BAR_THICKNESS = 3.0
LABEL_DEPTH = 0.6             # engraving depth

STL_DIR = Path(__file__).resolve().parent.parent / "stl"

plate_length = SPACING * (len(CLEARANCES) + 0.6)
plate_width = 16.0
xs = [(i - (len(CLEARANCES) - 1) / 2) * SPACING for i in range(len(CLEARANCES))]

# --------------------------------------------------------- plate with holes
with BuildPart() as plate:
    Box(plate_length, plate_width, PLATE_THICKNESS)
    for x, clearance in zip(xs, CLEARANCES):
        with Locations((x, 0, 0)):
            Hole(radius=(PEG_DIAMETER + clearance) / 2)
    # engrave the clearance value under each hole
    top = plate.faces().sort_by(Axis.Z)[-1]
    with BuildSketch(top):
        for x, clearance in zip(xs, CLEARANCES):
            with Locations((x, -5.5)):
                Text(f"{clearance:.1f}", font_size=3)
    extrude(amount=-LABEL_DEPTH, mode=Mode.SUBTRACT)

# --------------------------------------------------------------- peg bar
with BuildPart() as pegs:
    Box(plate_length, plate_width, BAR_THICKNESS)
    with Locations(*[(x, 0, BAR_THICKNESS / 2) for x in xs]):
        Cylinder(
            radius=PEG_DIAMETER / 2,
            height=PEG_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

if __name__ == "__main__":
    STL_DIR.mkdir(exist_ok=True)
    combined = plate.part.translate((0, 0, PLATE_THICKNESS / 2)) + pegs.part.translate(
        (0, plate_width + 4, BAR_THICKNESS / 2)
    )
    export_stl(combined, str(STL_DIR / "clearance_test.stl"))
    print(f"exported {STL_DIR / 'clearance_test.stl'}")
