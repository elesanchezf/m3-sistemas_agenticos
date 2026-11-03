export async function obtenerDepartamentos() {
  const respuesta = await fetch("/api/departamentos");
  return respuesta.json();
}

export async function obtenerEmpleados(filtros = {}) {
  const parametros = new URLSearchParams();
  if (filtros.buscar) parametros.set("buscar", filtros.buscar);
  if (filtros.departamento) parametros.set("departamento", filtros.departamento);
  const consulta = parametros.toString();
  const respuesta = await fetch(`/api/empleados${consulta ? `?${consulta}` : ""}`);
  return respuesta.json();
}

export async function crearEmpleado(datos) {
  const respuesta = await fetch("/api/empleados", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  });
  const cuerpo = await respuesta.json();
  if (!respuesta.ok) {
    const error = new Error(cuerpo.detail || "Ocurrió un error inesperado");
    error.campo = cuerpo.campo || null;
    throw error;
  }
  return cuerpo;
}
