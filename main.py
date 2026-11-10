"""
Servidor del agente de @otrabogota (FastAPI).

Es el "mesero" entre la app Android y el cerebro en Python:
- Recibe comentarios (junto con el contexto del post), pide la respuesta sugerida
  al cerebro (reglas fijas + Gemini) y la guarda como BORRADOR en una bandeja.
- La app Android muestra los borradores y el humano decide: aprobar, editar o rechazar.
- IMPORTANTE: por ahora NADA se publica en Instagram. Aprobar solo cambia el estado.

Seguridad:
- Todos los endpoints (menos "/") exigen la cabecera X-API-Key con la clave secreta
  guardada en la variable de entorno AGENTE_API_KEY.
"""

import itertools
import os
import secrets
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

import aprobacion
import config

# Falla al arrancar (y no más tarde) si falta la clave de Gemini.
config.verificar()

app = FastAPI(title="Agente @otrabogota")

# ---------------------------------------------------------------------------
# Estado en memoria (se pierde si el servidor se reinicia)
# ---------------------------------------------------------------------------
estado_agente = {
    "activo": True,  # Activado por defecto para facilitar las pruebas con la app
    "cuenta": "@otrabogota",
}

bandeja_borradores = []
_contador_ids = itertools.count(1)  # 1, 2, 3, ... sin repetir

# Tope de seguridad para los textos (evita mensajes enormes que cuesten dinero en Gemini)
_MAX_TEXTO = 2200


# ---------------------------------------------------------------------------
# Seguridad: clave secreta en la cabecera X-API-Key
# ---------------------------------------------------------------------------
_esquema_clave = APIKeyHeader(name="X-API-Key", auto_error=False)


def exigir_clave(clave_recibida: Optional[str] = Security(_esquema_clave)):
    """Deja pasar solo las peticiones que traen la clave correcta."""
    clave_esperada = os.getenv("AGENTE_API_KEY")

    # Si el servidor no tiene clave configurada, se bloquea TODO (más seguro que dejar abierto)
    if not clave_esperada:
        raise HTTPException(status_code=503, detail="El servidor no tiene AGENTE_API_KEY configurada.")

    # compare_digest compara sin dar pistas por el tiempo que tarda
    if not clave_recibida or not secrets.compare_digest(
        clave_recibida.encode("utf-8"), clave_esperada.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Clave inválida o ausente.")


# ---------------------------------------------------------------------------
# Modelos de datos (lo que el servidor acepta recibir)
# ---------------------------------------------------------------------------
class MensajeSimulado(BaseModel):
    usuario_origen: str = Field(min_length=1, max_length=100)
    texto_mensaje: str = Field(min_length=1, max_length=_MAX_TEXTO)
    post_caption: Optional[str] = Field(default="Publicación de @otrabogota", max_length=500)


class DatosEdicion(BaseModel):
    nuevo_texto: str = Field(min_length=1, max_length=_MAX_TEXTO)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def _buscar_borrador(id_mensaje):
    """Devuelve el borrador pendiente o lanza el error HTTP que corresponda."""
    borrador = next((b for b in bandeja_borradores if b["id_mensaje"] == id_mensaje), None)
    if not borrador:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")
    if borrador["estado"] != "pendiente_aprobacion":
        raise HTTPException(status_code=400, detail="Este borrador ya fue procesado anteriormente.")
    return borrador


def _exigir_agente_activo():
    """Aprobar equivale a publicar, así que no se permite con el agente pausado."""
    if not estado_agente["activo"]:
        raise HTTPException(status_code=403, detail="Acción bloqueada: el agente está PAUSADO.")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def verificar_estado():
    """Público a propósito. No muestra datos sensibles."""
    return {
        "estado": "activo" if estado_agente["activo"] else "pausado",
        "cuenta": estado_agente["cuenta"],
    }


@app.post("/cambiar-estado", dependencies=[Depends(exigir_clave)])
def cambiar_estado(activar: bool):
    estado_agente["activo"] = activar
    estado = "activo" if activar else "pausado"
    return {"resultado": "exito", "nuevo_estado": estado}


@app.post("/simular-mensaje", dependencies=[Depends(exigir_clave)])
def simular_mensaje(datos: MensajeSimulado):
    if not estado_agente["activo"]:
        raise HTTPException(
            status_code=403,
            detail="Acción bloqueada: el agente está PAUSADO. No se pueden procesar mensajes.",
        )

    # Pasamos el comentario y el caption del post a la lógica de aprobación
    sugerencia = aprobacion.obtener_respuesta_sugerida(datos.texto_mensaje, datos.post_caption)

    nuevo_borrador = {
        "id_mensaje": next(_contador_ids),
        "usuario": datos.usuario_origen,
        "mensaje_recibido": datos.texto_mensaje,
        "borrador_gemini": sugerencia,
        "estado": "pendiente_aprobacion",
        "post_caption": datos.post_caption,  # <--- Contexto guardado para la App Android
    }
    bandeja_borradores.append(nuevo_borrador)

    return {
        "resultado": "borrador_creado",
        "advertencia": "El mensaje NO se ha publicado en Instagram. Está esperando aprobación humana.",
        "detalle_borrador": nuevo_borrador,
    }


@app.get("/ver-pendientes", dependencies=[Depends(exigir_clave)])
def ver_pendientes():
    pendientes = [b for b in bandeja_borradores if b["estado"] == "pendiente_aprobacion"]
    return {
        "cuenta": estado_agente["cuenta"],
        "total_pendientes": len(pendientes),
        "bandeja": pendientes,
    }


@app.post("/aprobar-borrador/{id_mensaje}", dependencies=[Depends(exigir_clave)])
def aprobar_borrador(id_mensaje: int):
    _exigir_agente_activo()
    borrador = _buscar_borrador(id_mensaje)

    borrador["estado"] = "aprobado"

    return {
        "resultado": "exito",
        "mensaje": f"Borrador #{id_mensaje} aprobado. Aún NO se publica en Instagram (modo simulación).",
        "contenido_aprobado": borrador["borrador_gemini"],
    }


@app.post("/editar-borrador/{id_mensaje}", dependencies=[Depends(exigir_clave)])
def editar_borrador(id_mensaje: int, datos: DatosEdicion):
    _exigir_agente_activo()
    borrador = _buscar_borrador(id_mensaje)

    borrador["borrador_gemini"] = datos.nuevo_texto.strip()
    borrador["estado"] = "editado_y_aprobado"

    return {
        "resultado": "exito",
        "mensaje": f"Borrador #{id_mensaje} editado y aprobado. Aún NO se publica en Instagram (modo simulación).",
        "contenido_aprobado": borrador["borrador_gemini"],
    }


@app.post("/rechazar-borrador/{id_mensaje}", dependencies=[Depends(exigir_clave)])
def rechazar_borrador(id_mensaje: int):
    borrador = _buscar_borrador(id_mensaje)
    borrador["estado"] = "rechazado"

    return {
        "resultado": "exito",
        "mensaje": f"Borrador #{id_mensaje} rechazado. No se publicará nada.",
    }