from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
def verificar_estado():
    """Endpoint principal para verificar que el servidor está vivo en Render"""
    return {
        "estado": "activo",
        "cuenta": "@otrabogota",
        "mensaje": "El agente de Instagram está funcionando en la nube 24/7"
    }

@app.post("/ejecutar-agente")
def ejecutar_agente():
    """
    Aquí puedes disparar la lógica de tu agente de forma automática 
    sin depender de la función input() de la consola.
    """
    try:
        # Ejemplo de llamada a tus funciones existentes:
        # comentarios = instagram.obtener_comentarios()
        # respuesta = ia.generar_respuesta(comentarios)
        
        return {
            "exito": True, 
            "detalle": "El ciclo del agente se ejecutó correctamente."
        }
    except Exception as e:
        return {"exito": False, "error": str(e)}