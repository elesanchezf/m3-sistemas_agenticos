# Changelog

Cambios relevantes a los agentes, los validadores y los hooks de la fábrica respecto del material inicial del curso. Los cambios en `app/` y `salida/` los generó la fábrica y no se listan aquí.

## HU-10 · Reto (2026-11-05, pendiente de commit)

### Agentes

- `agentes/base.py`: `ejecutar_agente()` acepta `max_tokens` (por defecto 16000) y `effort` (opcional) por llamada.
  - Por encima de 16000 usa `messages.stream()` con `get_final_message()`, porque el SDK rechaza peticiones sin streaming que podrían superar los 10 minutos.
  - Con los valores por defecto, la petición es idéntica a la anterior.
- `agentes/analista.py`:
  - El analista lee también `contexto/reglas_negocio.md` y copia letra por letra los códigos y mensajes de las convenciones.
  - Nuevo `REFUERZO["HU-10"]`. Exige:
    - el contrato de `reglas_vacaciones.md` y `convenciones_vacaciones.md`;
    - las ocho validaciones y su orden, incluido el 404 frente a fechas inválidas;
    - los límites de antigüedad, saldo, días hábiles y año;
    - la consulta `GET ?anio=` con sus cinco campos, un POST en 2027 y los escenarios de pantalla con `vacaciones-abrir-{id}`, `vacaciones-disponibles` y `vacaciones-mensaje`.

    También impone reglas de formato para limitar la extensión.
  - Nuevo `LLAMADA = {"HU-10": {"max_tokens": 64000}}`. Dos corridas se cortaron por `max_tokens=16000` mientras el modelo razonaba. Las demás historias conservan los valores por defecto.
- `agentes/disenador_pruebas.py`: el diseñador lee también `reglas_negocio.md` para elegir fechas, festivos y límites concretos.
- `agentes/automatizador.py`:
  - Las reglas de negocio se añaden a la tarea, porque el hook de lectura confina al agente a `app/`.
  - Los datos de preparación deben respetar aniversarios, festivos y saldos.

### Contexto

- Se añadieron `historias/HU-10-solicitar-vacaciones.md`, `contexto/reglas_vacaciones.md` y `contexto/convenciones_vacaciones.md`, copiados sin cambios del material del reto.
- Las reglas y convenciones de vacaciones se anexaron una sola vez, entre marcas `<!-- inicio/fin -->`, a `reglas_negocio.md` y `convenciones_app.md`.
- Se añadió una aclaración: HU-10 usa los códigos (incluidos los 400) y los mensajes de su tabla específica, que prevalecen sobre la tabla general. HU-01 a HU-03 conservan 404, 409 y 422.

### Validadores y hooks

- Sin cambios en esta etapa.

### Resultado

`flujo_s4` con `DEFENSAS=1` terminó en estado LISTA:

- 46 pruebas aprobadas en 86.77 s: 22 de HU-10 y 24 de regresión de HU-02 y HU-03;
- 0 ciclos de corrección;
- 1.61 USD.

## Lab 4 · HU-03 y seguridad (543e638, 2026-11-05)

### Validadores

- `agentes/disenador_pruebas.py`: nuevo `revisar_contrato(plan)`, que se invoca en `guardar_casos` y en `validar_plan`.
  - Rechaza siempre identificadores `EMP-000X` en rutas y `data-testid`.
  - Solo en HU-03 rechaza `PATCH` y `POST /api/empleados/...`, porque edición y baja usan `PUT`. HU-10 conserva su `POST .../vacaciones`.
- `agentes/disenador_pruebas.py`: reglas de contrato en las instrucciones:
  - el id entero frente a `numero_empleado`;
  - solo métodos y rutas documentados;
  - `<select>` limitado al catálogo.

### Agentes

- `agentes/automatizador.py`: instrucciones nuevas para las pruebas.
  - Cada prueba se divide en bloques Preparación, Acción y Verificación, y los `assert` de preparación empiezan con «Preparación:».
  - Las fechas de baja deben ser coherentes.
  - `select_option` solo admite opciones reales.
- `agentes/triage.py`:
  - `Diagnostico` incorpora `linea_fallida` y `fase`.
  - `contexto_pruebas()` extrae con `ast` la prueba fallida, con la línea marcada, y los fixtures de `conftest`.
  - El triage recibe `reglas_negocio.md`.
- `flujos/verificacion.py`: `ejecutar_pruebas()` añade la ubicación `tests/...py:N` del fallo.

### Contexto

- `contexto/convenciones_app.md`: contrato de HU-03.
  - Identificadores con id entero.
  - `PUT /api/empleados/{id}` y `PUT /api/empleados/{id}/baja`.
  - Una baja repetida devuelve 200 y conserva la fecha.
  - Editar un empleado dado de baja devuelve 409.

### Hooks

- Sin cambios en `seguridad/hooks.py`:
  - `confinar_escritura` siempre está activo;
  - `confinar_lectura`, `comandos_permitidos` y `auditar` (que escribe en `auditoria.jsonl`) se activan con `DEFENSAS` distinto de 0.
- Comprobación con HU-99: `filtrar_historia` la bloqueó. Los detalles del contexto envenenado y del endurecimiento de prompts están en `salida/seguridad.md`.

## Lab 2 · HU-01 (d00ea73, 2026-11-03)

- `flujos/verificacion.py`: `verificar_frontend()` usa `npm.cmd` en Windows y `npm` en los demás sistemas, sin `shell=True`. Corrige el `FileNotFoundError` (WinError 2) que impedía compilar el frontend.
