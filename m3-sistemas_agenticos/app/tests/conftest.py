"""Fixtures compartidas por las pruebas de la app de empleados."""

import os
import sqlite3
import uuid
from datetime import date
from pathlib import Path

import httpx
import pytest

URL_API = os.environ.get("URL_API", "http://localhost:8000")
URL_WEB = os.environ.get("URL_WEB", "http://localhost:8080")

RUTA_BASE_DATOS = Path(__file__).resolve().parent.parent / "backend" / "datos" / "empleados.db"


@pytest.fixture
def url_api() -> str:
    return URL_API


@pytest.fixture
def url_web() -> str:
    return URL_WEB


@pytest.fixture
def crear_empleado(url_api):
    """Factory que crea empleados de prueba vía la API con correos únicos."""

    def _crear(**campos) -> dict:
        datos = {
            "nombre": "Empleado de Prueba",
            "correo": f"empleado.{uuid.uuid4().hex[:10]}@empresa.com",
            "puesto": "Analista",
            "departamento": "Tecnología",
            "fecha_ingreso": str(date.today()),
        }
        datos.update(campos)
        respuesta = httpx.post(f"{url_api}/api/empleados", json=datos)
        assert respuesta.status_code == 201, respuesta.text
        return respuesta.json()

    return _crear


@pytest.fixture
def marcar_baja():
    """Factory que da de baja a un empleado escribiendo directo en la BD.

    HU-02 no expone un endpoint para dar de baja, así que las pruebas
    preparan esta precondición en la BD en vez de modificar la app.
    """

    def _marcar(empleado_id: int, fecha_baja: str | None = None) -> None:
        conexion = sqlite3.connect(RUTA_BASE_DATOS)
        try:
            conexion.execute(
                "UPDATE empleados SET estado = 'baja', fecha_baja = ? WHERE id = ?",
                (fecha_baja or str(date.today()), empleado_id),
            )
            conexion.commit()
        finally:
            conexion.close()

    return _marcar
