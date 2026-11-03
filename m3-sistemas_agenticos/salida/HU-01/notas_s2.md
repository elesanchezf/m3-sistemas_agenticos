# Lab 2 · HU-01 Registrar empleado

## Revisión y aprobación del plan

Rechacé agregar una consulta por identificador y exigir una frase literal para el alta. Mi comentario fue:

> Rechazo los dos cambios propuestos. HU-01 exige que la confirmación incluya el numero_empleado devuelto por el POST, sin fijar una frase literal. Para comprobar el alta usa la respuesta 201 y, si necesitas verificar persistencia, el GET /api/empleados existente. Conserva la aplicación si ya cumple. Señala las discrepancias de CP-01 y CP-02 con la historia para corregirlas en el analista o el diseñador de pruebas.

El segundo plan incorporó ambas observaciones y lo aprobé. La bitácora registró una construcción, «Verificación: OK» y «app LISTA». Costo reportado para esa corrida: **0.58 USD**.

## Resultados de la revisión manual

| Caso | Resultado observado | Medio |
|---|---|---|
| Alta válida | Confirmación con EMP-0001. El directorio mostró el correo en minúsculas y estado activo. | Formulario y consulta GET |
| Correo duplicado con variación de mayúsculas | «El correo ya está registrado». Se mantuvo una fila. | Formulario |
| Dominio no corporativo | «Usa el correo corporativo @empresa.com». | Formulario |
| Nombre de un carácter | «El campo nombre debe tener de 2 a 80 caracteres». | Formulario |
| Nombre vacío | El navegador enfocó Nombre y mostró «Completa este campo». | Validación del navegador |
| Puesto de un carácter | «El campo puesto debe tener de 2 a 60 caracteres». | Formulario |
| Puesto vacío | El navegador enfocó Puesto y mostró «Completa este campo». | Validación del navegador |
| Departamento fuera del catálogo | Al enviar Marketing, la API devolvió 422, campo departamento y «El campo departamento debe ser uno de: Tecnología, Ventas, Finanzas, Recursos Humanos, Operaciones». | POST desde Swagger |
| Fecha de ingreso futura | El 3 de noviembre se intentó el alta con fecha 4 de noviembre de 2026. Apareció «La fecha de ingreso no puede ser futura». | Formulario |

El aviso rojo del intento con puesto corto persistió mientras el navegador señalaba un campo obligatorio vacío. La prueba de departamento se hizo directamente contra la API. Solo en ese caso se capturó el código HTTP del POST.

## Patrones observados

El flujo encadenó criterios, casos, plan, construcción y verificación. La aprobación humana permitió devolver el primer plan al desarrollador con un comentario concreto. Para evaluar la construcción, el verificador consultó la salud del backend y compiló el frontend. Una corrida anterior se interrumpió al intentar ejecutar npm en Windows. Tras ajustar el verificador de la fábrica para invocar npm.cmd en Windows, la comprobación independiente pasó y la corrida posterior llegó a «app LISTA».
