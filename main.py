import os
from fastapi import FastAPI, HTTPException
from google import genai

app = FastAPI()

# Inicializar el cliente de Gemini usando la variable de entorno configurada en Render
# (Asegúrate de agregar GEMINI_API_KEY en las Environment Variables de tu panel en Render)
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Estado global de seguridad controlado por tu app Android
estado_agente = {
    "activo": False,  # Inicia pausado por seguridad
    "cuenta": "@otrabogota",
    "mensaje": "El agente inteligente está en la nube 24/7"
}


@app.get("/")
def verificar_estado():
    return {
        "estado": "activo" if estado_agente["activo"] else "pausado",
        "cuenta": estado_agente["cuenta"],
        "mensaje": estado_agente["mensaje"]
    }


@app.post("/cambiar-estado")
def cambiar_estado(activar: bool):
    estado_agente["activo"] = activar
    estado = "activo" if activar else "pausado"
    return {
        "resultado": "exito",
        "nuevo_estado": estado,
        "mensaje": f"El agente ha sido {estado} correctamente."
    }


@app.post("/ejecutar-agente")
def ejecutar_agente(prompt_usuario: str):
    # REGLA DE ORO DE SEGURIDAD: Si el interruptor en el cel está apagado, el agente no hace nada
    if not estado_agente["activo"]:
        raise HTTPException(
            status_code=403,
            detail="Acción bloqueada: El agente se encuentra PAUSADO desde el panel de control móvil."
        )

    try:
        # Llamada inteligente a Gemini
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Actúa como un agente experto para la cuenta de Instagram {estado_agente['cuenta']}. Responde a lo siguiente: {prompt_usuario}",
        )

        return {
            "estado": "ejecutado_con_exito",
            "cuenta": estado_agente["cuenta"],
            "respuesta_gemini": response.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar con Gemini: {str(e)}")