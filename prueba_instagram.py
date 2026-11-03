import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)
TOKEN = (os.getenv("INSTAGRAM_TOKEN") or "").strip()

# Estos dos valores salen de la documentación de Meta y no los he podido confirmar.
# Si dan error, es lo primero que hay que probar con otros valores.
HOST = "https://graph.facebook.com"
VERSION = "v26.0"


def pedir(ruta, parametros=None):
    """Hace una petición de LECTURA (GET) a la API y devuelve el JSON."""
    url = f"{HOST}/{VERSION}/{ruta}"
    # El token va en un encabezado, no en la URL, para que nunca se imprima
    respuesta = requests.get(
        url,
        params=parametros,
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=30,
    )
    print(f"\nGET /{ruta} -> código {respuesta.status_code}")
    try:
        return respuesta.json()
    except ValueError:
        print("La respuesta no es JSON:", respuesta.text[:300])
        return None


if not TOKEN:
    raise SystemExit("Falta INSTAGRAM_TOKEN en el .env")

# Paso 1: ¿qué cuenta de Instagram tiene asignada el token?
cuentas = pedir("me/assigned_instagram_accounts", {"fields": "id,username"})
print(cuentas)
if not cuentas or not cuentas.get("data"):
    raise SystemExit("\nNo se obtuvo ninguna cuenta. Revisa el mensaje de arriba.")

cuenta_id = cuentas["data"][0]["id"]

# Paso 2: últimas publicaciones
posts = pedir(f"{cuenta_id}/media", {"fields": "id,caption,timestamp", "limit": 3})
if not posts or not posts.get("data"):
    print(posts)
    raise SystemExit("\nNo se obtuvieron publicaciones. Revisa el mensaje de arriba.")

for post in posts["data"]:
    descripcion = (post.get("caption") or "")[:40]
    print(f" - {post['id']} | {post.get('timestamp')} | {descripcion}")

# Paso 3: comentarios de cada una de las publicaciones
for post in posts["data"]:
    comentarios = pedir(f"{post['id']}/comments", {"fields": "id,text,username,timestamp"})
    if comentarios and "error" in comentarios:
        print("Error:", comentarios["error"].get("message"))
        continue
    lista = comentarios.get("data", []) if comentarios else []
    print(f"Publicación {post['id']}: {len(lista)} comentarios")