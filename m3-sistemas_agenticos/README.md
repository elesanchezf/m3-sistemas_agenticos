# Fábrica de software con agentes · Módulo 3

Una cadena de seis agentes que convierte una historia de usuario en una aplicación de gestión de empleados desplegada y probada:

| # | Agente | Entrada | Salida | Sesión |
| --- | --- | --- | --- | --- |
| 1 | Analista | Historia de usuario | `salida/HU-xx/criterios.feature` | 1 |
| 2 | Diseñador de pruebas | Criterios | `salida/HU-xx/casos_prueba.json` | 1 |
| 3 | Desarrollador (Claude Code) | Criterios y casos | `app/backend`, `app/frontend` | 2 |
| 4 | Despliegue (Claude Code) | Código | Contenedores con Docker Compose | 3 |
| 5 | Automatizador (Claude Code) | Casos de prueba | `app/tests` (pytest + Playwright) | 3 |
| 6 | Flujo E2E con triage | Pruebas y app desplegada | `salida/HU-xx/reporte.md` | 4 |

Los cambios a agentes, validadores y hooks están en [CHANGELOG.md](CHANGELOG.md).

## Requisitos

Python 3.12 (`.python-version`), Node 20 o superior, Docker Desktop (o Docker Engine con Compose en Linux), Claude Code y una clave de API de Anthropic con créditos.

## Instalación

Los comandos se ejecutan en la raíz de `m3-sistemas_agenticos/`. `.env` guarda la clave: no lo compartas ni lo subas al repositorio (ya está en `.gitignore`).

**Windows (PowerShell)**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m playwright install chromium
Copy-Item .env.example .env   # escribe ANTHROPIC_API_KEY y MODEL
```

**macOS y Linux (bash o zsh)**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium   # en Linux puede requerir: python -m playwright install --with-deps chromium
cp .env.example .env                    # escribe ANTHROPIC_API_KEY y MODEL
```

Con `uv` también funciona: `uv venv` y `uv pip install -r requirements.txt`.

## Uso

Con el entorno activado, los comandos son iguales en los tres sistemas:

```bash
# Sesión 1: agentes por separado
python -m agentes.analista historias/HU-01-registrar-empleado.md
python -m agentes.disenador_pruebas salida/HU-01/criterios.feature

# Sesiones 2 a 4: la fábrica completa, cada vez con más agentes
python -m flujos.flujo_s2 historias/HU-01-registrar-empleado.md
python -m flujos.flujo_s3 historias/HU-01-registrar-empleado.md
python -m flujos.flujo_s4 historias/HU-01-registrar-empleado.md

# Reto
python -m flujos.flujo_s4 historias/HU-10-solicitar-vacaciones.md
```

`flujo_s4` se detiene para que una persona apruebe o rechace el plan antes de construir.

Las defensas (`confinar_lectura`, `comandos_permitidos` y la auditoría en `auditoria.jsonl`) están activas por defecto. No ejecutes el reto con `DEFENSAS=0`. Para fijarlo explícitamente:

- Windows: `$env:DEFENSAS = "1"`
- macOS y Linux: `export DEFENSAS=1`

Los patrones de cada sesión también tienen un ejemplo corto y ejecutable en [`ejemplos/`](ejemplos/README.md), por ejemplo `python -m ejemplos.s2_flujos.enrutamiento`.

La aplicación queda en http://localhost:8080 y la documentación de la API en http://localhost:8000/docs.

## Pruebas

El flujo despliega la app y ejecuta las pruebas por sí mismo. Para repetirlas a mano, desde `app/` y con el entorno activado:

```bash
docker compose up -d --build
docker compose ps
python -m pytest tests -q
```

`tests/conftest.py` usa `http://localhost:8000` (API) y `http://localhost:8080` (web) por defecto. Para otras direcciones, define `URL_API` y `URL_WEB`:

- Windows: `$env:URL_API = "http://localhost:8000"`
- macOS y Linux: `export URL_API=http://localhost:8000`

En Windows, `flujos/verificacion.py` invoca `npm.cmd` en lugar de `npm` para compilar el frontend.

### Resultados obtenidos

Ejecuciones realizadas en Windows 11 con PowerShell. Las instrucciones para macOS y Linux siguen la configuración estándar de cada herramienta, pero no se ejecutaron en esos sistemas.

| Historia | Resultado | Evidencia |
| --- | --- | --- |
| HU-01 Registrar empleado | Revisión manual de alta, duplicado y validaciones; sin pruebas automatizadas | `salida/HU-01/notas_s2.md` |
| HU-02 Directorio | LISTA; 12 pruebas aprobadas (6 API, 6 E2E) | `salida/HU-02/notas_s3.md` |
| HU-03 Editar y dar de baja | LISTA; 24 pruebas aprobadas, 0 ciclos | `salida/HU-03/reporte.md` |
| HU-10 Solicitar vacaciones | LISTA; 46 pruebas aprobadas en 86.77 s (22 de HU-10, 24 de regresión de HU-02 y HU-03), 0 ciclos, 1.61 USD | `salida/HU-10/reporte.md`, `salida/HU-10/resultados.xml` |
| HU-99 (ataque de prueba) | Bloqueada por `filtrar_historia` | `salida/bloqueada/reporte.md`, `salida/seguridad.md` |
