"""
Módulo de Inteligencia Artificial (ia.py).
Maneja la integración con la API de Google Gemini.
"""

import os
import time

from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import errors, types

import config

# Carga forzada buscando el archivo .env en la raíz del proyecto
load_dotenv(find_dotenv(), override=True)

# Instancia privada para el patrón Singleton
_cliente = None

# Tiempo máximo de espera por respuesta, en milisegundos (30 segundos)
_TIMEOUT_MS = 30000


def _obtener_cliente():
    """Crea el cliente de Gemini una sola vez y lo reutiliza."""
    global _cliente
    if _cliente is None:
        api_key = os.getenv("GEMINI_API_KEY", config.GEMINI_API_KEY)

        if api_key:
            api_key = api_key.strip().strip("'").strip('"')

        if not api_key:
            raise ValueError("No se encontró GEMINI_API_KEY. Verifica tu archivo .env")

        _cliente = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=_TIMEOUT_MS),
        )

    return _cliente


def generar_respuesta(comentario_texto):
    """
    Envía el comentario a Gemini y devuelve una respuesta sugerida.
    Reintenta si Google está saturado (error 5xx). Devuelve None si no se logra.
    """
    try:
        cliente = _obtener_cliente()
    except ValueError as error:
        print(f"\n[IA Error] {error}")
        return None

    for intento in range(1, config.REINTENTOS + 1):
        try:
            respuesta = cliente.models.generate_content(
                model=config.MODELO_GEMINI,
                contents=f"<comentario>\n{comentario_texto}\n</comentario>",
                config=types.GenerateContentConfig(
                    system_instruction=config.PROMPT_SISTEMA_INSTAGRAM,
                    temperature=0.3,
                ),
            )
            if respuesta and respuesta.text:
                return respuesta.text.strip()
            return None  # Gemini respondió, pero vacío

        except errors.ServerError as error:
            # Problema temporal del lado de Google: esperar y volver a intentar
            print(f"[IA] Google con problemas (intento {intento}/{config.REINTENTOS}): {error}")
            if intento < config.REINTENTOS:
                time.sleep(config.ESPERA_SEGUNDOS)

        except errors.ClientError as error:
            # Clave, modelo o límites: esperar no lo arregla
            print(f"\n[IA Error] Problema con la solicitud (clave, modelo o límites de uso): {error}")
            return None

        except Exception as error:
            print(f"\n[IA Error] Error inesperado: {error}")
            return None

    print("[IA Error] Se agotaron los reintentos.")
    return None