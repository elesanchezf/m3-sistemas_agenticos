"""Reglas de negocio de vacaciones: festivos, días hábiles y antigüedad (HU-10)."""

from datetime import date, timedelta

TOPE_ANUAL_DIAS_HABILES = 12

FESTIVOS: dict[int, set[date]] = {
    2026: {
        date(2026, 1, 1),
        date(2026, 2, 2),
        date(2026, 3, 16),
        date(2026, 5, 1),
        date(2026, 9, 16),
        date(2026, 11, 16),
        date(2026, 12, 25),
    },
    2027: {
        date(2027, 1, 1),
        date(2027, 2, 1),
        date(2027, 3, 15),
        date(2027, 5, 1),
        date(2027, 9, 16),
        date(2027, 11, 15),
        date(2027, 12, 25),
    },
}


def anio_tiene_festivos(anio: int) -> bool:
    """Indica si el año tiene tabla de festivos cargada.

    Solo 2026 y 2027 están soportados; cualquier otro año no tiene
    festivos definidos y, por lo tanto, no se pueden calcular días
    hábiles ni aceptar solicitudes de vacaciones en él.

    Args:
        anio: Año calendario a verificar.

    Returns:
        True si el año está en la tabla de festivos (2026 o 2027).
    """
    return anio in FESTIVOS


def contar_dias_habiles(fecha_inicio: date, fecha_fin: date) -> int:
    """Cuenta los días hábiles de un periodo, extremos incluidos.

    Un día es hábil si no cae en sábado, no cae en domingo y no es
    festivo oficial del año de `fecha_inicio`. Tanto la fecha de
    inicio como la de fin se incluyen en el conteo.

    Args:
        fecha_inicio: Primer día del periodo (inclusive).
        fecha_fin: Último día del periodo (inclusive).

    Returns:
        Número de días hábiles dentro del periodo.

    Raises:
        KeyError: Si el año de `fecha_inicio` no tiene festivos
            cargados en `FESTIVOS`.
    """
    festivos = FESTIVOS[fecha_inicio.year]
    dias = 0
    actual = fecha_inicio
    while actual <= fecha_fin:
        if actual.weekday() < 5 and actual not in festivos:
            dias += 1
        actual += timedelta(days=1)
    return dias


def fecha_aniversario(fecha_ingreso: date) -> date:
    """Calcula la fecha en que el empleado cumple un año de antigüedad.

    Es el mismo día y mes de `fecha_ingreso`, un año después. Si
    `fecha_ingreso` cae en 29 de febrero y el año siguiente no es
    bisiesto, el aniversario se recorre al 1 de marzo.

    Args:
        fecha_ingreso: Fecha de ingreso del empleado.

    Returns:
        Fecha del primer aniversario de ingreso.
    """
    try:
        return fecha_ingreso.replace(year=fecha_ingreso.year + 1)
    except ValueError:
        # 29 de febrero: el aniversario en un año no bisiesto es el 1 de marzo.
        return date(fecha_ingreso.year + 1, 3, 1)


def cumple_antiguedad(fecha_ingreso: date, fecha_inicio: date) -> bool:
    """Verifica si el empleado tiene al menos un año de antigüedad.

    Compara `fecha_inicio` de las vacaciones contra el aniversario de
    ingreso (ver `fecha_aniversario`); se cumple la regla cuando la
    solicitud inicia en el aniversario o después.

    Args:
        fecha_ingreso: Fecha de ingreso del empleado.
        fecha_inicio: Fecha de inicio de las vacaciones solicitadas.

    Returns:
        True si el empleado ya cumplió un año de antigüedad a la
        fecha de inicio solicitada.
    """
    return fecha_inicio >= fecha_aniversario(fecha_ingreso)
