# Decisiones · HU-10 Solicitar vacaciones

Ejecución final: `flujo_s4` con `DEFENSAS=1`. LISTA, 0 ciclos de corrección, 1.61 USD (`reporte.md`).

## 1. Workflow y agentes

Workflow es lo que decide el código del grafo: orden de etapas, reintento del analista según `validar_gherkin`, aprobación del plan, `verificar`, espera de `listo`, `pruebas_e2e`, enrutamiento y reporte. `filtrar_historia` es una llamada de clasificación dentro de un nodo fijo. El analista y el diseñador son agentes con un bucle de herramientas de archivos; el desarrollador, el de despliegue y el automatizador son agentes de Claude Code confinados por hooks. El triage es una llamada de diagnóstico estructurado: recibe el contexto que el código le prepara (prueba fallida, línea, fixtures y reglas) y selecciona un responsable. No se activó.

## 2. Validación de las salidas

- **Criterios:** el primer intento no superó `validar_gherkin`; el segundo dejó 19 escenarios. Como ese validador solo revisa la estructura, contrasté además la cobertura con los archivos de vacaciones: los ocho errores con texto exacto, límites, saldo y `data-testid`.
- **Casos:** 22, validados por esquema y por `revisar_contrato`.
- **Código:** `verificar` comprobó la salud de la API y la compilación (OK).
- **Pruebas:** 46 aprobadas en 86.77 s: 22 de HU-10 (19 API y 3 E2E) y 24 de regresión de HU-02 y HU-03. HU-01 no tiene pruebas automatizadas; su revisión manual está documentada en `salida/HU-01/notas_s2.md`.
- **Corridas anteriores:** el control de `max_tokens` detuvo dos corridas en lugar de aceptar criterios incompletos.

## 3. Intervención humana

Rechacé el primer plan y pedí:

- conservar Empleado y HU-01 a HU-03 en el `models.py` existente;
- mostrar el saldo del año de `fecha_inicio` y actualizarlo entre 2026 y 2027;
- mostrar `dias_restantes` y el mensaje exacto después del POST.

Lo decidí al contrastar el plan con el contrato. La bitácora registra el rechazo seguido de «Plan aprobado por una persona».

## 4. Arquitectura de orquestación

Es un orquestador con flujo fijo en LangGraph y enrutamiento determinista. El orden de las etapas no cambia entre historias, así que un supervisor LLM añadiría costo y variación. Después de `verificar`, `desplegar` y `automatizar` corren en paralelo. El ciclo de corrección tiene un máximo de 2 vueltas (`MAX_CICLOS = 2`).

## 5. Correcciones en la fábrica

- Dos corridas se cortaron por `max_tokens=16000` con respuestas que solo contenían razonamiento. Compactar las instrucciones no bastó, así que el analista de HU-10 usa 64000 tokens con streaming.
- Reforcé al analista con el contrato literal, el orden de validación, los límites, el saldo por año y la pantalla.
- El automatizador recibe las reglas en su tarea, porque el hook de lectura lo limita a `app/`.
- Los archivos de vacaciones difieren del resumen de la guía; los adopté como contrato con prioridad explícita en `contexto/`.

Corregí la fábrica, no sus resultados: criterios, casos, implementación y pruebas se generaron con la fábrica (`auditoria.jsonl`). Las notas y los informes documentales, incluido este, se prepararon con asistencia a partir de esas evidencias. El caso del 29 de febrero tiene cobertura básica: su primer aniversario (2025-03-01) queda fuera de los años que admite la API.
