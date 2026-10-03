# ============================================================
#  THE LEGEND OF MOISES
#  Aventura estilo NES hecha con Python y pygame
# ============================================================
#  Controles:
#    Flechas o WASD ..... moverse
#    ESPACIO o Z ........ usar la espada
#    ENTER .............. empezar / continuar
#    M .................. sonido si / no
#    ESC ................ salir
#
#  Objetivo: busca la espada en la cueva, explora el mapa,
#  vence al guardian del norte y recupera el Triangulo Dorado.
# ============================================================

import math
import random
import sys
from array import array

import pygame

# ------------------------------------------------------------
# CONFIGURACION
# ------------------------------------------------------------
# El juego se dibuja en un lienzo chico (256 x 240, como el NES)
# y luego se agranda. Asi se ve con pixeles grandes y nitidos.

ANCHO, ALTO = 256, 240
TILE = 16                 # cada cuadro del mapa mide 16 x 16
HUD = 64                  # barra negra de arriba
COLS, FILAS = 16, 11      # cuadros por pantalla
CAMPO_ALTO = FILAS * TILE  # 176 pixeles de zona de juego
FPS = 60

# El sonido es opcional: si esta instalacion de pygame no trae el modulo
# de audio (mixer), el juego funciona igual, solo que en silencio.
AUDIO = {"activo": True, "silencio": False}
try:
    import pygame.mixer
    pygame.mixer.pre_init(22050, -16, 1, 512)
except (NotImplementedError, ImportError, pygame.error):
    AUDIO["activo"] = False

pygame.init()

_info = pygame.display.Info()
ESCALA = max(2, min(4, (_info.current_h - 130) // ALTO))

ventana = pygame.display.set_mode((ANCHO * ESCALA, ALTO * ESCALA))
pygame.display.set_caption("The Legend of Moises")
lienzo = pygame.Surface((ANCHO, ALTO))
reloj = pygame.time.Clock()

# ------------------------------------------------------------
# COLORES (paleta inspirada en el NES)
# ------------------------------------------------------------

NEGRO = (0, 0, 0)
BLANCO = (252, 252, 252)
ARENA = (252, 216, 168)
VERDE = (0, 168, 0)
VERDE_OSCURO = (0, 88, 0)
CAFE = (200, 76, 12)
CAFE_OSCURO = (88, 32, 0)
AGUA = (60, 108, 252)
AGUA_CLARA = (148, 188, 252)
ROJO = (216, 40, 0)
ROSA = (252, 188, 176)
GRIS = (116, 116, 116)
AZUL_HUD = (32, 56, 236)
DORADO = (228, 172, 56)
DORADO_CLARO = (252, 224, 120)

DIRS = {
    "arriba": (0, -1),
    "abajo": (0, 1),
    "izquierda": (-1, 0),
    "derecha": (1, 0),
}

# ------------------------------------------------------------
# SONIDO: se genera con matematica, sin archivos de audio
# ------------------------------------------------------------

SONIDOS = {}


def crear_sonido(notas, volumen=0.22, ruido=False):
    """notas = lista de (frecuencia en Hz, duracion en segundos)."""
    muestras = array("h")
    for frecuencia, duracion in notas:
        total = int(22050 * duracion)
        for i in range(total):
            if frecuencia <= 0:
                valor = 0.0
            elif ruido:
                valor = random.uniform(-1, 1)
            else:
                fase = (i * frecuencia / 22050) % 1
                valor = 1.0 if fase < 0.5 else -1.0
            apagado = 1 - 0.7 * i / total              # la nota se va apagando
            final = min(1.0, (total - i) / 200)          # evita "clics"
            muestras.append(int(valor * 32767 * volumen * apagado * final))
    return pygame.mixer.Sound(buffer=muestras.tobytes())


def preparar_sonidos():
    if not AUDIO["activo"]:
        return
    try:
        SONIDOS["espada"] = crear_sonido([(900, 0.03), (650, 0.03), (420, 0.05)])
        SONIDOS["rayo"] = crear_sonido([(1400, 0.04), (1100, 0.04), (900, 0.06)])
        SONIDOS["golpe"] = crear_sonido([(220, 0.04), (150, 0.07)])
        SONIDOS["muere"] = crear_sonido([(300, 0.05), (200, 0.05), (120, 0.1)], ruido=True)
        SONIDOS["herido"] = crear_sonido([(180, 0.08), (110, 0.12)])
        SONIDOS["escudo"] = crear_sonido([(1200, 0.03), (1600, 0.05)])
        SONIDOS["gema"] = crear_sonido([(1320, 0.05), (1760, 0.09)])
        SONIDOS["corazon"] = crear_sonido([(880, 0.05), (1175, 0.09)])
        SONIDOS["texto"] = crear_sonido([(760, 0.02)], volumen=0.12)
        SONIDOS["inicio"] = crear_sonido([(660, 0.08), (880, 0.08), (1320, 0.25)])
        SONIDOS["objeto"] = crear_sonido(
            [(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.4)])
        SONIDOS["gameover"] = crear_sonido(
            [(392, 0.2), (330, 0.2), (262, 0.2), (196, 0.6)])
        SONIDOS["victoria"] = crear_sonido(
            [(523, 0.15), (659, 0.15), (784, 0.15), (1047, 0.15),
             (784, 0.15), (1047, 0.6)])
        # Melodia original para la pantalla de titulo
        SONIDOS["musica"] = crear_sonido(
            [(294, 0.25), (349, 0.25), (440, 0.5), (587, 0.75), (523, 0.25),
             (440, 0.5), (466, 0.25), (392, 0.25), (440, 1.0), (0, 0.25),
             (349, 0.25), (440, 0.25), (523, 0.5), (587, 0.5), (659, 0.25),
             (587, 0.25), (523, 0.5), (440, 0.5), (294, 1.0), (0, 0.5)],
            volumen=0.12)
    except (NotImplementedError, ImportError, pygame.error):
        AUDIO["activo"] = False


def sonar(nombre, repetir=False):
    if AUDIO["activo"] and not AUDIO["silencio"] and nombre in SONIDOS:
        SONIDOS[nombre].play(loops=-1 if repetir else 0)


def parar(nombre):
    if AUDIO["activo"] and nombre in SONIDOS:
        SONIDOS[nombre].stop()


# ------------------------------------------------------------
# LETRAS: fuente de pixeles propia (5 x 7)
# ------------------------------------------------------------

LETRAS = {
    " ": "00000 00000 00000 00000 00000 00000 00000",
    "A": "01110 10001 10001 11111 10001 10001 10001",
    "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110",
    "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111",
    "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01110",
    "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110",
    "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001",
    "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001",
    "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110",
    "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101",
    "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110",
    "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110",
    "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 11011 10001",
    "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100",
    "Z": "11111 00001 00010 00100 01000 10000 11111",
    "0": "01110 10001 10011 10101 11001 10001 01110",
    "1": "00100 01100 00100 00100 00100 00100 01110",
    "2": "01110 10001 00001 00010 00100 01000 11111",
    "3": "11110 00001 00001 01110 00001 00001 11110",
    "4": "00010 00110 01010 10010 11111 00010 00010",
    "5": "11111 10000 11110 00001 00001 10001 01110",
    "6": "00110 01000 10000 11110 10001 10001 01110",
    "7": "11111 00001 00010 00100 01000 01000 01000",
    "8": "01110 10001 10001 01110 10001 10001 01110",
    "9": "01110 10001 10001 01111 00001 00010 01100",
    "-": "00000 00000 00000 11111 00000 00000 00000",
    "!": "00100 00100 00100 00100 00100 00000 00100",
    ".": "00000 00000 00000 00000 00000 01100 01100",
}

_letras_listas = {}


def letra(caracter, color, escala):
    clave = (caracter, color, escala)
    if clave not in _letras_listas:
        superficie = pygame.Surface((5 * escala, 7 * escala), pygame.SRCALPHA)
        filas = LETRAS.get(caracter, LETRAS[" "]).split()
        for y, bits in enumerate(filas):
            for x, bit in enumerate(bits):
                if bit == "1":
                    superficie.fill(color, (x * escala, y * escala, escala, escala))
        _letras_listas[clave] = superficie
    return _letras_listas[clave]


def ancho_texto(cadena, escala=1):
    return len(cadena) * 6 * escala - escala


def texto(sup, cadena, x, y, color=BLANCO, escala=1):
    for caracter in cadena:
        sup.blit(letra(caracter, color, escala), (x, y))
        x += 6 * escala


def texto_centrado(sup, cadena, y, color=BLANCO, escala=1):
    texto(sup, cadena, (ANCHO - ancho_texto(cadena, escala)) // 2, y, color, escala)


# ------------------------------------------------------------
# SPRITES: cada dibujo es una cuadricula de letras.
# Cada letra es un color; el punto es transparente.
# ------------------------------------------------------------

def crear_sprite(filas, paleta):
    superficie = pygame.Surface((len(filas[0]), len(filas)), pygame.SRCALPHA)
    for y, fila in enumerate(filas):
        for x, c in enumerate(fila):
            if c in paleta:
                superficie.set_at((x, y), paleta[c])
    return superficie


PALETA_HEROE = {"G": (128, 208, 16), "S": (252, 152, 56), "B": (200, 76, 12)}

HEROE_ABAJO = [
    "................",
    ".....GGGGGG.....",
    "....GGGGGGGG....",
    "...BGBBBBBBGB...",
    "...BBSSSSSSBB...",
    "...SSBSSSSBSS...",
    "...SSBSSSSBSS...",
    "....SSSSSSSS....",
    "..BBBGSSSSGGG...",
    ".BSSSBGGGGGGSS..",
    ".BSBSBGBBBBGSS..",
    ".BSSSBGGGGGGG...",
    ".BBBBBGGGGGGG...",
    "..BBBGGG.GGG....",
    ".....BB...BB....",
    "....BBB...BBB...",
]

HEROE_ARRIBA = [
    "................",
    ".....GGGGGG.....",
    "....GGGGGGGG....",
    "...GGGGGGGGGG...",
    "...BGGGGGGGGB...",
    "...BBGGGGGGBB...",
    "...SBBBBBBBBS...",
    "....BBBBBBBB....",
    "...GGGGGGGGGG...",
    "..SSGGGGGGGGSS..",
    "..SSGGBBBBGGSS..",
    "....GGGGGGGG....",
    "....GGGGGGGG....",
    "....GGG..GGG....",
    "....BB....BB....",
    "...BBB....BBB...",
]

HEROE_DERECHA = [
    "................",
    "....GGGGGG......",
    "...GGGGGGGG.....",
    "..GGGGBBBBBB....",
    ".GGG.BBSSSSS....",
    ".....BBSSBSS....",
    ".....BSSSSSSS...",
    "......SSSSSS....",
    "....GGGGSS......",
    "...GGGGGBBBB....",
    "...GGSSGBSSB....",
    "...GGSSGBSSB....",
    "...GGGGGBBBB....",
    "....GGGGGG......",
    "....BB..BB......",
    "....BBB.BBB.....",
]

HEROE = {
    "abajo": crear_sprite(HEROE_ABAJO, PALETA_HEROE),
    "arriba": crear_sprite(HEROE_ARRIBA, PALETA_HEROE),
    "derecha": crear_sprite(HEROE_DERECHA, PALETA_HEROE),
}
HEROE["izquierda"] = pygame.transform.flip(HEROE["derecha"], True, False)

ESPADA_FILAS = [
    "...W...",
    "..WWW..",
    "..WWW..",
    "..WWW..",
    "..WWW..",
    "..WWW..",
    "..WWW..",
    "..WWW..",
    "..WWW..",
    "..WWW..",
    "..WWW..",
    ".GGGGG.",
    "GGGGGGG",
    "...B...",
    "...B...",
    "...B...",
]


def crear_espada(paleta):
    base = crear_sprite(ESPADA_FILAS, paleta)
    return {
        "arriba": base,
        "abajo": pygame.transform.flip(base, False, True),
        "derecha": pygame.transform.rotate(base, -90),
        "izquierda": pygame.transform.rotate(base, 90),
    }


ESPADA = crear_espada({"W": BLANCO, "G": (128, 208, 16), "B": CAFE})
ESPADA_RAYO = crear_espada({"W": AGUA_CLARA, "G": BLANCO, "B": AGUA})

PULPO_FILAS = [
    "................",
    ".....RRRRRR.....",
    "...RRRRRRRRRR...",
    "..RRRRRRRRRRRR..",
    "..RRWWRRRRWWRR..",
    "..RRWKRRRRKWRR..",
    "..RRRRRRRRRRRR..",
    "...RRRRRRRRRR...",
    "..RRRRRKKRRRRR..",
    ".RRRRRRKKRRRRRR.",
    ".RR.RRRRRRRR.RR.",
    ".RR..RRRRRR..RR.",
    "......RRRR......",
    "....RR....RR....",
    "...RR......RR...",
    "................",
]


def crear_pulpo(color):
    base = crear_sprite(PULPO_FILAS, {"R": color, "W": BLANCO, "K": NEGRO})
    return {
        "abajo": base,
        "arriba": pygame.transform.flip(base, False, True),
        "derecha": pygame.transform.rotate(base, 90),
        "izquierda": pygame.transform.rotate(base, -90),
    }


PULPO_ROJO = crear_pulpo(ROJO)
PULPO_AZUL = crear_pulpo((0, 88, 248))

SALTARIN = crear_sprite([
    "................",
    "................",
    "......OOOO......",
    "....OOOOOOOO....",
    "...OOWKOOKWOO...",
    "...OOOOOOOOOO...",
    "..O.OOOOOOOO.O..",
    ".O...OOOOOO...O.",
    ".O..O.O..O.O..O.",
    "O...O......O...O",
    "O..O........O..O",
    "...O........O...",
    "..O..........O..",
    "................",
    "................",
    "................",
], {"O": (0, 132, 168), "W": BLANCO, "K": NEGRO})

JEFE = pygame.transform.scale(crear_sprite([
    "..K..........K..",
    "..KK........KK..",
    "..KPK......KPK..",
    "..KPPKKKKKKPPK..",
    ".KPPPPPPPPPPPPK.",
    ".KPPPWWWWWWPPPK.",
    "KPPPWWKKKKWWPPPK",
    "KPPPWWKRRKWWPPPK",
    "KPPPPWWKKWWPPPPK",
    "KPPPPPWWWWPPPPPK",
    "KPPKPPPPPPPPKPPK",
    "KPPKWKWKWKWKKPPK",
    ".KPPKKKKKKKKPPK.",
    ".KPPPPPPPPPPPPK.",
    "..KPPKK..KKPPK..",
    "..KKK......KKK..",
], {"P": (148, 0, 188), "W": BLANCO, "K": NEGRO, "R": ROJO}), (32, 32))

ROCA = crear_sprite([
    "..KKKK..",
    ".KRRRRK.",
    "KRRSRRRK",
    "KRSRRRRK",
    "KRRRRRRK",
    "KRRRRKRK",
    ".KRRRRK.",
    "..KKKK..",
], {"K": CAFE_OSCURO, "R": CAFE, "S": ARENA})

VIEJO = crear_sprite([
    "......SSSS......",
    ".....SSSSSS.....",
    ".....SKSSKS.....",
    ".....SSSSSS.....",
    "....WWWWWWWW....",
    "...RWWWWWWWWR...",
    "..RRRWWWWWWRRR..",
    "..RRRRWWWWRRRR..",
    "..RRRRRWWRRRRR..",
    "..SRRRRRRRRRRS..",
    "..SRRRRRRRRRRS..",
    "...RRRRRRRRRR...",
    "...RRRRRRRRRR...",
    "...RRRRRRRRRR...",
    "...RRRRRRRRRR...",
    "..RRRRRRRRRRRR..",
], {"S": (252, 152, 56), "W": BLANCO, "R": ROJO, "K": NEGRO})

FUEGO = crear_sprite([
    "................",
    "......O.........",
    ".....OO....O....",
    ".....OOO..OO....",
    "..O..OOOO.OO....",
    "..OO.OOOOOOO..O.",
    "..OOOOOYYOOO.OO.",
    "..OOOOYYYYOOOOO.",
    ".OOOOYYYYYYOOOO.",
    ".OOOYYYWWYYYOOO.",
    ".OOOYYWWWWYYOOO.",
    ".OOOYYWWWWYYOOO.",
    "..OOOYYWWYYOOO..",
    "..OOOOYYYYOOOO..",
    "...OOOOOOOOOO...",
    ".....OOOOOO.....",
], {"O": ROJO, "Y": (252, 152, 56), "W": DORADO_CLARO})
FUEGOS = [FUEGO, pygame.transform.flip(FUEGO, True, False)]

CORAZON_FILAS = [
    ".AA.BB..",
    "AAAABBB.",
    "AAAABBB.",
    "AAAABBB.",
    ".AAABB..",
    "..AAB...",
    "...A....",
    "........",
]
CORAZON_LLENO = crear_sprite(CORAZON_FILAS, {"A": ROJO, "B": ROJO})
CORAZON_MEDIO = crear_sprite(CORAZON_FILAS, {"A": ROJO, "B": ROSA})
CORAZON_VACIO = crear_sprite(CORAZON_FILAS, {"A": ROSA, "B": ROSA})

GEMA_FILAS = [
    "...OO...",
    "..OOOO..",
    "..OWOO..",
    ".OOWOOO.",
    ".OWOOOO.",
    ".OWOOOO.",
    ".OOOOOO.",
    ".OOOOOO.",
    ".OOOOOO.",
    ".OOOOOO.",
    ".OOOOWO.",
    ".OOOWOO.",
    "..OOOO..",
    "..OOOO..",
    "...OO...",
    "........",
]
GEMA = crear_sprite(GEMA_FILAS, {"O": (252, 152, 56), "W": BLANCO})
GEMA_AZUL = crear_sprite(GEMA_FILAS, {"O": (0, 88, 248), "W": BLANCO})

TRIANGULO = pygame.Surface((16, 16), pygame.SRCALPHA)
pygame.draw.polygon(TRIANGULO, DORADO, [(8, 1), (15, 14), (0, 14)])
pygame.draw.polygon(TRIANGULO, DORADO_CLARO, [(8, 4), (11, 11), (5, 11)])

# ------------------------------------------------------------
# CUADROS DEL MAPA
# ------------------------------------------------------------

ARBOL = crear_sprite([
    ".....GGGGGG.....",
    "...GGGGGGGGGG...",
    "..GGGDGGGGGGGG..",
    ".GGGDGGGGGDGGGG.",
    ".GGGGGGGGDGGGGG.",
    "GGGGGGDGGGGGGGGG",
    "GGDGGDGGGGGGDGGG",
    "GDGGGGGGGGGDGGGG",
    "GGGGGGGGDGGGGGGG",
    "GGGGDGGDGGGGGDGG",
    ".GGDGGGGGGGGDGG.",
    ".GGGGGGGGGGGGGG.",
    "..GGGGGGDGGGGG..",
    "...DGGGGGGGGD...",
    ".....DDDDDD.....",
    "................",
], {"G": VERDE, "D": VERDE_OSCURO})

ARBUSTO = crear_sprite([
    "................",
    "....GGGGGGGG....",
    "..GGGGGGGGGGGG..",
    ".GGGDGGGGGGGGGG.",
    ".GGDGGGGGGDGGGG.",
    "GGGGGGGGGDGGGGGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGDGGGGGGGGDGG",
    "GGGDGGGGGGGGDGGG",
    "GGGGGGGDGGGGGGGG",
    "GGGGGGDGGGGGGGGG",
    ".GGGGGGGGGGGGGG.",
    ".GGGGGGGGGGGDGG.",
    "..GGGGGGGGGGGG..",
    "...DDGGGGGGDD...",
    "....DDDDDDDD....",
], {"G": VERDE, "D": VERDE_OSCURO})

PIEDRA = crear_sprite([
    "..RRRRRRRRRRRR..",
    ".RRRRRRRRRRRRRR.",
    "RRRSRRRRRRRRRRRR",
    "RRSRRRRRRRKRRRRR",
    "RRRRRRRRRKRRRRRR",
    "RRRRRKRRRRRRRRSR",
    "RRRRKRRRRRRRRRRR",
    "RRRRRRRRRRSRRRRR",
    "RRKRRRRRRRRRRKRR",
    "RRRRRRSRRRRRKRRR",
    "RRRRRRRRRRRRRRRR",
    "RRRRRRRRKRRRRRRR",
    "KRRRRRRKRRRRRRRK",
    "KKRRRRRRRRRRRRKK",
    ".KKKRRRRRRRRKKK.",
    "..KKKKKKKKKKKK..",
], {"R": CAFE, "K": CAFE_OSCURO, "S": ARENA})

SOLIDOS = "TRBW"      # cuadros que no se pueden atravesar
MUROS = "TRB"         # cuadros que detienen las rocas (el agua no)


class Sala:
    """Una pantalla del mapa. Se describe con 11 filas de 16 letras:
       . arena   T arbol   R roca   B arbusto   W agua   C cueva"""

    def __init__(self, filas, oscura=False):
        self.filas = filas
        self.oscura = oscura
        self.fondos = [self.pintar(0), self.pintar(1)]   # 2 cuadros: el agua se mueve

    def tile(self, col, fila):
        if 0 <= col < COLS and 0 <= fila < FILAS:
            return self.filas[fila][col]
        return "."

    def choca(self, caja, solidos=SOLIDOS):
        for fila in range(caja.top // TILE, (caja.bottom - 1) // TILE + 1):
            for col in range(caja.left // TILE, (caja.right - 1) // TILE + 1):
                if self.tile(col, fila) in solidos:
                    return True
        return False

    def pintar(self, cuadro):
        fondo = pygame.Surface((ANCHO, CAMPO_ALTO))
        fondo.fill(NEGRO if self.oscura else ARENA)
        for fila in range(FILAS):
            for col in range(COLS):
                c = self.filas[fila][col]
                x, y = col * TILE, fila * TILE
                if c == "T":
                    fondo.fill(VERDE_OSCURO, (x, y, TILE, TILE))
                    fondo.blit(ARBOL, (x, y))
                elif c == "R":
                    fondo.fill(CAFE_OSCURO, (x, y, TILE, TILE))
                    fondo.blit(PIEDRA, (x, y))
                elif c == "B":
                    fondo.blit(ARBUSTO, (x, y))
                elif c == "C":
                    fondo.fill(NEGRO, (x, y, TILE, TILE))
                elif c == "W":
                    fondo.fill(AGUA, (x, y, TILE, TILE))
                    for i in range(2):
                        ox = (i * 8 + cuadro * 4 + fila * 3) % 16
                        fondo.fill(AGUA_CLARA, (x + ox, y + 3 + i * 8, 5, 1))
        return fondo


# El mundo: 3 x 3 pantallas. La clave es (columna, fila).
SALAS = {
    (0, 0): Sala([
        "TTTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTTT",
        "TT............TT",
        "TT.B.B....B.B.TT",
        "TT..............",
        "TT.B.B....B.B...",
        "TT..............",
        "TT.B.B....B.B.TT",
        "TT............TT",
        "TTTTTTT..TTTTTTT",
        "TTTTTTT..TTTTTTT",
    ]),
    (1, 0): Sala([
        "RRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRR",
        "RR............RR",
        "RR............RR",
        "................",
        "................",
        "................",
        "RR............RR",
        "RR............RR",
        "RRRRRRR..RRRRRRR",
        "RRRRRRR..RRRRRRR",
    ]),
    (2, 0): Sala([
        "RRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRR",
        "RR............RR",
        "RR..RR....RR..RR",
        "....RR....RR..RR",
        "..............RR",
        "....RR....RR..RR",
        "RR..RR....RR..RR",
        "RR............RR",
        "RRRRRRR..RRRRRRR",
        "RRRRRRR..RRRRRRR",
    ]),
    (0, 1): Sala([
        "RRRRRRR..RRRRRRR",
        "RRRRRRR..RRRRRRR",
        "RR............RR",
        "RR..R......R..RR",
        "RR..............",
        "RR.....RR.......",
        "RR..............",
        "RR..R......R..RR",
        "RR............RR",
        "RRRRRRR..RRRRRRR",
        "RRRRRRR..RRRRRRR",
    ]),
    (1, 1): Sala([
        "TTTTTTT..TTTTTTT",
        "TTTTTT....TTTTTT",
        "TT............TT",
        "T...B......B...T",
        "................",
        "................",
        "................",
        "T...B......B...T",
        "TT............TT",
        "TTTTTT....TTTTTT",
        "TTTTTTT..TTTTTTT",
    ]),
    (2, 1): Sala([
        "TTTTTTT..TTTTTTT",
        "TTTTTTT..TTTTTTT",
        "TT............TT",
        "TT..WW....WW..TT",
        "....WW....WW..TT",
        "..............TT",
        "....WW....WW..TT",
        "TT..WW....WW..TT",
        "TT............TT",
        "TTTTTTT..TTTTTTT",
        "TTTTTTT..TTTTTTT",
    ]),
    (0, 2): Sala([
        "TTTTTTT..TTTTTTT",
        "TTTTTTT..TTTTTTT",
        "TT............TT",
        "TT...WWWWWW...TT",
        "TT...WWWWWW.....",
        "TT...WWWWWW.....",
        "TT...WWWWWW.....",
        "TT............TT",
        "TT..B......B..TT",
        "TTTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTTT",
    ]),
    (1, 2): Sala([
        "RRRRRRR..RRRRRRR",
        "RRRRCRR..RRRRRRR",
        "RRR.........RRRR",
        "RR...........RRR",
        "................",
        "................",
        "................",
        "RR............RR",
        "RRR..........RRR",
        "RRRRRRRRRRRRRRRR",
        "RRRRRRRRRRRRRRRR",
    ]),
    (2, 2): Sala([
        "TTTTTTT..TTTTTTT",
        "TTTTTTT..TTTTTTT",
        "TT............TT",
        "TT..B..B..B...TT",
        "..............TT",
        "....B..B..B...TT",
        "..............TT",
        "TT..B..B..B...TT",
        "TT............TT",
        "TTTTTTTTTTTTTTTT",
        "TTTTTTTTTTTTTTTT",
    ]),
}

CUEVA = Sala([
    "RRRRRRRRRRRRRRRR",
    "RRRRRRRRRRRRRRRR",
    "RR............RR",
    "RR............RR",
    "RR............RR",
    "RR............RR",
    "RR............RR",
    "RR............RR",
    "RR............RR",
    "RRRRRRR..RRRRRRR",
    "RRRRRRR..RRRRRRR",
], oscura=True)

INICIO = (1, 2)            # pantalla donde empieza el heroe
SALA_JEFE = (1, 0)
PUERTA_CUEVA = (64, 32)    # donde aparece el heroe al salir de la cueva

ENEMIGOS_POR_SALA = {
    (0, 2): ["pulpo", "pulpo", "pulpo"],
    (2, 2): ["pulpo", "pulpo", "pulpo", "pulpo"],
    (0, 1): ["saltarin", "saltarin", "saltarin"],
    (1, 1): ["pulpo", "pulpo", "saltarin", "saltarin"],
    (2, 1): ["pulpo_azul", "pulpo_azul", "pulpo", "pulpo"],
    (0, 0): ["saltarin", "saltarin", "saltarin", "saltarin"],
    (2, 0): ["pulpo_azul", "pulpo_azul", "pulpo_azul"],
    (1, 0): ["jefe"],
}


def limitar(valor, minimo, maximo):
    return max(minimo, min(maximo, valor))


# ------------------------------------------------------------
# JUGADOR
# ------------------------------------------------------------

class Jugador:
    VELOCIDAD = 1.25

    def __init__(self):
        self.max_vida = 6          # se cuenta en medios corazones (6 = 3 corazones)
        self.tiene_espada = False
        self.gemas = 0
        self.revivir()

    def revivir(self):
        self.x, self.y = 120.0, 80.0
        self.dir = "abajo"
        self.vida = self.max_vida
        self.ataque = 0            # cuadros que le quedan al golpe de espada
        self.invul = 0             # cuadros de invulnerabilidad tras un golpe
        self.empuje = [0, 0, 0]    # retroceso: dx, dy, cuadros
        self.paso = 0

    def caja(self):
        """Zona donde el heroe recibe golpes y recoge objetos."""
        return pygame.Rect(math.floor(self.x) + 3, math.floor(self.y) + 3, 10, 12)

    def caja_espada(self):
        x, y = math.floor(self.x), math.floor(self.y)
        if self.dir == "arriba":
            return pygame.Rect(x + 3, y - 12, 10, 16)
        if self.dir == "abajo":
            return pygame.Rect(x + 3, y + 12, 10, 16)
        if self.dir == "izquierda":
            return pygame.Rect(x - 12, y + 4, 16, 10)
        return pygame.Rect(x + 12, y + 4, 16, 10)

    def intentar(self, dx, dy, sala):
        """Se mueve solo si los pies no chocan con algo solido."""
        pies = pygame.Rect(math.floor(self.x + dx) + 2,
                           math.floor(self.y + dy) + 8, 12, 8)
        if sala.choca(pies):
            return False
        self.x += dx
        self.y += dy
        return True

    def alinear(self, eje, sala):
        """Acomoda al heroe a una cuadricula de 8 pixeles, como en el NES.
           Asi es mas facil pasar por los huecos."""
        valor = self.y if eje == "y" else self.x
        resto = valor % 8
        if resto < 0.01:
            return
        ajuste = -min(1.0, resto) if resto < 4 else min(1.0, 8 - resto)
        if eje == "y":
            self.intentar(0, ajuste, sala)
        else:
            self.intentar(ajuste, 0, sala)

    def actualizar(self, teclas, sala):
        if self.invul > 0:
            self.invul -= 1

        if self.empuje[2] > 0:                       # retroceso por un golpe
            self.empuje[2] -= 1
            self.intentar(self.empuje[0], 0, sala)
            self.intentar(0, self.empuje[1], sala)
            self.x = limitar(self.x, 0, ANCHO - 16)
            self.y = limitar(self.y, 0, CAMPO_ALTO - 16)
            return

        if self.ataque > 0:                          # mientras ataca no camina
            self.ataque -= 1
            return

        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.dir = "arriba"
            self.alinear("x", sala)
            self.intentar(0, -self.VELOCIDAD, sala)
        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.dir = "abajo"
            self.alinear("x", sala)
            self.intentar(0, self.VELOCIDAD, sala)
        elif teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.dir = "izquierda"
            self.alinear("y", sala)
            self.intentar(-self.VELOCIDAD, 0, sala)
        elif teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.dir = "derecha"
            self.alinear("y", sala)
            self.intentar(self.VELOCIDAD, 0, sala)
        else:
            return
        self.paso += 1

    def atacar(self, juego):
        if not self.tiene_espada or self.ataque > 0 or self.empuje[2] > 0:
            return
        self.ataque = 14
        sonar("espada")
        # Con la vida llena, la espada lanza un rayo
        if self.vida == self.max_vida and juego.rayo is None:
            juego.rayo = Rayo(self)
            sonar("rayo")

    def bloquea(self, vx, vy):
        """El escudo detiene las rocas que vienen de frente."""
        if self.ataque > 0:
            return False
        if abs(vx) >= abs(vy):
            viene_de = "izquierda" if vx > 0 else "derecha"
        else:
            viene_de = "arriba" if vy > 0 else "abajo"
        return self.dir == viene_de

    def herir(self, juego, dano, origen_x, origen_y):
        if self.invul > 0 or juego.estado != "juego":
            return
        self.vida -= dano
        self.invul = 60
        dx, dy = self.x - origen_x, self.y - origen_y
        if abs(dx) > abs(dy):
            self.empuje = [3 if dx > 0 else -3, 0, 8]
        else:
            self.empuje = [0, 3 if dy > 0 else -3, 8]
        sonar("herido")
        if self.vida <= 0:
            juego.morir()


# ------------------------------------------------------------
# ENEMIGOS
# ------------------------------------------------------------

class Enemigo:
    VIDA = 1
    DANO = 1
    TAM = 16
    VUELA = False     # si es True, pasa por encima de arboles y rocas

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vida = self.VIDA
        self.invul = 0
        self.empuje = [0, 0, 0]
        self.aparece = 45      # primero se ve una nube y luego aparece
        self.vivo = True

    def caja(self):
        return pygame.Rect(int(self.x) + 2, int(self.y) + 2, self.TAM - 4, self.TAM - 4)

    def puede(self, sala, x, y):
        if x < 0 or y < 0 or x > ANCHO - self.TAM or y > CAMPO_ALTO - self.TAM:
            return False
        if self.VUELA:
            return True
        return not sala.choca(pygame.Rect(int(x) + 1, int(y) + 1, self.TAM - 2, self.TAM - 2))

    def mover(self, sala, dx, dy):
        if self.puede(sala, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def listo(self, juego):
        """Parte comun de todos los enemigos. Devuelve True si puede actuar."""
        if self.aparece > 0:
            self.aparece -= 1
            return False
        if self.invul > 0:
            self.invul -= 1
        if self.empuje[2] > 0:
            self.empuje[2] -= 1
            self.mover(juego.sala, self.empuje[0], self.empuje[1])
            return False
        return True

    def golpear(self, juego, dx, dy):
        if self.invul > 0 or self.aparece > 0:
            return False
        self.vida -= 1
        self.invul = 20
        self.empuje = [dx * 3, dy * 3, 8]
        if self.vida <= 0:
            self.morir(juego)
        else:
            sonar("golpe")
        return True

    def morir(self, juego):
        self.vivo = False
        centro = self.TAM // 2
        juego.efectos.append(Humo(self.x + centro, self.y + centro))
        sonar("muere")
        suerte = random.random()
        if suerte < 0.30:
            juego.objetos.append(Objeto("corazon", self.x + 4, self.y + 4))
        elif suerte < 0.60:
            juego.objetos.append(Objeto("gema", self.x + 4, self.y))
        elif suerte < 0.68:
            juego.objetos.append(Objeto("gema_azul", self.x + 4, self.y))

    def imagen(self):
        return SALTARIN

    def altura(self):
        return 0

    def dibujar(self, sup, tiempo):
        x, y = int(self.x), int(self.y) + HUD
        if self.aparece > 0:                         # nube de aparicion
            if (self.aparece // 4) % 2 == 0:
                c = self.TAM // 2
                for ox, oy in ((-4, -3), (4, -2), (0, 4)):
                    pygame.draw.circle(sup, BLANCO, (x + c + ox, y + c + oy), 4)
            return
        if self.invul > 0 and (self.invul // 2) % 2:   # parpadea al ser golpeado
            return
        sup.blit(self.imagen(), (x, y - int(self.altura())))


class Pulpo(Enemigo):
    """Camina en linea recta, se detiene y escupe una roca."""
    VELOCIDAD = 0.5
    PROB_DISPARO = 0.35
    IMAGENES = PULPO_ROJO

    def __init__(self, x, y):
        super().__init__(x, y)
        self.dir = random.choice(list(DIRS))
        self.pasos = random.randint(24, 96)
        self.pausa = 0

    def actualizar(self, juego):
        if not self.listo(juego):
            return
        dx, dy = DIRS[self.dir]
        if self.pausa > 0:
            self.pausa -= 1
            if self.pausa == 12:
                juego.proyectiles.append(Roca(self.x + 4, self.y + 4, dx * 2, dy * 2))
            return
        if self.pasos > 0 and self.mover(juego.sala, dx * self.VELOCIDAD, dy * self.VELOCIDAD):
            self.pasos -= 1
        else:
            self.dir = random.choice(list(DIRS))
            self.pasos = random.randint(24, 96)
            if random.random() < self.PROB_DISPARO:
                self.pausa = 36

    def imagen(self):
        return self.IMAGENES[self.dir]


class PulpoAzul(Pulpo):
    VIDA = 2
    VELOCIDAD = 0.75
    PROB_DISPARO = 0.55
    IMAGENES = PULPO_AZUL


class Saltarin(Enemigo):
    """Espera un momento y salta hacia donde esta el heroe."""
    VUELA = True
    DURACION = 32

    def __init__(self, x, y):
        super().__init__(x, y)
        self.espera = random.randint(30, 90)
        self.salto = None      # [x inicial, y inicial, x final, y final, cuadro]

    def actualizar(self, juego):
        if not self.listo(juego):
            self.salto = None
            return
        if self.salto is None:
            self.espera -= 1
            if self.espera <= 0:
                j = juego.jugador
                dx = random.randint(-48, 48) + (16 if j.x > self.x else -16)
                dy = random.randint(-32, 32) + (8 if j.y > self.y else -8)
                self.salto = [self.x, self.y,
                              limitar(self.x + dx, 16, ANCHO - 32),
                              limitar(self.y + dy, 16, CAMPO_ALTO - 32), 0]
        else:
            s = self.salto
            s[4] += 1
            avance = s[4] / self.DURACION
            self.x = s[0] + (s[2] - s[0]) * avance
            self.y = s[1] + (s[3] - s[1]) * avance
            if s[4] >= self.DURACION:
                self.salto = None
                self.espera = random.randint(20, 70)

    def altura(self):
        if self.salto is None:
            return 0
        return math.sin(math.pi * self.salto[4] / self.DURACION) * 14


class Jefe(Enemigo):
    """El guardian: grande, resistente y dispara tres rocas a la vez."""
    VIDA = 8
    DANO = 2
    TAM = 32

    def __init__(self, x, y):
        super().__init__(x, y)
        self.vx, self.vy = 0.6, 0.4
        self.disparo = 120

    def actualizar(self, juego):
        if not self.listo(juego):
            return
        if not self.mover(juego.sala, self.vx, 0):
            self.vx = -self.vx
        if not self.mover(juego.sala, 0, self.vy):
            self.vy = -self.vy
        self.disparo -= 1
        if self.disparo <= 0:
            self.disparo = 110
            j = juego.jugador
            angulo = math.atan2(j.y - (self.y + 8), j.x - (self.x + 8))
            for desvio in (-0.35, 0, 0.35):
                juego.proyectiles.append(Roca(
                    self.x + 12, self.y + 12,
                    math.cos(angulo + desvio) * 1.8,
                    math.sin(angulo + desvio) * 1.8))

    def golpear(self, juego, dx, dy):
        return super().golpear(juego, 0, 0)      # el jefe no retrocede

    def morir(self, juego):
        self.vivo = False
        juego.jefe_vencido = True
        for ox, oy in ((8, 8), (24, 8), (8, 24), (24, 24), (16, 16)):
            juego.efectos.append(Humo(self.x + ox, self.y + oy))
        sonar("muere")
        juego.objetos.append(Objeto("triangulo", self.x + 8, self.y + 8))

    def imagen(self):
        return JEFE


TIPOS_ENEMIGO = {
    "pulpo": Pulpo,
    "pulpo_azul": PulpoAzul,
    "saltarin": Saltarin,
    "jefe": Jefe,
}


# ------------------------------------------------------------
# PROYECTILES, OBJETOS Y EFECTOS
# ------------------------------------------------------------

class Roca:
    def __init__(self, x, y, vx, vy):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.viva = True

    def actualizar(self, juego):
        self.x += self.vx
        self.y += self.vy
        caja = pygame.Rect(int(self.x) + 1, int(self.y) + 1, 6, 6)
        fuera = (self.x < -8 or self.x > ANCHO or self.y < -8 or self.y > CAMPO_ALTO)
        if fuera or juego.sala.choca(caja, MUROS):
            self.viva = False
            return
        jugador = juego.jugador
        if caja.colliderect(jugador.caja()):
            self.viva = False
            if jugador.bloquea(self.vx, self.vy):
                sonar("escudo")
            else:
                jugador.herir(juego, 1, self.x - 4, self.y - 4)

    def dibujar(self, sup):
        sup.blit(ROCA, (int(self.x), int(self.y) + HUD))


class Rayo:
    """La espada que sale volando cuando el heroe tiene la vida llena."""

    def __init__(self, jugador):
        self.dir = jugador.dir
        caja = jugador.caja_espada()
        self.x, self.y = float(caja.x), float(caja.y)
        self.ancho, self.alto = caja.width, caja.height

    def actualizar(self, juego):
        dx, dy = DIRS[self.dir]
        self.x += dx * 3
        self.y += dy * 3
        caja = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
        if not caja.colliderect(pygame.Rect(0, 0, ANCHO, CAMPO_ALTO)):
            juego.rayo = None
            return
        for enemigo in juego.enemigos:
            if caja.colliderect(enemigo.caja()) and enemigo.golpear(juego, dx, dy):
                juego.efectos.append(Humo(caja.centerx, caja.centery))
                juego.rayo = None
                return

    def dibujar(self, sup, tiempo):
        imagenes = ESPADA_RAYO if (tiempo // 3) % 2 else ESPADA
        imagen = imagenes[self.dir]
        x = int(self.x) + (self.ancho - imagen.get_width()) // 2
        y = int(self.y) + (self.alto - imagen.get_height()) // 2
        sup.blit(imagen, (x, y + HUD))


class Objeto:
    IMAGENES = {
        "corazon": CORAZON_LLENO,
        "gema": GEMA,
        "gema_azul": GEMA_AZUL,
        "espada": ESPADA["arriba"],
        "triangulo": TRIANGULO,
    }

    def __init__(self, tipo, x, y):
        self.tipo = tipo
        self.x, self.y = int(x), int(y)
        self.imagen = self.IMAGENES[tipo]
        # Los objetos importantes no desaparecen; los demas duran 8 segundos
        self.tiempo = None if tipo in ("espada", "triangulo") else 480

    def caja(self):
        return pygame.Rect(self.x, self.y, self.imagen.get_width(), self.imagen.get_height())

    def dibujar(self, sup, tiempo):
        if self.tiempo is not None and self.tiempo < 120 and (tiempo // 4) % 2:
            return                                    # parpadea antes de irse
        if self.tipo == "triangulo" and (tiempo // 6) % 2:
            sup.blit(self.imagen, (self.x, self.y + HUD - 1))
        else:
            sup.blit(self.imagen, (self.x, self.y + HUD))


class Humo:
    """Estallido corto cuando un enemigo desaparece."""

    def __init__(self, x, y):
        self.x, self.y = int(x), int(y)
        self.edad = 0

    def dibujar(self, sup):
        radio = 2 + self.edad // 2
        color = BLANCO if self.edad % 4 < 2 else DORADO_CLARO
        for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)):
            sup.fill(color, (self.x + dx * radio - 2, self.y + dy * radio - 2 + HUD, 4, 4))


# ------------------------------------------------------------
# PANTALLA DE TITULO
# ------------------------------------------------------------

FONDO_TITULO = (228, 180, 172)
SOMBRA_TITULO = (84, 44, 12)
ROCA_TITULO = (188, 164, 204)
ROCA_TITULO_SOMBRA = (124, 100, 148)


def crear_marco_hojas():
    """Marco de enredadera alrededor del logo."""
    azar = random.Random(11)
    marco = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    borde = pygame.Rect(18, 18, 220, 142)
    puntos = []
    for x in range(borde.left, borde.right, 3):
        puntos += [(x, borde.top), (x, borde.bottom)]
    for y in range(borde.top, borde.bottom, 3):
        puntos += [(borde.left, y), (borde.right, y)]
    for x, y in puntos:
        color = (0, 148, 0) if azar.random() < 0.6 else (88, 184, 60)
        dx, dy = azar.randint(-2, 2), azar.randint(-2, 2)
        marco.fill(color, (x + dx, y + dy, azar.choice((2, 3)), azar.choice((2, 3))))
        if azar.random() < 0.12:                      # hojas mas grandes
            marco.fill((0, 104, 0), (x + dx - 1, y + dy - 1, 4, 4))
            marco.fill((88, 184, 60), (x + dx, y + dy, 2, 2))
    return marco


def crear_rocas_titulo():
    """Acantilado de la parte baja, con un hueco para la cascada."""
    azar = random.Random(5)
    rocas = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    for x in range(0, ANCHO, 8):
        if 104 <= x < 152:                             # hueco de la cascada
            continue
        distancia = abs(x + 4 - 128)
        alto_columna = 192 - min(26, max(0, distancia - 30) * 0.4) + azar.randint(-5, 5)
        arriba = int(alto_columna)
        rocas.fill(ROCA_TITULO, (x, arriba, 8, ALTO - arriba))
        rocas.fill(ROCA_TITULO_SOMBRA, (x, arriba, 8, 2))
        for _ in range(7):                             # grietas y sombras
            gy = azar.randint(arriba + 3, ALTO - 4)
            color = NEGRO if azar.random() < 0.55 else ROCA_TITULO_SOMBRA
            rocas.fill(color, (x + azar.randint(0, 5), gy, azar.randint(2, 4), azar.randint(2, 6)))
    return rocas


MARCO_HOJAS = crear_marco_hojas()
ROCAS_TITULO = crear_rocas_titulo()


def dibujar_titulo(sup, tiempo):
    sup.fill(FONDO_TITULO)

    # Cascada animada
    cascada = pygame.Rect(104, 186, 48, ALTO - 186)
    sup.fill((92, 180, 240), cascada)
    sup.set_clip(cascada)
    for k in range(-1, 5):
        y = cascada.top + k * 16 + (tiempo // 3) % 16
        puntos = [(104, y), (116, y + 5), (128, y), (140, y + 5), (152, y)]
        pygame.draw.lines(sup, BLANCO, False, puntos, 3)
    sup.set_clip(None)
    sup.blit(ROCAS_TITULO, (0, 0))

    # Triangulo dorado detras del nombre
    pygame.draw.polygon(sup, DORADO, [(60, 50), (196, 50), (128, 152)])
    pygame.draw.polygon(sup, FONDO_TITULO, [(78, 60), (178, 60), (128, 134)])

    sup.blit(MARCO_HOJAS, (0, 0))

    # "THE LEGEND OF" y su linea
    texto(sup, "THE LEGEND OF", 46, 36, SOMBRA_TITULO)
    sup.fill(SOMBRA_TITULO, (128, 39, 82, 2))

    # El nombre en grande, con sombra para darle volumen
    nombre = "MOISES"
    escala = 5
    x = (ANCHO - ancho_texto(nombre, escala)) // 2
    y = 62
    for i in range(4, 0, -1):
        texto(sup, nombre, x - i, y + i, SOMBRA_TITULO, escala)
    texto(sup, nombre, x, y, (216, 148, 40), escala)
    brillo = (tiempo // 8) % 60                       # destello que recorre el nombre
    if brillo < 6:
        letra_brillante = nombre[brillo]
        texto(sup, letra_brillante, x + brillo * 6 * escala, y, DORADO_CLARO, escala)

    # Espada bajo el nombre
    sup.fill((200, 224, 248), (58, 114, 122, 3))       # hoja
    sup.fill(BLANCO, (58, 114, 122, 1))
    pygame.draw.polygon(sup, (200, 224, 248), [(50, 115), (58, 113), (58, 117)])
    sup.fill((60, 108, 252), (180, 108, 4, 15))        # guarda
    sup.fill((148, 188, 252), (184, 112, 18, 7))       # mango
    for i in range(3):
        sup.fill(BLANCO, (187 + i * 5, 112, 2, 7))
    sup.fill((60, 108, 252), (202, 110, 4, 11))        # pomo

    texto_centrado(sup, "2026 EL SALVADOR", 142, SOMBRA_TITULO)

    if (tiempo // 30) % 2 == 0:
        texto_centrado(sup, "PUSH START BUTTON", 168, (60, 40, 40))


# ------------------------------------------------------------
# EL JUEGO
# ------------------------------------------------------------

MENSAJE_CUEVA = ["ES PELIGROSO IR SOLO!", "TOMA ESTO."]


class Juego:
    def __init__(self):
        self.tiempo = 0
        self.jugador = Jugador()
        self.ir_al_titulo()

    # ---------- cambios de estado ----------

    def cambiar_estado(self, estado):
        self.estado = estado
        self.t_estado = 0

    def ir_al_titulo(self):
        self.cambiar_estado("titulo")
        sonar("musica", repetir=True)

    def nueva_partida(self):
        parar("musica")
        sonar("inicio")
        self.jugador = Jugador()
        self.limpias = set()          # pantallas donde ya no quedan enemigos
        self.jefe_vencido = False
        self.empezar_en_inicio()

    def empezar_en_inicio(self):
        self.coord = INICIO
        self.sala = SALAS[INICIO]
        self.en_cueva = False
        self.vaciar_sala()
        self.scroll = None
        self.cortina = 0              # telon que se abre al empezar
        self.negro = 0
        self.letras_cueva = 0
        self.cambiar_estado("juego")

    def vaciar_sala(self):
        self.enemigos = []
        self.proyectiles = []
        self.objetos = []
        self.efectos = []
        self.rayo = None

    def morir(self):
        self.proyectiles = []
        self.rayo = None
        sonar("gameover")
        self.cambiar_estado("muerte")

    def continuar(self):
        self.jugador.revivir()
        self.limpias.clear()
        self.empezar_en_inicio()

    # ---------- teclas ----------

    def tecla(self, tecla):
        if tecla == pygame.K_m:
            AUDIO["silencio"] = not AUDIO["silencio"]
            if AUDIO["silencio"] and AUDIO["activo"]:
                pygame.mixer.stop()
            elif not AUDIO["silencio"] and self.estado == "titulo":
                sonar("musica", repetir=True)
        elif self.estado == "titulo":
            if tecla in (pygame.K_RETURN, pygame.K_SPACE):
                self.nueva_partida()
        elif self.estado == "juego":
            if tecla in (pygame.K_SPACE, pygame.K_z, pygame.K_x):
                self.jugador.atacar(self)
        elif self.estado == "gameover":
            if tecla == pygame.K_RETURN:
                self.continuar()
        elif self.estado == "victoria":
            if tecla == pygame.K_RETURN and self.t_estado > 150:
                self.ir_al_titulo()

    # ---------- actualizar ----------

    def actualizar(self, teclas):
        self.tiempo += 1
        self.t_estado += 1

        if self.estado == "juego":
            self.actualizar_juego(teclas)
        elif self.estado == "scroll":
            self.scroll["cuadro"] += 1
            if self.scroll["cuadro"] >= self.scroll["total"]:
                self.scroll = None
                self.cambiar_estado("juego")
                self.aparecer_enemigos()
        elif self.estado == "obtener":
            if self.t_estado > 100:
                self.cambiar_estado("juego")
        elif self.estado == "muerte":
            if self.t_estado > 100:
                self.cambiar_estado("gameover")

    def actualizar_juego(self, teclas):
        jugador = self.jugador
        if self.cortina < 128:
            self.cortina += 4
        if self.negro > 0:
            self.negro -= 1

        jugador.actualizar(teclas, self.sala)
        if self.en_cueva:
            jugador.y = max(jugador.y, 72.0)      # no se puede pasar del viejo
            if not jugador.tiene_espada and self.tiempo % 4 == 0:
                total = sum(len(linea) for linea in MENSAJE_CUEVA)
                if self.letras_cueva < total:
                    self.letras_cueva += 1
                    sonar("texto")

        # Golpe de espada
        if jugador.ataque > 3:
            dx, dy = DIRS[jugador.dir]
            caja = jugador.caja_espada()
            for enemigo in self.enemigos:
                if caja.colliderect(enemigo.caja()):
                    enemigo.golpear(self, dx, dy)

        if self.rayo:
            self.rayo.actualizar(self)

        # Enemigos
        for enemigo in self.enemigos:
            enemigo.actualizar(self)
            if (enemigo.vivo and enemigo.aparece == 0
                    and enemigo.caja().colliderect(jugador.caja())):
                centro = enemigo.TAM // 2 - 8
                jugador.herir(self, enemigo.DANO, enemigo.x + centro, enemigo.y + centro)
        habia_enemigos = bool(self.enemigos)
        self.enemigos = [e for e in self.enemigos if e.vivo]
        if habia_enemigos and not self.enemigos:
            self.limpias.add(self.coord)

        # Rocas
        for roca in self.proyectiles:
            roca.actualizar(self)
        self.proyectiles = [r for r in self.proyectiles if r.viva]

        # Objetos
        for objeto in self.objetos[:]:
            if objeto.tiempo is not None:
                objeto.tiempo -= 1
                if objeto.tiempo <= 0:
                    self.objetos.remove(objeto)
                    continue
            if objeto.caja().colliderect(jugador.caja()):
                self.objetos.remove(objeto)
                self.recoger(objeto.tipo)

        # Efectos
        for efecto in self.efectos:
            efecto.edad += 1
        self.efectos = [e for e in self.efectos if e.edad < 16]

        if self.estado == "juego":
            self.revisar_salidas()

    def recoger(self, tipo):
        jugador = self.jugador
        if tipo == "corazon":
            jugador.vida = min(jugador.max_vida, jugador.vida + 2)
            sonar("corazon")
        elif tipo == "gema":
            jugador.gemas += 1
            sonar("gema")
        elif tipo == "gema_azul":
            jugador.gemas += 5
            sonar("gema")
        elif tipo == "espada":
            jugador.tiene_espada = True
            sonar("objeto")
            self.cambiar_estado("obtener")
        elif tipo == "triangulo":
            self.proyectiles = []
            sonar("victoria")
            self.cambiar_estado("victoria")

    def revisar_salidas(self):
        """Revisa si el heroe entra a la cueva o sale por un borde."""
        jugador = self.jugador
        if self.en_cueva:
            if jugador.y > CAMPO_ALTO - 12:
                self.en_cueva = False
                self.sala = SALAS[self.coord]
                self.vaciar_sala()
                jugador.x, jugador.y = float(PUERTA_CUEVA[0]), float(PUERTA_CUEVA[1])
                jugador.dir = "abajo"
                self.negro = 12
            return

        centro = jugador.caja()
        if self.sala.tile(centro.centerx // TILE, centro.centery // TILE) == "C":
            self.en_cueva = True
            self.sala = CUEVA
            self.vaciar_sala()
            jugador.x, jugador.y, jugador.dir = 120.0, 150.0, "arriba"
            self.letras_cueva = 0
            self.negro = 12
            if not jugador.tiene_espada:
                self.objetos.append(Objeto("espada", 124, 92))
            return

        if jugador.x < -5:
            self.empezar_scroll(-1, 0)
        elif jugador.x > ANCHO - 11:
            self.empezar_scroll(1, 0)
        elif jugador.y < -5:
            self.empezar_scroll(0, -1)
        elif jugador.y > CAMPO_ALTO - 11:
            self.empezar_scroll(0, 1)

    def empezar_scroll(self, dx, dy):
        """Desliza la pantalla hacia la sala vecina, como en el NES."""
        jugador = self.jugador
        nueva = (self.coord[0] + dx, self.coord[1] + dy)
        if nueva not in SALAS:
            jugador.x = limitar(jugador.x, 0, ANCHO - 16)
            jugador.y = limitar(jugador.y, 0, CAMPO_ALTO - 16)
            return
        origen = (jugador.x, jugador.y)
        if dx == -1:
            jugador.x = float(ANCHO - 17)
        elif dx == 1:
            jugador.x = 1.0
        elif dy == -1:
            jugador.y = float(CAMPO_ALTO - 17)
        else:
            jugador.y = 1.0
        self.scroll = {
            "dx": dx, "dy": dy, "cuadro": 0,
            "total": (ANCHO if dx else CAMPO_ALTO) // 4,
            "vieja": self.sala, "origen": origen,
        }
        self.coord = nueva
        self.sala = SALAS[nueva]
        self.vaciar_sala()
        jugador.ataque = 0
        self.cambiar_estado("scroll")

    def aparecer_enemigos(self):
        jugador = self.jugador
        if self.coord == SALA_JEFE and self.jefe_vencido:
            self.objetos.append(Objeto("triangulo", 120, 72))
            return
        if self.coord in self.limpias:
            return
        for tipo in ENEMIGOS_POR_SALA.get(self.coord, []):
            if tipo == "jefe":
                self.enemigos.append(Jefe(112, 48))
                continue
            x, y = 112, 80
            for _ in range(80):                        # busca un lugar libre
                col, fila = random.randint(2, 13), random.randint(2, 8)
                lejos = abs(col * TILE - jugador.x) + abs(fila * TILE - jugador.y) > 72
                if self.sala.tile(col, fila) == "." and lejos:
                    x, y = col * TILE, fila * TILE
                    break
            self.enemigos.append(TIPOS_ENEMIGO[tipo](x, y))

    # ---------- dibujar ----------

    def dibujar(self, sup):
        if self.estado == "titulo":
            dibujar_titulo(sup, self.t_estado)
            return

        sup.set_clip(pygame.Rect(0, HUD, ANCHO, CAMPO_ALTO))
        if self.estado == "gameover":
            sup.fill(NEGRO)
            texto_centrado(sup, "GAME OVER", 130, ROJO, 2)
            if (self.t_estado // 30) % 2 == 0:
                texto_centrado(sup, "ENTER PARA CONTINUAR", 170)
        elif self.estado == "scroll":
            self.dibujar_scroll(sup)
        else:
            self.dibujar_campo(sup)
        sup.set_clip(None)
        self.dibujar_hud(sup)

    def dibujar_scroll(self, sup):
        s = self.scroll
        cuadro_agua = (self.tiempo // 24) % 2
        avance = s["cuadro"] * 4
        dx, dy = s["dx"], s["dy"]
        sup.blit(s["vieja"].fondos[cuadro_agua], (-dx * avance, HUD - dy * avance))
        sup.blit(self.sala.fondos[cuadro_agua],
                 (dx * (ANCHO - avance), HUD + dy * (CAMPO_ALTO - avance)))
        progreso = s["cuadro"] / s["total"]
        x = s["origen"][0] + (self.jugador.x - s["origen"][0]) * progreso
        y = s["origen"][1] + (self.jugador.y - s["origen"][1]) * progreso
        self.dibujar_jugador(sup, x, y)

    def dibujar_campo(self, sup):
        sup.blit(self.sala.fondos[(self.tiempo // 24) % 2], (0, HUD))

        if self.en_cueva:
            fuego = FUEGOS[(self.tiempo // 8) % 2]
            sup.blit(fuego, (72, 64 + HUD))
            sup.blit(fuego, (168, 64 + HUD))
            if not self.jugador.tiene_espada or self.estado == "obtener":
                sup.blit(VIEJO, (120, 64 + HUD))
            if not self.jugador.tiene_espada:
                quedan = self.letras_cueva
                for i, linea in enumerate(MENSAJE_CUEVA):
                    visible = linea[:quedan]
                    quedan = max(0, quedan - len(linea))
                    x = (ANCHO - ancho_texto(linea)) // 2
                    texto(sup, visible, x, 36 + i * 12 + HUD)

        for objeto in self.objetos:
            objeto.dibujar(sup, self.tiempo)
        for enemigo in self.enemigos:
            enemigo.dibujar(sup, self.tiempo)
        self.dibujar_jugador(sup, self.jugador.x, self.jugador.y)
        for roca in self.proyectiles:
            roca.dibujar(sup)
        if self.rayo:
            self.rayo.dibujar(sup, self.tiempo)
        for efecto in self.efectos:
            efecto.dibujar(sup)

        if self.estado == "victoria" and self.t_estado > 150:
            caja = pygame.Rect(24, HUD + 44, ANCHO - 48, 88)
            sup.fill(NEGRO, caja)
            pygame.draw.rect(sup, DORADO, caja, 2)
            texto_centrado(sup, "FELICIDADES!", caja.top + 10, DORADO_CLARO, 2)
            texto_centrado(sup, "RECUPERASTE EL TRIANGULO DORADO", caja.top + 36)
            texto_centrado(sup, "LA PAZ VOLVIO AL REINO", caja.top + 50)
            if (self.t_estado // 30) % 2 == 0:
                texto_centrado(sup, "ENTER - VOLVER AL TITULO", caja.top + 70, ROSA)

        if self.cortina < 128:                         # telon de inicio
            sup.fill(NEGRO, (0, HUD, 128 - self.cortina, CAMPO_ALTO))
            sup.fill(NEGRO, (128 + self.cortina, HUD, 128 - self.cortina, CAMPO_ALTO))
        if self.negro > 0:
            sup.fill(NEGRO, (0, HUD, ANCHO, CAMPO_ALTO))

    def dibujar_jugador(self, sup, x, y):
        jugador = self.jugador
        px, py = math.floor(x), math.floor(y) + HUD

        if self.estado == "muerte":                    # gira antes de caer
            if self.t_estado < 70:
                giro = list(DIRS)[(self.t_estado // 5) % 4]
                sup.blit(HEROE[giro], (px, py))
            elif self.t_estado < 86:
                estallido = Humo(px + 8, py - HUD + 8)
                estallido.edad = self.t_estado - 70
                estallido.dibujar(sup)
            return

        if self.estado in ("obtener", "victoria"):     # levanta el objeto
            sup.blit(HEROE["abajo"], (px, py))
            objeto = ESPADA["arriba"] if self.estado == "obtener" else TRIANGULO
            sup.blit(objeto, (px + 8 - objeto.get_width() // 2, py - objeto.get_height()))
            return

        if jugador.invul > 0 and (jugador.invul // 3) % 2:
            return                                     # parpadeo tras un golpe

        if jugador.ataque > 0 and self.estado == "juego":
            caja = jugador.caja_espada()
            imagen = ESPADA[jugador.dir]
            sup.blit(imagen, (caja.centerx - imagen.get_width() // 2,
                              caja.centery - imagen.get_height() // 2 + HUD))

        rebote = 1 if (jugador.paso // 8) % 2 and jugador.ataque == 0 else 0
        sup.blit(HEROE[jugador.dir], (px, py - rebote))

    def dibujar_hud(self, sup):
        jugador = self.jugador
        sup.fill(NEGRO, (0, 0, ANCHO, HUD))

        # Minimapa: un cuadro por pantalla y un punto donde esta el heroe
        sup.fill(GRIS, (16, 20, 48, 30))
        sup.fill((128, 208, 16), (16 + self.coord[0] * 16 + 6, 20 + self.coord[1] * 10 + 3, 4, 4))

        # Gemas
        sup.blit(GEMA, (76, 18))
        texto(sup, "X" + str(jugador.gemas), 86, 23)

        # Casillas B y A
        for i, nombre in enumerate("BA"):
            x = 120 + i * 24
            pygame.draw.rect(sup, AZUL_HUD, (x, 20, 18, 30), 1)
            sup.fill(NEGRO, (x + 5, 16, 8, 8))
            texto(sup, nombre, x + 6, 16)
        if jugador.tiene_espada:
            sup.blit(ESPADA["arriba"], (144 + 6, 28))

        # Vida
        texto(sup, "-VIDA-", 184, 20, ROJO)
        for i in range(jugador.max_vida // 2):
            puntos = jugador.vida - i * 2
            if puntos >= 2:
                imagen = CORAZON_LLENO
            elif puntos == 1:
                imagen = CORAZON_MEDIO
            else:
                imagen = CORAZON_VACIO
            sup.blit(imagen, (184 + i * 9, 38))


# ------------------------------------------------------------
# BUCLE PRINCIPAL
# ------------------------------------------------------------

def main():
    preparar_sonidos()
    juego = Juego()

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                juego.tecla(evento.key)

        juego.actualizar(pygame.key.get_pressed())
        juego.dibujar(lienzo)

        # Agranda el lienzo chico a la ventana, sin suavizar los pixeles
        ventana.blit(pygame.transform.scale(lienzo, ventana.get_size()), (0, 0))
        pygame.display.flip()
        reloj.tick(FPS)


if __name__ == "__main__":
    main()