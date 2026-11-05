import { useEffect, useState } from "react";
import { crearVacaciones, obtenerSaldoVacaciones } from "../services/api";

export default function FormularioVacaciones({ empleado, onCancelar }) {
  const [fechaInicio, setFechaInicio] = useState("");
  const [fechaFin, setFechaFin] = useState("");
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [diasDisponibles, setDiasDisponibles] = useState(null);
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    obtenerSaldoVacaciones(empleado.id, anio).then((saldo) => {
      setDiasDisponibles(saldo.dias_disponibles);
    });
  }, [empleado.id, anio]);

  function manejarCambioFechaInicio(valor) {
    setFechaInicio(valor);
    if (valor.length === 10) {
      setAnio(Number(valor.slice(0, 4)));
    }
  }

  async function manejarEnviar(evento) {
    evento.preventDefault();
    setMensaje("");

    try {
      const resultado = await crearVacaciones(empleado.id, {
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin,
      });
      const anioSolicitud = Number(fechaInicio.slice(0, 4));
      setMensaje(
        `Solicitud registrada: ${resultado.dias_habiles} días hábiles. ` +
          `Te quedan ${resultado.dias_restantes} días hábiles en ${anioSolicitud}.`
      );
      setDiasDisponibles(resultado.dias_restantes);
    } catch (error) {
      setMensaje(error.message);
    }
  }

  return (
    <form onSubmit={manejarEnviar}>
      <h2>Vacaciones de {empleado.numero_empleado}</h2>

      <p>
        Días disponibles en {anio}:{" "}
        <span data-testid="vacaciones-disponibles">{diasDisponibles}</span>
      </p>

      <div>
        <label htmlFor="vacaciones-fecha-inicio">Fecha de inicio</label>
        <input
          id="vacaciones-fecha-inicio"
          data-testid="vacaciones-fecha-inicio"
          type="date"
          value={fechaInicio}
          onChange={(e) => manejarCambioFechaInicio(e.target.value)}
          required
        />
      </div>

      <div>
        <label htmlFor="vacaciones-fecha-fin">Fecha de fin</label>
        <input
          id="vacaciones-fecha-fin"
          data-testid="vacaciones-fecha-fin"
          type="date"
          value={fechaFin}
          onChange={(e) => setFechaFin(e.target.value)}
          required
        />
      </div>

      <button type="submit" data-testid="vacaciones-enviar">
        Enviar solicitud
      </button>
      <button type="button" onClick={onCancelar}>
        Cancelar
      </button>

      {mensaje && <p data-testid="vacaciones-mensaje">{mensaje}</p>}
    </form>
  );
}
