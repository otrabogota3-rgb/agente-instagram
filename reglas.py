"""Reglas fijas: respuestas confiables para preguntas frecuentes."""
import re
import unicodedata

# Respuesta neutra: no afirma nada, no promete nada, solo manda a DM.
# Mientras no tengas los datos REALES (precios, domicilios, horarios, dirección),
# TODAS las reglas usan esta respuesta. Así nunca se aprueba un dato inventado.
RESPUESTA_DM = "Gracias por preguntar. Te escribimos por DM."

# El orden importa: gana la primera regla que coincida.
# Cada regla es una pareja: (palabras que la activan, respuesta).
# Las palabras van en minúsculas y SIN tildes, y se comparan COMPLETAS:
# "precio" activa la regla, pero "preciosa" no.
# Por eso se escriben las variantes (singular y plural) de forma explícita.
#
# CUANDO TENGAS UN DATO REAL, cambia RESPUESTA_DM de esa regla por el texto verdadero.
# Ejemplo: en la regla de horario, escribe el horario de verdad.
REGLAS = [
    (
        ("envio", "envios", "domicilio", "domicilios"),
        RESPUESTA_DM,
    ),
    (
        ("precio", "precios", "cuesta", "cuestan"),
        RESPUESTA_DM,
    ),
    (
        ("horario", "horarios"),
        RESPUESTA_DM,
    ),
    (
        # "ubicación" puede significar dónde se tomó la foto o dónde queda un local:
        # en los dos casos la respuesta segura es mandar a DM.
        ("ubicacion", "ubicado", "ubicada", "ubicados", "ubicadas"),
        RESPUESTA_DM,
    ),
]

# Para comentarios que solo traen emojis. Va en la voz de la cuenta, sin frases de empresa.
RESPUESTA_EMOJIS = "Bogotá en su punto 🫶"

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