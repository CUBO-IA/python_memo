# ============================================================
# SET — Conjuntos
# ============================================================
# Un set guarda valores SIN REPETIDOS y SIN ORDEN, dentro
# de { } (como el diccionario, pero sin "clave: valor").
#
# Se usa para eliminar duplicados o comparar grupos.

# --- 1. Crear un set ---
frutas = {"mango", "piña", "mango", "coco", "piña"}
print("Frutas:", frutas)  # los repetidos desaparecen solos

# --- 2. Ver el tipo ---
print("¿Qué tipo es?", type(frutas))  # <class 'set'>

# --- 3. ⚠️ No tiene orden → no se puede usar frutas[0] ---
# Cada vez que lo imprimís puede salir en distinto orden.

# --- 4. Quitar duplicados de una lista (uso más común) ---
correos = ["a@mail.com", "b@mail.com", "a@mail.com", "c@mail.com"]
unicos = set(correos)
print("Correos únicos:", unicos)
print("Había", len(correos), "y quedaron", len(unicos))

# --- 5. Agregar y quitar ---
frutas.add("marañón")
frutas.discard("coco")
print("Actualizado:", frutas)

# --- 6. Comparar grupos ---
equipo_a = {"Memo", "Nohemy", "Mario"}
equipo_b = {"Mario", "Ernesto"}

print("En los dos equipos:", equipo_a & equipo_b)   # {'Mario'}
print("Todos juntos:", equipo_a | equipo_b)
print("Solo en el A:", equipo_a - equipo_b)

# --- 7. Preguntar si algo está ---
print("¿Está Memo en el A?", "Memo" in equipo_a)  # True

# ============================================================
# 🧪 PRUEBA VOS: hacé una lista con nombres repetidos y
#    convertila en set.   python3 set.py
# ============================================================
