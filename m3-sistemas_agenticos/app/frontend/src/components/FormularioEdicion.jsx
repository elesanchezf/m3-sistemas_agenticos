import { useState } from "react";
import { editarEmpleado } from "../services/api";

export default function FormularioEdicion({
  empleado,
  departamentos,
  onCancelar,
  onEmpleadoActualizado,
}) {
  const [puesto, setPuesto] = useState(empleado.puesto);
  const [departamento, setDepartamento] = useState(empleado.departamento);
  const [campoInvalido, setCampoInvalido] = useState(null);
  const [mensajeExito, setMensajeExito] = useState("");
  const [mensajeError, setMensajeError] = useState("");

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setMensajeExito("");
    setMensajeError("");
    setCampoInvalido(null);

    try {
      const actualizado = await editarEmpleado(empleado.id, { puesto, departamento });
      setMensajeExito(`Empleado ${actualizado.numero_empleado} actualizado`);
      onEmpleadoActualizado?.(actualizado);
    } catch (error) {
      setMensajeError(error.message);
      setCampoInvalido(error.campo || null);
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <h2>Editar empleado {empleado.numero_empleado}</h2>

      <div>
        <label htmlFor="empleado-puesto">Puesto</label>
        <input
          id="empleado-puesto"
          data-testid="empleado-puesto"
          type="text"
          value={puesto}
          onChange={(e) => setPuesto(e.target.value)}
          aria-invalid={campoInvalido === "puesto"}
          required
        />
      </div>

      <div>
        <label htmlFor="empleado-departamento">Departamento</label>
        <select
          id="empleado-departamento"
          data-testid="empleado-departamento"
          value={departamento}
          onChange={(e) => setDepartamento(e.target.value)}
          aria-invalid={campoInvalido === "departamento"}
          required
        >
          {departamentos.map((d) => (
            <option key={d} value={d}>
              {d}
            </option>
          ))}
        </select>
      </div>

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  );
}
