# ============================================================
# NONE (NoneType) — "Nada", vacío, sin valor
# ============================================================
# None significa que una variable existe pero TODAVÍA NO TIENE
# un valor. No es cero, no es texto vacío: es "nada".
# ⚠️ Se escribe con N mayúscula.
#
# Ejemplo de la vida real: un formulario donde el usuario aún
# no ha escrito su teléfono.

# --- 1. Crear una variable con None ---
telefono = None
print("Teléfono:", telefono)

# --- 2. Ver el tipo ---
print("¿Qué tipo es?", type(telefono))  # <class 'NoneType'>

# --- 3. None NO es lo mismo que 0 o "" ---
print("¿None es igual a 0?", None == 0)    # False
print("¿None es igual a ''?", None == "")  # False

# --- 4. Preguntar si algo es None (se usa "is") ---
if telefono is None:
    print("El usuario todavía no ha dado su teléfono.")

# --- 5. Más tarde le damos un valor ---
telefono = "7777-7777"
if telefono is not None:
    print("Ahora sí tenemos teléfono:", telefono)

# ============================================================
# 🧪 PRUEBA VOS: creá una variable correo = None y escribí un
#    if que avise si falta.   python3 none.py
# ============================================================
