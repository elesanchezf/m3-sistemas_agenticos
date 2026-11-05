"""Sesión 4 · Triage: ante pruebas fallidas, decide qué agente debe corregir.

Es el supervisor del flujo E2E: no corrige nada, solo enruta con una justificación.
"""
import ast
import os
import re
from typing import Literal

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from agentes.base import APP, RAIZ, SALIDA


class Diagnostico(BaseModel):
    linea_fallida: str  # archivo:línea y código de la línea marcada con >>
    fase: Literal["preparacion", "accion", "verificacion"]  # en qué bloque del test está esa línea
    responsable: Literal["desarrollador", "automatizador", "despliegue"]
    causa: str          # qué falló, en una o dos frases
    criterio: str       # escenario de aceptación que se usa como referencia
    instruccion: str    # qué debe corregir el responsable


PROMPT = """Eres líder técnico. Unas pruebas automatizadas fallaron. Decide quién debe corregir:
- "desarrollador": la aplicación no cumple un criterio de aceptación.
- "automatizador": la prueba contradice el criterio, usa un selector incorrecto, prepara datos
  inválidos o es frágil.
- "despliegue": la aplicación no responde (conexión rechazada, 502, contenedor caído).
El criterio de aceptación manda: si la prueba y la aplicación no coinciden, gana quien siga el criterio.

Antes de elegir responsable, para cada prueba fallida:
1. Localiza la línea fallida (marcada con >> en el código de la prueba) y di en qué fase está:
   preparación (fixtures, creación de datos o llamadas previas a la acción del caso), acción
   (el paso que el caso pone a prueba) o verificación (los asserts sobre el resultado de la acción).
2. Si falla en la preparación, comprueba primero si los datos preparados cumplen las reglas de
   negocio (fechas, catálogos, formatos). Si no las cumplen, la aplicación hizo bien en rechazarlos
   y el responsable es el automatizador. Solo es del desarrollador si los datos son válidos y la
   aplicación los rechaza en contra de un criterio.
3. Si `select_option` agota el tiempo con «did not find some options», el valor no existe en el
   control: compáralo con el catálogo de las reglas antes de culpar a la aplicación.

## Reglas de negocio
{reglas}

## Criterios de aceptación
{criterios}

## Pruebas fallidas
{fallos}

## Código de las pruebas fallidas y sus fixtures
{codigo}"""


def _funciones(ruta) -> dict[str, ast.FunctionDef]:
    return {n.name: n for n in ast.walk(ast.parse(ruta.read_text(encoding="utf-8")))
            if isinstance(n, ast.FunctionDef)}


def _fragmento(ruta, nodo: ast.FunctionDef, linea: int | None) -> str:
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    desde = min([nodo.lineno] + [d.lineno for d in nodo.decorator_list])
    return "\n".join(f"{'>>' if i == linea else '  '} {i:4} | {lineas[i - 1]}"
                     for i in range(desde, nodo.end_lineno + 1))


def contexto_pruebas(fallos: str) -> str:
    """Código de cada test fallido (con la línea fallida marcada) y de los fixtures que usa."""
    conftest = APP / "tests" / "conftest.py"
    fixtures = _funciones(conftest) if conftest.exists() else {}
    bloques, vistos = [], set()
    patron = r"^- (tests\.[\w.]+)::(\w+)[^\n]*(?:\n  en (tests/\S+?\.py):(\d+))?"
    for modulo, nombre, ruta_linea, linea in re.findall(patron, fallos, re.MULTILINE):
        ruta = APP / (modulo.replace(".", "/") + ".py")
        if not ruta.exists() or nombre not in (funciones := _funciones(ruta)):
            continue
        en_test = ruta_linea == modulo.replace(".", "/") + ".py"
        nodo = funciones[nombre]
        bloques.append(f"### {ruta.relative_to(APP).as_posix()}\n{_fragmento(ruta, nodo, int(linea) if en_test else None)}")
        for arg in (a.arg for a in nodo.args.args):
            if arg in fixtures and arg not in vistos:
                vistos.add(arg)
                fallo_aqui = int(linea) if ruta_linea == "tests/conftest.py" else None
                bloques.append(f"### tests/conftest.py · fixture {arg}\n{_fragmento(conftest, fixtures[arg], fallo_aqui)}")
    return "\n\n".join(bloques)[:8000] or "(no se encontró el código de las pruebas)"


def diagnosticar(hu: str, fallos: str) -> Diagnostico:
    llm = ChatAnthropic(model=os.environ["MODEL"], max_tokens=2000)
    criterios = (SALIDA / hu / "criterios.feature").read_text(encoding="utf-8")
    reglas = (RAIZ / "contexto" / "reglas_negocio.md").read_text(encoding="utf-8")
    return llm.with_structured_output(Diagnostico).invoke(PROMPT.format(
        reglas=reglas, criterios=criterios, fallos=fallos[:6000], codigo=contexto_pruebas(fallos)))
