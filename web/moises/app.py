# ============================================================
#  Pagina web de THE LEGEND OF MOISES
#  Hecha con Python y Flask
# ============================================================
#  Como correrla (desde la carpeta web/moises):
#
#    python3 -m venv venv
#    source venv/bin/activate
#    pip install -r requirements.txt
#    python3 app.py
#
#  Luego abri en el navegador:  http://localhost:5050
# ============================================================

from flask import Flask, render_template

app = Flask(__name__)

# ------------------------------------------------------------
# CONTENIDO DE LA PAGINA
# ------------------------------------------------------------
# Todo el contenido vive aqui, en listas y diccionarios de Python.
# La plantilla HTML solo lo recorre y lo muestra. Para cambiar un
# texto de la pagina, se cambia aqui y no en el HTML.
#
# Los nombres que se muestran con la letra de pixeles van sin tilde,
# igual que en el juego: esa letra no tiene mayusculas acentuadas.

CONTROLES = [
    {"teclas": ["▲", "▼", "◀", "▶"], "extra": "o W A S D", "accion": "Moverte"},
    {"teclas": ["ESPACIO"], "extra": "o Z", "accion": "Usar la espada"},
    {"teclas": ["ENTER"], "extra": "", "accion": "Empezar o continuar"},
    {"teclas": ["M"], "extra": "", "accion": "Sonido sí o no"},
    {"teclas": ["ESC"], "extra": "", "accion": "Salir del juego"},
]

TRUCOS = [
    "Tu escudo detiene las rocas si las mirás de frente y no estás atacando.",
    "Con los tres corazones llenos, la espada lanza un rayo a distancia.",
    "Los enemigos a veces sueltan corazones y gemas. Desaparecen a los 8 segundos.",
    "Una pantalla sin enemigos se queda vacía hasta que perdés.",
]

ENEMIGOS = [
    {
        "nombre": "Pulpo rojo",
        "imagen": "pulpo.png",
        "golpes": 1,
        "descripcion": "Camina en línea recta, se detiene y escupe una roca.",
    },
    {
        "nombre": "Pulpo azul",
        "imagen": "pulpo_azul.png",
        "golpes": 2,
        "descripcion": "Más rápido que el rojo y dispara más seguido.",
    },
    {
        "nombre": "Saltarin",
        "imagen": "saltarin.png",
        "golpes": 1,
        "descripcion": "Salta hacia donde estás y pasa por encima de árboles y rocas.",
    },
    {
        "nombre": "El guardian",
        "imagen": "jefe.png",
        "golpes": 8,
        "descripcion": "Dispara tres rocas a la vez y te quita un corazón entero si te toca.",
    },
]

# El mapa tiene 3 columnas y 3 filas. Cada pantalla es (columna, fila).
MARCAS_DEL_MAPA = {
    (1, 2): "Inicio y cueva",
    (1, 0): "Guardian",
}

MAPA = []
for fila in range(3):
    for columna in range(3):
        MAPA.append({
            "imagen": f"sala_{columna}_{fila}.png",
            "marca": MARCAS_DEL_MAPA.get((columna, fila), ""),
        })

REPOSITORIO = "https://github.com/CUBO-IA/python_memo"


# ------------------------------------------------------------
# RUTAS
# ------------------------------------------------------------

@app.route("/")
def inicio():
    return render_template(
        "index.html",
        controles=CONTROLES,
        trucos=TRUCOS,
        enemigos=ENEMIGOS,
        mapa=MAPA,
        repositorio=REPOSITORIO,
    )


if __name__ == "__main__":
    # El puerto 5000 lo usa AirPlay en la Mac, por eso se usa el 5050.
    app.run(port=5050, debug=True)
