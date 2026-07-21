"""Ralo Oculto Inteligente V2 — 890 x 35 mm, 5 impressões, portas articuladas.

Conceito (do Rafael):
- Calha de 890 x 35 mm dividida em 5 segmentos de base (~178 mm cada),
  colados entre si na instalação (chaves de alinhamento macho/fêmea).
- Cada segmento tem uma PORTA que abre para cima para limpeza, girando
  sobre um pino de dobradiça — use um pedaço de filamento 1.75 mm de
  ~180 mm como pino (barato, inoxidável, substituível).
- O segmento CENTRAL (sobre a saída de esgoto) recebe um CESTO removível
  que retém cabelos. O fundo do cesto é fechado: ele segura uma coluna
  de ~14 mm de água que funciona como selo de odor (mini-sifão passivo,
  sem peça móvel). A água entra pelas ranhuras superiores, transborda
  por elas, e o cheiro não sobe.

Peças exportadas (execute este arquivo):
    stl/v2_segmento_base.stl     -> imprimir 4x  (PETG recomendado)
    stl/v2_segmento_central.stl  -> imprimir 1x
    stl/v2_porta.stl             -> imprimir 5x
    stl/v2_cesto_retentor.stl    -> imprimir 1x

Montagem: passe o pino de filamento pelo furo da dobradiça a partir da
extremidade do segmento ANTES de colar o segmento vizinho — depois de
colado, o pino fica travado.

MEDIR ANTES DE IMPRIMIR TUDO: profundidade livre sob o nível do piso
(o conjunto precisa de FRAME_H + BASKET_DEPTH = ~42 mm no segmento
central), diâmetro e posição do cano de saída. Imprima 1 segmento + 1
porta primeiro para validar os encaixes.
"""

from pathlib import Path

from build123d import Box, Cylinder, Pos, Rot, export_stl

# ---------------------------------------------------------------- parâmetros
TOTAL_LENGTH = 890.0
SEG_COUNT = 5
SEG_LENGTH = TOTAL_LENGTH / SEG_COUNT   # 178 mm — cabe em qualquer Bambu
WIDTH = 35.0

FRAME_H = 12.0          # altura da moldura da base
WALL = 2.0              # parede externa
LEDGE_W = 4.0           # aba de apoio da porta (lado livre)
LEDGE_T = 1.5
DOOR_T = 4.0
DOOR_RECESS = 0.5       # porta fica 0.5 mm abaixo do nível do piso
KEY_CLEARANCE = 0.35    # folga das chaves de alinhamento (ajuste com o gauge)

# dobradiça — pino = filamento 1.75 mm
PIN_HOLE_R = 1.15
HINGE_KNUCKLE_R_BASE = 2.5
HINGE_KNUCKLE_R_DOOR = 2.0
KNUCKLE_LEN = 14.0
BASE_KNUCKLE_XS = (20.0, 87.0, 154.0)
DOOR_KNUCKLE_XS = (53.5, 120.5)

# segmento central — poço e cesto
WELL_LENGTH = 62.0
WELL_WALL = 2.0
BASKET_DEPTH = 30.0     # abaixo da flange; confira a profundidade real!
BASKET_WALL = 1.6
BASKET_SLOT_W = 2.0
BASKET_SLOT_PITCH = 6.0
WATER_SEAL_H = 14.0     # parede cega inferior = coluna do selo d'água

STL_DIR = Path(__file__).resolve().parent.parent / "stl"

# ------------------------------------------------------------- derivados
inner_half = WIDTH / 2 - WALL                      # 15.5
door_rest_z = FRAME_H - DOOR_T - DOOR_RECESS       # 7.5
hinge_y = 11.2                                     # eixo da dobradiça
hinge_z = door_rest_z + DOOR_T / 2                 # 9.5
door_free_edge = -13.0                             # folga de 2.5 mm = ranhura de vazão
well_x0 = (SEG_LENGTH - WELL_LENGTH) / 2           # 58
well_x1 = well_x0 + WELL_LENGTH                    # 120


def box_at(cx, cy, cz, length, width, height):
    return Pos(cx, cy, cz) * Box(length, width, height)


def cyl_x(cx, cy, cz, length, radius):
    """Cilindro com eixo em X (eixo da dobradiça)."""
    return Pos(cx, cy, cz) * Rot(0, 90, 0) * Cylinder(radius, length)


def build_base(central=False):
    """Segmento da base: moldura em U aberto embaixo, abas de apoio da
    porta, castanhas da dobradiça e chaves de colagem nas extremidades."""
    # paredes laterais
    part = box_at(SEG_LENGTH / 2, WIDTH / 2 - WALL / 2, FRAME_H / 2,
                  SEG_LENGTH, WALL, FRAME_H)
    part += box_at(SEG_LENGTH / 2, -(WIDTH / 2 - WALL / 2), FRAME_H / 2,
                   SEG_LENGTH, WALL, FRAME_H)

    # travessas inferiores nas extremidades (rigidez + face de colagem)
    for tx in (2.0, SEG_LENGTH - 2.0):
        part += box_at(tx, 0, 1.5, 4.0, 2 * inner_half, 3.0)

    # abas de apoio da porta no lado livre (com vãos = passagem de água)
    tab_xs = (20.0, 155.0) if central else (20.0, 65.0, 110.0, 155.0)
    for tx in tab_xs:
        part += box_at(tx, -(inner_half - LEDGE_W / 2),
                       door_rest_z - LEDGE_T / 2, 12.0, LEDGE_W, LEDGE_T)

    # castanhas da dobradiça (lado +y), ligadas à parede
    for xk in BASE_KNUCKLE_XS:
        part += cyl_x(xk, hinge_y, hinge_z, KNUCKLE_LEN, HINGE_KNUCKLE_R_BASE)
        part += box_at(xk, (hinge_y + inner_half) / 2, 9.5,
                       KNUCKLE_LEN, inner_half - hinge_y, 5.0)

    if central:
        # paredes do poço do cesto
        for wx in (well_x0 - WELL_WALL / 2, well_x1 + WELL_WALL / 2):
            part += box_at(wx, 0, FRAME_H / 2, WELL_WALL, 2 * inner_half, FRAME_H)
        # prateleiras onde a flange do cesto apoia (topo 1.5 mm abaixo da porta)
        shelf_top = door_rest_z - 1.5
        for sx in (well_x0 + 1.5, well_x1 - 1.5):
            part += box_at(sx, 0, shelf_top - LEDGE_T / 2, 3.0,
                           2 * inner_half, LEDGE_T)

    # chave macho (x = fim) e fêmea (x = início) para colar os segmentos
    part += box_at(SEG_LENGTH + 1.8, 0, 1.5, 4.0, 8.0, 3.0)
    part -= box_at(2.2, 0, 1.6,
                   4.4 + KEY_CLEARANCE, 8.0 + 2 * KEY_CLEARANCE,
                   3.0 + 2 * KEY_CLEARANCE)

    # furo do pino de dobradiça, de ponta a ponta
    part -= cyl_x(SEG_LENGTH / 2, hinge_y, hinge_z, SEG_LENGTH + 20, PIN_HOLE_R)
    return part


def build_door():
    """Porta que abre para cima. Fresta de 2.5 mm no lado livre e vãos nas
    castanhas = ranhuras de vazão. Rebaixo raso para abrir com o pé."""
    plate_w = hinge_y - door_free_edge                       # 24.2
    part = box_at(SEG_LENGTH / 2, (hinge_y + door_free_edge) / 2, hinge_z,
                  SEG_LENGTH - 4.0, plate_w, DOOR_T)

    # castanhas da porta, intercaladas com as da base
    for xk in DOOR_KNUCKLE_XS:
        part += cyl_x(xk, hinge_y, hinge_z, KNUCKLE_LEN, HINGE_KNUCKLE_R_DOOR)

    # recortes onde ficam as castanhas da base
    for xk in BASE_KNUCKLE_XS:
        part -= box_at(xk, 11.0, hinge_z, KNUCKLE_LEN + 1.0, 5.6, 6.0)

    # rebaixo para o dedo/pé levantar a porta
    part -= box_at(SEG_LENGTH / 2, -9.0, FRAME_H - DOOR_RECESS - 0.35,
                   26.0, 6.0, 1.4)

    # furo do pino
    part -= cyl_x(SEG_LENGTH / 2, hinge_y, hinge_z, SEG_LENGTH + 20, PIN_HOLE_R)
    return part


def build_basket():
    """Cesto retentor de cabelos com selo d'água. Flange no topo apoia nas
    prateleiras do poço; alça em barra rente ao topo (a porta fecha por
    cima). Fundo fechado + ranhuras só na metade superior = a água fica
    represada embaixo e bloqueia o odor; cabelo fica retido nas ranhuras."""
    flange_l = WELL_LENGTH - 1.0                 # 61 — apoia nas prateleiras
    body_l = WELL_LENGTH - 6.0 - 0.6             # passa entre as prateleiras
    body_w = 2 * inner_half - 0.6                # 30.4
    z0 = -1.5                                    # base da flange

    part = box_at(0, 0, z0 + 0.75, flange_l, body_w, 1.5)                 # flange
    part += box_at(0, 0, z0 - BASKET_DEPTH / 2, body_l, body_w, BASKET_DEPTH)
    # cavidade (abre o topo através da flange, deixa fundo de 2 mm)
    cavity_h = BASKET_DEPTH + 1.5 - 2.0
    part -= box_at(0, 0, -cavity_h / 2,
                   body_l - 2 * BASKET_WALL, body_w - 2 * BASKET_WALL, cavity_h + 1.0)

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


if __name__ == "__main__":
    STL_DIR.mkdir(exist_ok=True)
    print(f"{TOTAL_LENGTH:.0f} mm em {SEG_COUNT} segmentos de {SEG_LENGTH:.0f} mm")
    print(f"profundidade necessária no centro: {FRAME_H + BASKET_DEPTH:.0f} mm — MEÇA!")

    exports = {
        "v2_segmento_base": build_base(central=False),
        "v2_segmento_central": build_base(central=True),
        "v2_porta": build_door(),
        "v2_cesto_retentor": build_basket(),
    }
    for name, part in exports.items():
        export_stl(part, str(STL_DIR / f"{name}.stl"))
        print(f"exportado stl/{name}.stl")
