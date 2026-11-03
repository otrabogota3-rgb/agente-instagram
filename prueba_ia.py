import time
import ia
import config

comentarios = [
    "Qué buena foto, ¿dónde la tomaron?",
    "Hermosa vista de los cerros orientales 😍",
    "¿Qué cámara usan?",
]

print("Modelo:", config.MODELO_GEMINI)

for texto in comentarios:
    inicio = time.time()
    respuesta = ia.generar_respuesta(texto)
    print(f"\nComentario: {texto}")
    print(f"Respuesta: {respuesta}")
    print(f"Tardó {time.time() - inicio:.1f} segundos")