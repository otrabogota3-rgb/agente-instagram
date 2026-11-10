"""
Módulo de Aprobación (Human-in-the-Loop).
Gestión de revisión manual de respuestas sugeridas antes de su publicación oficial.
"""

import ia
import reglas


def obtener_respuesta_sugerida(comentario_texto, post_caption=""):
    """
    Determina la mejor respuesta sugerida para un comentario.
    Aplica la jerarquía de decisión:
    1. Revisa si aplica una regla fija o filtro de emoji (reglas.py).
    2. Si no hay regla, consulta a la IA (ia.py).

    Args:
        comentario_texto (str): El texto del comentario recibido.
        post_caption (str): El texto o tema de la publicación de Instagram.

    Returns:
        str: La respuesta sugerida por reglas o por Gemini.
    """
    # Paso 1: Buscar si responde una regla estática (ahorra costos y tiempo)
    respuesta_regla = reglas.buscar_regla(comentario_texto)
    if respuesta_regla:
        return respuesta_regla

    # Paso 2: Si no hubo coincidencia en reglas, consultar a Gemini
    # (Si deseas que la IA tenga en cuenta el contexto del post, se lo puedes inyectar aquí)
    respuesta_ia = ia.generar_respuesta(comentario_texto)
    if respuesta_ia:
        return respuesta_ia

    # Respuesta de respaldo (fallback) por si la IA o la red fallan
    return "¡Gracias por escribirnos! Te responderemos muy pronto por mensaje directo."