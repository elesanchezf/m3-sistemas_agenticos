"""Pruebas end-to-end para HU-10: solicitar y consultar vacaciones."""

import httpx
from playwright.sync_api import expect


def test_cp18_el_boton_de_vacaciones_solo_aparece_para_empleados_activos(
    url_api, page, url_web, crear_empleado
):
    """CP-18: el botón de solicitar vacaciones solo aparece para empleados activos."""
    # Preparación
    activo = crear_empleado(fecha_ingreso="2024-03-10")
    baja = crear_empleado(fecha_ingreso="2020-01-01")
    respuesta_baja = httpx.put(
        f"{url_api}/api/empleados/{baja['id']}/baja", json={"fecha_baja": "2024-06-15"}
    )
    assert respuesta_baja.status_code == 200, f"Preparación: {respuesta_baja.text}"

    # Acción
    page.goto(url_web)

    # Verificación
    expect(page.get_by_test_id("tabla-empleados")).to_be_visible()
    expect(page.get_by_test_id(f"vacaciones-abrir-{activo['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"vacaciones-abrir-{baja['id']}")).to_have_count(0)


def test_cp20_camino_feliz_e2e_registrar_una_solicitud_desde_el_formulario(
    page, url_web, crear_empleado
):
    """CP-20: camino feliz e2e - registrar una solicitud desde el formulario."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")
    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()
    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("12")

    # Acción
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-06")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-10")
    page.get_by_test_id("vacaciones-enviar").click()

    # Verificación
    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."
    )
    expect(page.get_by_test_id("vacaciones-disponibles")).to_have_text("7")


def test_cp22_error_e2e_el_formulario_muestra_el_detail_exacto_de_la_api(
    page, url_web, crear_empleado
):
    """CP-22: error e2e - el formulario muestra el detail exacto de la API."""
    # Preparación
    empleado = crear_empleado(fecha_ingreso="2024-03-10")
    page.goto(url_web)
    page.get_by_test_id(f"vacaciones-abrir-{empleado['id']}").click()

    # Acción
    page.get_by_test_id("vacaciones-fecha-inicio").fill("2026-07-10")
    page.get_by_test_id("vacaciones-fecha-fin").fill("2026-07-06")
    page.get_by_test_id("vacaciones-enviar").click()

    # Verificación
    expect(page.get_by_test_id("vacaciones-mensaje")).to_have_text(
        "La fecha de fin no puede ser anterior a la fecha de inicio"
    )
