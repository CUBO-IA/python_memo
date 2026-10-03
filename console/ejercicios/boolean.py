# Ejercicio: pedir nombre y edad por consola

# input() hace una pregunta y espera a que el usuario escriba.
# Lo que se escribe siempre llega como texto (str).
nombre = input("¿Cómo te llamás? ")

# Convertimos la edad a número entero con int() para poder compararla.
edad = int(input("¿Cuántos años tenés? "))

# Mensaje 1: ¿es menor de edad?
if edad < 18:
    print(f"{nombre}, sos menor de edad.")
else:
    print(f"{nombre}, sos mayor de edad.")

# Mensaje 2: ¿la edad es igual a 18?
# La comparación == devuelve True (verdadero) o False (falso).
print(f"¿Tenés exactamente 18 años? {edad == 18}")