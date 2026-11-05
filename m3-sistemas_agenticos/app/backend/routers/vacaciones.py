"""Rutas del recurso /api/empleados/{empleado_id}/vacaciones (HU-10)."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import obtener_db
from models import Empleado, Vacaciones as VacacionesModelo
from schemas import SaldoVacaciones, SolicitudResumen, VacacionesCrear, VacacionesSalida
from vacaciones import (
    TOPE_ANUAL_DIAS_HABILES,
    anio_tiene_festivos,
    contar_dias_habiles,
    cumple_antiguedad,
)

router = APIRouter(tags=["vacaciones"])


def _solicitudes_del_anio(db: Session, empleado_id: int, anio: int) -> list[VacacionesModelo]:
    """Obtiene las solicitudes de vacaciones de un empleado en un año.

    Filtra por el año calendario de `fecha_inicio` de cada solicitud;
    se usa tanto para calcular los días usados al validar una nueva
    solicitud como para armar el saldo que se consulta.

    Args:
        db: Sesión de base de datos activa.
        empleado_id: Identificador interno del empleado.
        anio: Año calendario a consultar.

    Returns:
        Las solicitudes del empleado en ese año, ordenadas por id.
    """
    todas = (
        db.query(VacacionesModelo)
        .filter(VacacionesModelo.empleado_id == empleado_id)
        .order_by(VacacionesModelo.id)
        .all()
    )
    return [s for s in todas if s.fecha_inicio.year == anio]


@router.post(
    "/empleados/{empleado_id}/vacaciones",
    response_model=VacacionesSalida,
    status_code=201,
)
def crear_vacaciones(
    empleado_id: int, datos: VacacionesCrear, db: Session = Depends(obtener_db)
) -> VacacionesSalida:
    """Registra una solicitud de vacaciones si cumple todas las reglas.

    Valida en este orden, devolviendo el primer error que aplique:
    1. El empleado existe (404).
    2. El empleado no está dado de baja (409).
    3. `fecha_fin` no es anterior a `fecha_inicio` (400).
    4. El periodo no cruza de un año a otro (400).
    5. El año de la solicitud tiene festivos cargados, es decir,
       es 2026 o 2027 (400).
    6. El empleado cumple al menos un año de antigüedad a la fecha
       de inicio (400).
    7. El periodo incluye al menos un día hábil (400).
    8. Los días hábiles solicitados no rebasan el tope anual de
       12 días hábiles menos lo ya usado en ese año (400).

    Si todo se cumple, crea la solicitud y calcula los días hábiles
    restantes del año tras descontarla.

    Args:
        empleado_id: Identificador interno del empleado.
        datos: Fechas de inicio y fin solicitadas.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        La solicitud creada, con sus días hábiles y los días
        restantes del tope anual tras registrarla.

    Raises:
        HTTPException: Con el código y la validación que falló,
            según el orden descrito arriba.
    """
    empleado = db.get(Empleado, empleado_id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    if empleado.estado == "baja":
        raise HTTPException(
            status_code=409,
            detail="No se pueden solicitar vacaciones para un empleado dado de baja",
        )
    if datos.fecha_fin < datos.fecha_inicio:
        raise HTTPException(
            status_code=400,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio",
        )
    if datos.fecha_inicio.year != datos.fecha_fin.year:
        raise HTTPException(
            status_code=400,
            detail="Las vacaciones deben estar dentro de un mismo año calendario",
        )

    anio = datos.fecha_inicio.year
    if not anio_tiene_festivos(anio):
        raise HTTPException(
            status_code=400, detail="Solo se pueden solicitar vacaciones en 2026 y 2027"
        )
    if not cumple_antiguedad(empleado.fecha_ingreso, datos.fecha_inicio):
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un año de antigüedad a la fecha de inicio",
        )

    dias_habiles = contar_dias_habiles(datos.fecha_inicio, datos.fecha_fin)
    if dias_habiles == 0:
        raise HTTPException(status_code=400, detail="El periodo no incluye días hábiles")

    dias_usados = sum(s.dias_habiles for s in _solicitudes_del_anio(db, empleado_id, anio))
    dias_disponibles = TOPE_ANUAL_DIAS_HABILES - dias_usados
    if dias_habiles > dias_disponibles:
        raise HTTPException(
            status_code=400,
            detail=(
                "La solicitud excede los días disponibles: "
                f"quedan {dias_disponibles} días hábiles"
            ),
        )

    solicitud = VacacionesModelo(
        empleado_id=empleado_id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_habiles=dias_habiles,
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    return VacacionesSalida(
        id=solicitud.id,
        empleado_id=empleado_id,
        fecha_inicio=solicitud.fecha_inicio,
        fecha_fin=solicitud.fecha_fin,
        dias_habiles=dias_habiles,
        dias_restantes=dias_disponibles - dias_habiles,
    )


@router.get("/empleados/{empleado_id}/vacaciones", response_model=SaldoVacaciones)
def obtener_saldo_vacaciones(
    empleado_id: int,
    anio: int | None = Query(default=None),
    db: Session = Depends(obtener_db),
) -> SaldoVacaciones:
    """Consulta el saldo de vacaciones de un empleado en un año.

    El tope anual es de 12 días hábiles por año calendario; los días
    disponibles son ese tope menos la suma de días hábiles de todas
    las solicitudes registradas en el año consultado.

    Args:
        empleado_id: Identificador interno del empleado.
        anio: Año calendario a consultar; si no se indica, se usa
            el año en curso.
        db: Sesión de base de datos inyectada por FastAPI.

    Returns:
        El resumen del año: días usados, días disponibles y el
        detalle de las solicitudes registradas.

    Raises:
        HTTPException: Código 404 si el empleado no existe.
    """
    empleado = db.get(Empleado, empleado_id)
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    anio_consulta = anio if anio is not None else date.today().year
    solicitudes = _solicitudes_del_anio(db, empleado_id, anio_consulta)
    dias_usados = sum(s.dias_habiles for s in solicitudes)

    return SaldoVacaciones(
        empleado_id=empleado_id,
        anio=anio_consulta,
        dias_usados=dias_usados,
        dias_disponibles=TOPE_ANUAL_DIAS_HABILES - dias_usados,
        solicitudes=[SolicitudResumen.model_validate(s) for s in solicitudes],
    )
