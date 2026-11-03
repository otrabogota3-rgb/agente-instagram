"""
Módulo Principal (main.py).
Ejecuta el ciclo completo de prueba del agente de Instagram:
1. Obtiene comentarios entrantes de instagram.py.
2. Procesa cada comentario en aprobacion.py (Humano en el ciclo).
3. Si el usuario aprueba o edita, publica la respuesta vía instagram.py.
"""

import aprobacion
import instagram


def ejecutar_agente():
    """Ejecuta el flujo principal de procesamiento de comentarios."""
    print("\n🚀 INICIANDO AGENTE DE INSTAGRAM PARA @otrabogota...")

    # Paso 1: Consultar los comentarios pendientes
    comentarios = instagram.obtener_comentarios()

    if not comentarios:
        print("[Main] No hay nuevos comentarios por procesar.")
        return

    print(f"[Main] Se encontraron {len(comentarios)} comentarios para revisar.\n")

    # Paso 2: Procesar cada comentario de forma secuencial
    for comentario in comentarios:
        # Llamamos al módulo de aprobación para que nos muestre la sugerencia
        # y nos permita aprobar (1), editar (2) o rechazar (3)
        fue_aprobado, respuesta_final = aprobacion.procesar_aprobacion_consola(comentario)

        # Paso 3: Si se dio el visto bueno, enviamos a publicar
        if fue_aprobado:
            instagram.publicar_respuesta(
                comentario_id=comentario["id"],
                texto=respuesta_final
            )
        else:
            print(f"[Main] Se omitió la respuesta al comentario ID: {comentario['id']}\n")

    print("\n✨ Proceso finalizado. Todos los comentarios fueron revisados.")


if __name__ == "__main__":
    ejecutar_agente()