# -*- coding: utf-8 -*-
"""
Ralo Oculto Inteligente V1 — gerador de conceito para Autodesk Fusion.

O script cria:
- 3 módulos estruturais para um ralo de 900 mm;
- tampa com ranhuras de vazão;
- nervuras inferiores, longarina central e trilhos laterais;
- encaixes macho/fêmea entre módulos;
- pequenas saliências antiderrapantes;
- 3 cartuchos tipo "pente" para estudo de retenção de cabelo;
- um cupom estrutural de 100 mm para impressão e ensaio inicial.

IMPORTANTE:
Este é um protótipo geométrico, não um componente estrutural certificado.
Meça o ralo real, ajuste as constantes abaixo e faça ensaios progressivos antes
de permitir que alguém pise na peça instalada.
"""

import adsk.core
import adsk.fusion
import traceback
import math

# ============================================================
# CONFIGURAÇÃO — EDITE AQUI E EXECUTE NOVAMENTE
# Todas as dimensões estão em milímetros.
# ============================================================

TOTAL_LENGTH_MM = 900.0
DRAIN_WIDTH_MM = 78.0
MODULE_COUNT = 3
MODULE_GAP_MM = 1.0

TOP_PLATE_THICKNESS_MM = 5.5
RIB_HEIGHT_MM = 8.0
RIB_OVERLAP_MM = 0.15

SIDE_RAIL_WIDTH_MM = 3.5
CENTER_SPINE_WIDTH_MM = 4.0
CROSS_RIB_THICKNESS_MM = 3.0
CROSS_RIB_PITCH_MM = 40.0

SLOT_WIDTH_MM = 3.2
SLOT_LENGTH_MM = 28.0
SLOT_PITCH_MM = 40.0
SLOT_EDGE_MARGIN_MM = 6.0

BUMPS_ENABLED = True
BUMP_RADIUS_MM = 1.15
BUMP_HEIGHT_MM = 0.65
BUMP_PITCH_MM = 40.0

CONNECTOR_ENABLED = True
CONNECTOR_TAB_LENGTH_MM = 9.0
CONNECTOR_TAB_WIDTH_MM = 10.0
CONNECTOR_TAB_HEIGHT_MM = 4.0
CONNECTOR_CLEARANCE_MM = 0.35
CONNECTOR_Y_MM = 22.0

FILTER_ENABLED = True
FILTER_EXPLODED_Z_MM = -15.0
FILTER_MARGIN_X_MM = 9.0
FILTER_RAIL_WIDTH_MM = 3.0
FILTER_RAIL_Y_MM = 22.0
FILTER_BAR_THICKNESS_MM = 2.4
FILTER_BAR_PITCH_MM = 14.0
FILTER_THICKNESS_MM = 3.0

CREATE_TEST_COUPON = True
TEST_COUPON_LENGTH_MM = 100.0
TEST_COUPON_Y_MM = 125.0

# ============================================================

_app = None
_ui = None
_mgr = None

def mm(value):
    """Fusion API geometry uses centimeters internally."""
    return float(value) / 10.0

def point_mm(x, y, z):
    return adsk.core.Point3D.create(mm(x), mm(y), mm(z))

def box_mm(cx, cy, cz, length, width, height):
    center = point_mm(cx, cy, cz)
    x_dir = adsk.core.Vector3D.create(1, 0, 0)
    y_dir = adsk.core.Vector3D.create(0, 1, 0)
    obb = adsk.core.OrientedBoundingBox3D.create(
        center, x_dir, y_dir, mm(length), mm(width), mm(height)
    )
    body = _mgr.createBox(obb)
    if not body:
        raise RuntimeError("Falha ao criar caixa BRep.")
    return body

def cylinder_z_mm(x, y, z_bottom, z_top, radius):
    p1 = point_mm(x, y, z_bottom)
    p2 = point_mm(x, y, z_top)
    body = _mgr.createCylinderOrCone(p1, mm(radius), p2, mm(radius))
    if not body:
        raise RuntimeError("Falha ao criar cilindro BRep.")
    return body

def union_into(target, tool, description="união"):
    ok = _mgr.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.UnionBooleanType
    )
    if not ok:
        raise RuntimeError(f"Falha na {description}.")
    return target

def cut_from(target, tool, description="corte"):
    ok = _mgr.booleanOperation(
        target, tool, adsk.fusion.BooleanTypes.DifferenceBooleanType
    )
    if not ok:
        raise RuntimeError(f"Falha no {description}.")
    return target

def persist_body(root, transient_body, name):
    body = root.bRepBodies.add(transient_body)
    if not body:
        raise RuntimeError(f"Não foi possível persistir o corpo: {name}")
    body.name = name
    return body

def module_length():
    return (
        TOTAL_LENGTH_MM - MODULE_GAP_MM * (MODULE_COUNT - 1)
    ) / MODULE_COUNT

def add_support_structure(target, x_start, length, y0=0.0):
    # Os reforços invadem a tampa em RIB_OVERLAP_MM para garantir uma união sólida.
    support_h = RIB_HEIGHT_MM + RIB_OVERLAP_MM
    support_z = support_h / 2.0

    # Trilhos laterais.
    rail_y = DRAIN_WIDTH_MM / 2.0 - SIDE_RAIL_WIDTH_MM / 2.0
    for sign in (-1.0, 1.0):
        rail = box_mm(
            x_start + length / 2.0,
            y0 + sign * rail_y,
            support_z,
            length,
            SIDE_RAIL_WIDTH_MM,
            support_h,
        )
        union_into(target, rail, "união do trilho lateral")

    # Longarina central.
    spine = box_mm(
        x_start + length / 2.0,
        y0,
        support_z,
        length,
        CENTER_SPINE_WIDTH_MM,
        support_h,
    )
    union_into(target, spine, "união da longarina central")

    # Nervuras transversais.
    usable_width = DRAIN_WIDTH_MM - 2.0 * SIDE_RAIL_WIDTH_MM
    rib_count = max(2, int(math.floor(length / CROSS_RIB_PITCH_MM)) + 1)
    for idx in range(rib_count + 1):
        x = x_start + min(length - 1.5, 1.5 + idx * CROSS_RIB_PITCH_MM)
        rib = box_mm(
            x,
            y0,
            support_z,
            CROSS_RIB_THICKNESS_MM,
            usable_width,
            support_h,
        )
        union_into(target, rib, "união da nervura transversal")

def add_connectors(target, module_index, x_start, length, y0=0.0):
    if not CONNECTOR_ENABLED:
        return

    connector_z = CONNECTOR_TAB_HEIGHT_MM / 2.0 + 1.0

    # Rebaixos fêmea nos módulos 2 e 3.
    if module_index > 0:
        receiver_depth = CONNECTOR_TAB_LENGTH_MM + 1.0
        receiver_width = CONNECTOR_TAB_WIDTH_MM + 2.0 * CONNECTOR_CLEARANCE_MM
        receiver_height = CONNECTOR_TAB_HEIGHT_MM + 2.0 * CONNECTOR_CLEARANCE_MM

        for sign in (-1.0, 1.0):
            receiver = box_mm(
                x_start + receiver_depth / 2.0,
                y0 + sign * CONNECTOR_Y_MM,
                connector_z,
                receiver_depth,
                receiver_width,
                receiver_height,
            )
            cut_from(target, receiver, "corte do encaixe fêmea")

    # Linguetas macho nos módulos 1 e 2.
    if module_index < MODULE_COUNT - 1:
        overlap = 0.2
        for sign in (-1.0, 1.0):
            tab = box_mm(
                x_start + length + CONNECTOR_TAB_LENGTH_MM / 2.0 - overlap,
                y0 + sign * CONNECTOR_Y_MM,
                connector_z,
                CONNECTOR_TAB_LENGTH_MM + 2.0 * overlap,
                CONNECTOR_TAB_WIDTH_MM,
                CONNECTOR_TAB_HEIGHT_MM,
            )
            union_into(target, tab, "união da lingueta macho")

def add_drain_slots(target, x_start, length, y0=0.0):
    top_bottom = RIB_HEIGHT_MM
    cut_bottom = top_bottom - 0.15
    cut_top = top_bottom + TOP_PLATE_THICKNESS_MM + 0.35
    cut_h = cut_top - cut_bottom
    cut_z = (cut_bottom + cut_top) / 2.0

    # Quatro fileiras, evitando a longarina central.
    row_limit = DRAIN_WIDTH_MM / 2.0 - SLOT_EDGE_MARGIN_MM - SLOT_WIDTH_MM / 2.0
    row_positions = (-row_limit, -8.0, 8.0, row_limit)

    first_center = SLOT_PITCH_MM / 2.0
    count = max(1, int(math.floor((length - SLOT_LENGTH_MM) / SLOT_PITCH_MM)) + 1)

    for i in range(count):
        local_x = first_center + i * SLOT_PITCH_MM
        if local_x + SLOT_LENGTH_MM / 2.0 > length - 4.0:
            continue

        x = x_start + local_x
        for row_y in row_positions:
            slot = box_mm(
                x,
                y0 + row_y,
                cut_z,
                SLOT_LENGTH_MM,
                SLOT_WIDTH_MM,
                cut_h,
            )
            cut_from(target, slot, "corte da ranhura de vazão")

def add_antislip_bumps(target, x_start, length, y0=0.0):
    if not BUMPS_ENABLED:
        return

    top_z = RIB_HEIGHT_MM + TOP_PLATE_THICKNESS_MM
    z1 = top_z - 0.10
    z2 = top_z + BUMP_HEIGHT_MM
    y_positions = (
        -DRAIN_WIDTH_MM / 2.0 + 9.0,
        0.0,
        DRAIN_WIDTH_MM / 2.0 - 9.0,
    )

    count = max(1, int(math.floor((length - 10.0) / BUMP_PITCH_MM)) + 1)
    for i in range(count):
        x = x_start + 5.0 + i * BUMP_PITCH_MM
        if x > x_start + length - 4.0:
            continue
        for y in y_positions:
            bump = cylinder_z_mm(x, y0 + y, z1, z2, BUMP_RADIUS_MM)
            union_into(target, bump, "união da saliência antiderrapante")

def build_module(root, module_index, x_start, length, y0=0.0, name_prefix="Tampa"):
    plate_z = RIB_HEIGHT_MM + TOP_PLATE_THICKNESS_MM / 2.0
    body = box_mm(
        x_start + length / 2.0,
        y0,
        plate_z,
        length,
        DRAIN_WIDTH_MM,
        TOP_PLATE_THICKNESS_MM,
    )

    add_support_structure(body, x_start, length, y0)
    add_connectors(body, module_index, x_start, length, y0)
    add_drain_slots(body, x_start, length, y0)
    add_antislip_bumps(body, x_start, length, y0)

    return persist_body(
        root,
        body,
        f"{name_prefix}_{module_index + 1:02d}_{length:.1f}mm",
    )

def build_filter(root, module_index, x_start, length, y0=0.0):
    filter_length = max(40.0, length - 2.0 * FILTER_MARGIN_X_MM)
    x_center = x_start + length / 2.0
    z_center = FILTER_EXPLODED_Z_MM + FILTER_THICKNESS_MM / 2.0

    # Começa por uma barra transversal, depois une os trilhos.
    first_x = x_start + FILTER_MARGIN_X_MM + FILTER_BAR_THICKNESS_MM / 2.0
    full_width = 2.0 * FILTER_RAIL_Y_MM + FILTER_RAIL_WIDTH_MM
    body = box_mm(
        first_x,
        y0,
        z_center,
        FILTER_BAR_THICKNESS_MM,
        full_width,
        FILTER_THICKNESS_MM,
    )

    for sign in (-1.0, 1.0):
        rail = box_mm(
            x_center,
            y0 + sign * FILTER_RAIL_Y_MM,
            z_center,
            filter_length,
            FILTER_RAIL_WIDTH_MM,
            FILTER_THICKNESS_MM,
        )
        union_into(body, rail, "união do trilho do cartucho")

    bar_count = max(2, int(math.floor(filter_length / FILTER_BAR_PITCH_MM)))
    for i in range(1, bar_count + 1):
        x = x_start + FILTER_MARGIN_X_MM + i * FILTER_BAR_PITCH_MM
        if x > x_start + length - FILTER_MARGIN_X_MM:
            break
        bar = box_mm(
            x,
            y0,
            z_center,
            FILTER_BAR_THICKNESS_MM,
            full_width,
            FILTER_THICKNESS_MM,
        )
        union_into(body, bar, "união da barra do cartucho")

    # Puxador achatado para retirada rápida.
    pull = box_mm(
        x_start + FILTER_MARGIN_X_MM + 7.0,
        y0,
        z_center,
        14.0,
        12.0,
        FILTER_THICKNESS_MM,
    )
    union_into(body, pull, "união do puxador do cartucho")

    return persist_body(
        root,
        body,
        f"Filtro_Pente_{module_index + 1:02d}",
    )

def build_test_coupon(root):
    # Cupom fora do conjunto principal, com a mesma seção estrutural.
    x_start = 0.0
    y0 = TEST_COUPON_Y_MM
    length = TEST_COUPON_LENGTH_MM

    plate_z = RIB_HEIGHT_MM + TOP_PLATE_THICKNESS_MM / 2.0
    body = box_mm(
        x_start + length / 2.0,
        y0,
        plate_z,
        length,
        DRAIN_WIDTH_MM,
        TOP_PLATE_THICKNESS_MM,
    )
    add_support_structure(body, x_start, length, y0)
    add_drain_slots(body, x_start, length, y0)
    add_antislip_bumps(body, x_start, length, y0)

    return persist_body(root, body, "CUPOM_TESTE_ESTRUTURAL_100mm")

def run(context):
    global _app, _ui, _mgr

    try:
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        _mgr = adsk.fusion.TemporaryBRepManager.get()

        doc = _app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(_app.activeProduct)
        if not design:
            raise RuntimeError("Não foi possível acessar o ambiente Design.")

        # Corpos BRep diretos: robustos para um gerador inicial e fáceis de editar.
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = design.rootComponent
        root.name = "Ralo_Oculto_Inteligente_V1"

        length = module_length()
        created = []

        for idx in range(MODULE_COUNT):
            x_start = idx * (length + MODULE_GAP_MM)
            created.append(build_module(root, idx, x_start, length))

            if FILTER_ENABLED:
                created.append(build_filter(root, idx, x_start, length))

        if CREATE_TEST_COUPON:
            created.append(build_test_coupon(root))

        _app.activeViewport.fit()

        _ui.messageBox(
            "Ralo Oculto Inteligente V1 criado com sucesso.\n\n"
            f"Comprimento total: {TOTAL_LENGTH_MM:.1f} mm\n"
            f"Largura inicial: {DRAIN_WIDTH_MM:.1f} mm\n"
            f"Módulos: {MODULE_COUNT} × {length:.1f} mm\n\n"
            "Próximo passo: confira as medidas reais do ralo, ajuste as "
            "constantes no início do script e execute novamente.\n\n"
            "ATENÇÃO: protótipo não ensaiado. Imprima primeiro o cupom de "
            "100 mm e não permita carga humana na instalação sem testes."
        )

    except Exception:
        if _ui:
            _ui.messageBox(
                "Falha ao gerar o projeto:\n\n" + traceback.format_exc()
            )

def stop(context):
    pass
