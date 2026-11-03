# language: es

Característica: Consultar el directorio de empleados
  Como persona del área de Recursos Humanos
  quiero ver el directorio de empleados, buscarlos por nombre o correo y filtrarlos por departamento
  para encontrar rápido a una persona

  Escenario: Camino feliz - Ver el directorio de empleados
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | puesto          | departamento      | estado |
      | EMP-0001        | Ana López     | Analista        | Tecnología        | activo |
      | EMP-0002        | Juan Pérez    | Vendedor        | Ventas            | activo |
    Cuando abro el directorio de empleados
    Entonces veo una lista con 2 empleados
    Y cada fila muestra número de empleado, nombre, puesto, departamento y estado

  Escenario: Buscar un empleado por nombre sin distinguir mayúsculas de minúsculas
    Dado que existe un empleado registrado con número "EMP-0001", nombre "Ana López" y correo "ana.lopez@empresa.com"
    Cuando busco en el directorio el texto "ANA LÓPEZ"
    Entonces veo en los resultados al empleado "EMP-0001" con nombre "Ana López"

  Escenario: Buscar un empleado por correo sin distinguir mayúsculas de minúsculas
    Dado que existe un empleado registrado con número "EMP-0001", nombre "Ana López" y correo "ana.lopez@empresa.com"
    Cuando busco en el directorio el texto "ANA.LOPEZ@EMPRESA.COM"
    Entonces veo en los resultados al empleado "EMP-0001" con correo "ana.lopez@empresa.com"

  Escenario: Filtrar empleados por departamento
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | departamento      | estado |
      | EMP-0001        | Ana López     | Tecnología        | activo |
      | EMP-0002        | Juan Pérez    | Ventas            | activo |
      | EMP-0003        | Luis Ramírez  | Tecnología        | activo |
    Cuando filtro el directorio por el departamento "Tecnología"
    Entonces veo 2 empleados en los resultados
    Y todos los empleados mostrados tienen departamento "Tecnología"

  Escenario: Buscar un término sin resultados muestra un mensaje
    Dado que existen los siguientes empleados registrados:
      | numero_empleado | nombre        | departamento      | estado |
      | EMP-0001        | Ana López     | Tecnología        | activo |
    Cuando busco en el directorio el texto "Carlos Mendoza"
    Entonces veo el mensaje "No se encontraron resultados"
    Y la lista de resultados está vacía

  Escenario: Un empleado dado de baja sigue apareciendo en el directorio
    Dado que existe un empleado registrado con número "EMP-0004", nombre "Marta Ruiz", departamento "Finanzas" y estado "baja"
    Cuando abro el directorio de empleados
    Entonces veo en la lista al empleado "EMP-0004" con nombre "Marta Ruiz"
    Y el empleado "EMP-0004" muestra estado "baja"

# Preguntas abiertas
# - No se especifica qué ocurre si se filtra por un departamento que no es uno de los cinco válidos (Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones). ¿Se debe mostrar un error o simplemente no listar resultados?
# - No se especifica si la búsqueda por nombre/correo es exacta, por coincidencia parcial o requiere un mínimo de caracteres.
# - No se especifica si se pueden combinar búsqueda por texto y filtro por departamento al mismo tiempo.
