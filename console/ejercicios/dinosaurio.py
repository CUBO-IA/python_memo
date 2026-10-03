# ============================================================
# 🦖 DINO — El juego del dinosaurio de Chrome, en la terminal
# ============================================================
# Controles:
#   ESPACIO o ↑  → saltar (y empezar / reiniciar)
#   ↓            → agacharse (y caer más rápido en el aire)
#   Q            → salir
#
# Cómo correrlo (desde console/ejercicios):  python3 dinosaurio.py
# Tip: agrandá el panel de la terminal (mínimo 50 x 14).
#
# Usa "curses", una librería que ya trae Python para dibujar
# en la terminal cuadro por cuadro, como una animación.

import curses
import locale
import os
import random
import time

os.environ.setdefault("ESCDELAY", "25")  # que la tecla ESC responda rápido
locale.setlocale(locale.LC_ALL, "")      # para poder dibujar con bloques █ ▀ ▄

# ------------------------------------------------------------
# Configuración del juego
# ------------------------------------------------------------
FPS = 30                    # cuadros por segundo
ALTURA_SALTO = 6            # cuántas filas sube el dino
DURACION_SALTO = 26         # cuántos cuadros dura un salto
VEL_SALTO = 2 * ALTURA_SALTO / (DURACION_SALTO / 2)
GRAVEDAD = VEL_SALTO / (DURACION_SALTO / 2)
VEL_INICIAL = 0.7           # columnas que avanza el mundo por cuadro
VEL_MAXIMA = 1.5
DINO_COL = 3                # columna donde corre el dino
ANCHO_MIN, ALTO_MIN = 50, 14

# ------------------------------------------------------------
# Dibujos (sprites). Los espacios son "transparentes".
# ------------------------------------------------------------
DINO_PARADO = [
    "    ▄█▀██",
    "▄   ████▀",
    "▀█▄████▄ ",
    "  █▀ █▀  ",
]
DINO_CORRE = [
    ["    ▄█▀██",
     "▄   ████▀",
     "▀█▄████▄ ",
     "  █▀ ▀   "],
    ["    ▄█▀██",
     "▄   ████▀",
     "▀█▄████▄ ",
     "  ▀  █▀  "],
]
DINO_AGACHADO = [
    ["▀▄▄█████▀██",
     "  █▀ ▀     "],
    ["▀▄▄█████▀██",
     "  ▀  █▀    "],
]
DINO_MUERTO = [
    "    ▄█x██",
    "▄   ████▀",
    "▀█▄████▄ ",
    "  █▀ █▀  ",
]
CACTUS_CHICO = [
    " █▄",
    "▀█ ",
    " █ ",
]
CACTUS_GRANDE = [
    "  █ ▄",
    "▄ █ █",
    "▀▀█▀▀",
    "  █  ",
]
AVE = [
    ["   ▄    ",
     "▄▄███▀▀▀"],
    ["▄▄███▀▀▀",
     "   ▀    "],
]
NUBE = [
    " .--. ",
    "(____)",
]


def juntar(*sprites):
    """Pone varios cactus uno al lado del otro, alineados abajo."""
    alto = max(len(s) for s in sprites)
    filas = []
    for i in range(alto):
        partes = []
        for s in sprites:
            relleno = alto - len(s)
            partes.append(s[i - relleno] if i >= relleno else " " * len(s[0]))
        filas.append(" ".join(partes))
    return filas


def dibujar(pantalla, sprite, fila_abajo, col, atributo=curses.A_NORMAL):
    """Dibuja un sprite con su fila de abajo en fila_abajo."""
    alto, ancho = pantalla.getmaxyx()
    fila_arriba = fila_abajo - len(sprite) + 1
    for i, linea in enumerate(sprite):
        for j, letra in enumerate(linea):
            f, c = fila_arriba + i, col + j
            dentro = 0 <= f < alto and 0 <= c < ancho
            if letra != " " and dentro and not (f == alto - 1 and c == ancho - 1):
                try:
                    pantalla.addstr(f, c, letra, atributo)
                except curses.error:
                    pass


def celdas(sprite, fila_abajo, col):
    """Devuelve las posiciones que ocupa un sprite (para detectar choques)."""
    fila_arriba = fila_abajo - len(sprite) + 1
    return {
        (fila_arriba + i, col + j)
        for i, linea in enumerate(sprite)
        for j, letra in enumerate(linea)
        if letra != " "
    }


def texto_centrado(pantalla, fila, texto, atributo=curses.A_NORMAL):
    alto, ancho = pantalla.getmaxyx()
    col = max(0, (ancho - len(texto)) // 2)
    try:
        pantalla.addstr(fila, col, texto[: ancho - 1], atributo)
    except curses.error:
        pass


def crear_obstaculo(puntos, velocidad, x):
    """Elige al azar el próximo obstáculo. Se pone más difícil con el tiempo."""
    if puntos > 300 and random.random() < 0.25:
        # Ave a tres alturas: 0 = saltar, 2 = agacharse, 4 = pasar por debajo
        return {"x": x, "cuadros": AVE, "elev": random.choice([0, 2, 4])}

    opciones = [CACTUS_CHICO, CACTUS_GRANDE]
    if velocidad > 0.9:
        opciones.append(juntar(CACTUS_CHICO, CACTUS_CHICO))
    if velocidad > 1.1:
        opciones.append(juntar(CACTUS_GRANDE, CACTUS_CHICO))
    return {"x": x, "cuadros": [random.choice(opciones)], "elev": 0}


def sprite_obstaculo(obstaculo, cuadro):
    cuadros = obstaculo["cuadros"]
    return cuadros[(cuadro // 8) % len(cuadros)]  # las aves aletean


def sprite_dino(p, estado):
    if estado == "fin":
        return DINO_MUERTO
    if estado == "inicio" or p["y"] > 0:
        return DINO_PARADO
    paso = (p["cuadro"] // 4) % 2  # alterna las patas
    if p["agachado"]:
        return DINO_AGACHADO[paso]
    return DINO_CORRE[paso]


def nueva_partida():
    return {
        "y": 0.0,            # altura del dino sobre el suelo
        "vy": 0.0,           # velocidad vertical
        "agachado": 0,       # cuadros que le quedan agachado
        "obstaculos": [],
        "distancia": 0.0,
        "puntos": 0,
        "velocidad": VEL_INICIAL,
        "proximo": 40.0,     # columnas hasta el próximo obstáculo
        "cuadro": 0,
        "parpadeo": 0,       # el puntaje parpadea cada 100 puntos
    }


def juego(pantalla):
    try:
        curses.curs_set(0)  # esconder el cursor
    except curses.error:
        pass
    pantalla.nodelay(True)  # no esperar teclas: el juego sigue corriendo
    pantalla.keypad(True)   # entender flechas

    estado = "inicio"       # "inicio" → "jugando" → "fin"
    p = nueva_partida()
    record = 0
    fin_tiempo = 0.0
    nubes = [[random.randint(10, 90), random.randint(1, 2)] for _ in range(3)]
    terreno = "".join(random.choice("      .  -  ' ") for _ in range(500))
    # Línea del suelo con lomitas de vez en cuando, como en Chrome
    linea_suelo = "".join(random.choice(["─" * 20, "─" * 35, "╭╮─", "╭─╮"]) for _ in range(60))

    while True:
        inicio_cuadro = time.perf_counter()
        alto, ancho = pantalla.getmaxyx()

        # ---------- 1. Leer teclas ----------
        saltar = agachar = False
        while (tecla := pantalla.getch()) != -1:
            if tecla in (ord("q"), ord("Q"), 27):
                return record
            if tecla in (ord(" "), curses.KEY_UP, ord("w"), ord("W")):
                saltar = True
            if tecla in (curses.KEY_DOWN, ord("s"), ord("S")):
                agachar = True

        pantalla.erase()

        if alto < ALTO_MIN or ancho < ANCHO_MIN:
            texto_centrado(pantalla, alto // 2, f"Agrandá la terminal (mínimo {ANCHO_MIN}x{ALTO_MIN})")
            pantalla.refresh()
            time.sleep(0.1)
            continue

        suelo = alto - 2  # fila donde está la línea del suelo

        # ---------- 2. Cambiar de estado ----------
        if estado == "inicio" and saltar:
            estado = "jugando"
        elif estado == "fin" and saltar and time.perf_counter() - fin_tiempo > 0.6:
            p = nueva_partida()
            estado = "jugando"

        # ---------- 3. Actualizar el mundo ----------
        if estado == "jugando":
            # Agacharse: cada vez que llega la tecla ↓ se renueva el tiempo
            if agachar:
                p["agachado"] = 12
            elif p["agachado"] > 0:
                p["agachado"] -= 1

            # Saltar solo si está en el suelo
            if saltar and p["y"] == 0:
                p["vy"] = VEL_SALTO
                p["agachado"] = 0

            # Física: la gravedad lo jala hacia abajo (más fuerte si se agacha)
            p["y"] += p["vy"]
            p["vy"] -= GRAVEDAD * (3 if p["agachado"] else 1)
            if p["y"] <= 0:
                p["y"] = 0.0
                p["vy"] = 0.0

            # Velocidad y puntos
            p["velocidad"] = min(VEL_MAXIMA, VEL_INICIAL + p["puntos"] * 0.001)
            v = p["velocidad"]
            p["distancia"] += v
            antes = p["puntos"]
            p["puntos"] = int(p["distancia"] * 0.4)
            if p["puntos"] // 100 > antes // 100:
                p["parpadeo"] = 30
            if p["parpadeo"] > 0:
                p["parpadeo"] -= 1

            # Mover obstáculos y borrar los que ya salieron
            for o in p["obstaculos"]:
                o["x"] -= v
            p["obstaculos"] = [o for o in p["obstaculos"] if o["x"] > -15]

            # Crear el siguiente obstáculo
            p["proximo"] -= v
            if p["proximo"] <= 0:
                p["obstaculos"].append(crear_obstaculo(p["puntos"], v, ancho))
                minimo = v * DURACION_SALTO + 14
                p["proximo"] = minimo + random.random() * minimo

            # Nubes (van más lento, parecen lejanas)
            for nube in nubes:
                nube[0] -= v * 0.15
                if nube[0] < -8:
                    nube[0] = ancho + random.randint(0, 30)
                    nube[1] = random.randint(1, 2)

            p["cuadro"] += 1

            # ¿Chocó? Comparamos las celdas del dino con las de cada obstáculo
            fila_dino = suelo - 1 - round(p["y"])
            cuerpo = celdas(sprite_dino(p, estado), fila_dino, DINO_COL)
            for o in p["obstaculos"]:
                forma = celdas(sprite_obstaculo(o, p["cuadro"]), suelo - 1 - o["elev"], round(o["x"]))
                if cuerpo & forma:
                    estado = "fin"
                    record = max(record, p["puntos"])
                    fin_tiempo = time.perf_counter()
                    break

        # ---------- 4. Dibujar ----------
        for x, fila in nubes:
            dibujar(pantalla, NUBE, fila + 1, round(x), curses.A_DIM)

        try:
            inicio = int(p["distancia"])
            linea = "".join(linea_suelo[(inicio + i) % len(linea_suelo)] for i in range(ancho))
            pantalla.addstr(suelo, 0, linea)
            piedritas = "".join(terreno[(inicio + i) % len(terreno)] for i in range(ancho - 1))
            pantalla.addstr(suelo + 1, 0, piedritas, curses.A_DIM)
        except curses.error:
            pass

        for o in p["obstaculos"]:
            dibujar(pantalla, sprite_obstaculo(o, p["cuadro"]), suelo - 1 - o["elev"], round(o["x"]))

        dibujar(pantalla, sprite_dino(p, estado), suelo - 1 - round(p["y"]), DINO_COL, curses.A_BOLD)

        # Puntaje arriba a la derecha (parpadea cada 100)
        actual = f"{p['puntos']:05d}"
        if p["parpadeo"] and (p["parpadeo"] // 5) % 2:
            actual = "     "
        marcador = f"HI {record:05d}  {actual}" if record else actual
        try:
            pantalla.addstr(0, ancho - len(marcador) - 2, marcador)
        except curses.error:
            pass

        if estado == "inicio":
            texto_centrado(pantalla, 4, "D I N O", curses.A_BOLD)
            texto_centrado(pantalla, 6, "ESPACIO o ↑ para saltar y empezar")
            texto_centrado(pantalla, 7, "↓ agacharse  ·  Q salir", curses.A_DIM)
        elif estado == "fin":
            texto_centrado(pantalla, 4, "G A M E   O V E R", curses.A_BOLD)
            texto_centrado(pantalla, 6, "↻  ESPACIO para jugar otra vez  ·  Q salir")

        pantalla.refresh()

        # ---------- 5. Esperar hasta el siguiente cuadro ----------
        transcurrido = time.perf_counter() - inicio_cuadro
        time.sleep(max(0.0, 1 / FPS - transcurrido))


if __name__ == "__main__":
    record_final = curses.wrapper(juego)
    print(f"¡Gracias por jugar! 🦖  Tu récord: {record_final} puntos")
