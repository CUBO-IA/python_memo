# ============================================================
# Ejercicio: Convertidor de dólares ↔ Bitcoin ↔ sats
# ============================================================
# 1 bitcoin (BTC) se divide en 100,000,000 de "sats" (satoshis).
# Es como el dólar y los centavos, pero con muchos más pedacitos.

SATS_POR_BTC = 100_000_000  # en MAYÚSCULAS porque nunca cambia (constante)

print("===== Convertidor Bitcoin ₿ =====")

# El precio de Bitcoin cambia todo el tiempo, por eso lo pedimos.
# .replace(",", "") quita las comas por si el usuario escribe 84,352
precio_btc = float(input("Precio actual de 1 BTC en dólares: $").replace(",", ""))

print()
print("¿Qué querés convertir?")
print("1. Dólares → Bitcoin y sats")
print("2. Sats → Dólares")
opcion = input("Elegí 1 o 2: ")
print()

if opcion == "1":
    dolares = float(input("¿Cuántos dólares? $").replace(",", ""))

    # División: cuántos bitcoin compro con esos dólares
    bitcoin = dolares / precio_btc

    # Multiplicación: pasar de bitcoin a sats
    sats = bitcoin * SATS_POR_BTC

    print(f"${dolares:.2f} equivalen a:")
    print(f"  {bitcoin:.8f} BTC")        # :.8f = 8 decimales
    print(f"  {round(sats):,} sats")     # :, = separador de miles

elif opcion == "2":
    sats = int(input("¿Cuántos sats? ").replace(",", ""))

    # De sats a bitcoin (división) y de bitcoin a dólares (multiplicación)
    bitcoin = sats / SATS_POR_BTC
    dolares = bitcoin * precio_btc

    print(f"{sats:,} sats equivalen a:")
    print(f"  {bitcoin:.8f} BTC")
    print(f"  ${dolares:.2f}")           # :.2f = 2 decimales, como dinero

else:
    print("Opción no válida. Corré el programa de nuevo y elegí 1 o 2.")

print()
print("Bitoo te recuerda: esto es educación, no consejo de inversión. 😉")
