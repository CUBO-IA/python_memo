# ============================================================
# FLOAT — Números decimales
# ============================================================
# Un float es un número CON punto decimal.
# Ejemplos: 3.14, -0.5, 19.99, 1.0
#
# Se usa para precios, medidas, porcentajes, temperaturas...
# ⚠️ En Python el decimal se escribe con PUNTO, no con coma.

# --- 1. Crear una variable decimal ---
precio_pupusa = 0.75
estatura = 1.72
precio_bitcoin = 65432.10

print("Precio de una pupusa: $", precio_pupusa)
print("Estatura:", estatura, "m")
print("Precio de Bitcoin: $", precio_bitcoin)

# --- 2. Ver el tipo ---
print("¿Qué tipo es estatura?", type(estatura))  # <class 'float'>

# --- 3. Un entero con .0 también es float ---
print("¿Qué tipo es 1.0?", type(1.0))  # float, aunque "parezca" entero

# --- 4. Operaciones ---
pupusas = 4
total = pupusas * precio_pupusa
print("4 pupusas cuestan: $", total)  # 3.0

# --- 5. Redondear con round() ---
pi = 3.14159265
print("Pi redondeado a 2 decimales:", round(pi, 2))  # 3.14

# --- 6. Curiosidad: los decimales no son 100% exactos ---
# La compu guarda los decimales en binario y a veces hay
# diferencias muy pequeñas. Es normal en todos los lenguajes.
print("0.1 + 0.2 =", 0.1 + 0.2)  # 0.30000000000000004 😅
print("Redondeado:", round(0.1 + 0.2, 2))  # 0.3

# --- 7. Convertir texto a decimal con float() ---
texto = "2.50"
numero = float(texto)
print("Texto convertido a decimal x 2 =", numero * 2)  # 5.0

# ============================================================
# 🧪 PRUEBA VOS: calculá cuánto cuestan 12 pupusas.
#    python3 float.py
# ============================================================
