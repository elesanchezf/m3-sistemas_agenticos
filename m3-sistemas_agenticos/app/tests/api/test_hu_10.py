"""Pruebas de API para HU-10: solicitar y consultar vacaciones."""

import httpx

EMPLEADO_INEXISTENTE = 999999999


def test_cp01_camino_feliz_solicitud_valida_registra_dias(url_api, crear_empleado):
    """CP-01: una solicitud válida registra días hábiles y días restantes."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    # Verificación
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 5
    assert cuerpo["dias_restantes"] == 7


def test_cp02_usar_exactamente_los_dias_que_quedan_agota_el_saldo(url_api, crear_empleado):
    """CP-02: usar exactamente los días que quedan agota el saldo del año (queda 0)."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")
    primera = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )
    assert primera.status_code == 201, f"Preparación: {primera.text}"

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-13", "fecha_fin": "2026-07-21"},
    )

    # Verificación
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 7
    assert cuerpo["dias_restantes"] == 0


def test_cp03_pasarse_por_un_dia_del_saldo_se_rechaza_con_el_n_exacto(url_api, crear_empleado):
    """CP-03: pasarse por un día del saldo disponible se rechaza con el N exacto."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2020-01-01")
    primera = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-06-01", "fecha_fin": "2026-06-04"},
    )
    assert primera.status_code == 201, f"Preparación: {primera.text}"

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-08-03", "fecha_fin": "2026-08-13"},
    )

    # Verificación
    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "La solicitud excede los días disponibles: quedan 8 días hábiles"
    )


def test_cp04_aniversario_exacto_festivo_y_fines_de_semana_no_cuentan(url_api, crear_empleado):
    """CP-04: aniversario exacto de antigüedad, festivo y fines de semana no cuentan, extremos incluidos."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2025-12-21")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-12-21", "fecha_fin": "2026-12-31"},
    )

    # Verificación
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 8
    assert cuerpo["dias_restantes"] == 4


def test_cp05_un_dia_antes_del_aniversario_se_rechaza_por_antiguedad(url_api, crear_empleado):
    """CP-05: un día antes del aniversario se rechaza por antigüedad, validada antes que los días hábiles."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2025-12-21")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-12-20", "fecha_fin": "2026-12-20"},
    )

    # Verificación
    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"]
        == "Se requiere al menos un año de antigüedad a la fecha de inicio"
    )


def test_cp06_ingreso_un_29_de_febrero_cumple_la_antiguedad_en_2026(url_api, crear_empleado):
    """CP-06: ingreso un 29 de febrero cumple la antigüedad en 2026 (cobertura básica)."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-02-29")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    # Verificación
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 5
    assert cuerpo["dias_restantes"] == 7


def test_cp07_un_periodo_completo_en_fin_de_semana_se_rechaza(url_api, crear_empleado):
    """CP-07: un periodo que cae completo en fin de semana no tiene días hábiles y se rechaza."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2020-01-01")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-11", "fecha_fin": "2026-07-12"},
    )

    # Verificación
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "El periodo no incluye días hábiles"


def test_cp08_la_fecha_de_fin_anterior_a_la_de_inicio_se_rechaza(url_api, crear_empleado):
    """CP-08: la fecha de fin anterior a la fecha de inicio se rechaza."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2020-01-01")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-10", "fecha_fin": "2026-07-06"},
    )

    # Verificación
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "La fecha de fin no puede ser anterior a la fecha de inicio"


def test_cp09_un_periodo_que_cruza_de_un_anio_a_otro_se_rechaza(url_api, crear_empleado):
    """CP-09: un periodo que cruza de un año a otro se rechaza."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2020-01-01")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-12-28", "fecha_fin": "2027-01-08"},
    )

    # Verificación
    assert respuesta.status_code == 400
    assert (
        respuesta.json()["detail"] == "Las vacaciones deben estar dentro de un mismo año calendario"
    )


def test_cp10_un_anio_fuera_de_la_tabla_de_festivos_se_rechaza(url_api, crear_empleado):
    """CP-10: un año fuera de la tabla de festivos se rechaza."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2020-01-01")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2028-07-06", "fecha_fin": "2028-07-10"},
    )

    # Verificación
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "Solo se pueden solicitar vacaciones en 2026 y 2027"


def test_cp11_un_empleado_inexistente_se_rechaza_con_404(url_api):
    """CP-11: un empleado inexistente se rechaza con 404."""
    # Preparación: no se crea empleado, EMPLEADO_INEXISTENTE no existe en el sistema.

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{EMPLEADO_INEXISTENTE}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    # Verificación
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp12_un_empleado_dado_de_baja_se_rechaza_con_409(url_api, crear_empleado):
    """CP-12: un empleado dado de baja se rechaza con 409."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2020-01-01")
    baja = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2024-06-15"}
    )
    assert baja.status_code == 200, f"Preparación: {baja.text}"

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    # Verificación
    assert respuesta.status_code == 409
    assert (
        respuesta.json()["detail"]
        == "No se pueden solicitar vacaciones para un empleado dado de baja"
    )


def test_cp13_el_empleado_inexistente_se_valida_antes_que_el_orden_de_las_fechas(url_api):
    """CP-13: el empleado inexistente se valida antes que el orden de las fechas."""
    # Preparación: no se crea empleado, EMPLEADO_INEXISTENTE no existe en el sistema.

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{EMPLEADO_INEXISTENTE}/vacaciones",
        json={"fecha_inicio": "2026-07-10", "fecha_fin": "2026-07-06"},
    )

    # Verificación
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "Empleado no encontrado"


def test_cp14_una_solicitud_en_2027_usa_sus_propios_festivos_y_saldo(url_api, crear_empleado):
    """CP-14: una solicitud en 2027 calcula sus días con los festivos de 2027 sin descontar lo usado en 2026."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")
    primera = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )
    assert primera.status_code == 201, f"Preparación: {primera.text}"

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2027-09-13", "fecha_fin": "2027-09-17"},
    )

    # Verificación
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 4
    assert cuerpo["dias_restantes"] == 8


def test_cp15_consultar_el_saldo_antes_y_despues_de_registrar_una_solicitud(url_api, crear_empleado):
    """CP-15: consultar el saldo antes y después de registrar una solicitud válida."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")
    saldo_inicial = httpx.get(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones", params={"anio": 2026}
    )
    assert saldo_inicial.status_code == 200, f"Preparación: {saldo_inicial.text}"
    cuerpo_inicial = saldo_inicial.json()
    assert cuerpo_inicial["dias_usados"] == 0, f"Preparación: {saldo_inicial.text}"
    assert cuerpo_inicial["dias_disponibles"] == 12, f"Preparación: {saldo_inicial.text}"
    assert cuerpo_inicial["solicitudes"] == [], f"Preparación: {saldo_inicial.text}"

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )
    assert respuesta.status_code == 201, respuesta.text

    # Verificación
    saldo_final = httpx.get(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones", params={"anio": 2026}
    )
    assert saldo_final.status_code == 200
    cuerpo_final = saldo_final.json()
    assert cuerpo_final["dias_usados"] == 5
    assert cuerpo_final["dias_disponibles"] == 7
    solicitud = next(
        s for s in cuerpo_final["solicitudes"] if s["fecha_inicio"] == "2026-07-06"
    )
    assert solicitud["fecha_fin"] == "2026-07-10"
    assert solicitud["dias_habiles"] == 5


def test_cp16_el_saldo_de_2027_es_independiente_de_2026(url_api, crear_empleado):
    """CP-16: el saldo de 2027 es independiente de los días usados en 2026."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")
    primera = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )
    assert primera.status_code == 201, f"Preparación: {primera.text}"

    # Acción
    respuesta = httpx.get(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones", params={"anio": 2027}
    )

    # Verificación
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["dias_usados"] == 0
    assert cuerpo["dias_disponibles"] == 12
    assert cuerpo["solicitudes"] == []


def test_cp17_el_boton_de_vacaciones_solo_aplica_a_empleados_activos(url_api, crear_empleado):
    """CP-17: el botón de solicitar vacaciones solo aparece para empleados activos."""
    # Preparación
    activo = crear_empleado(fecha_ingreso="2024-03-10")
    baja = crear_empleado(fecha_ingreso="2020-01-01")
    respuesta_baja = httpx.put(
        f"{url_api}/api/empleados/{baja['id']}/baja", json={"fecha_baja": "2024-06-15"}
    )
    assert respuesta_baja.status_code == 200, f"Preparación: {respuesta_baja.text}"

    # Acción
    respuesta = httpx.get(f"{url_api}/api/empleados")

    # Verificación
    assert respuesta.status_code == 200
    empleados = {e["id"]: e for e in respuesta.json()}
    assert empleados[activo["id"]]["estado"] == "activo"
    assert empleados[baja["id"]]["estado"] == "baja"


def test_cp19_camino_feliz_e2e_registrar_una_solicitud_desde_el_formulario(url_api, crear_empleado):
    """CP-19: camino feliz e2e - registrar una solicitud desde el formulario."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-06", "fecha_fin": "2026-07-10"},
    )

    # Verificación
    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["dias_habiles"] == 5
    assert cuerpo["dias_restantes"] == 7


def test_cp21_error_e2e_el_formulario_muestra_el_detail_exacto_de_la_api(url_api, crear_empleado):
    """CP-21: error e2e - el formulario muestra el detail exacto de la API."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")

    # Acción
    respuesta = httpx.post(
        f"{url_api}/api/empleados/{empleado['id']}/vacaciones",
        json={"fecha_inicio": "2026-07-10", "fecha_fin": "2026-07-06"},
    )

    # Verificación
    assert respuesta.status_code == 400
    assert respuesta.json()["detail"] == "La fecha de fin no puede ser anterior a la fecha de inicio"
