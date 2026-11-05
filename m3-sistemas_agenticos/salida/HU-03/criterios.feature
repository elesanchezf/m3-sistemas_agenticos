# language: es
Característica: Editar y dar de baja a un empleado
  Como persona del área de Recursos Humanos
  quiero cambiar el puesto y el departamento de un empleado, y poder darlo de baja
  para mantener el directorio al día sin perder el historial

  Escenario: Editar puesto y departamento de un empleado activo
    Dado que existe un empleado activo con numero_empleado "EMP-0007", correo "ana.lopez@empresa.com", puesto "Analista" y departamento "Ventas"
    Cuando edito el puesto a "Analista Senior" y el departamento a "Finanzas"
    Entonces el sistema responde 200
    Y el empleado "EMP-0007" tiene puesto "Analista Senior" y departamento "Finanzas"
    Y el numero_empleado del empleado sigue siendo "EMP-0007"
    Y el correo del empleado sigue siendo "ana.lopez@empresa.com"

  Escenario: No se puede editar a un empleado dado de baja
    Dado que existe un empleado con numero_empleado "EMP-0008" y estado "baja"
    Cuando intento editar su puesto a "Gerente"
    Entonces el sistema responde 409 con el mensaje "No se puede editar a un empleado dado de baja"
    Y el puesto del empleado "EMP-0008" no cambia

  Escenario: Error al editar con puesto inválido
    Dado que existe un empleado activo con numero_empleado "EMP-0009" y puesto "Analista"
    Cuando edito el puesto a "A"
    Entonces el sistema responde 422
    Y la pantalla indica que el campo "puesto" debe corregirse
    Y el puesto del empleado "EMP-0009" no cambia

  Escenario: Error al editar con departamento inválido
    Dado que existe un empleado activo con numero_empleado "EMP-0010" y departamento "Ventas"
    Cuando edito el departamento a "Marketing"
    Entonces el sistema responde 422
    Y la pantalla indica que el campo "departamento" debe corregirse
    Y el departamento del empleado "EMP-0010" no cambia

  Escenario: Dar de baja a un empleado activo
    Dado que existe un empleado activo con numero_empleado "EMP-0011" y fecha_ingreso "2022-05-01"
    Cuando doy de baja al empleado "EMP-0011" con fecha_baja "2024-03-15"
    Entonces el sistema responde 200
    Y el estado del empleado "EMP-0011" es "baja"
    Y la fecha_baja del empleado "EMP-0011" es "2024-03-15"
    Y el empleado "EMP-0011" sigue apareciendo en el directorio

  Escenario: Error al dar de baja con fecha_baja anterior a la fecha de ingreso
    Dado que existe un empleado activo con numero_empleado "EMP-0012" y fecha_ingreso "2023-06-01"
    Cuando doy de baja al empleado "EMP-0012" con fecha_baja "2023-01-01"
    Entonces el sistema responde 422
    Y la pantalla indica que el campo "fecha_baja" debe corregirse
    Y el estado del empleado "EMP-0012" sigue siendo "activo"

# Preguntas abiertas
# - ¿Qué debe hacer el sistema si en una edición se envían también numero_empleado o correo con un valor distinto al actual?
#   (por ejemplo: ignorar esos campos silenciosamente, responder 422, o bloquearlos solo en la pantalla).
#   No se encontró una regla de negocio explícita para este caso.
