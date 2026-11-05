"""Reglas fijas: respuestas confiables para preguntas frecuentes."""
import re
import unicodedata

# El orden importa: gana la primera regla que coincida.
# Cada regla es una pareja: (palabras que la activan, respuesta).
# Las palabras van en minúsculas y SIN tildes, y se comparan COMPLETAS:
# "precio" activa la regla, pero "preciosa" no.
# Por eso se escriben las variantes (singular y plural) de forma explícita.
REGLAS = [
    (
        ("envio", "envios", "domicilio", "domicilios"),
        "Hacemos domicilios gratis en Bogotá.",  # TEXTO DE PRUEBA: reemplazar por el real
    ),
    (
        ("precio", "precios", "cuesta", "cuestan"),
        "¡Hola! Te enviamos el precio por mensaje directo.",
    ),
    (
        ("horario", "horarios"),
        "Atendemos de lunes a sábado de 9 a 6.",  # TEXTO DE PRUEBA: reemplazar por el real
    ),
    (
        ("ubicacion", "ubicado", "ubicada", "ubicados", "ubicadas"),
        "Estamos ubicados en Bogotá. Te enviamos la dirección por mensaje directo.",
    ),
]

RESPUESTA_EMOJIS = "¡Gracias por apoyarnos! 🫶"

# Categorías Unicode que forman parte de un emoji (símbolo, modificador, unión)
_CATEGORIAS_EMOJI = ("So", "Sk", "Mn", "Cf")


def es_solo_emojis(comentario):
    """True si el comentario solo tiene emojis (y espacios), sin letras ni números."""
    texto = "".join(comentario.split())  # quita espacios y saltos de línea
    if not texto:
        return False
    hay_emoji = False
    for caracter in texto:
        categoria = unicodedata.category(caracter)
        if categoria not in _CATEGORIAS_EMOJI:
            return False
        if categoria == "So":
            hay_emoji = True
    return hay_emoji


def normalizar(texto):
    """Pasa a minúsculas y quita las tildes para comparar sin errores."""
    texto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def buscar_regla(comentario):
    """Devuelve la respuesta fija que corresponda, o None si ninguna aplica."""
    if es_solo_emojis(comentario):
        return RESPUESTA_EMOJIS

    # Se separa el comentario en palabras sueltas: "¿Cuánto cuesta?" -> {"cuanto", "cuesta"}
    palabras = set(re.findall(r"\w+", normalizar(comentario)))

    for claves, respuesta in REGLAS:
        # Hay coincidencia si el comentario tiene AL MENOS UNA palabra de la regla
        if palabras & set(claves):
            return respuesta
    return None