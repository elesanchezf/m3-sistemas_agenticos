"""Pruebas end-to-end para HU-03: editar empleados y darlos de baja."""

import httpx
from playwright.sync_api import expect


def test_cp02_editar_puesto_y_departamento_de_empleado_activo(page, url_web, crear_empleado):
    """CP-02: editar correctamente el puesto y el departamento de un empleado activo."""
    # Preparación
    empleado = crear_empleado(puesto="Analista", departamento="Ventas")
    page.goto(url_web)
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    # Acción
    page.get_by_test_id("empleado-puesto").fill("Analista Senior")
    page.get_by_test_id("empleado-departamento").select_option("Finanzas")
    page.get_by_test_id("empleado-guardar").click()

    # Verificación
    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado['id']}")).to_have_text(
        empleado["numero_empleado"]
    )


def test_cp04_no_se_puede_editar_a_un_empleado_dado_de_baja(url_api, page, url_web, crear_empleado):
    """CP-04: no se puede editar a un empleado dado de baja."""
    # Preparación
    empleado = crear_empleado(puesto="Analista", fecha_ingreso="2022-01-01")
    baja = httpx.put(
        f"{url_api}/api/empleados/{empleado['id']}/baja", json={"fecha_baja": "2024-01-15"}
    )
    assert baja.status_code == 200, f"Preparación: {baja.text}"

    page.goto(url_web)
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    # Acción
    page.get_by_test_id("empleado-puesto").fill("Gerente")
    page.get_by_test_id("empleado-guardar").click()

    # Verificación
    mensaje_error = page.get_by_test_id("mensaje-error")
    expect(mensaje_error).to_be_visible()
    expect(mensaje_error).to_contain_text("No se puede editar a un empleado dado de baja")


def test_cp06_error_al_editar_con_puesto_invalido(page, url_web, crear_empleado):
    """CP-06: error al editar con un puesto que no cumple la longitud mínima."""
    # Preparación
    empleado = crear_empleado(puesto="Analista")
    page.goto(url_web)
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    # Acción
    page.get_by_test_id("empleado-puesto").fill("A")
    page.get_by_test_id("empleado-guardar").click()

    # Verificación
    mensaje_error = page.get_by_test_id("mensaje-error")
    expect(mensaje_error).to_be_visible()
    expect(mensaje_error).to_contain_text("puesto")


def test_cp08_el_selector_de_departamento_no_ofrece_valores_fuera_del_catalogo(
    url_api, page, url_web, crear_empleado
):
    """CP-08: el selector de departamento no ofrece valores fuera del catálogo."""
    # Preparación
    empleado = crear_empleado(departamento="Ventas")
    catalogo = httpx.get(f"{url_api}/api/departamentos")
    assert catalogo.status_code == 200, f"Preparación: {catalogo.text}"
    departamentos_validos = catalogo.json()

    page.goto(url_web)
    page.get_by_test_id(f"editar-empleado-{empleado['id']}").click()

    # Acción
    opciones = page.get_by_test_id("empleado-departamento").locator("option").all_text_contents()

    # Verificación
    assert set(opciones) == set(departamentos_validos)
    assert "Marketing" not in opciones


def test_cp10_dar_de_baja_a_un_empleado_activo(page, url_web, crear_empleado):
    """CP-10: dar de baja a un empleado activo."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2022-05-01")
    page.goto(url_web)
    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()

    # Acción
    page.get_by_test_id("empleado-fecha-baja").fill("2024-03-15")
    page.get_by_test_id("confirmar-baja").click()

    # Verificación
    expect(page.get_by_test_id("mensaje-exito")).to_be_visible()
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")


def test_cp12_error_al_dar_de_baja_con_fecha_anterior_a_ingreso(page, url_web, crear_empleado):
    """CP-12: error al dar de baja con una fecha_baja anterior a la fecha de ingreso."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2023-06-01")
    page.goto(url_web)
    page.get_by_test_id(f"baja-empleado-{empleado['id']}").click()

    # Acción
    page.get_by_test_id("empleado-fecha-baja").fill("2023-01-01")
    page.get_by_test_id("confirmar-baja").click()

    # Verificación
    mensaje_error = page.get_by_test_id("mensaje-error")
    expect(mensaje_error).to_be_visible()
    expect(mensaje_error).to_contain_text("anterior")
