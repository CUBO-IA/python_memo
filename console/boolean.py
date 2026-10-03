# ============================================================
# BOOLEAN (bool) — Verdadero o Falso
# ============================================================
# Un booleano solo tiene DOS valores posibles:
#   True  (verdadero)
#   False (falso)
# ⚠️ Se escriben con la primera letra en MAYÚSCULA.
#
# Se usa para tomar decisiones: ¿está logueado?, ¿es mayor
# de edad?, ¿tiene saldo?, ¿es una estafa?

# --- 1. Crear booleanos ---
esta_conectado = True
es_estafa = False

print("¿Está conectado?", esta_conectado)
print("¿Es estafa?", es_estafa)

# --- 2. Ver el tipo ---
print("¿Qué tipo es?", type(esta_conectado))  # <class 'bool'>

# --- 3. Las comparaciones DEVUELVEN booleanos ---
edad = 44
print("¿Edad mayor que 18?", edad > 18)    # True
print("¿Edad menor que 18?", edad < 18)    # False
print("¿Edad igual a 44?", edad == 44)     # True  (== compara)
print("¿Edad distinta de 30?", edad != 30) # True
# ⚠️ =  guarda un valor       (edad = 44)
#    == pregunta si es igual (edad == 44)

# --- 4. Operadores lógicos: and, or, not ---
tiene_wallet = True
tiene_saldo = False

# and → True solo si LAS DOS son True
print("¿Puede pagar? (wallet y saldo):", tiene_wallet and tiene_saldo)  # False

# or → True si AL MENOS UNA es True
print("¿Tiene algo? (wallet o saldo):", tiene_wallet or tiene_saldo)    # True

# not → da vuelta el valor
print("¿NO tiene saldo?:", not tiene_saldo)  # True

# --- 5. Usar un booleano para decidir con if ---
if es_estafa:
    print("🚨 Cuidado: este mensaje es una estafa")
else:
    print("✅ Este mensaje parece seguro")

# --- 6. Curiosidad: True vale 1 y False vale 0 ---
print("True + True =", True + True)  # 2

# ============================================================
# 🧪 PRUEBA VOS: cambiá es_estafa a True y volvé a correr.
#    python3 boolean.py
# ============================================================
