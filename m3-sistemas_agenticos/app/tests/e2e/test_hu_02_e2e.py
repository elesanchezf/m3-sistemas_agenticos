"""Pruebas end-to-end para HU-02: ver y buscar el directorio de empleados."""

import uuid

from playwright.sync_api import expect


def test_cp02_directorio_muestra_las_filas_de_empleados_activos(page, url_web, crear_empleado):
    """CP-02: el directorio muestra la fila de cada empleado con sus datos."""
    emp1 = crear_empleado(nombre="Ana López", departamento="Tecnología")
    emp2 = crear_empleado(nombre="Juan Pérez", departamento="Ventas")

    page.goto(url_web)

    expect(page.get_by_test_id("tabla-empleados")).to_be_visible()
    expect(page.get_by_test_id(f"fila-empleado-{emp1['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"fila-empleado-{emp2['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{emp1['id']}")).to_have_text(emp1["numero_empleado"])
    expect(page.get_by_test_id(f"numero-empleado-{emp2['id']}")).to_have_text(emp2["numero_empleado"])
    expect(page.get_by_test_id(f"estado-empleado-{emp1['id']}")).to_have_text("Activo")
    expect(page.get_by_test_id(f"estado-empleado-{emp2['id']}")).to_have_text("Activo")


def test_cp04_buscar_por_nombre_sin_distinguir_mayusculas(page, url_web, crear_empleado):
    """CP-04: buscar por nombre en mayúsculas encuentra al empleado."""
    nombre = f"Ana López {uuid.uuid4().hex[:6]}"
    empleado = crear_empleado(nombre=nombre)

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(nombre.upper())

    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(fila).to_contain_text(nombre)


def test_cp06_buscar_por_correo_sin_distinguir_mayusculas(page, url_web, crear_empleado):
    """CP-06: buscar por correo en mayúsculas encuentra al empleado."""
    empleado = crear_empleado()

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(empleado["correo"].upper())

    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(fila).to_contain_text(empleado["correo"])


def test_cp08_filtrar_por_departamento(page, url_web, crear_empleado):
    """CP-08: filtrar por departamento muestra solo empleados de ese departamento."""
    emp1 = crear_empleado(departamento="Tecnología")
    emp2 = crear_empleado(departamento="Ventas")
    emp3 = crear_empleado(departamento="Tecnología")

    page.goto(url_web)
    page.get_by_test_id("filtro-departamento").select_option("Tecnología")

    expect(page.get_by_test_id(f"fila-empleado-{emp1['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"fila-empleado-{emp3['id']}")).to_be_visible()
    expect(page.get_by_test_id(f"fila-empleado-{emp2['id']}")).to_have_count(0)


def test_cp10_buscar_sin_resultados_muestra_mensaje(page, url_web):
    """CP-10: buscar un término inexistente muestra el mensaje de sin resultados."""
    termino = f"Inexistente-{uuid.uuid4().hex}"

    page.goto(url_web)
    page.get_by_test_id("buscar-empleados").fill(termino)

    sin_resultados = page.get_by_test_id("sin-resultados")
    expect(sin_resultados).to_be_visible()
    expect(sin_resultados).to_have_text("No se encontraron resultados")
    expect(page.get_by_test_id("tabla-empleados")).to_have_count(0)


def test_cp12_empleado_de_baja_aparece_en_el_directorio(page, url_web, crear_empleado, marcar_baja):
    """CP-12: un empleado dado de baja aparece en el directorio con estado Baja."""
    empleado = crear_empleado(nombre="Marta Ruiz", departamento="Finanzas")
    marcar_baja(empleado["id"])

    page.goto(url_web)

    fila = page.get_by_test_id(f"fila-empleado-{empleado['id']}")
    expect(fila).to_be_visible()
    expect(page.get_by_test_id(f"numero-empleado-{empleado['id']}")).to_have_text(empleado["numero_empleado"])
    expect(page.get_by_test_id(f"estado-empleado-{empleado['id']}")).to_have_text("Baja")
