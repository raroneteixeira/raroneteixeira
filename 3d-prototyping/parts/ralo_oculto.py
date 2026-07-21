"""Ralo Oculto Inteligente — hidden linear drain cover, ported to build123d.

Port of the Fusion 360 generator (RaloOcultoV1) so STLs export directly,
no Fusion needed. Same concept: a TOTAL_LENGTH cover split into printable
modules with side rails, a center spine, cross ribs, drainage slots,
male/female connectors between modules, optional anti-slip bumps, a
comb-style hair-catcher cartridge, and a short structural test coupon.

Exports (run this file):
    stl/ralo_cupom_teste.stl   <- PRINT AND LOAD-TEST THIS FIRST
    stl/ralo_tampa_inicio.stl  (male connector at one end)
    stl/ralo_tampa_meio.stl    (female + male; print MODULE_COUNT-2 of these)
    stl/ralo_tampa_fim.stl     (female connector only)
    stl/ralo_filtro_pente.stl  (hair-catcher cartridge, print MODULE_COUNT)

Print notes
-----------
- Orientation: top face DOWN on the textured plate gives the best finish
  and zero bridging (ribs grow upward from the solid plate). Anti-slip
  bumps prevent that orientation — if you keep ANTISLIP_BUMPS = True,
  print top face UP and accept bridged spans between ribs instead.
- Material: PLA is fine for fit tests. For a wet, load-bearing install
  use PETG or ASA — PLA creeps under sustained load and softens with
  heat/humidity.
- This is an unvalidated prototype. Load-test the coupon on a bench
  before anyone steps on an installed part.
"""

from pathlib import Path

from build123d import Align, Box, Cylinder, Pos, export_stl

# ---------------------------------------------------------------- parameters
TOTAL_LENGTH = 900.0
DRAIN_WIDTH = 78.0
MODULE_COUNT = 3          # 3 -> ~299 mm modules (needs a big bed, e.g. H2D).
MODULE_GAP = 1.0          # 4 -> ~224 mm modules (fits X1C/P1S 256 mm beds).

TOP_PLATE_THICKNESS = 5.5
RIB_HEIGHT = 8.0
RIB_OVERLAP = 0.15        # ribs invade the plate slightly for a solid union

SIDE_RAIL_WIDTH = 3.5
CENTER_SPINE_WIDTH = 4.0
CROSS_RIB_THICKNESS = 3.0
CROSS_RIB_PITCH = 40.0

SLOT_WIDTH = 3.2
SLOT_LENGTH = 28.0
SLOT_PITCH = 40.0
SLOT_EDGE_MARGIN = 6.0

ANTISLIP_BUMPS = True     # see "Orientation" note above
BUMP_RADIUS = 1.15
BUMP_HEIGHT = 0.65
BUMP_PITCH = 40.0

CONNECTOR_TAB_LENGTH = 9.0
CONNECTOR_TAB_WIDTH = 10.0
CONNECTOR_TAB_HEIGHT = 4.0
CONNECTOR_CLEARANCE = 0.35  # from your clearance_test print (free fit + margin)
CONNECTOR_Y = 22.0

FILTER_MARGIN_X = 9.0
FILTER_RAIL_WIDTH = 3.0
FILTER_RAIL_Y = 22.0
FILTER_BAR_THICKNESS = 2.4
FILTER_BAR_PITCH = 14.0
FILTER_THICKNESS = 3.0

TEST_COUPON_LENGTH = 100.0
PRINTER_BED = 250.0       # warn if a module exceeds this

STL_DIR = Path(__file__).resolve().parent.parent / "stl"


def box_at(cx, cy, cz, length, width, height):
    return Pos(cx, cy, cz) * Box(length, width, height)


def module_length():
    return (TOTAL_LENGTH - MODULE_GAP * (MODULE_COUNT - 1)) / MODULE_COUNT


def rib_positions(length):
    """First and last rib flush with the module ends, the rest on pitch."""
    xs = {1.5, length - 1.5}
    x = 1.5 + CROSS_RIB_PITCH
    while x < length - 1.5:
        xs.add(x)
        x += CROSS_RIB_PITCH
    return sorted(xs)


def build_cover(length, male=False, female=False, bumps=ANTISLIP_BUMPS):
    """One cover module: plate on top, support structure below (z=0 at rib
    bottom), connectors on the ends."""
    plate_z = RIB_HEIGHT + TOP_PLATE_THICKNESS / 2
    part = box_at(length / 2, 0, plate_z, length, DRAIN_WIDTH, TOP_PLATE_THICKNESS)

    # rails, spine, cross ribs
    support_h = RIB_HEIGHT + RIB_OVERLAP
    sz = support_h / 2
    rail_y = DRAIN_WIDTH / 2 - SIDE_RAIL_WIDTH / 2
    for sign in (-1, 1):
        part += box_at(length / 2, sign * rail_y, sz, length, SIDE_RAIL_WIDTH, support_h)
    part += box_at(length / 2, 0, sz, length, CENTER_SPINE_WIDTH, support_h)
    usable_width = DRAIN_WIDTH - 2 * SIDE_RAIL_WIDTH
    for x in rib_positions(length):
        part += box_at(x, 0, sz, CROSS_RIB_THICKNESS, usable_width, support_h)

    # male tabs / female recesses between modules
    connector_z = CONNECTOR_TAB_HEIGHT / 2 + 1.0
    if female:
        depth = CONNECTOR_TAB_LENGTH + 1.0
        recess_w = CONNECTOR_TAB_WIDTH + 2 * CONNECTOR_CLEARANCE
        recess_h = CONNECTOR_TAB_HEIGHT + 2 * CONNECTOR_CLEARANCE
        for sign in (-1, 1):
            part -= box_at(depth / 2, sign * CONNECTOR_Y, connector_z, depth, recess_w, recess_h)
    if male:
        overlap = 0.2
        for sign in (-1, 1):
            part += box_at(
                length + CONNECTOR_TAB_LENGTH / 2 - overlap,
                sign * CONNECTOR_Y,
                connector_z,
                CONNECTOR_TAB_LENGTH + 2 * overlap,
                CONNECTOR_TAB_WIDTH,
                CONNECTOR_TAB_HEIGHT,
            )

    # drainage slots — 4 rows avoiding the center spine
    cut_bottom = RIB_HEIGHT - 0.15
    cut_top = RIB_HEIGHT + TOP_PLATE_THICKNESS + 0.35
    cut_z = (cut_bottom + cut_top) / 2
    cut_h = cut_top - cut_bottom
    row_limit = DRAIN_WIDTH / 2 - SLOT_EDGE_MARGIN - SLOT_WIDTH / 2
    rows = (-row_limit, -8.0, 8.0, row_limit)
    x = SLOT_PITCH / 2
    while x + SLOT_LENGTH / 2 <= length - 4.0:
        for row_y in rows:
            part -= box_at(x, row_y, cut_z, SLOT_LENGTH, SLOT_WIDTH, cut_h)
        x += SLOT_PITCH

    # anti-slip bumps on the walking surface
    if bumps:
        top_z = RIB_HEIGHT + TOP_PLATE_THICKNESS
        bump_ys = (-DRAIN_WIDTH / 2 + 9.0, 0.0, DRAIN_WIDTH / 2 - 9.0)
        x = 5.0
        while x <= length - 4.0:
            for y in bump_ys:
                part += Pos(x, y, top_z - 0.10) * Cylinder(
                    BUMP_RADIUS,
                    BUMP_HEIGHT + 0.10,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            x += BUMP_PITCH

    return part


def build_filter(length):
    """Comb-style hair-catcher cartridge that sits below the slots."""
    filter_length = max(40.0, length - 2 * FILTER_MARGIN_X)
    full_width = 2 * FILTER_RAIL_Y + FILTER_RAIL_WIDTH
    zc = FILTER_THICKNESS / 2

    part = box_at(
        FILTER_MARGIN_X + FILTER_BAR_THICKNESS / 2, 0, zc,
        FILTER_BAR_THICKNESS, full_width, FILTER_THICKNESS,
    )
    for sign in (-1, 1):
        part += box_at(
            length / 2, sign * FILTER_RAIL_Y, zc,
            filter_length, FILTER_RAIL_WIDTH, FILTER_THICKNESS,
        )
    x = FILTER_MARGIN_X + FILTER_BAR_PITCH
    while x <= length - FILTER_MARGIN_X:
        part += box_at(x, 0, zc, FILTER_BAR_THICKNESS, full_width, FILTER_THICKNESS)
        x += FILTER_BAR_PITCH

    # flat pull tab for quick removal
    part += box_at(FILTER_MARGIN_X + 7.0, 0, zc, 14.0, 12.0, FILTER_THICKNESS)
    return part


if __name__ == "__main__":
    STL_DIR.mkdir(exist_ok=True)
    length = module_length()

    print(f"total {TOTAL_LENGTH} mm -> {MODULE_COUNT} modules of {length:.1f} mm")
    if length > PRINTER_BED:
        print(
            f"  WARNING: {length:.1f} mm exceeds a {PRINTER_BED:.0f} mm bed — "
            f"raise MODULE_COUNT (4 -> {(TOTAL_LENGTH - 3 * MODULE_GAP) / 4:.1f} mm/module)"
        )

    exports = {
        "ralo_cupom_teste": build_cover(TEST_COUPON_LENGTH),
        "ralo_tampa_inicio": build_cover(length, male=True),
        "ralo_tampa_meio": build_cover(length, male=True, female=True),
        "ralo_tampa_fim": build_cover(length, female=True),
        "ralo_filtro_pente": build_filter(length),
    }
    for name, part in exports.items():
        export_stl(part, str(STL_DIR / f"{name}.stl"))
        print(f"exported stl/{name}.stl")
