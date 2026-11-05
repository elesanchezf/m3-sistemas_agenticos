import { useEffect, useState } from "react";
import { obtenerDepartamentos } from "../services/api";

export default function DirectorioEmpleados({
  empleados,
  buscar,
  onBuscarCambia,
  departamento,
  onDepartamentoCambia,
  onEditar,
  onBaja,
}) {
  const [departamentos, setDepartamentos] = useState([]);

  useEffect(() => {
    obtenerDepartamentos().then(setDepartamentos);
  }, []);

  return (
    <section>
      <div>
        <label htmlFor="buscar-empleados">Buscar</label>
        <input
          id="buscar-empleados"
          data-testid="buscar-empleados"
          type="text"
          value={buscar}
          onChange={(e) => onBuscarCambia(e.target.value)}
          placeholder="Nombre o correo"
        />
      </div>

      <div>
        <label htmlFor="filtro-departamento">Departamento</label>
        <select
          id="filtro-departamento"
          data-testid="filtro-departamento"
          value={departamento}
          onChange={(e) => onDepartamentoCambia(e.target.value)}
        >
          <option value="">Todos los departamentos</option>
          {departamentos.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      {empleados.length === 0 ? (
        <p data-testid="sin-resultados">No se encontraron resultados</p>
      ) : (
        <table data-testid="tabla-empleados">
          <thead>
            <tr>
              <th>Número</th>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Puesto</th>
              <th>Departamento</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {empleados.map((empleado) => (
              <tr key={empleado.id} data-testid={`fila-empleado-${empleado.id}`}>
                <td data-testid={`numero-empleado-${empleado.id}`}>
                  {empleado.numero_empleado}
                </td>
                <td>{empleado.nombre}</td>
                <td>{empleado.correo}</td>
                <td>{empleado.puesto}</td>
                <td>{empleado.departamento}</td>
                <td data-testid={`estado-empleado-${empleado.id}`}>
                  {empleado.estado === "activo" ? "Activo" : "Baja"}
                </td>
                <td>
                  <button
                    type="button"
                    data-testid={`editar-empleado-${empleado.id}`}
                    onClick={() => onEditar?.(empleado)}
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    data-testid={`baja-empleado-${empleado.id}`}
                    onClick={() => onBaja?.(empleado)}
                  >
                    Dar de baja
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
