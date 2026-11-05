import { useState } from "react";
import { darDeBajaEmpleado } from "../services/api";

export default function ModalBaja({ empleado, onCancelar, onEmpleadoActualizado }) {
  const [fechaBaja, setFechaBaja] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");
  const [mensajeError, setMensajeError] = useState("");

  async function manejarConfirmar(evento) {
    evento.preventDefault();
    setMensajeExito("");
    setMensajeError("");

    try {
      const actualizado = await darDeBajaEmpleado(empleado.id, fechaBaja);
      setMensajeExito(`Empleado ${actualizado.numero_empleado} dado de baja`);
      onEmpleadoActualizado?.(actualizado);
    } catch (error) {
      setMensajeError(error.message);
    }
  }

  return (
    <form onSubmit={manejarConfirmar}>
      <h2>Dar de baja a {empleado.numero_empleado}</h2>

      <div>
        <label htmlFor="empleado-fecha-baja">Fecha de baja</label>
        <input
          id="empleado-fecha-baja"
          data-testid="empleado-fecha-baja"
          type="date"
          value={fechaBaja}
          onChange={(e) => setFechaBaja(e.target.value)}
          required
        />
      </div>

      <button type="submit" data-testid="confirmar-baja">
        Confirmar baja
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  );
}
