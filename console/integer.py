# ============================================================
# INTEGER (int) — Números enteros
# ============================================================
# Un entero es un número SIN decimales: puede ser positivo,
# negativo o cero. Ejemplos: 5, -20, 0, 1000000
#
# Se usa para contar cosas: edad, cantidad de productos,
# número de estudiantes, años...

# --- 1. Crear una variable entera ---
edad = 44
estudiantes = 30
temperatura = -3

print("Edad:", edad)
print("Estudiantes:", estudiantes)
print("Temperatura:", temperatura)

# --- 2. Ver el tipo de dato con type() ---
# type() te dice qué tipo de dato es una variable.
print("¿Qué tipo es edad?", type(edad))  # <class 'int'>

# --- 3. Operaciones matemáticas ---
a = 10
b = 3

print("Suma:", a + b)               # 13
print("Resta:", a - b)              # 7
print("Multiplicación:", a * b)     # 30
print("División:", a / b)           # 3.333... (¡ojo! da decimal)
print("División entera:", a // b)   # 3  (quita los decimales)
print("Residuo (módulo):", a % b)   # 1  (lo que sobra al dividir)
print("Potencia:", a ** b)          # 1000 (10 x 10 x 10)

# --- 4. Números grandes ---
# Podés usar guion bajo para que se lean mejor. Python lo ignora.
poblacion_el_salvador = 6_300_000
print("Población:", poblacion_el_salvador)

# --- 5. Convertir texto a entero con int() ---
texto = "25"
numero = int(texto)
print("Texto convertido a número + 5 =", numero + 5)  # 30

# ============================================================
# 🧪 PRUEBA VOS: cambiá los valores de a y b y volvé a correr:
#    python3 integer.py
# ============================================================
