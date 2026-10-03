# ============================================================
# LIST — Listas
# ============================================================
# Una lista guarda VARIOS valores en orden, dentro de [ ].
# Se puede CAMBIAR: agregar, quitar, modificar elementos.
#
# Como la lista del súper o el menú de una pupusería.

# --- 1. Crear una lista ---
pupusas = ["queso", "revuelta", "frijol con queso", "loroco"]
numeros = [10, 20, 30]
mezcla = ["Memo", 44, True, 1.72]  # puede mezclar tipos

print("Menú:", pupusas)
print("Números:", numeros)
print("Mezcla:", mezcla)

# --- 2. Ver el tipo ---
print("¿Qué tipo es?", type(pupusas))  # <class 'list'>

# --- 3. Sacar elementos por posición (empieza en 0) ---
print("Primera:", pupusas[0])   # queso
print("Segunda:", pupusas[1])   # revuelta
print("Última:", pupusas[-1])   # loroco

# --- 4. Cuántos elementos tiene ---
print("Cantidad de sabores:", len(pupusas))  # 4

# --- 5. Agregar elementos ---
pupusas.append("chicharrón")  # al final
print("Con chicharrón:", pupusas)

# --- 6. Cambiar un elemento ---
pupusas[0] = "queso con loroco"
print("Cambiamos la primera:", pupusas)

# --- 7. Quitar un elemento ---
pupusas.remove("frijol con queso")
print("Sin frijol con queso:", pupusas)

# --- 8. Preguntar si algo está en la lista ---
print("¿Hay revuelta?", "revuelta" in pupusas)  # True

# --- 9. Recorrer la lista con for ---
print("Menú del día:")
for sabor in pupusas:
    print(" -", sabor)

# --- 10. Ordenar ---
numeros_desordenados = [5, 2, 9, 1]
numeros_desordenados.sort()
print("Ordenados:", numeros_desordenados)  # [1, 2, 5, 9]

# ============================================================
# 🧪 PRUEBA VOS: hacé una lista con 5 canciones que te gusten
#    y recorrela con un for.   python3 list.py
# ============================================================
