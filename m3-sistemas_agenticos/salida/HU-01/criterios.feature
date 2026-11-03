# language: es
Característica: Registrar empleado
  Como persona del área de Recursos Humanos
  quiero registrar a un empleado con su nombre, correo corporativo, puesto, departamento y fecha de ingreso
  para darlo de alta en la empresa

  Escenario: Registrar un empleado con datos válidos
    Dado que no existe ningún empleado con correo "ana.lopez@empresa.com"
    Y el último número de empleado asignado es "EMP-0007"
    Cuando registro un empleado con los siguientes datos:
      | campo          | valor                   |
      | nombre         | Ana López               |
      | correo         | Ana.Lopez@Empresa.com   |
      | puesto         | Analista de Datos       |
      | departamento   | Tecnología              |
      | fecha_ingreso  | 2024-01-15              |
    Entonces el sistema responde con código 201
    Y el empleado queda registrado con estado "activo"
    Y el número de empleado asignado es "EMP-0008"
    Y el correo se guarda como "ana.lopez@empresa.com"
    Y la pantalla muestra el mensaje de confirmación "Empleado EMP-0008 registrado con éxito"

  Escenario: Intentar registrar un empleado con un correo ya registrado
    Dado que ya existe un empleado registrado con correo "ana.lopez@empresa.com"
    Cuando registro un empleado con correo "ANA.LOPEZ@EMPRESA.COM"
    Entonces el sistema responde con código 409
    Y la pantalla muestra el mensaje "El correo ya está registrado"
    Y no se crea ningún empleado nuevo

  Escenario: Intentar registrar un empleado con un correo no corporativo
    Dado que no existe ningún empleado registrado con correo "carlos.ruiz@gmail.com"
    Cuando registro un empleado con los siguientes datos:
      | campo          | valor                   |
      | nombre         | Carlos Ruiz             |
      | correo         | carlos.ruiz@gmail.com   |
      | puesto         | Vendedor                |
      | departamento   | Ventas                  |
      | fecha_ingreso  | 2024-03-01              |
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "Usa el correo corporativo @empresa.com"
    Y no se crea ningún empleado nuevo

  Esquema del escenario: Intentar registrar un empleado con un dato obligatorio inválido
    Dado que no existe ningún empleado registrado con correo "luis.diaz@empresa.com"
    Cuando registro un empleado con los siguientes datos:
      | campo          | valor               |
      | nombre         | <nombre>            |
      | correo         | <correo>            |
      | puesto         | <puesto>            |
      | departamento   | <departamento>      |
      | fecha_ingreso  | <fecha_ingreso>     |
    Entonces el sistema responde con código 422
    Y la pantalla muestra que el campo "<campo_a_corregir>" debe corregirse
    Y no se crea ningún empleado nuevo

    Ejemplos:
      | nombre | correo                   | puesto             | departamento | fecha_ingreso | campo_a_corregir |
      | A      | luis.diaz@empresa.com    | Soporte Técnico    | Operaciones  | 2024-02-10    | nombre           |
      |        | luis.diaz@empresa.com    | Soporte Técnico    | Operaciones  | 2024-02-10    | nombre           |
      | Luis Díaz | luis.diaz@empresa.com | S                  | Operaciones  | 2024-02-10    | puesto           |
      | Luis Díaz | luis.diaz@empresa.com |                    | Operaciones  | 2024-02-10    | puesto           |
      | Luis Díaz | luis.diaz@empresa.com | Soporte Técnico    | Marketing    | 2024-02-10    | departamento     |

  Escenario: Intentar registrar un empleado con fecha de ingreso futura
    Dado que la fecha actual del sistema es "2024-06-01"
    Cuando registro un empleado con los siguientes datos:
      | campo          | valor                   |
      | nombre         | Marta Gómez             |
      | correo         | marta.gomez@empresa.com |
      | puesto         | Contadora               |
      | departamento   | Finanzas                |
      | fecha_ingreso  | 2024-06-02              |
    Entonces el sistema responde con código 422
    Y la pantalla muestra el mensaje "La fecha de ingreso no puede ser futura"
    Y no se crea ningún empleado nuevo

# Preguntas abiertas
# - No se especifica el formato exacto de fecha que recibe el formulario/API (se asumió YYYY-MM-DD).
# - No se indica cuál es el primer número de empleado si la base está vacía (se asumió que inicia en EMP-0001).
# - No se especifica el texto exacto que debe mostrar la pantalla para cada campo inválido bajo la regla 3
#   (se usó un texto genérico "debe corregirse"); falta confirmar la redacción exacta de los mensajes por campo
#   (nombre, puesto, departamento, fecha_ingreso).
