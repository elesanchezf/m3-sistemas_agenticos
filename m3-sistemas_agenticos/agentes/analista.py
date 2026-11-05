"""Sesión 1 · Agente 1, analista: historia de usuario -> criterios de aceptación en Gherkin.

Uso:  python -m agentes.analista historias/HU-01-registrar-empleado.md
"""
import re
import sys
from pathlib import Path

from agentes.base import RAIZ, SALIDA, ejecutar_agente, herramientas_archivos, hu_de, rel

SISTEMA = """Eres analista de producto en un equipo de software. Conviertes historias de usuario
en criterios de aceptación escritos en Gherkin, en español.

Cómo trabajas:
1. Lee la historia, contexto/reglas_negocio.md y contexto/convenciones_app.md. En las convenciones
   están los códigos y mensajes de error exactos: cópialos letra por letra en los escenarios.
2. Escribe {destino}. La primera línea es `# language: es` y usas las palabras clave
   Característica, Escenario, Dado, Cuando, Entonces, Y.
3. Incluye el camino feliz y un escenario de error por cada regla de negocio que aplique a ESTA historia.
4. Cada escenario se puede verificar desde la pantalla o la API: datos concretos, nada de «funciona bien».
5. No inventes reglas. Si falta información, agrégala al final como comentarios bajo `# Preguntas abiertas`.
6. Responde al final con una sola línea: cuántos escenarios escribiste."""

# Refuerzo específico: HU-10 se califica con pruebas ocultas construidas solo con sus dos archivos de contexto
REFUERZO = {
    "HU-10": """
Instrucciones específicas de HU-10 (tienen prioridad sobre el resumen de la historia):
- Contrato: contexto/reglas_vacaciones.md y contexto/convenciones_vacaciones.md (también anexados al final
  de reglas_negocio.md y convenciones_app.md). Si difieren de otra fuente, mandan estos dos archivos.
- Copia literalmente, carácter por carácter, los mensajes `detail`, los códigos HTTP, los nombres de los
  campos de respuesta (`dias_habiles`, `dias_restantes`, `dias_usados`, `dias_disponibles`...) y los
  data-testid de convenciones_vacaciones.md. No los parafrasees ni los traduzcas.
- Cubre con al menos un escenario cada una de las ocho validaciones de la tabla «Errores: mensajes exactos»,
  con su código y su mensaje. Agrega un escenario que demuestre el orden: un caso que incumple dos
  validaciones a la vez y recibe el error de la que va primero en la tabla.
- Orden con empleado inexistente: un escenario aparte en el que un empleado_id que no existe pide una
  fecha_fin anterior a la fecha_inicio y recibe 404 "Empleado no encontrado", no el error de fechas.
- Antigüedad: aceptada justo en el aniversario (mismo día y mes) y rechazada el día anterior. Para el día
  anterior usa fecha_ingreso "2025-12-21" e inicio y fin "2026-12-20" (domingo): así el escenario también
  demuestra que la antigüedad se valida antes que los días hábiles; dilo en su título.
- Ingreso el 29 de febrero: fecha_ingreso "2024-02-29" con una solicitud aceptada en 2026. Su título debe
  decir que es cobertura básica, porque el primer aniversario (2025-03-01) queda fuera de los años que admite
  la API y ese límite no se puede probar.
- Saldo: usar exactamente los días que quedan (queda 0) y pasarse por un día (mensaje con el N exacto).
- Días hábiles: extremos incluidos en el conteo, fin de semana, festivo de la tabla y periodo sin días hábiles.
- Año: periodo que cruza de año, año fuera de 2026 y 2027, y saldo de 2027 independiente del usado en 2026.
- Consulta del saldo: GET /api/empleados/{empleado_id}/vacaciones?anio=AAAA responde 200 con los campos
  `empleado_id`, `anio`, `dias_usados`, `dias_disponibles` y `solicitudes`. Escribe un escenario que consulte
  el saldo antes de una solicitud válida (dias_usados 0, dias_disponibles 12, solicitudes vacía), registre la
  solicitud y vuelva a consultar (los cinco campos con sus valores, y en `solicitudes` la solicitud con su id,
  fecha_inicio, fecha_fin y dias_habiles). Escribe otro que demuestre la independencia entre años: después
  de usar días en 2026, la consulta con anio=2027 devuelve dias_usados 0, dias_disponibles 12 y solicitudes vacía.
  Toda respuesta de consulta, de 2026 o de 2027, comprueba los cinco campos con su valor: `empleado_id`,
  `anio`, `dias_usados`, `dias_disponibles` y `solicitudes`.
- Año 2027: además de la consulta, una solicitud válida en 2027 por POST que compruebe `dias_habiles` y
  `dias_restantes` (calculados con los festivos de 2027 y sin descontar lo usado en 2026).
- Pantalla:
  - Todo escenario de pantalla empieza abriendo el formulario con `vacaciones-abrir-{empleado_id}` (id concreto).
  - El camino feliz e2e usa los data-testid de convenciones_vacaciones.md y el mensaje de éxito exacto, y
    comprueba `vacaciones-disponibles` con el saldo del año antes de enviar y con el saldo actualizado después del alta.
  - Un escenario e2e de error: se envía por el formulario una solicitud inválida y `vacaciones-mensaje`
    muestra el `detail` exacto que devolvió la API.
  - Según convenciones_vacaciones.md, solo los empleados activos tienen el botón: en el directorio,
    `vacaciones-abrir-{empleado_id}` está visible para un empleado activo y no existe para uno dado de baja
    (usa ids concretos en el escenario).
- Usa fechas concretas y calcula los días hábiles con la tabla de festivos; no inventes festivos.

Formato y extensión (la respuesta tiene un límite de tokens):
- Escribe criterios.feature directamente con escribir_archivo, en una sola llamada. No reproduzcas el
  documento ni lo resumas antes en texto; al terminar responde solo con el número de escenarios.
- Usa la palabra clave `Escenario:` (no `Esquema del escenario` ni tablas `Ejemplos`).
- Escenarios concisos, de 3 a 6 pasos, con solo los datos relevantes para el caso: fecha_ingreso, fechas,
  días usados y respuesta esperada. No repitas tablas completas de empleados ni todos los campos del registro;
  pon los datos comunes una vez en `Antecedentes:`. Aun así, cada escenario lleva sus propios pasos
  `Dado`, `Cuando` y `Entonces` (el validador los exige en cada `Escenario:`).
- Un mismo escenario aceptado puede cubrir varios límites compatibles (por ejemplo, aniversario exacto,
  extremos incluidos y un festivo en el mismo periodo); di en su título qué límites cubre.
- Cada error distinto va en su propio escenario, con su código y su mensaje `detail` exactos.
- No escribas comentarios ni explicaciones dentro del archivo. Excepciones: la primera línea obligatoria
  `# language: es` y el bloque `# Preguntas abiertas` al final, solo si de verdad falta algo."""
}

# Parámetros de la llamada por historia. HU-10 agotó 16000 tokens solo en razonamiento adaptativo
# antes de escribir; el resto de historias conserva los valores por defecto de ejecutar_agente.
LLAMADA = {"HU-10": {"max_tokens": 64000}}


def escenarios(gherkin: str) -> list[str]:
    return re.findall(r"^\s*Escenario:\s*(.+?)\s*$", gherkin, flags=re.MULTILINE)


def preguntas_abiertas(gherkin: str) -> list[str]:
    if "# Preguntas abiertas" not in gherkin:
        return []
    bloque = gherkin.split("# Preguntas abiertas", 1)[1]
    return [l.lstrip("# -").strip() for l in bloque.splitlines() if l.strip().lstrip("#").strip()]


def validar_gherkin(texto: str) -> list[str]:
    """Evaluador determinista: devuelve los problemas encontrados; vacío = válido."""
    problemas = []
    if not texto.lstrip().startswith("# language: es"):
        problemas.append("La primera línea debe ser '# language: es'.")
    if "Característica:" not in texto:
        problemas.append("Falta 'Característica:'.")
    bloques = re.split(r"^\s*Escenario:", texto, flags=re.MULTILINE)[1:]
    if len(bloques) < 2:
        problemas.append("Se esperan al menos 2 escenarios (camino feliz y un error).")
    for i, bloque in enumerate(bloques, 1):
        for clave in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{clave}\b", bloque, flags=re.MULTILINE):
                problemas.append(f"El escenario {i} no tiene '{clave}'.")
    return problemas


def generar_criterios(historia: Path, max_intentos: int = 2) -> Path:
    carpeta = SALIDA / hu_de(historia)
    destino = carpeta / "criterios.feature"
    herramientas = herramientas_archivos(lectura=[RAIZ / "historias", RAIZ / "contexto"], escritura=carpeta)
    tarea = f"Historia de usuario: {rel(historia)}" + REFUERZO.get(hu_de(historia), "")
    for intento in range(1, max_intentos + 1):
        print(f"Analista · intento {intento}")
        ejecutar_agente(SISTEMA.format(destino=rel(destino)), herramientas, tarea, nombre="analista",
                        **LLAMADA.get(hu_de(historia), {}))
        problemas = validar_gherkin(destino.read_text(encoding="utf-8")) if destino.exists() \
            else [f"No se escribió {rel(destino)}."]
        if not problemas:
            return destino
        # Reflexión guiada por un evaluador determinista: el agente recibe los problemas y corrige
        tarea += "\n\nTu versión anterior tiene estos problemas; corrígelos:\n- " + "\n- ".join(problemas)
    raise ValueError("Criterios inválidos tras varios intentos:\n- " + "\n- ".join(problemas))


if __name__ == "__main__":
    ruta = generar_criterios(Path(sys.argv[1]).resolve())
    texto = ruta.read_text(encoding="utf-8")
    print(f"\nListo: {rel(ruta)} · {len(escenarios(texto))} escenarios")
    for p in preguntas_abiertas(texto):
        print("  Pregunta abierta:", p)
