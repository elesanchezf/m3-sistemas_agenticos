"""Pruebas de API para HU-03: editar empleados y darlos de baja."""

import httpx


def test_cp01_editar_puesto_y_departamento_de_empleado_activo(url_api, crear_empleado):
    """CP-01: editar correctamente el puesto y el departamento de un empleado activo."""
    # Preparación
    empleado = crear_empleado(puesto="Analista", departamento="Ventas")

    # Acción
    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}",
        json={"puesto": "Analista Senior", "departamento": "Finanzas"},
    )

    # Verificación
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["puesto"] == "Analista Senior"
    assert cuerpo["departamento"] == "Finanzas"
    assert cuerpo["numero_empleado"] == empleado["numero_empleado"]
    assert cuerpo["correo"] == empleado["correo"]


def test_cp03_no_se_puede_editar_a_un_empleado_dado_de_baja(url_api, crear_empleado):
    """CP-03: no se puede editar a un empleado dado de baja."""
    # Preparación
    empleado = crear_empleado(puesto="Analista", fecha_ingreso="2022-01-01")
    baja = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2024-01-15"}
    )
    assert baja.status_code == 200, f"Preparación: {baja.text}"

    # Acción
    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}", json={"puesto": "Gerente"}
    )

    # Verificación
    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No se puede editar a un empleado dado de baja"
    listado = httpx.get(f"{url_api}/api/empleados")
    actual = next(e for e in listado.json() if e["id"] == empleado["id"])
    assert actual["puesto"] == "Analista"


def test_cp05_error_al_editar_con_puesto_invalido(url_api, crear_empleado):
    """CP-05: error al editar con un puesto que no cumple la longitud mínima."""
    # Preparación
    empleado = crear_empleado(puesto="Analista")

    # Acción
    respuesta = httpx.put(f"{url_api}/api/empleados/{empleado['id']}", json={"puesto": "A"})

    # Verificación
    assert respuesta.status_code == 422
    assert respuesta.json()["campo"] == "puesto"
    listado = httpx.get(f"{url_api}/api/empleados")
    actual = next(e for e in listado.json() if e["id"] == empleado["id"])
    assert actual["puesto"] == "Analista"


def test_cp07_error_al_editar_con_departamento_invalido(url_api, crear_empleado):
    """CP-07: error al editar con un departamento fuera del catálogo."""
    # Preparación
    empleado = crear_empleado(departamento="Ventas")

    # Acción
    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}", json={"departamento": "Marketing"}
    )

    # Verificación
    assert respuesta.status_code == 422
    assert respuesta.json()["campo"] == "departamento"
    listado = httpx.get(f"{url_api}/api/empleados")
    actual = next(e for e in listado.json() if e["id"] == empleado["id"])
    assert actual["departamento"] == "Ventas"


def test_cp09_dar_de_baja_a_un_empleado_activo(url_api, crear_empleado):
    """CP-09: dar de baja a un empleado activo."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2022-05-01")

    # Acción
    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2024-03-15"}
    )

    # Verificación
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "baja"
    assert cuerpo["fecha_baja"] == "2024-03-15"
    listado = httpx.get(f"{url_api}/api/empleados")
    assert any(e["id"] == empleado["id"] for e in listado.json())


def test_cp11_error_al_dar_de_baja_con_fecha_anterior_a_ingreso(url_api, crear_empleado):
    """CP-11: error al dar de baja con una fecha_baja anterior a la fecha de ingreso."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2023-06-01")

    # Acción
    respuesta = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2023-01-01"}
    )

    # Verificación
    assert respuesta.status_code == 422
    assert respuesta.json()["campo"] == "fecha_baja"
    listado = httpx.get(f"{url_api}/api/empleados")
    actual = next(e for e in listado.json() if e["id"] == empleado["id"])
    assert actual["estado"] == "activo"
