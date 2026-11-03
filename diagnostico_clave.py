import os
from dotenv import load_dotenv, find_dotenv

ruta = find_dotenv()
print("Archivo .env usado:", ruta or "NO ENCONTRADO")
load_dotenv(ruta, override=True)

clave = os.getenv("GEMINI_API_KEY")
token_ig = os.getenv("INSTAGRAM_TOKEN")

if not clave:
    print("GEMINI_API_KEY: no existe o está vacía")
else:
    print("Longitud de la clave:", len(clave))
    print("Tiene espacios al inicio o al final:", clave != clave.strip())
    print("Tiene comillas:", "'" in clave or '"' in clave)
    print("Es igual al token de Instagram:", clave == token_ig)

if ruta:
    with open(ruta, encoding="utf-8") as archivo:
        lineas = [l for l in archivo if l.strip().startswith("GEMINI_API_KEY")]
    print("Líneas GEMINI_API_KEY en el .env:", len(lineas))