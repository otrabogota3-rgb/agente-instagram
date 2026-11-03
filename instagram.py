"""
Módulo de comunicación con Instagram.
Se encarga de la capa de interfaz con la red social (o entorno de pruebas),
permitiendo la obtención de comentarios entrantes y la publicación de respuestas aprobadas.
"""

# Lista simulada (Mock) para desarrollo local y pruebas en entorno aislado.
# Representa los comentarios que van llegando a las publicaciones de @otrabogota.
_COMENTARIOS_SIMULADOS = [
    {
        "id": "comment_001",
        "usuario": "carlos_foto",
        "texto": "¿Cuánto cuesta el tiraje de la foto de la Candelaria?"
    },
    {
        "id": "comment_002",
        "usuario": "laura_bogota",
        "texto": "Hermosa vista de los cerros orientales 😍"
    },
    {
        "id": "comment_003",
        "usuario": "andres_urbano",
        "texto": "¿Hacen envíos de los afiches impresos?"
    }
]


def obtener_comentarios():
    """
    Obtiene los comentarios nuevos provenientes de las publicaciones de Instagram.

    Returns:
        list[dict]: Una lista de diccionarios donde cada diccionario contiene:
            - 'id': Identificador único del comentario en Instagram.
            - 'usuario': Nombre de usuario de la persona que comentó.
            - 'texto': Contenido textual o emojis del comentario.
    """
    # En una fase de producción, aquí se realizaría la petición HTTP a la Instagram Graph API.
    # Por ahora, retornamos nuestra estructura simulada para validar el flujo completo.
    print("[Instagram] Consultando nuevos comentarios en la plataforma...")
    return _COMENTARIOS_SIMULADOS


def publicar_respuesta(comentario_id, texto):
    """
    Publica la respuesta aprobada (generada por reglas o por Gemini)
    debajo del comentario correspondiente en Instagram.

    Args:
        comentario_id (str): El ID único del comentario al que se va a responder.
        texto (str): El mensaje de respuesta que fue previamente aprobado por el usuario.

    Returns:
        bool: True si la publicación fue exitosa, False en caso contrario.
    """
    # En producción, aquí se enviará una solicitud POST a la API de Meta con el token de acceso.
    # Para nuestra fase de desarrollo local, simulamos el envío en la consola con claridad.
    print("-" * 50)
    print(f"[Instagram API] Respondiendo al comentario ID: {comentario_id}")
    print(f"[Instagram API] Texto publicado: '{texto}'")
    print("-" * 50)

    # Retornamos True indicando que la acción se completó con éxito
    return True