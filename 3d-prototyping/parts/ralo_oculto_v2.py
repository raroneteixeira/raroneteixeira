"""Ralo Oculto Inteligente V3 — 890 x 50 mm, registro acionado com o pé.

Conceito (do Rafael):
- Calha de 890 x 50 mm dividida em 5 segmentos de base (~178 mm cada),
  colados entre si na instalação (chaves de alinhamento macho/fêmea).
  Perfil real do canal: bordas 15 mm com relevo de 4 mm (a parede da
  base tem rebaixo que encaixa por cima), calha central 30 mm, bolsão
  da saída ~73 mm com cano de 40 mm.
- Cada segmento tem uma PORTA que abre para cima para limpeza, girando
  sobre pino de filamento 1.75 mm (~180 mm). Topo das portas = PISO
  MASSAGEADOR: domos arredondados antiderrapantes.
- CÂMARA CENTRAL (v2_camara_registro): caixa que assenta no bolsão da
  saída, com janelas de entrada nas duas extremidades (a água que corre
  pela calha entra por elas), fundo com 3 ranhuras sobre o cano e saia
  perimetral que sela no fundo do bolsão (assente com silicone).
- REGISTRO DESLIZANTE (v2_registro_deslizante): placa que desliza 8 mm
  sobre o fundo da câmara. Ranhuras alinhadas = ABERTO; deslizou =
  FECHADO (bloqueia odor e bichos). A haste sobe por uma fenda na porta
  central, rente ao piso: empurre com o dedão do pé. Sem molas, folgas
  generosas — não trava com água nem cabelo.
- CESTO RETENTOR (v2_cesto_retentor): peneira removível dentro do poço,
  paredes e fundo ranhurados, retém cabelo da água que cai por cima.
  Para limpar: abre a porta central, puxa pela alça.

Peças exportadas (execute este arquivo):
    stl/v2_segmento_base.stl       -> imprimir 4x  (PETG recomendado)
    stl/v2_segmento_central.stl    -> imprimir 1x
    stl/v2_porta.stl               -> imprimir 4x  (6 paredes, 40% infill)
    stl/v2_porta_central.stl       -> imprimir 1x  (tem a fenda da haste)
    stl/v2_camara_registro.stl     -> imprimir 1x  (saia p/ baixo)
    stl/v2_registro_deslizante.stl -> imprimir 1x  (haste p/ cima)
    stl/v2_cesto_retentor.stl      -> imprimir 1x

Montagem: câmara no bolsão sobre um cordão de silicone na saia ->
registro dentro dela (haste na fenda -x) -> segmentos colados por cima
(pino de filamento na dobradiça ANTES de colar o vizinho) -> cesto no
poço -> portas.

Imprima 1 segmento + 1 porta primeiro para validar encaixes.
"""

from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot, Sphere, export_stl

# ---------------------------------------------------------------- parâmetros
TOTAL_LENGTH = 890.0
SEG_COUNT = 5
SEG_LENGTH = TOTAL_LENGTH / SEG_COUNT   # 178 mm — cabe em qualquer Bambu
WIDTH = 49.0            # boca do canal = 50; 0.5 mm de folga por lado

# perfil real do canal (fotos de 2026-07-21):
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

# segmento central — poço, câmara, registro e cesto
WELL_LENGTH = 62.0      # < POCKET_LENGTH (73)
WELL_WALL = 2.0

SUMP_L = 70.0           # câmara: comprimento externo (cabe no bolsão de 73)
SUMP_W = 44.0           # largura externa (confirme a largura do bolsão!)
SUMP_WALL = 2.0
SUMP_SLAB_T = 2.0       # fundo da câmara
SKIRT_H = 4.0           # saia que sela no fundo do bolsão (silicone)
FLOW_SLOT_W = 7.0       # 3 ranhuras de vazão no fundo
FLOW_SLOT_L = 28.0
FLOW_SLOT_PITCH = 16.0

SLIDER_T = 2.5          # registro deslizante
SLIDER_TRAVEL = 8.0     # curso: aberto <-> fechado
TAB_W = 6.0             # haste que sobe pela fenda da porta

BASKET_WALL = 1.6
BASKET_SLOT_W = 2.0
BASKET_SLOT_PITCH = 6.0

STL_DIR = Path(__file__).resolve().parent.parent / "stl"

# ------------------------------------------------------------- derivados
inner_half = WIDTH / 2 - WALL                      # 20.0
door_rest_z = FRAME_H - DOOR_T - DOOR_RECESS       # 9.5
hinge_y = inner_half - 4.3                         # 15.7 — eixo da dobradiça
hinge_z = door_rest_z + DOOR_T / 2                 # 12.0
door_free_edge = -(inner_half - 2.5)               # fresta de 2.5 mm = vazão
well_x0 = (SEG_LENGTH - WELL_LENGTH) / 2           # 58
well_x1 = well_x0 + WELL_LENGTH                    # 120
shelf_top = door_rest_z - 1.5                      # 8.0 — apoio do cesto
sump_x0 = (SEG_LENGTH - SUMP_L) / 2                # 54
sump_x1 = sump_x0 + SUMP_L                         # 124
slab_top = -FRAME_H + POCKET_DEPTH - SKIRT_H - SUMP_SLAB_T - 0.5   # -8.5... via:
slab_top = -(SUMP_SLAB_T + SKIRT_H + 0.5) - 2.0    # explícito abaixo
SLAB_TOP_Z = -8.5       # topo do fundo da câmara
SLAB_BOT_Z = SLAB_TOP_Z - SUMP_SLAB_T              # -10.5
SKIRT_BOT_Z = SLAB_BOT_Z - SKIRT_H                 # -14.5 (bolsão: -15)
SLIDER_TOP_Z = SLAB_TOP_Z + SLIDER_T               # -6.0
TAB_TOP_Z = FRAME_H - DOOR_RECESS                  # 14.5 — rente ao piso
SLOT_XS = (89.0 - FLOW_SLOT_PITCH, 89.0, 89.0 + FLOW_SLOT_PITCH)  # 73/89/105
TAB_X_OPEN = 71.0       # centro da haste com o registro ABERTO
DOOR_SLOT_X = 67.0      # centro da fenda na porta central (curso -8 = fechar)

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
    apoio da porta, castanhas da dobradiça e chaves de colagem. O pé das
    paredes tem rebaixo que encaixa por cima do relevo de 4 mm da borda."""
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
    # baixo) — porta de 49 mm apoiada no meio do vão = piso firme
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
        # prateleira +x integral onde a flange do cesto apoia
        solids.append(box_at(well_x1 - 1.5, 0, shelf_top - LEDGE_T / 2,
                             3.0, 2 * inner_half, LEDGE_T))
        # prateleira -x parcial: vão central livre p/ a haste do registro
        for sy in (-14.0, 14.0):
            solids.append(box_at(well_x0 + 1.5, sy, shelf_top - LEDGE_T / 2,
                                 3.0, 12.0, LEDGE_T))

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
    for sign in (-1, 1):
        cuts.append(box_at(SEG_LENGTH / 2,
                           sign * (WIDTH / 2 - RELEVO_W / 2 + 0.5),
                           RELEVO_H / 2 - 0.05,
                           SEG_LENGTH + 10, RELEVO_W + 1.0, RELEVO_H + 0.1))
    part -= cuts
    return part


def build_door(with_slot=False):
    """Porta que abre para cima, com piso massageador no topo. A porta
    central (with_slot=True) tem a fenda por onde sobe a haste do
    registro — empurre a haste com o dedão: 8 mm de curso."""
    plate_w = hinge_y - door_free_edge
    solids = [box_at(SEG_LENGTH / 2, (hinge_y + door_free_edge) / 2, hinge_z,
                     SEG_LENGTH - 4.0, plate_w, DOOR_T)]

    # castanhas da porta, intercaladas com as da base
    for xk in DOOR_KNUCKLE_XS:
        solids.append(cyl_x(xk, hinge_y, hinge_z, KNUCKLE_LEN, HINGE_KNUCKLE_R))

    # domos massageadores/antiderrapantes
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
            near_slot = with_slot and (
                abs(bx - DOOR_SLOT_X) < 13.0 and abs(by) < 9.0
            )
            if not (near_notch or near_hinge_recess or near_slot):
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
    # fenda da haste do registro (só na porta central)
    if with_slot:
        cuts.append(box_at(DOOR_SLOT_X, 0, hinge_z, 18.0, 10.0, DOOR_T + 8.0))
    # furo do pino
    cuts.append(cyl_x(SEG_LENGTH / 2, hinge_y, hinge_z,
                      SEG_LENGTH + 20, PIN_HOLE_R))
    part -= cuts
    return part


def build_sump():
    """Câmara central: assenta no bolsão da saída, sob o segmento central.
    Janelas nas extremidades recebem a água da calha; o fundo tem 3
    ranhuras sobre o cano; a saia perimetral sela no fundo do bolsão com
    silicone. Pilares internos apoiam a flange do cesto; abas laterais
    retêm o registro deslizante."""
    cx = SEG_LENGTH / 2
    solids = [
        # fundo
        box_at(cx, 0, SLAB_TOP_Z - SUMP_SLAB_T / 2, SUMP_L, SUMP_W, SUMP_SLAB_T),
        # saia perimetral (sela no fundo do bolsão)
        box_at(cx, 0, (SLAB_BOT_Z + SKIRT_BOT_Z) / 2, SUMP_L, SUMP_W, SKIRT_H),
        # paredes laterais e de extremidade (do fundo até z=0, base da moldura)
        box_at(cx, SUMP_W / 2 - 1, SLAB_TOP_Z / 2, SUMP_L, 2.0, -SLAB_TOP_Z),
        box_at(cx, -(SUMP_W / 2 - 1), SLAB_TOP_Z / 2, SUMP_L, 2.0, -SLAB_TOP_Z),
        box_at(sump_x0 + 1, 0, SLAB_TOP_Z / 2, 2.0, SUMP_W, -SLAB_TOP_Z),
        box_at(sump_x1 - 1, 0, SLAB_TOP_Z / 2, 2.0, SUMP_W, -SLAB_TOP_Z),
    ]
    # abas que retêm o registro (o registro desliza por baixo delas)
    for sign in (-1, 1):
        solids.append(box_at(cx, sign * 18.5, SLIDER_TOP_Z + 0.5, 62.0, 3.0, 0.6))
    # pilares que apoiam a flange do cesto no lado -x
    for sign in (-1, 1):
        solids.append(box_at(73.0, sign * 18.2, (SLAB_TOP_Z + shelf_top) / 2,
                             4.0, 3.0, shelf_top - SLAB_TOP_Z))

    part = solids[0] + solids[1:]
    cuts = [
        # vão interno da saia (vira a moldura de vedação)
        box_at(cx, 0, (SLAB_BOT_Z + SKIRT_BOT_Z) / 2,
               SUMP_L - 5.0, SUMP_W - 5.0, SKIRT_H + 1.0),
        # janelas de entrada da água nas duas extremidades
        box_at(sump_x0 + 1, 0, -3.5, 3.0, 32.0, 5.0),
        box_at(sump_x1 - 1, 0, -3.5, 3.0, 32.0, 5.0),
    ]
    # 3 ranhuras de vazão no fundo, sobre o cano de 40 mm
    for sx in SLOT_XS:
        cuts.append(box_at(sx, 0, SLAB_TOP_Z - SUMP_SLAB_T / 2,
                           FLOW_SLOT_W, FLOW_SLOT_L, SUMP_SLAB_T + 1.0))
    part -= cuts
    return part


def build_slider():
    """Registro deslizante: desliza sobre o fundo da câmara. Construído na
    posição ABERTA (ranhuras alinhadas); empurrar a haste 8 mm no sentido
    -x FECHA o ralo. Haste rente ao piso, acionada com o dedão."""
    cx = SEG_LENGTH / 2
    plate_z = SLAB_TOP_Z + SLIDER_T / 2
    solids = [
        box_at(cx, 0, plate_z, 48.0, 36.0, SLIDER_T),
        # haste que sobe pela fenda da porta central (topo rente ao piso)
        box_at(TAB_X_OPEN, 0, (SLIDER_TOP_Z - SLIDER_T + TAB_TOP_Z) / 2,
               8.0, TAB_W, TAB_TOP_Z - (SLIDER_TOP_Z - SLIDER_T)),
        # reforço na base da haste (do topo da placa para cima)
        box_at(TAB_X_OPEN, 0, SLIDER_TOP_Z + 5.0, 8.0, 10.0, 10.0),
    ]
    part = solids[0] + solids[1:]
    cuts = []
    # ranhuras (coincidem com as do fundo da câmara na posição aberta)
    for sx in SLOT_XS:
        cuts.append(box_at(sx, 0, plate_z, FLOW_SLOT_W, FLOW_SLOT_L, SLIDER_T + 2.0))
    # recortes de canto p/ passar pelos pilares do cesto durante o curso
    for sign in (-1, 1):
        cuts.append(box_at(69.0, sign * 18.0, plate_z, 15.0, 5.0, SLIDER_T + 2.0))
    part -= cuts
    return part


def build_basket():
    """Cesto retentor de cabelos: peneira removível com paredes e fundo
    ranhurados. Flange apoia na prateleira +x e nos pilares da câmara;
    o recorte -x da flange deixa a haste do registro passar. Alça em
    barra rente ao topo (a porta fecha por cima)."""
    bcx = 96.0              # corpo deslocado p/ +x, longe da haste
    solids = [
        box_at(bcx, 0, shelf_top + 0.75, 50.0, 38.0, 1.5),   # flange
        box_at(bcx, 0, 1.5, 40.0, 36.0, 13.0),               # corpo (z -5..8)
    ]
    part = solids[0] + solids[1:]
    cuts = [
        # cavidade (abre o topo através da flange, deixa fundo de 2 mm)
        box_at(bcx, 0, 6.0, 40.0 - 2 * BASKET_WALL, 36.0 - 2 * BASKET_WALL, 18.0),
        # recorte da flange p/ a haste do registro
        box_at(66.0, 0, shelf_top + 0.75, 23.0, 12.0, 2.5),
    ]
    # ranhuras verticais nas paredes longas
    sx = 80.0
    while sx <= 112.0:
        cuts.append(box_at(sx, 0, 2.5, BASKET_SLOT_W, 40.0 + 2.0, 10.0))
        sx += BASKET_SLOT_PITCH
    # ranhuras verticais nas paredes de extremidade
    for sy in (-15.0, -9.0, -3.0, 3.0, 9.0, 15.0):
        cuts.append(box_at(bcx, sy, 2.5, 44.0 + 2.0, BASKET_SLOT_W, 10.0))
    # ranhuras no fundo
    sx = 80.0
    while sx <= 112.0:
        cuts.append(box_at(sx, 0, -4.0, BASKET_SLOT_W, 28.0, 2.4))
        sx += BASKET_SLOT_PITCH
    part -= cuts
    # alça em barra, rente ao topo (dedos passam por baixo)
    part += box_at(bcx, 0, shelf_top + 0.5, 8.0, 36.0, 2.0)
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
    print(f"{TOTAL_LENGTH:.0f} mm em {SEG_COUNT} segmentos de {SEG_LENGTH:.0f} mm, "
          f"largura {WIDTH:.0f} mm, moldura {FRAME_H:.0f} mm")
    depth_needed = FRAME_H - SKIRT_BOT_Z - 0.5
    print(f"câmara chega a {depth_needed:.1f} mm abaixo do piso "
          f"(bolsão: {POCKET_DEPTH:.0f} mm)")
    door_gap_area = SEG_COUNT * 2.5 * (SEG_LENGTH - 8) / 100.0
    slot_area = len(SLOT_XS) * FLOW_SLOT_W * FLOW_SLOT_L / 100.0
    pipe_area = 3.1416 * (OUTLET_D / 2) ** 2 / 100.0
    print(f"vazão — frestas das portas: {door_gap_area:.1f} cm² | "
          f"ranhuras do registro: {slot_area:.1f} cm² | "
          f"cano 40 mm: {pipe_area:.1f} cm²")

    exports = {
        "v2_segmento_base": build_base(central=False),
        "v2_segmento_central": build_base(central=True),
        "v2_porta": build_door(),
        "v2_porta_central": build_door(with_slot=True),
        "v2_camara_registro": build_sump(),
        "v2_registro_deslizante": build_slider(),
        "v2_cesto_retentor": build_basket(),
    }
    for name, part in exports.items():
        save_stl(part, STL_DIR / f"{name}.stl")
        print(f"exportado stl/{name}.stl")
