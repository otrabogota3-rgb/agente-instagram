import time
from google import genai
from google.genai import types
import config

COMENTARIOS = [
    "Qué buena foto, ¿dónde la tomaron?",
    "Hermosa vista de los cerros orientales 😍",
    "¿Qué cámara usan?",
    "¿Cuándo es la próxima salida fotográfica?",
]
MODELOS = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]

# timeout en milisegundos: si Google no responde en 30 s, se corta
cliente = genai.Client(
    api_key=config.GEMINI_API_KEY.strip(),
    http_options=types.HttpOptions(timeout=30000),
)

for modelo in MODELOS:
    print(f"\n===== {modelo} =====")
    for texto in COMENTARIOS:
        inicio = time.time()
        try:
            respuesta = cliente.models.generate_content(
                model=modelo,
                contents=texto,
                config=types.GenerateContentConfig(
                    system_instruction=config.PROMPT_SISTEMA_INSTAGRAM,
                    temperature=0.3,
                ),
            )
            print(f"\nComentario: {texto}")
            print(f"Respuesta: {respuesta.text}")
            print(f"Tardó {time.time() - inicio:.1f} s")
        except Exception as error:
            print(f"\nComentario: {texto}")
            print(f"ERROR tras {time.time() - inicio:.1f} s -> {str(error)[:200]}")