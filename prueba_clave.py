import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)
clave = os.getenv("GEMINI_API_KEY", "").strip()

# Solo datos de la clave, nunca la clave misma
print("Empieza con 'AIza':", clave.startswith("AIza"))
print("Longitud:", len(clave))

respuesta = requests.get(
    "https://generativelanguage.googleapis.com/v1beta/models",
    headers={"x-goog-api-key": clave},
    timeout=30,
)
print("Código de respuesta:", respuesta.status_code)

if respuesta.status_code == 200:
    print("\nModelos que sirven para generar texto:")
    for modelo in respuesta.json().get("models", []):
        if "generateContent" in modelo.get("supportedGenerationMethods", []):
            print(" -", modelo["name"])
else:
    print("Respuesta de Google:", respuesta.text[:300])