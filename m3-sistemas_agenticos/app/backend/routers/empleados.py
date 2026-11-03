"""Rutas del recurso /api/empleados y catálogo de departamentos."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import obtener_db
from models import Empleado
from schemas import DEPARTAMENTOS_VALIDOS, EmpleadoCrear, EmpleadoSalida

router = APIRouter(tags=["empleados"])


def _siguiente_numero_empleado(db: Session) -> str:
    ultimo = db.query(Empleado).order_by(Empleado.id.desc()).first()
    if ultimo is None:
        return "EMP-0001"
    consecutivo = int(ultimo.numero_empleado.split("-")[1]) + 1
    return f"EMP-{consecutivo:04d}"


@router.post("/empleados", response_model=EmpleadoSalida, status_code=201)
def crear_empleado(datos: EmpleadoCrear, db: Session = Depends(obtener_db)) -> Empleado:
    existe = db.query(Empleado).filter(func.lower(Empleado.correo) == datos.correo).first()
    if existe is not None:
        raise HTTPException(status_code=409, detail="El correo ya está registrado")

    empleado = Empleado(
        numero_empleado=_siguiente_numero_empleado(db),
        nombre=datos.nombre,
        correo=datos.correo,
        puesto=datos.puesto,
        departamento=datos.departamento,
        fecha_ingreso=datos.fecha_ingreso,
        estado="activo",
    )
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return empleado


@router.get("/empleados", response_model=list[EmpleadoSalida])
def listar_empleados(
    buscar: str | None = Query(default=None),
    departamento: str | None = Query(default=None),
    db: Session = Depends(obtener_db),
) -> list[Empleado]:
    consulta = db.query(Empleado)
    if departamento:
        consulta = consulta.filter(Empleado.departamento == departamento)
    if buscar:
        patron = f"%{buscar.strip().lower()}%"
        consulta = consulta.filter(
            func.minusculas_unicode(Empleado.nombre).like(patron)
            | func.minusculas_unicode(Empleado.correo).like(patron)
        )
    return consulta.order_by(Empleado.id).all()


@router.get("/departamentos", response_model=list[str])
def listar_departamentos() -> list[str]:
    return DEPARTAMENTOS_VALIDOS
