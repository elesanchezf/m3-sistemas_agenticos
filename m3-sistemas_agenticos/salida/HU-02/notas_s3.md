# Lab 3 · HU-02 Consultar el directorio

La bitácora cerró con app LISTA, construcción 1, despliegue OK y un costo reportado de 2.36 USD. Rechacé el primer plan para exigir que la búsqueda de ANA LÓPEZ encontrara a Ana López. El plan revisado incorporó la conversión Unicode y conservó el alta de HU-01. Tras mi aprobación, despliegue y automatización trabajaron en paralelo sobre la aplicación verificada.

## Estado de Docker observado

```text
NAME             IMAGE          COMMAND                  SERVICE    CREATED          STATUS                    PORTS
app-backend-1    app-backend    "uvicorn main:app --…"   backend    12 minutes ago   Up 12 minutes (healthy)   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp
app-frontend-1   app-frontend   "/docker-entrypoint.…"   frontend   12 minutes ago   Up 12 minutes             0.0.0.0:8080->80/tcp, [::]:8080->80/tcp
```

## Pruebas ejecutadas contra los contenedores

| Comando | Resultado |
|---|---|
| pytest tests/api -q | 6 passed in 8.13s |
| pytest tests/e2e -q --headed | 6 passed in 7.40s |

La captura del directorio muestra el buscador, el filtro y la fila EMP-0001 registrada durante el Lab 2. Las pruebas de HU-02 amplían la revisión manual de HU-01 con cobertura del directorio. Las dos ejecuciones suman 12 pruebas aprobadas. La ejecución conjunta de pytest tests -q terminó con «12 passed in 9.65s».

## Auditoría

La auditoría registró en ts 1793744814.10 un intento de Write del desarrollador sobre app/test_payload.json. Su rol permite backend/* y frontend/*. El destino está en la raíz de app, fuera de ambos patrones, por lo que confinar_escritura devuelve deny para esa solicitud. El archivo de auditoría registra el intento; la decisión se deduce al contrastarlo con la regla del hook. La marca de tiempo corresponde al historial de la fábrica y no se atribuye a la corrida de HU-02.
