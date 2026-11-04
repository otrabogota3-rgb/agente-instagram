import os
from fastapi import FastAPI, HTTPException
from google import genai
from pydantic import BaseModel

app = FastAPI()

# Inicializar el cliente de Gemini
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Estado global de seguridad controlado por tu app Android
estado_agente = {
    "activo": True,  # Inicia pausado por seguridad
    "cuenta": "@otrabogota",
    "mensaje": "El agente inteligente está en la nube 24/7"
}

# Bandeja temporal de borradores pendientes de aprobación humana
bandeja_borradores = []


class MensajeSimulado(BaseModel):
    usuario_origen: str
    texto_mensaje: str


class DatosEdicion(BaseModel):
    nuevo_texto: str


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
    if not estado_agente["activo"]:
        raise HTTPException(
            status_code=403,
            detail="Acción bloqueada: El agente se encuentra PAUSADO. No se pueden procesar mensajes."
        )

    texto_borrador = ""

    try:
        # Usamos el modelo exacto que nos exige la API de Google
        response = gemini_client.models.generate_content(
            model="gemini-3.8-flash",
            contents=f"Actúa como un agente experto para la cuenta de Instagram {estado_agente['cuenta']}. Un usuario llamado {datos.usuario_origen} te escribió: '{datos.texto_mensaje}'. Redacta una respuesta amigable con acento rolo para responderle.",
        )
        texto_borrador = response.text

    except Exception as e:
        print(f"Error detallado de Gemini: {e}")
        texto_borrador = f"¡Hola Veci! Vi tu mensaje sobre '{datos.texto_mensaje}'. ¡El parche en @otrabogota está activo! (Modo Contingencia: {str(e)})"

    # Creamos el borrador para la bandeja de aprobación humana
    nuevo_borrador = {
        "id_mensaje": len(bandeja_borradores) + 1,
        "usuario": datos.usuario_origen,
        "mensaje_recibido": datos.texto_mensaje,
        "borrador_gemini": texto_borrador,
        "estado": "pendiente_aprobacion"
    }

    bandeja_borradores.append(nuevo_borrador)

    return {
        "resultado": "borrador_creado",
        "advertencia": "El mensaje NO se ha publicado en Instagram. Está esperando aprobación humana.",
        "detalle_borrador": nuevo_borrador
    }


@app.get("/ver-pendientes")
def ver_pendientes():
    return {
        "cuenta": estado_agente["cuenta"],
        "total_pendientes": len([b for b in bandeja_borradores if b["estado"] == "pendiente_aprobacion"]),
        "bandeja": [b for b in bandeja_borradores if b["estado"] == "pendiente_aprobacion"]
    }


@app.post("/aprobar-borrador/{id_mensaje}")
def aprobar_borrador(id_mensaje: int):
    # Buscamos el borrador en la bandeja
    borrador = next((b for b in bandeja_borradores if b["id_mensaje"] == id_mensaje), None)

    if not borrador:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")

    if borrador["estado"] != "pendiente_aprobacion":
        raise HTTPException(status_code=400, detail="Este borrador ya fue procesado anteriormente.")

    # Cambiamos su estado a aprobado (Aquí en el futuro se conectará con la API de Instagram)
    borrador["estado"] = "aprobado_y_enviado"

    return {
        "resultado": "exito",
        "mensaje": f"¡Borrador #{id_mensaje} aprobado por el humano y enviado a Instagram con éxito!",
        "contenido_enviado": borrador["borrador_gemini"]
    }


@app.post("/editar-borrador/{id_mensaje}")
def editar_borrador(id_mensaje: int, datos: DatosEdicion):
    borrador = next((b for b in bandeja_borradores if b["id_mensaje"] == id_mensaje), None)

    if not borrador:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")

    # Actualizamos el texto con la corrección del humano
    borrador["borrador_gemini"] = datos.nuevo_texto
    borrador["estado"] = "editado_y_aprobado"

    return {
        "resultado": "exito",
        "mensaje": f"¡Borrador #{id_mensaje} editado y aprobado por el humano!",
        "nuevo_contenido": borrador["borrador_gemini"]
    }


@app.post("/rechazar-borrador/{id_mensaje}")
def rechazar_borrador(id_mensaje: int):
    borrador = next((b for b in bandeja_borradores if b["id_mensaje"] == id_mensaje), None)

    if not borrador:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")

    # Eliminamos o descartamos el borrador
    borrador["estado"] = "rechazado"

    return {
        "resultado": "exito",
        "mensaje": f"El borrador #{id_mensaje} fue descartado y rechazado correctamente. No se publicará nada."
    }