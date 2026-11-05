"""Sesión 3 · Agente 5, automatizador: casos de prueba -> pruebas con pytest y Playwright.

Uso:  python -m agentes.automatizador HU-01
"""
import sys

from agentes.base import APP, RAIZ, SALIDA
from agentes.claude_code import EDICION, ejecutar_claude_code

INSTRUCCIONES = """Eres el ingeniero de automatización de pruebas del equipo. Conviertes casos de prueba
en pruebas automatizadas. Nunca modificas el código de la aplicación: si una prueba falla
porque la aplicación está mal, lo reportas, no lo arreglas."""

ESCRITURA = ["tests/*"]
PROGRAMAS = {"cd", "ls", "cat", "python", "python3", "pytest"}

TAREA = """Automatiza los casos de prueba de {hu}:

{casos}

Reglas:
- tests/conftest.py define dos fixtures: `url_api` (variable URL_API, por defecto http://localhost:8000)
  y `url_web` (variable URL_WEB, por defecto http://localhost:8080). Si ya existe, consérvalo.
- Casos de nivel "api": tests/api/test_{hu_min}.py con pytest y httpx.
- Casos de nivel "e2e": tests/e2e/test_{hu_min}_e2e.py con pytest-playwright (fixture `page`),
  usando page.get_by_test_id(...) con los data-testid de CLAUDE.md.
- Un test por caso; su docstring empieza con el id del caso (por ejemplo "CP-03: ...").
- Cada test crea sus propios datos con correos únicos (uuid) para poder repetirse sin choques.
- Separa cada test en tres bloques comentados: `# Preparación`, `# Acción` y `# Verificación`.
  La acción es solo el paso que el caso pone a prueba. Todo assert de la preparación lleva un
  mensaje que empieza con "Preparación:" e incluye la respuesta (`respuesta.text`), para que un
  fallo al preparar datos no se confunda con un fallo de la aplicación.
- Los datos de preparación cumplen las reglas de negocio que van al final de esta tarea (fechas de
  ingreso, aniversarios, festivos, saldos y límites del año). Para un empleado dado de
  baja, pasa siempre una `fecha_ingreso` explícita en el pasado y una `fecha_baja` igual o posterior
  a ella y no futura (por ejemplo, ingreso "2022-03-01" y baja "2024-06-15"). Nunca combines
  `date.today()` con una fecha fija pasada. Prepara los estados con los endpoints de la app cuando existan.
- Antes de usar `select_option`, comprueba las opciones reales (con `GET /api/departamentos` o
  leyendo los `option` del control) y elige solo valores que existan. Un valor fuera del catálogo no
  se puede elegir en pantalla: el caso e2e de un valor fuera del catálogo comprueba que las opciones
  del selector coinciden con el catálogo y no incluyen el valor inválido, sin intentar seleccionarlo.
  El rechazo del valor inválido se prueba en el caso api equivalente, que se conserva.
- Comprueba la sintaxis con `python -m pytest tests --collect-only -q`. No ejecutes las pruebas completas.
Responde con la lista de archivos y cuántos tests escribiste."""


def automatizar(hu: str, errores: str = "") -> tuple[str, float]:
    casos = (SALIDA / hu / "casos_prueba.json").read_text(encoding="utf-8")
    prompt = TAREA.format(hu=hu, casos=casos, hu_min=hu.lower().replace("-", "_"))
    # el hook de lectura no deja salir de app/: las reglas viajan en el prompt, como con el desarrollador
    prompt += f"\n\n## Reglas de negocio\n{(RAIZ / 'contexto' / 'reglas_negocio.md').read_text(encoding='utf-8')}"
    if errores:
        prompt += f"\n\nEstas pruebas fallaron y el diagnóstico dice que el error está en la prueba:\n{errores}"
    return ejecutar_claude_code(prompt, agente="automatizador", cwd=APP, herramientas=EDICION,
                                escritura=ESCRITURA, programas=PROGRAMAS, instrucciones=INSTRUCCIONES)


if __name__ == "__main__":
    print(automatizar(sys.argv[1])[0])
