"""Pruebas de API para HU-02: ver y buscar el directorio de empleados."""

import uuid

import httpx


def test_cp01_directorio_devuelve_empleados_con_todos_los_campos(url_api, crear_empleado):
    """CP-01: el directorio de empleados devuelve los campos esperados."""
    emp1 = crear_empleado(nombre="Ana López", puesto="Analista", departamento="Tecnología")
    emp2 = crear_empleado(nombre="Juan Pérez", puesto="Vendedor", departamento="Ventas")

    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200

    empleados = {e["correo"]: e for e in respuesta.json()}
    for esperado in (emp1, emp2):
        encontrado = empleados[esperado["correo"]]
        assert encontrado["numero_empleado"] == esperado["numero_empleado"]
        assert encontrado["nombre"] == esperado["nombre"]
        assert encontrado["puesto"] == esperado["puesto"]
        assert encontrado["departamento"] == esperado["departamento"]
        assert encontrado["estado"] == "activo"


def test_cp03_buscar_por_nombre_sin_distinguir_mayusculas(url_api, crear_empleado):
    """CP-03: buscar por nombre no distingue mayúsculas ni minúsculas."""
    nombre = f"Ana López {uuid.uuid4().hex[:6]}"
    empleado = crear_empleado(nombre=nombre)

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": nombre.upper()})
    assert respuesta.status_code == 200

    empleados = respuesta.json()
    encontrado = next(e for e in empleados if e["correo"] == empleado["correo"])
    assert encontrado["nombre"] == nombre


def test_cp05_buscar_por_correo_sin_distinguir_mayusculas(url_api, crear_empleado):
    """CP-05: buscar por correo no distingue mayúsculas ni minúsculas."""
    empleado = crear_empleado()

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": empleado["correo"].upper()})
    assert respuesta.status_code == 200

    empleados = respuesta.json()
    encontrado = next(e for e in empleados if e["correo"] == empleado["correo"])
    assert encontrado["correo"] == empleado["correo"]


def test_cp07_filtrar_por_departamento(url_api, crear_empleado):
    """CP-07: filtrar empleados por departamento devuelve solo ese departamento."""
    emp1 = crear_empleado(departamento="Tecnología")
    emp2 = crear_empleado(departamento="Ventas")
    emp3 = crear_empleado(departamento="Tecnología")

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"departamento": "Tecnología"})
    assert respuesta.status_code == 200

    empleados = respuesta.json()
    assert all(e["departamento"] == "Tecnología" for e in empleados)

    correos_devueltos = {e["correo"] for e in empleados}
    assert emp1["correo"] in correos_devueltos
    assert emp3["correo"] in correos_devueltos
    assert emp2["correo"] not in correos_devueltos


def test_cp09_buscar_sin_resultados_devuelve_lista_vacia(url_api):
    """CP-09: buscar un término inexistente devuelve una lista vacía."""
    termino = f"Inexistente-{uuid.uuid4().hex}"

    respuesta = httpx.get(f"{url_api}/api/empleados", params={"buscar": termino})
    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_cp11_empleado_de_baja_aparece_en_el_directorio(url_api, crear_empleado, marcar_baja):
    """CP-11: un empleado dado de baja sigue apareciendo en el listado general."""
    empleado = crear_empleado(nombre="Marta Ruiz", departamento="Finanzas")
    marcar_baja(empleado["id"])

    respuesta = httpx.get(f"{url_api}/api/empleados")
    assert respuesta.status_code == 200

    encontrado = next(e for e in respuesta.json() if e["correo"] == empleado["correo"])
    assert encontrado["nombre"] == "Marta Ruiz"
    assert encontrado["departamento"] == "Finanzas"
    assert encontrado["estado"] == "baja"
