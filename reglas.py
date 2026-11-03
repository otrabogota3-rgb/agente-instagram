"""Reglas fijas: respuestas confiables para preguntas frecuentes."""
import unicodedata

# El orden importa: se usa la primera coincidencia.
# Las palabras clave van en minúsculas y SIN tildes.
REGLAS = {
    "envio": "Hacemos domicilios gratis en Bogotá.",
    "domicilio": "Hacemos domicilios gratis en Bogotá.",
    "precio": "¡Hola! Te enviamos el precio por mensaje directo.",
    "cuesta": "¡Hola! Te enviamos el precio por mensaje directo.",
    "horario": "Atendemos de lunes a sábado de 9 a 6.",
    "ubicad": "Estamos ubicados en Bogotá. Te enviamos la dirección por mensaje directo.",
}

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
    texto = normalizar(comentario)
    for palabra, respuesta in REGLAS.items():
        if palabra in texto:
            return respuesta
    return None