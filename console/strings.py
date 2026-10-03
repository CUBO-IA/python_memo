# ============================================================
# STRING (str) — Texto
# ============================================================
# Un string es TEXTO: letras, palabras, frases, emojis...
# Siempre va entre comillas: "hola" o 'hola' (las dos sirven).
#
# Nota: este archivo se llama strings.py (con s) y no string.py
# porque Python ya tiene un módulo interno llamado "string" y
# no queremos que se confundan.

# --- 1. Crear texto ---
nombre = "Memo"
pais = 'El Salvador'
frase = "Bitoo no te reemplaza. Te hace más capaz."

print(nombre)
print(pais)
print(frase)

# --- 2. Ver el tipo ---
print("¿Qué tipo es nombre?", type(nombre))  # <class 'str'>

# --- 3. Unir textos (concatenar) con + ---
saludo = "Hola, " + nombre + "!"
print(saludo)

# --- 4. f-strings: la forma moderna de mezclar texto y variables ---
# Ponés una f antes de las comillas y las variables entre { }
edad = 44
print(f"Me llamo {nombre}, tengo {edad} años y vivo en {pais}.")

# --- 5. Cosas útiles que se le pueden hacer al texto ---
print("Mayúsculas:", nombre.upper())        # MEMO
print("Minúsculas:", nombre.lower())        # memo
print("Largo (letras):", len(nombre))       # 4
print("¿Contiene 'Salva'?", "Salva" in pais)  # True
print("Reemplazar:", pais.replace("El ", ""))  # Salvador

# --- 6. Sacar letras por posición (índice) ---
# Python cuenta desde 0, no desde 1.
#   M  e  m  o
#   0  1  2  3
print("Primera letra:", nombre[0])   # M
print("Última letra:", nombre[-1])   # o
print("Primeras 2:", nombre[0:2])    # Me

# --- 7. Texto de varias líneas con triple comilla ---
mensaje = """Línea 1
Línea 2
Línea 3"""
print(mensaje)

# --- 8. ⚠️ Un número entre comillas es TEXTO, no número ---
print("5" + "5")  # 55  (une textos)
print(5 + 5)      # 10  (suma números)

# ============================================================
# 🧪 PRUEBA VOS: cambiá nombre por el tuyo completo y mirá
#    cómo cambia todo.  python3 strings.py
# ============================================================
