import os
from fastapi import FastAPI, HTTPException
from google import genai
from pydantic import BaseModel

app = FastAPI()

# Inicializar el cliente de Gemini
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Estado global de seguridad controlado por tu app Android
estado_agente = {
    "activo": False,  # Inicia pausado por seguridad
    "cuenta": "@otrabogota",
    "mensaje": "El agente inteligente está en la nube 24/7"
}

# Bandeja temporal de borradores pendientes de aprobación humana
bandeja_borradores = []

class MensajeSimulado(BaseModel):
    usuario_origen: str
    texto_mensaje: str


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


@app.post("/simular-mensaje")
def simular_mensaje(datos: MensajeSimulado):
    # REGLA DE ORO DE SEGURIDAD: Si el interruptor está apagado, no se hace nada
    if not estado_agente["activo"]:
        raise HTTPException(
            status_code=403,
            detail="Acción bloqueada: El agente se encuentra PAUSADO. No se pueden procesar mensajes."
        )

    try:
        # Gemini redacta UN BORRADOR de respuesta (No se publica automáticamente)
        response = gemini_client.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"Actúa como un agente experto para la cuenta de Instagram {estado_agente['cuenta']}. Un usuario llamado {datos.usuario_origen} te escribió: '{datos.texto_mensaje}'. Redacta una respuesta amigable con acento rolo para responderle.",
        )

        # Creamos el borrador para la bandeja de aprobación
        nuevo_borrador = {
            "id_mensaje": len(bandeja_borradores) + 1,
            "usuario": datos.usuario_origen,
            "mensaje_recibido": datos.texto_mensaje,
            "borrador_gemini": response.text,
            "estado": "pendiente_aprobacion"
        }

        bandeja_borradores.append(nuevo_borrador)

        return {
            "resultado": "borrador_creado",
            "advertencia": "El mensaje NO se ha publicado en Instagram. Está esperando aprobación humana.",
            "detalle_borrador": nuevo_borrador
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar borrador con Gemini: {str(e)}")


@app.get("/ver-pendientes")
def ver_pendientes():
    return {
        "cuenta": estado_agente["cuenta"],
        "total_pendientes": len(bandeja_borradores),
        "bandeja": bandeja_borradores
    }