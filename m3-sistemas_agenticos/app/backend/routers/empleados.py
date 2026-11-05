"""Rutas del recurso /api/empleados y catálogo de departamentos."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import obtener_db
from models import Empleado
from schemas import (
    DEPARTAMENTOS_VALIDOS,
    EmpleadoBaja,
    EmpleadoCrear,
    EmpleadoEditar,
    EmpleadoSalida,
)

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


@router.put("/empleados/{id}", response_model=EmpleadoSalida)
def editar_empleado(id: int, datos: EmpleadoEditar, db: Session = Depends(obtener_db)) -> Empleado:
    empleado = db.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    if empleado.estado == "baja":
        raise HTTPException(status_code=409, detail="No se puede editar a un empleado dado de baja")

    if datos.puesto is not None:
        empleado.puesto = datos.puesto
    if datos.departamento is not None:
        empleado.departamento = datos.departamento

    db.commit()
    db.refresh(empleado)
    return empleado


@router.put("/empleados/{id}/baja", response_model=EmpleadoSalida)
def dar_de_baja_empleado(id: int, datos: EmpleadoBaja, db: Session = Depends(obtener_db)) -> Empleado:
    empleado = db.get(Empleado, id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    if empleado.estado == "baja":
        return empleado

    if datos.fecha_baja < empleado.fecha_ingreso:
        return JSONResponse(
            status_code=422,
            content={
                "detail": "La fecha de baja no puede ser anterior a la fecha de ingreso",
                "campo": "fecha_baja",
            },
        )

    empleado.estado = "baja"
    empleado.fecha_baja = datos.fecha_baja
    db.commit()
    db.refresh(empleado)
    return empleado
