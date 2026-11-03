from fastapi import FastAPI

app = FastAPI()

# Variable global de control (por seguridad inicia en False o True según prefieras)
estado_agente = {
    "activo": False,  # False por defecto para evitar ejecuciones accidentales en pruebas
    "cuenta": "@otrabogota",
    "mensaje": "El agente de Instagram está en la nube 24/7"
}

@app.get("/")
def verificar_estado():
    # Devuelve el estado actual del agente
    return {
        "estado": "activo" if estado_agente["activo"] else "pausado",
        "cuenta": estado_agente["cuenta"],
        "mensaje": estado_agente["mensaje"]
    }

@app.post("/cambiar-estado")
def cambiar_estado(activar: bool):
    # Recibe una orden desde la app para encender o apagar el agente
    estado_agente["activo"] = activar
    estado = "activo" if activar else "pausado"
    return {
        "resultado": "exito",
        "nuevo_estado": estado,
        "mensaje": f"El agente ha sido {estado} correctamente."
    }