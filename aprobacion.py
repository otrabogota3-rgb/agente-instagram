"""
Módulo de Aprobación (Human-in-the-Loop).
Gestión de revisión manual de respuestas sugeridas antes de su publicación oficial.
"""

import ia
import reglas


def obtener_respuesta_sugerida(comentario_texto):
    """
    Determina la mejor respuesta sugerida para un comentario.
    Aplica la jerarquía de decisión:
    1. Revisa si aplica una regla fija o filtro de emoji (reglas.py).
    2. Si no hay regla, consulta a la IA (ia.py).

    Args:
        comentario_texto (str): El texto del comentario recibido.

    Returns:
        str: La respuesta sugerida por reglas o por Gemini.
    """
    # Paso 1: Buscar si responde una regla estática (ahorra costos y tiempo)
    respuesta_regla = reglas.buscar_regla(comentario_texto)
    if respuesta_regla:
        return respuesta_regla

    # Paso 2: Si no hubo coincidencia en reglas, consultar a Gemini
    respuesta_ia = ia.generar_respuesta(comentario_texto)
    if respuesta_ia:
        return respuesta_ia

    # Respuesta de respaldo (fallback) por si la IA o la red fallan
    return "¡Gracias por escribirnos! Te responderemos muy pronto por mensaje directo."


def procesar_aprobacion_consola(comentario):
    """
    Muestra la sugerencia en la consola y solicita interacción humana para decidir.

    Args:
        comentario (dict): Diccionario con keys 'id', 'usuario', 'texto'.

    Returns:
        tuple[bool, str]:
            - bool: True si la respuesta fue aprobada o editada, False si fue rechazada.
            - str: El texto final listo para publicarse (o cadena vacía si se rechazó).
    """
    usuario = comentario.get("usuario", "Anónimo")
    texto = comentario.get("texto", "")

    # Obtener la sugerencia automática
    sugerencia = obtener_respuesta_sugerida(texto)

    print("\n" + "=" * 60)
    print(" 📩 NUEVO COMENTARIO RECIBIDO")
    print(f" Usuario: @{usuario}")
    print(f" Comentario: \"{texto}\"")
    print("-" * 60)
    print(f" 🤖 Respuesta Sugerida: \"{sugerencia}\"")
    print("=" * 60)

    # Menú interactivo: se repite hasta recibir una opción válida
    print("¿Qué deseas hacer?")
    print(" [1] Aprobar y publicar tal cual")
    print(" [2] Editar la respuesta manualmente")
    print(" [3] Rechazar (No responder)")

    while True:
        opcion = input("Selecciona una opción (1/2/3): ").strip()

        if opcion == "1":
            print("\n✅ Respuesta APROBADA.")
            return True, sugerencia

        elif opcion == "2":
            nueva_respuesta = input("\n✏️ Escribe la nueva respuesta ajustada: ").strip()
            if nueva_respuesta:
                print("✅ Respuesta EDITADA y APROBADA.")
                return True, nueva_respuesta
            print("⚠️ Entrada vacía. Se cancela el envío.")
            return False, ""

        elif opcion == "3":
            print("\n❌ Respuesta RECHAZADA. No se enviará nada a Instagram.")
            return False, ""

        else:
            print("⚠️ Opción no válida. Escribe 1, 2 o 3.")