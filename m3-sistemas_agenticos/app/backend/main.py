"""Punto de entrada de la API de gestión de empleados."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from database import Base, engine
from routers import empleados

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de gestión de empleados")

app.include_router(empleados.router, prefix="/api")


@app.get("/api/salud")
def salud() -> dict[str, str]:
    return {"estado": "ok"}


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(request: Request, exc: RequestValidationError) -> JSONResponse:
    primer_error = exc.errors()[0]
    mensaje = primer_error["msg"]
    campo = primer_error["loc"][-1] if len(primer_error["loc"]) > 1 else None
    if mensaje.startswith("Value error, "):
        mensaje = mensaje[len("Value error, "):]
    elif primer_error["type"] == "missing":
        mensaje = f"El campo {campo} es obligatorio"
    return JSONResponse(status_code=422, content={"detail": mensaje, "campo": campo})
