# ============================================================
# DICTIONARY (dict) — Diccionarios
# ============================================================
# Un diccionario guarda datos en pares CLAVE: VALOR, dentro
# de { }. En vez de buscar por posición (0, 1, 2...), buscás
# por nombre (la clave).
#
# Como una ficha de contacto: nombre → Memo, edad → 44...
# Es uno de los tipos más usados, sobre todo con IA y APIs
# (el formato JSON es básicamente un diccionario).

# --- 1. Crear un diccionario ---
persona = {
    "nombre": "Memo",
    "edad": 44,
    "pais": "El Salvador",
    "estudia_ia": True,
}
print("Persona:", persona)

# --- 2. Ver el tipo ---
print("¿Qué tipo es?", type(persona))  # <class 'dict'>

# --- 3. Leer un valor usando su clave ---
print("Nombre:", persona["nombre"])  # Memo
print("Edad:", persona["edad"])      # 44

# --- 4. .get() — leer sin error si la clave no existe ---
print("Teléfono:", persona.get("telefono"))  # None
print("Teléfono:", persona.get("telefono", "no registrado"))

# --- 5. Agregar o cambiar valores ---
persona["programa"] = "CUBO AI"   # agrega una clave nueva
persona["edad"] = 45              # cambia una existente
print("Actualizado:", persona)

# --- 6. Borrar una clave ---
del persona["programa"]
print("Sin programa:", persona)

# --- 7. Ver solo claves o solo valores ---
print("Claves:", list(persona.keys()))
print("Valores:", list(persona.values()))

# --- 8. Recorrer el diccionario ---
print("Ficha:")
for clave, valor in persona.items():
    print(f"  {clave}: {valor}")

# --- 9. Diccionarios dentro de listas (muy común) ---
menu = [
    {"sabor": "queso", "precio": 0.75},
    {"sabor": "revuelta", "precio": 0.80},
]
for pupusa in menu:
    print(f"Pupusa de {pupusa['sabor']}: ${pupusa['precio']}")

# ============================================================
# 🧪 PRUEBA VOS: creá un diccionario con los datos de tu
#    equipo del challenge.   python3 dictionary.py
# ============================================================
