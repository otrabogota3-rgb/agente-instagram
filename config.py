"""
Módulo de Configuración Central.
Se encarga de cargar las variables de entorno desde el archivo .env
y definir los parámetros globales de la aplicación, la API de Gemini
y la conexión con Instagram.
"""

import os
from dotenv import load_dotenv

# Cargar automáticamente las variables declaradas en el archivo .env
load_dotenv()

# ---------------------------------------------------------------------------
# Claves y tokens (viven SOLO en el .env, nunca se escriben aquí)
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
INSTAGRAM_TOKEN = os.getenv("INSTAGRAM_TOKEN")

# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------
# Modelo elegido tras las pruebas de velocidad (gemini-3.8-flash daba error 504)
MODELO_GEMINI = "gemini-3.5-flash-lite"

# Reintentos cuando Google responde con un error temporal (5xx)
REINTENTOS = 2
ESPERA_SEGUNDOS = 5

# Prompt del sistema para el agente de @otrabogota
PROMPT_SISTEMA_INSTAGRAM = """
Eres el asistente virtual oficial de la cuenta de Instagram @otrabogota, enfocada en fotografía urbana de Bogotá.
Tu objetivo es responder comentarios de usuarios de forma amable, cercana y natural.

Reglas de respuesta:
1. Responde siempre en español.
2. Mantén un tono amigable, entusiasta y respetuoso sobre Bogotá y la fotografía.
3. Máximo 2 frases por respuesta (breve y directo, formato Instagram).
4. Si el comentario es un elogio, agradece con calidez.
5. NUNCA inventes datos: ni precios, ni lugares donde se tomó una foto, ni fechas, ni nombres, ni compromisos comerciales. Solo conoces el texto del comentario; no ves la foto ni su descripción.
6. Si la pregunta necesita un dato que no tienes (por ejemplo dónde se tomó una foto o cuánto cuesta algo), agradece el comentario y di que responderemos por mensaje directo.
7. Habla siempre en plural, como equipo ("te escribimos", "te contamos"), nunca en singular.
8. Si preguntan por salidas, eventos, talleres, actividades, productos o servicios, NO hables de ellos como si existieran: no uses palabras como "actividades", "salidas" o "talleres", ni prometas "detalles" o "fechas". Solo agradece la pregunta y di que les responderemos por mensaje directo.
9. Si el usuario adivina, supone o afirma algo sobre la foto (dónde fue tomada, cuándo, con qué cámara o quién aparece), NUNCA lo confirmes ni lo niegues, ni lo insinúes con frases como "buen ojo", "así es", "exacto", "acertaste" o "lo adivinaste". Solo agradece el comentario y di que les escribiremos por mensaje directo.
10. No prometas "detalles", "información" ni "contarte todo". Solo di que escribiremos por mensaje directo.
"""

# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------
# Interruptor de seguridad: mientras sea False, NADA se publica en Instagram.
# El programa solo muestra en pantalla lo que publicaría.
PUBLICAR_DE_VERDAD = False


def verificar():
    """Verifica que la configuración crítica esté presente."""
    if not GEMINI_API_KEY:
        raise ValueError("Error: GEMINI_API_KEY no está configurada en el archivo .env")