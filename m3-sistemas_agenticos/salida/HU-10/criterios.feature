# language: es
Característica: Solicitar vacaciones

  Antecedentes:
    Dado que el sistema tiene registrados los siguientes empleados:
      | id | nombre     | fecha_ingreso | estado |
      | 20 | Ana García | 2024-03-10    | activo |
      | 21 | Luis Pérez | 2025-12-21    | activo |
      | 22 | Marta Ruiz | 2024-02-29    | activo |
      | 23 | Jorge Díaz | 2020-01-01    | baja   |
      | 24 | Carla Soto | 2020-01-01    | activo |

  Escenario: Camino feliz - solicitud válida registra días hábiles y días restantes
    Dado que el empleado 20 no tiene solicitudes registradas en 2026
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10"
    Entonces la respuesta tiene código 201
    Y el campo `dias_habiles` es 5
    Y el campo `dias_restantes` es 7

  Escenario: Usar exactamente los días que quedan agota el saldo del año (queda 0)
    Dado que el empleado 20 ya tiene registrada una solicitud de 5 días hábiles en 2026 del "2026-07-06" al "2026-07-10"
    Cuando solicita vacaciones del "2026-07-13" al "2026-07-21"
    Entonces la respuesta tiene código 201
    Y el campo `dias_habiles` es 7
    Y el campo `dias_restantes` es 0

  Escenario: Pasarse por un día del saldo disponible se rechaza con el N exacto
    Dado que el empleado 24 ya tiene registrada una solicitud de 4 días hábiles en 2026 del "2026-06-01" al "2026-06-04"
    Cuando solicita vacaciones del "2026-08-03" al "2026-08-13"
    Entonces la respuesta tiene código 400
    Y el campo `detail` es "La solicitud excede los días disponibles: quedan 8 días hábiles"

  Escenario: Aniversario exacto de antigüedad, festivo y fines de semana no cuentan, extremos incluidos
    Dado que el empleado 21 no tiene solicitudes registradas en 2026
    Cuando solicita vacaciones del "2026-12-21" al "2026-12-31"
    Entonces la respuesta tiene código 201
    Y el campo `dias_habiles` es 8
    Y el campo `dias_restantes` es 4

  Escenario: Un día antes del aniversario se rechaza por antigüedad, validada antes que los días hábiles
    Dado que el empleado 21 no tiene solicitudes registradas en 2026
    Cuando solicita vacaciones del "2026-12-20" al "2026-12-20"
    Entonces la respuesta tiene código 400
    Y el campo `detail` es "Se requiere al menos un año de antigüedad a la fecha de inicio"

  Escenario: Ingreso un 29 de febrero cumple la antigüedad en 2026 (cobertura básica)
    Dado que el empleado 22 no tiene solicitudes registradas en 2026
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10"
    Entonces la respuesta tiene código 201
    Y el campo `dias_habiles` es 5
    Y el campo `dias_restantes` es 7

  Escenario: Un periodo que cae completo en fin de semana no tiene días hábiles y se rechaza
    Dado que el empleado 24 no tiene solicitudes registradas en 2026
    Cuando solicita vacaciones del "2026-07-11" al "2026-07-12"
    Entonces la respuesta tiene código 400
    Y el campo `detail` es "El periodo no incluye días hábiles"

  Escenario: La fecha de fin anterior a la fecha de inicio se rechaza
    Dado que el empleado 24 no tiene solicitudes registradas en 2026
    Cuando solicita vacaciones del "2026-07-10" al "2026-07-06"
    Entonces la respuesta tiene código 400
    Y el campo `detail` es "La fecha de fin no puede ser anterior a la fecha de inicio"

  Escenario: Un periodo que cruza de un año a otro se rechaza
    Dado que el empleado 24 no tiene solicitudes registradas en 2026
    Cuando solicita vacaciones del "2026-12-28" al "2027-01-08"
    Entonces la respuesta tiene código 400
    Y el campo `detail` es "Las vacaciones deben estar dentro de un mismo año calendario"

  Escenario: Un año fuera de la tabla de festivos se rechaza
    Dado que el empleado 24 no tiene solicitudes registradas en 2028
    Cuando solicita vacaciones del "2028-07-06" al "2028-07-10"
    Entonces la respuesta tiene código 400
    Y el campo `detail` es "Solo se pueden solicitar vacaciones en 2026 y 2027"

  Escenario: Un empleado inexistente se rechaza con 404
    Dado que el empleado 999 no existe en el sistema
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10"
    Entonces la respuesta tiene código 404
    Y el campo `detail` es "Empleado no encontrado"

  Escenario: Un empleado dado de baja se rechaza con 409
    Dado que el empleado 23 está dado de baja
    Cuando solicita vacaciones del "2026-07-06" al "2026-07-10"
    Entonces la respuesta tiene código 409
    Y el campo `detail` es "No se pueden solicitar vacaciones para un empleado dado de baja"

  Escenario: El empleado inexistente se valida antes que el orden de las fechas
    Dado que el empleado 999 no existe en el sistema
    Cuando solicita vacaciones del "2026-07-10" al "2026-07-06"
    Entonces la respuesta tiene código 404
    Y el campo `detail` es "Empleado no encontrado"

  Escenario: Una solicitud en 2027 calcula sus días con los festivos de 2027 sin descontar lo usado en 2026
    Dado que el empleado 20 ya tiene registrada una solicitud de 5 días hábiles en 2026 del "2026-07-06" al "2026-07-10"
    Cuando solicita vacaciones del "2027-09-13" al "2027-09-17"
    Entonces la respuesta tiene código 201
    Y el campo `dias_habiles` es 4
    Y el campo `dias_restantes` es 8

  Escenario: Consultar el saldo antes y después de registrar una solicitud válida
    Dado que el empleado 20 no tiene solicitudes registradas en 2026
    Cuando consulta su saldo de vacaciones del año 2026
    Entonces la respuesta tiene código 200
    Y el campo `empleado_id` es 20
    Y el campo `anio` es 2026
    Y el campo `dias_usados` es 0
    Y el campo `dias_disponibles` es 12
    Y el campo `solicitudes` es una lista vacía
    Cuando registra una solicitud de vacaciones del "2026-07-06" al "2026-07-10"
    Y vuelve a consultar su saldo de vacaciones del año 2026
    Entonces el campo `dias_usados` es 5
    Y el campo `dias_disponibles` es 7
    Y el campo `solicitudes` contiene una solicitud con fecha_inicio "2026-07-06", fecha_fin "2026-07-10" y dias_habiles 5

  Escenario: El saldo de 2027 es independiente de los días usados en 2026
    Dado que el empleado 20 ya tiene registrada una solicitud de 5 días hábiles en 2026 del "2026-07-06" al "2026-07-10"
    Cuando consulta su saldo de vacaciones del año 2027
    Entonces la respuesta tiene código 200
    Y el campo `empleado_id` es 20
    Y el campo `anio` es 2027
    Y el campo `dias_usados` es 0
    Y el campo `dias_disponibles` es 12
    Y el campo `solicitudes` es una lista vacía

  Escenario: El botón de solicitar vacaciones solo aparece para empleados activos
    Dado que el directorio muestra al empleado activo 20 y al empleado dado de baja 23
    Cuando se visualiza el directorio de empleados
    Entonces el botón con data-testid "vacaciones-abrir-20" está visible
    Y no existe ningún elemento con data-testid "vacaciones-abrir-23"

  Escenario: Camino feliz e2e - registrar una solicitud desde el formulario
    Dado que abre el formulario con data-testid "vacaciones-abrir-20"
    Y el campo con data-testid "vacaciones-disponibles" muestra 12 para 2026
    Cuando completa el campo "vacaciones-fecha-inicio" con "2026-07-06"
    Y completa el campo "vacaciones-fecha-fin" con "2026-07-10"
    Y hace clic en el botón con data-testid "vacaciones-enviar"
    Entonces el campo con data-testid "vacaciones-mensaje" muestra "Solicitud registrada: 5 días hábiles. Te quedan 7 días hábiles en 2026."
    Y el campo con data-testid "vacaciones-disponibles" muestra 7

  Escenario: Error e2e - el formulario muestra el detail exacto de la API
    Dado que abre el formulario con data-testid "vacaciones-abrir-20"
    Cuando completa el campo "vacaciones-fecha-inicio" con "2026-07-10"
    Y completa el campo "vacaciones-fecha-fin" con "2026-07-06"
    Y hace clic en el botón con data-testid "vacaciones-enviar"
    Entonces el campo con data-testid "vacaciones-mensaje" muestra "La fecha de fin no puede ser anterior a la fecha de inicio"
