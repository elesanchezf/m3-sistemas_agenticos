"""Configuración de la base de datos SQLite para la app de empleados."""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DIRECTORIO_DATOS = os.path.join(os.path.dirname(__file__), "datos")
os.makedirs(DIRECTORIO_DATOS, exist_ok=True)

RUTA_BASE_DATOS = os.path.join(DIRECTORIO_DATOS, "empleados.db")
URL_BASE_DATOS = f"sqlite:///{RUTA_BASE_DATOS}"

engine = create_engine(URL_BASE_DATOS, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "connect")
def _registrar_funciones_sqlite(conexion_dbapi, _):
    # LOWER() nativo de SQLite solo cubre ASCII; str.lower() de Python sí
    # normaliza acentos y mayúsculas Unicode (necesario para buscar "Ana López").
    conexion_dbapi.create_function(
        "minusculas_unicode", 1, lambda valor: valor.lower() if valor is not None else None
    )


class Base(DeclarativeBase):
    pass


def obtener_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
