"""
Servidor del agente de @otrabogota (FastAPI).

Es el "mesero" entre la app Android, Instagram (Meta) y el cerebro en Python:
- Recibe comentarios/mensajes (simulados o vía Webhook real de Meta), pide la respuesta
  sugerida al cerebro en segundo plano (BackgroundTasks) y la guarda en SQLite.
- Garantiza idempotencia mediante instagram_message_id para evitar duplicados si Meta reintenta.
- La app Android muestra los borradores y el humano decide: aprobar, editar o rechazar.
"""

import os
import secrets
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request, Security
from fastapi.responses import PlainTextResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import aprobacion
import config
from database import AsyncSessionLocal, Base, engine, get_db
from models import MensajePendienteDB

# Falla al arrancar (y no más tarde) si falta la clave de Gemini.
config.verificar()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Base de datos SQLite inicializada correctamente.")
    yield


# ÚNICA instancia de FastAPI con el lifespan integrado
app = FastAPI(lifespan=lifespan)


# ---------------------------------------------------------------------------
# Estado en memoria (arranca PAUSADO por seguridad en producción)
# ---------------------------------------------------------------------------
estado_agente = {
    "activo": os.getenv("AGENTE_ACTIVO_AL_INICIAR", "false").strip().lower() == "true",
    "cuenta": "@otrabogota",
}

_MAX_TEXTO = 2200


# ---------------------------------------------------------------------------
# Seguridad: clave secreta en la cabecera X-API-Key (para tu App Android)
# ---------------------------------------------------------------------------
_esquema_clave = APIKeyHeader(name="X-API-Key", auto_error=False)


def exigir_clave(clave_recibida: Optional[str] = Security(_esquema_clave)):
    """Deja pasar solo las peticiones de la App Android que traen la clave correcta."""
    clave_esperada = os.getenv("AGENTE_API_KEY")

    if not clave_esperada:
        raise HTTPException(
            status_code=503,
            detail="El servidor no tiene AGENTE_API_KEY configurada.",
        )

    if not clave_recibida or not secrets.compare_digest(
        clave_recibida.encode("utf-8"), clave_esperada.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Clave inválida o ausente.")


# ---------------------------------------------------------------------------
# Modelos de datos
# ---------------------------------------------------------------------------
class MensajeSimulado(BaseModel):
    usuario_origen: str = Field(min_length=1, max_length=100)
    texto_mensaje: str = Field(min_length=1, max_length=_MAX_TEXTO)
    post_caption: Optional[str] = Field(
        default="Publicación de @otrabogota", max_length=500
    )


class DatosEdicion(BaseModel):
    nuevo_texto: str = Field(min_length=1, max_length=_MAX_TEXTO)


# ---------------------------------------------------------------------------
# Utilidades de Base de Datos
# ---------------------------------------------------------------------------
async def _buscar_borrador(db: AsyncSession, id_mensaje: int):
    resultado = await db.execute(
        select(MensajePendienteDB).filter_by(id=id_mensaje)
    )
    borrador = resultado.scalars().first()

    if not borrador:
        raise HTTPException(status_code=404, detail="Borrador no encontrado.")
    if borrador.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Este borrador ya fue procesado anteriormente.",
        )
    return borrador


def _exigir_agente_activo():
    if not estado_agente["activo"]:
        raise HTTPException(
            status_code=403, detail="Acción bloqueada: el agente está PAUSADO."
        )


# ---------------------------------------------------------------------------
# Tarea en Segundo Plano (BackgroundTask) para IA y SQLite
# ---------------------------------------------------------------------------
async def procesar_y_guardar_borrador(
    ig_message_id: str,
    sender_id: str,
    user_message: str,
    post_caption: str,
):
    async with AsyncSessionLocal() as db:
        try:
            existe = await db.execute(
                select(MensajePendienteDB).filter_by(instagram_message_id=ig_message_id)
            )
            if existe.scalars().first():
                print(f"[Webhook] Mensaje duplicado ignorado: {ig_message_id}")
                return

            sugerencia = aprobacion.obtener_respuesta_sugerida(
                user_message, post_caption
            )

            nuevo_borrador = MensajePendienteDB(
                instagram_message_id=ig_message_id,
                sender_id=sender_id,
                user_message=user_message[:_MAX_TEXTO],
                draft_response=sugerencia,
                post_caption=post_caption,
                status="pending",
            )
            db.add(nuevo_borrador)
            await db.commit()
            print(f"[Webhook] Borrador guardado con éxito para mensaje {ig_message_id}")

        except Exception as e:
            await db.rollback()
            print(f"[Error BackgroundTask] Falló el procesamiento de {ig_message_id}: {e}")


# ---------------------------------------------------------------------------
# Endpoints Públicos y Webhooks de Meta
# ---------------------------------------------------------------------------
@app.get("/")
def verificar_estado():
    return {
        "estado": "activo" if estado_agente["activo"] else "pausado",
        "cuenta": estado_agente["cuenta"],
    }


@app.get("/webhook")
def verificar_webhook_meta(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """Endpoint que Meta consulta una sola vez al configurar el Webhook."""
    token_esperado = os.getenv("META_VERIFY_TOKEN")
    if (
        hub_mode == "subscribe"
        and token_esperado
        and hub_verify_token == token_esperado
    ):
        return PlainTextResponse(content=hub_challenge or "", status_code=200)
    raise HTTPException(status_code=403, detail="Token de verificación inválido.")


@app.post("/webhook")
async def recibir_webhook_meta(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    payload = await request.json()

    if not estado_agente["activo"]:
        return {"status": "ignored", "reason": "agente_pausado"}

    for entry in payload.get("entry", []):
        for messaging in entry.get("messaging", []):
            mensaje = messaging.get("message", {})
            if mensaje.get("is_echo"):
                continue

            msg_id = mensaje.get("mid")
            texto = mensaje.get("text")
            sender_id = messaging.get("sender", {}).get("id", "usuario_ig")

            if msg_id and texto:
                existe = await db.execute(
                    select(MensajePendienteDB).filter_by(instagram_message_id=msg_id)
                )
                if not existe.scalars().first():
                    background_tasks.add_task(
                        procesar_y_guardar_borrador,
                        ig_message_id=msg_id,
                        sender_id=sender_id,
                        user_message=texto,
                        post_caption="Mensaje directo (DM) a @otrabogota",
                    )

        for change in entry.get("changes", []):
            if change.get("field") == "comments":
                valor = change.get("value", {})
                comment_id = valor.get("id")
                texto = valor.get("text")
                sender_id = valor.get("from", {}).get("username", "comentarista_ig")

                if comment_id and texto:
                    existe = await db.execute(
                        select(MensajePendienteDB).filter_by(instagram_message_id=comment_id)
                    )
                    if not existe.scalars().first():
                        background_tasks.add_task(
                            procesar_y_guardar_borrador,
                            ig_message_id=comment_id,
                            sender_id=sender_id,
                            user_message=texto,
                            post_caption="Comentario en publicación de @otrabogota",
                        )

    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Endpoints Privados (Protegidos con X-API-Key para la App Android)
# ---------------------------------------------------------------------------
@app.post("/cambiar-estado", dependencies=[Depends(exigir_clave)])
def cambiar_estado(activar: bool):
    estado_agente["activo"] = activar
    estado = "activo" if activar else "pausado"
    return {"resultado": "exito", "nuevo_estado": estado}


@app.post("/simular-mensaje", dependencies=[Depends(exigir_clave)])
async def simular_mensaje(
    datos: MensajeSimulado,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if not estado_agente["activo"]:
        raise HTTPException(
            status_code=403,
            detail="Acción bloqueada: el agente está PAUSADO.",
        )

    fake_ig_id = f"sim_{datos.usuario_origen}_{hash(datos.texto_mensaje)}"

    resultado = await db.execute(
        select(MensajePendienteDB).filter_by(instagram_message_id=fake_ig_id)
    )
    if resultado.scalars().first():
        raise HTTPException(
            status_code=400, detail="Este mensaje simulado ya fue registrado."
        )

    background_tasks.add_task(
        procesar_y_guardar_borrador,
        ig_message_id=fake_ig_id,
        sender_id=datos.usuario_origen,
        user_message=datos.texto_mensaje,
        post_caption=datos.post_caption or "Publicación de @otrabogota",
    )

    return {
        "resultado": "procesando_en_segundo_plano",
        "mensaje": "El mensaje fue recibido. Gemini está generando el borrador en segundo plano.",
    }


@app.get("/ver-pendientes", dependencies=[Depends(exigir_clave)])
async def ver_pendientes(db: AsyncSession = Depends(get_db)):
    resultado = await db.execute(
        select(MensajePendienteDB).filter_by(status="pending")
    )
    pendientes = resultado.scalars().all()

    lista_formateada = [
        {
            "id_mensaje": p.id,
            "usuario": p.sender_id,
            "mensaje_recibido": p.user_message,
            "borrador_gemini": p.draft_response,
            "estado": p.status,
            "post_caption": p.post_caption,
        }
        for p in pendientes
    ]

    return {
        "cuenta": estado_agente["cuenta"],
        "total_pendientes": len(lista_formateada),
        "bandeja": lista_formateada,
    }


@app.post("/aprobar-borrador/{id_mensaje}", dependencies=[Depends(exigir_clave)])
async def aprobar_borrador(
    id_mensaje: int, db: AsyncSession = Depends(get_db)
):
    _exigir_agente_activo()
    borrador = await _buscar_borrador(db, id_mensaje)

    borrador.status = "approved"
    await db.commit()

    return {
        "resultado": "exito",
        "mensaje": f"Borrador #{id_mensaje} aprobado.",
        "contenido_aprobado": borrador.draft_response,
    }


@app.post("/editar-borrador/{id_mensaje}", dependencies=[Depends(exigir_clave)])
async def editar_borrador(
    id_mensaje: int, datos: DatosEdicion, db: AsyncSession = Depends(get_db)
):
    _exigir_agente_activo()
    borrador = await _buscar_borrador(db, id_mensaje)

    borrador.draft_response = datos.nuevo_texto.strip()
    borrador.status = "edited_and_approved"
    await db.commit()

    return {
        "resultado": "exito",
        "mensaje": f"Borrador #{id_mensaje} editado y aprobado.",
        "contenido_aprobado": borrador.draft_response,
    }


@app.post("/rechazar-borrador/{id_mensaje}", dependencies=[Depends(exigir_clave)])
async def rechazar_borrador(
    id_mensaje: int, db: AsyncSession = Depends(get_db)
):
    borrador = await _buscar_borrador(db, id_mensaje)
    borrador.status = "rejected"
    await db.commit()

    return {
        "resultado": "exito",
        "mensaje": f"Borrador #{id_mensaje} rechazado.",
    }