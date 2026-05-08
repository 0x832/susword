import itertools
import random
import unicodedata


# ─────────────────────────────────────────────
# SUSTITUCIONES PONDERADAS
# Cada entrada: (sustituto, peso)
# Mayor peso → más probable en modo realista
# ─────────────────────────────────────────────
SUSTITUCIONES = {
    'a': [('a', 10), ('A', 6), ('4', 5), ('@', 4), ('á', 2), ('^', 1), ('/-\\', 1)],
    'e': [('e', 10), ('E', 6), ('3', 5), ('€', 2), ('&', 1)],
    'i': [('i', 10), ('I', 6), ('1', 5), ('!', 3), ('|', 1), ('¡', 1)],
    'o': [('o', 10), ('O', 6), ('0', 5), ('()', 1), ('*', 1)],
    's': [('s', 10), ('S', 6), ('5', 5), ('$', 4), ('z', 2), ('Z', 1)],
    't': [('t', 10), ('T', 6), ('7', 5), ('+', 2)],
    'b': [('b', 10), ('B', 6), ('8', 3), ('|3', 1)],
    'g': [('g', 10), ('G', 6), ('6', 4), ('9', 3)],
    'l': [('l', 10), ('L', 6), ('1', 4), ('|', 2)],
    'c': [('c', 10), ('C', 6), ('(', 2), ('k', 3), ('K', 2)],
    'v': [('v', 10), ('V', 6), ('\\/', 1)],
    'r': [('r', 10), ('R', 6), ('|2', 1)],
    'n': [('n', 10), ('N', 6), ('^/', 1)],
    'u': [('u', 10), ('U', 6), ('ü', 2), ('Ü', 1)],
    'x': [('x', 10), ('X', 6), ('*', 2), ('%', 1)],
    'z': [('z', 10), ('Z', 6), ('2', 4)],
    'p': [('p', 10), ('P', 6), ('|°', 1)],
    'h': [('h', 10), ('H', 6), ('#', 2)],
    'k': [('k', 10), ('K', 6), ('|<', 1)],
    'w': [('w', 10), ('W', 6), ('vv', 2), ('VV', 1)],
    'f': [('f', 10), ('F', 6), ('ph', 2)],
    'm': [('m', 10), ('M', 6), ('|v|', 1)],
    'q': [('q', 10), ('Q', 6), ('0,', 1)],
    'd': [('d', 10), ('D', 6), ('|)', 1)],
    'y': [('y', 10), ('Y', 6), ('`/', 1)],
    'j': [('j', 10), ('J', 6), ('_|', 1)],
}

# Sufijos y prefijos comunes que usan las personas reales
SUFIJOS_COMUNES = [
    '', '1', '12', '123', '1234', '!', '!!',
    '2024', '2025', '2026', '#1', '.', '_',
    '01', '007', '99', '00',
]

PREFIJOS_COMUNES = [
    '', 'el', 'la', 'mr', 'the', 'sr', 'dr', 'super', 'mega',
]


def normalizar(c: str) -> str:
    return unicodedata.normalize('NFD', c).encode('ascii', 'ignore').decode('ascii').lower()


def sustitucion_ponderada(letra: str) -> str:
    """Elige una sustitución usando pesos (resultado más realista)."""
    clave = normalizar(letra)
    if clave not in SUSTITUCIONES:
        return random.choice([letra.lower(), letra.upper()])
    opciones, pesos = zip(*SUSTITUCIONES[clave])
    return random.choices(opciones, weights=pesos, k=1)[0]


def calcular_legibilidad(variacion: str, original: str) -> float:
    """
    Puntuación 0-1.
    Penaliza variaciones con demasiados símbolos raros seguidos
    o que se alejan mucho del original en longitud.
    """
    score = 1.0

    # Penalizar si la longitud es el doble o más (ej: muchos '/-\\')
    if len(variacion) > len(original) * 2.2:
        score -= 0.4

    # Penalizar símbolos extraños consecutivos
    raros = set('|\\/<>^°{}[]')
    raros_seguidos = 0
    for c in variacion:
        if c in raros:
            raros_seguidos += 1
            if raros_seguidos >= 3:
                score -= 0.3
                break
        else:
            raros_seguidos = 0

    # Penalizar si todas las letras fueron sustituidas por símbolo
    letras_alfa = sum(1 for c in variacion if c.isalpha())
    if letras_alfa == 0 and len(variacion) > 0:
        score -= 0.5

    return max(score, 0.0)


def generar_variacion_realista(palabra: str, intensidad: float = 0.4) -> str:
    """
    Genera UNA variación realista de la palabra.
    intensidad: 0.0 = casi nada cambia, 1.0 = todo cambia
    """
    resultado = []
    for letra in palabra:
        clave = normalizar(letra)
        # Solo sustituir con probabilidad = intensidad
        if clave in SUSTITUCIONES and random.random() < intensidad:
            resultado.append(sustitucion_ponderada(letra))
        else:
            # Mantener original con posible cambio de capitalización
            if random.random() < 0.15:
                resultado.append(letra.upper() if letra.islower() else letra.lower())
            else:
                resultado.append(letra)
    return "".join(resultado)


def aplicar_patrones_humanos(variacion: str) -> list[str]:
    """
    Devuelve variantes con patrones comunes reales:
    - Primera letra mayúscula
    - Todo mayúsculas
    - Con sufijo numérico
    - Con prefijo
    """
    variantes = [variacion]

    # Capitalizar primera letra
    if variacion and not variacion[0].isupper():
        variantes.append(variacion[0].upper() + variacion[1:])

    # Todo mayúsculas (si tiene sentido)
    variantes.append(variacion.upper())

    # Sufijos comunes (elegir 2 aleatorios)
    for suf in random.sample(SUFIJOS_COMUNES, k=min(3, len(SUFIJOS_COMUNES))):
        if suf:
            variantes.append(variacion + suf)
            # También con primera mayúscula + sufijo
            if variacion:
                variantes.append(variacion[0].upper() + variacion[1:] + suf)

    return variantes


def generar_variaciones():
    palabra = input("Introduce la palabra base: ").strip()
    if not palabra:
        print("¡No has introducido nada!")
        return

    print(f"\n[*] Palabra base: '{palabra}'")
    print("\n¿Qué modo quieres?")
    print(" [1] Realista (variaciones que una persona real usaría)")
    print(" [2] Exhaustivo (todas las combinaciones posibles, limitadas)")
    print(" [3] Ambos")
    modo = input("Modo (1/2/3): ").strip() or "1"

    print("\n¿Intensidad de sustitución? (0.1 = mínima, 1.0 = máxima)")
    print(" Recomendado: 0.3-0.5 para resultados realistas")
    try:
        intensidad = float(input("Intensidad [0.3]: ").strip() or "0.3")
        intensidad = max(0.05, min(1.0, intensidad))
    except ValueError:
        intensidad = 0.3

    LIMITE_REALISTA = 10_000
    LIMITE_EXHAUSTIVO = 50_000
    LIMITE_MOSTRAR = 30

    resultados_finales = []

    # ── MODO REALISTA ──────────────────────────────────────────────────────────
    if modo in ('1', '3'):
        print(f"\n[*] Generando variaciones realistas (intensidad={intensidad})...")
        realistas = set()
        realistas.add(palabra) # incluir original

        intentos = 0
        while len(realistas) < LIMITE_REALISTA and intentos < LIMITE_REALISTA * 5:
            variacion = generar_variacion_realista(palabra, intensidad)
            legibilidad = calcular_legibilidad(variacion, palabra)

            # Solo aceptar si la legibilidad supera el umbral
            if legibilidad >= 0.6:
                realistas.add(variacion)
                # Con probabilidad añadir patrones humanos
                if random.random() < 0.3:
                    for v in aplicar_patrones_humanos(variacion):
                        if calcular_legibilidad(v, palabra) >= 0.5:
                            realistas.add(v)
            intentos += 1

        realistas = list(realistas)
        random.shuffle(realistas)
        resultados_finales.extend(realistas)

        print(f" → {len(realistas):,} variaciones realistas generadas")

    # ── MODO EXHAUSTIVO ────────────────────────────────────────────────────────
    if modo in ('2', '3'):
        print(f"\n[*] Generando variaciones exhaustivas...")
        opciones_ex = []
        for letra in palabra:
            clave = normalizar(letra)
            if clave in SUSTITUCIONES:
                opciones_ex.append([s for s, _ in SUSTITUCIONES[clave]])
            else:
                opciones_ex.append([letra.lower(), letra.upper()])

        total_posible = 1
        for op in opciones_ex:
            total_posible *= len(op)

        print(f" → Combinaciones posibles: {total_posible:,}")

        if total_posible <= LIMITE_EXHAUSTIVO:
            todas = list(itertools.product(*opciones_ex))
            random.shuffle(todas)
            exhaustivas = ["".join(c) for c in todas]
        else:
            exhaustivas_set = set()
            intentos = 0
            while len(exhaustivas_set) < LIMITE_EXHAUSTIVO and intentos < LIMITE_EXHAUSTIVO * 3:
                combo = "".join(random.choice(op) for op in opciones_ex)
                exhaustivas_set.add(combo)
                intentos += 1
            exhaustivas = list(exhaustivas_set)
            random.shuffle(exhaustivas)

        resultados_finales.extend(exhaustivas)
        print(f" → {len(exhaustivas):,} variaciones exhaustivas generadas")

    # ── DEDUPLICAR ─────────────────────────────────────────────────────────────
    resultados_finales = list(dict.fromkeys(resultados_finales)) # preserva orden, quita dupes
    random.shuffle(resultados_finales)

    # ── MOSTRAR MUESTRA ────────────────────────────────────────────────────────
    print(f"\n{'─'*45}")
    print(f" MUESTRA — primeras {LIMITE_MOSTRAR} variaciones")
    print(f"{'─'*45}")
    for r in resultados_finales[:LIMITE_MOSTRAR]:
        print(f" {r}")
    print(f"{'─'*45}")
    print(f" Mostrando {min(LIMITE_MOSTRAR, len(resultados_finales))} de {len(resultados_finales):,} variaciones")

    # ── EXPORTAR ───────────────────────────────────────────────────────────────
    nombre_archivo = f"variaciones_{palabra[:10].replace(' ', '_')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(f"# Variaciones de: {palabra}\n")
        f.write(f"# Modo: {['','Realista','Exhaustivo','Ambos'][int(modo)]}\n")
        f.write(f"# Intensidad: {intensidad}\n")
        f.write(f"# Total generadas: {len(resultados_finales)}\n\n")
        for linea in resultados_finales:
            f.write(linea + "\n")

    print(f"\n[✓] {len(resultados_finales):,} variaciones exportadas a: {nombre_archivo}\n")


if __name__ == "__main__":
    generar_variaciones()
