# ============================================================
# TUPLE — Tuplas
# ============================================================
# Una tupla es como una lista, pero NO SE PUEDE CAMBIAR
# después de crearla (es "inmutable"). Va entre ( ).
#
# Se usa para datos que no deben cambiar: coordenadas,
# fechas, colores RGB, los días de la semana...

# --- 1. Crear una tupla ---
coordenadas_san_salvador = (13.6929, -89.2182)
dias = ("lunes", "martes", "miércoles", "jueves", "viernes")
color_rojo = (255, 0, 0)

print("Coordenadas:", coordenadas_san_salvador)
print("Días de clase:", dias)
print("Rojo en RGB:", color_rojo)

# --- 2. Ver el tipo ---
print("¿Qué tipo es?", type(dias))  # <class 'tuple'>

# --- 3. Leer elementos (igual que en listas) ---
print("Latitud:", coordenadas_san_salvador[0])
print("Longitud:", coordenadas_san_salvador[1])
print("Cantidad de días:", len(dias))

# --- 4. ⚠️ No se puede cambiar ---
# Si quitás el # de la línea de abajo, Python da un ERROR:
# dias[0] = "domingo"
# TypeError: 'tuple' object does not support item assignment

# --- 5. "Desempacar": sacar los valores en variables ---
latitud, longitud = coordenadas_san_salvador
print(f"Latitud {latitud}, longitud {longitud}")

# --- 6. Lista vs Tupla ---
#   Lista [ ] → se puede cambiar  (menú, carrito de compras)
#   Tupla ( ) → NO se puede cambiar (coordenadas, fechas)

# ============================================================
# 🧪 PRUEBA VOS: quitá el # de dias[0] = "domingo" y mirá el
#    error. Después volvé a ponerlo.   python3 tuple.py
# ============================================================
