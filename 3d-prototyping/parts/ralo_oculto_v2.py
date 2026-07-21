"""Ralo Oculto Inteligente V2.1 — 890 x 50 mm, 35 mm de profundidade.

Conceito (do Rafael):
- Calha de 890 x 50 mm (35 mm de profundidade útil) dividida em 5
  segmentos de base (~178 mm cada), colados entre si na instalação
  (chaves de alinhamento macho/fêmea).
- Cada segmento tem uma PORTA que abre para cima para limpeza, girando
  sobre um pino de dobradiça — use um pedaço de filamento 1.75 mm de
  ~180 mm como pino (barato, inoxidável, substituível).
- O topo das portas é um PISO MASSAGEADOR: grade de domos arredondados
  (~0.8 mm acima do nível do piso) que massageiam a sola e funcionam
  como antiderrapante. Porta de 5 mm com apoios centrais = resistente.
- O segmento CENTRAL (sobre a saída de esgoto) recebe um CESTO removível
  que retém cabelos. O fundo do cesto é fechado: ele segura uma coluna
  de ~10 mm de água que funciona como selo de odor (mini-sifão passivo,
  sem peça móvel). A água entra pelas ranhuras superiores, transborda
  por elas, e o cheiro não sobe.

Peças exportadas (execute este arquivo):
    stl/v2_segmento_base.stl     -> imprimir 4x  (PETG recomendado)
    stl/v2_segmento_central.stl  -> imprimir 1x
    stl/v2_porta.stl             -> imprimir 5x  (6 paredes, 40% infill)
    stl/v2_cesto_retentor.stl    -> imprimir 1x

Montagem: passe o pino de filamento pelo furo da dobradiça a partir da
extremidade do segmento ANTES de colar o segmento vizinho — depois de
colado, o pino fica travado.

Imprima 1 segmento + 1 porta primeiro para validar encaixes e a
sensação dos domos sob o pé.
"""

from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot, Sphere, export_stl

# ---------------------------------------------------------------- parâmetros
TOTAL_LENGTH = 890.0
SEG_COUNT = 5
SEG_LENGTH = TOTAL_LENGTH / SEG_COUNT   # 178 mm — cabe em qualquer Bambu
WIDTH = 49.0            # boca do canal = 50; 0.5 mm de folga por lado

# perfil real do canal (fotos de 2026-07-21):
#   bordas: 15 mm de profundidade, com relevo de ~4 mm onde a base assenta
#   centro: 30 mm de profundidade (calha de escoamento)
#   bolsão da saída: ~73 mm de comprimento, ~30-35 mm, cano de 40 mm
EDGE_DEPTH = 15.0       # profundidade nas bordas = altura da moldura
RELEVO_H = 4.6          # altura do rebaixo no pé da parede (relevo = 4 mm)
RELEVO_W = 3.0          # quanto o rebaixo entra a partir da face externa
POCKET_DEPTH = 30.0     # bolsão da saída (use 30 por segurança; foto diz 35)
POCKET_LENGTH = 73.0
OUTLET_D = 40.0

FRAME_H = EDGE_DEPTH    # moldura apoia na borda de 15 mm, topo rente ao piso
WALL = 4.5              # parede grossa p/ acomodar o rebaixo do relevo
LEDGE_W = 4.0           # aba de apoio da porta (lado livre)
LEDGE_T = 1.5
DOOR_T = 5.0            # porta grossa = "bem resistente"
DOOR_RECESS = 0.5       # topo plano da porta 0.5 mm abaixo do nível do piso
KEY_CLEARANCE = 0.35    # folga das chaves de alinhamento (ajuste com o gauge)

# piso massageador — domos arredondados no topo das portas
BUMP_SPHERE_R = 3.0
BUMP_HEIGHT = 1.3       # quanto o domo sobressai do topo da porta
BUMP_PITCH_X = 12.0
BUMP_ROW_COUNT = 5

# dobradiça — pino = filamento 1.75 mm
PIN_HOLE_R = 1.15
HINGE_KNUCKLE_R = 2.5
KNUCKLE_LEN = 14.0
BASE_KNUCKLE_XS = (20.0, 87.0, 154.0)
DOOR_KNUCKLE_XS = (53.5, 120.5)

# segmento central — poço e cesto (dimensionados p/ o bolsão da saída)
WELL_LENGTH = 62.0      # < POCKET_LENGTH (73)
WELL_WALL = 2.0
BASKET_DEPTH = 20.0     # abaixo da flange — cabe no bolsão de 30 mm
BASKET_WALL = 1.6
BASKET_SLOT_W = 2.0
BASKET_SLOT_PITCH = 6.0
WATER_SEAL_H = 9.0      # parede cega inferior = coluna do selo d'água

STL_DIR = Path(__file__).resolve().parent.parent / "stl"

# ------------------------------------------------------------- derivados
inner_half = WIDTH / 2 - WALL                      # 20.0
door_rest_z = FRAME_H - DOOR_T - DOOR_RECESS       # 9.5
hinge_y = inner_half - 4.3                         # 15.7 — eixo da dobradiça
hinge_z = door_rest_z + DOOR_T / 2                 # 12.0
door_free_edge = -(inner_half - 2.5)               # fresta de 2.5 mm = vazão
well_x0 = (SEG_LENGTH - WELL_LENGTH) / 2           # 58
well_x1 = well_x0 + WELL_LENGTH                    # 120

# fileiras dos domos distribuídas na largura útil da porta
_row_lo = door_free_edge + BUMP_SPHERE_R + 0.5
_row_hi = hinge_y - BUMP_SPHERE_R - 0.5
BUMP_ROWS_Y = tuple(
    _row_lo + i * (_row_hi - _row_lo) / (BUMP_ROW_COUNT - 1)
    for i in range(BUMP_ROW_COUNT)
)


def box_at(cx, cy, cz, length, width, height):
    return Pos(cx, cy, cz) * Box(length, width, height)


def cyl_x(cx, cy, cz, length, radius):
    """Cilindro com eixo em X (eixo da dobradiça)."""
    return Pos(cx, cy, cz) * Rot(0, 90, 0) * Cylinder(radius, length)


def build_base(central=False):
    """Segmento da base: moldura em U aberto embaixo, abas e travessas de
    apoio da porta, castanhas da dobradiça e chaves de colagem."""
    solids = [
        box_at(SEG_LENGTH / 2, WIDTH / 2 - WALL / 2, FRAME_H / 2,
               SEG_LENGTH, WALL, FRAME_H),
        box_at(SEG_LENGTH / 2, -(WIDTH / 2 - WALL / 2), FRAME_H / 2,
               SEG_LENGTH, WALL, FRAME_H),
    ]

    # travessas inferiores nas extremidades (rigidez + face de colagem)
    for tx in (2.0, SEG_LENGTH - 2.0):
        solids.append(box_at(tx, 0, 1.5, 4.0, 2 * inner_half, 3.0))

    # abas de apoio da porta no lado livre (com vãos = passagem de água)
    tab_xs = (20.0, 155.0) if central else (20.0, 65.0, 110.0, 155.0)
    for tx in tab_xs:
        solids.append(box_at(tx, -(inner_half - LEDGE_W / 2),
                             door_rest_z - LEDGE_T / 2, 12.0, LEDGE_W, LEDGE_T))

    # travessas de apoio central da porta (parede a parede; água passa por
    # baixo) — porta de 50 mm apoiada no meio do vão = piso firme
    bridge_xs = (30.0, 148.0) if central else (45.0, 133.0)
    for bx in bridge_xs:
        solids.append(box_at(bx, 0, door_rest_z - LEDGE_T / 2,
                             8.0, 2 * inner_half, LEDGE_T))

    # castanhas da dobradiça (lado +y), ligadas à parede
    for xk in BASE_KNUCKLE_XS:
        solids.append(cyl_x(xk, hinge_y, hinge_z, KNUCKLE_LEN, HINGE_KNUCKLE_R))
        solids.append(box_at(xk, (hinge_y + inner_half) / 2, hinge_z,
                             KNUCKLE_LEN, inner_half - hinge_y, 5.0))

    if central:
        # paredes do poço do cesto
        for wx in (well_x0 - WELL_WALL / 2, well_x1 + WELL_WALL / 2):
            solids.append(box_at(wx, 0, FRAME_H / 2,
                                 WELL_WALL, 2 * inner_half, FRAME_H))
        # prateleiras onde a flange do cesto apoia (1.5 mm abaixo da porta)
        shelf_top = door_rest_z - 1.5
        for sx in (well_x0 + 1.5, well_x1 - 1.5):
            solids.append(box_at(sx, 0, shelf_top - LEDGE_T / 2, 3.0,
                                 2 * inner_half, LEDGE_T))

    # chave macho (x = fim) para colar no próximo segmento
    solids.append(box_at(SEG_LENGTH + 1.8, 0, 1.5, 4.0, 8.0, 3.0))

    part = solids[0] + solids[1:]
    cuts = [
        # chave fêmea (x = início)
        box_at(2.2, 0, 1.6, 4.4 + KEY_CLEARANCE, 8.0 + 2 * KEY_CLEARANCE,
               3.0 + 2 * KEY_CLEARANCE),
        # furo do pino de dobradiça, de ponta a ponta
        cyl_x(SEG_LENGTH / 2, hinge_y, hinge_z, SEG_LENGTH + 20, PIN_HOLE_R),
    ]
    # rebaixo no pé das duas paredes: encaixa por cima do relevo de 4 mm
    # da borda do canal — trava a base lateralmente e vira canal de cola.
    # O lábio interno restante (WALL - RELEVO_W) apoia na borda de 15 mm.
    for sign in (-1, 1):
        cuts.append(box_at(SEG_LENGTH / 2,
                           sign * (WIDTH / 2 - RELEVO_W / 2 + 0.5),
                           RELEVO_H / 2 - 0.05,
                           SEG_LENGTH + 10, RELEVO_W + 1.0, RELEVO_H + 0.1))
    part -= cuts
    return part


def build_door():
    """Porta que abre para cima, com piso massageador no topo. Fresta de
    2.5 mm no lado livre e vãos nas castanhas = ranhuras de vazão."""
    plate_w = hinge_y - door_free_edge
    solids = [box_at(SEG_LENGTH / 2, (hinge_y + door_free_edge) / 2, hinge_z,
                     SEG_LENGTH - 4.0, plate_w, DOOR_T)]

    # castanhas da porta, intercaladas com as da base
    for xk in DOOR_KNUCKLE_XS:
        solids.append(cyl_x(xk, hinge_y, hinge_z, KNUCKLE_LEN, HINGE_KNUCKLE_R))

    # domos massageadores/antiderrapantes (esferas semi-embutidas,
    # sobressaem BUMP_HEIGHT; ficam ~0.8 mm acima do nível do piso)
    top_z = door_rest_z + DOOR_T
    bump_center_z = top_z - (BUMP_SPHERE_R - BUMP_HEIGHT)
    notch_x, notch_y = SEG_LENGTH / 2, -9.0     # rebaixo do pé fica livre
    for row_i, by in enumerate(BUMP_ROWS_Y):
        bx = 14.0 + (BUMP_PITCH_X / 2 if row_i % 2 else 0.0)
        while bx <= SEG_LENGTH - 14.0:
            near_notch = abs(bx - notch_x) < 17.0 and abs(by - notch_y) < 7.0
            near_hinge_recess = by > 10.0 and any(
                abs(bx - xk) < KNUCKLE_LEN / 2 + BUMP_SPHERE_R + 1.5
                for xk in BASE_KNUCKLE_XS
            )
            if not (near_notch or near_hinge_recess):
                solids.append(Pos(bx, by, bump_center_z) * Sphere(BUMP_SPHERE_R))
            bx += BUMP_PITCH_X

    part = solids[0] + solids[1:]

    cuts = [
        # recortes onde ficam as castanhas da base
        box_at(xk, hinge_y - 0.2, hinge_z, KNUCKLE_LEN + 1.0, 5.6, DOOR_T + 6.0)
        for xk in BASE_KNUCKLE_XS
    ]
    # rebaixo para o dedo/pé levantar a porta
    cuts.append(box_at(notch_x, notch_y, FRAME_H - DOOR_RECESS - 0.35,
                       26.0, 6.0, 1.4))
    # furo do pino
    cuts.append(cyl_x(SEG_LENGTH / 2, hinge_y, hinge_z,
                      SEG_LENGTH + 20, PIN_HOLE_R))
    part -= cuts
    return part


def build_basket():
    """Cesto retentor de cabelos com selo d'água. Flange no topo apoia nas
    prateleiras do poço; alça em barra rente ao topo (a porta fecha por
    cima). Fundo fechado + ranhuras só na parte superior = a água fica
    represada embaixo e bloqueia o odor; cabelo fica retido nas ranhuras."""
    flange_l = WELL_LENGTH - 1.0                 # apoia nas prateleiras
    body_l = WELL_LENGTH - 6.0 - 0.6             # passa entre as prateleiras
    body_w = 2 * inner_half - 0.6
    z0 = -1.5                                    # base da flange

    part = box_at(0, 0, z0 + 0.75, flange_l, body_w, 1.5)                 # flange
    part += box_at(0, 0, z0 - BASKET_DEPTH / 2, body_l, body_w, BASKET_DEPTH)
    # cavidade (abre o topo através da flange, deixa fundo de 2 mm)
    cavity_h = BASKET_DEPTH + 1.5 - 2.0
    part -= box_at(0, 0, -cavity_h / 2,
                   body_l - 2 * BASKET_WALL, body_w - 2 * BASKET_WALL,
                   cavity_h + 1.0)

    # ranhuras verticais nas paredes longas, só acima do selo d'água
    slot_top = z0 - 2.0
    slot_bottom = z0 - (BASKET_DEPTH - WATER_SEAL_H)
    slot_h = slot_top - slot_bottom
    n = int((body_l - 10.0) // BASKET_SLOT_PITCH)
    for i in range(n + 1):
        sx = -(n * BASKET_SLOT_PITCH) / 2 + i * BASKET_SLOT_PITCH
        part -= box_at(sx, 0, (slot_top + slot_bottom) / 2,
                       BASKET_SLOT_W, body_w + 2.0, slot_h)

    # alça em barra, rente ao topo (dedos passam por baixo)
    part += box_at(0, 0, -1.0, 8.0, body_w, 2.0)
    return part


def save_stl(part, path):
    """Exporta e solda vértices quase-duplicados (os polos das esferas dos
    domos saem da OCC com vértices não soldados, o que abre a malha)."""
    export_stl(part, str(path))
    try:
        import trimesh
    except ImportError:
        return
    m = trimesh.load(str(path))
    if not m.is_watertight:
        m.merge_vertices(digits_vertex=4)
        m.update_faces(m.nondegenerate_faces())
        m.export(str(path))


if __name__ == "__main__":
    STL_DIR.mkdir(exist_ok=True)
    depth_needed = FRAME_H - (door_rest_z - 1.5 - BASKET_DEPTH)
    print(f"{TOTAL_LENGTH:.0f} mm em {SEG_COUNT} segmentos de {SEG_LENGTH:.0f} mm, "
          f"largura {WIDTH:.0f} mm, moldura {FRAME_H:.0f} mm (borda de "
          f"{EDGE_DEPTH:.0f} mm)")
    print(f"fundo do cesto: {depth_needed:.0f} mm abaixo do piso "
          f"(bolsão da saída: {POCKET_DEPTH:.0f} mm)")
    if depth_needed > POCKET_DEPTH - 2.0:
        print("  AVISO: reduza BASKET_DEPTH!")
    if WELL_LENGTH > POCKET_LENGTH - 4.0:
        print("  AVISO: poço maior que o bolsão da saída — reduza WELL_LENGTH!")

    exports = {
        "v2_segmento_base": build_base(central=False),
        "v2_segmento_central": build_base(central=True),
        "v2_porta": build_door(),
        "v2_cesto_retentor": build_basket(),
    }
    for name, part in exports.items():
        save_stl(part, STL_DIR / f"{name}.stl")
        print(f"exportado stl/{name}.stl")
