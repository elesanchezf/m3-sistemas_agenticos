# Notas de la sesión 1

## Permisos
La lectura de HU-01 funcionó. Leer secretos_demo.txt produjo PermissionError porque está fuera de las carpetas permitidas. La herramienta bloqueó el acceso.

## Validación y vueltas
El analista necesitó dos intentos y terminó con cinco escenarios. La salida muestra que hubo una corrección solicitada por el validador, pero no indica qué problema concreto encontró; no puedo afirmarlo sin revisar más evidencia.

Cada intento del analista realizó tres llamadas al modelo: lectura, escritura y respuesta final. En total fueron seis llamadas.

El diseñador necesitó un intento con tres llamadas al modelo: lectura, guardado y respuesta final. Generó diez casos: cinco API y cinco E2E.

## Qué mejoraría
El analista dejó dudas sobre la fecha de referencia y los mensajes de validación. Mejoraría sus instrucciones para registrar la información faltante sin convertir mensajes supuestos en criterios confirmados.