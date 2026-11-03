import { useEffect, useState } from "react";
import { crearEmpleado, obtenerDepartamentos } from "../services/api";

const VALORES_INICIALES = {
  nombre: "",
  correo: "",
  puesto: "",
  departamento: "",
  fecha_ingreso: "",
};

export default function FormularioEmpleado({ onEmpleadoCreado }) {
  const [valores, setValores] = useState(VALORES_INICIALES);
  const [departamentos, setDepartamentos] = useState([]);
  const [campoInvalido, setCampoInvalido] = useState(null);
  const [mensajeExito, setMensajeExito] = useState("");
  const [mensajeError, setMensajeError] = useState("");

  useEffect(() => {
    obtenerDepartamentos().then(setDepartamentos);
  }, []);

  function actualizarCampo(campo, valor) {
    setValores((anteriores) => ({ ...anteriores, [campo]: valor }));
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setMensajeExito("");
    setMensajeError("");
    setCampoInvalido(null);

    try {
      const empleado = await crearEmpleado(valores);
      setMensajeExito(
        `Empleado registrado con el número ${empleado.numero_empleado}`,
      );
      setValores(VALORES_INICIALES);
      onEmpleadoCreado?.(empleado);
    } catch (error) {
      setMensajeError(error.message);
      setCampoInvalido(error.campo || null);
    }
  }

  return (
    <form onSubmit={manejarEnvio}>
      <div>
        <label htmlFor="empleado-nombre">Nombre</label>
        <input
          id="empleado-nombre"
          data-testid="empleado-nombre"
          type="text"
          value={valores.nombre}
          onChange={(e) => actualizarCampo("nombre", e.target.value)}
          aria-invalid={campoInvalido === "nombre"}
          required
        />
      </div>

      <div>
        <label htmlFor="empleado-correo">Correo</label>
        <input
          id="empleado-correo"
          data-testid="empleado-correo"
          type="email"
          value={valores.correo}
          onChange={(e) => actualizarCampo("correo", e.target.value)}
          aria-invalid={campoInvalido === "correo"}
          required
        />
      </div>

      <div>
        <label htmlFor="empleado-puesto">Puesto</label>
        <input
          id="empleado-puesto"
          data-testid="empleado-puesto"
          type="text"
          value={valores.puesto}
          onChange={(e) => actualizarCampo("puesto", e.target.value)}
          aria-invalid={campoInvalido === "puesto"}
          required
        />
      </div>

      <div>
        <label htmlFor="empleado-departamento">Departamento</label>
        <select
          id="empleado-departamento"
          data-testid="empleado-departamento"
          value={valores.departamento}
          onChange={(e) => actualizarCampo("departamento", e.target.value)}
          aria-invalid={campoInvalido === "departamento"}
          required
        >
          <option value="">Selecciona un departamento</option>
          {departamentos.map((departamento) => (
            <option key={departamento} value={departamento}>
              {departamento}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="empleado-fecha-ingreso">Fecha de ingreso</label>
        <input
          id="empleado-fecha-ingreso"
          data-testid="empleado-fecha-ingreso"
          type="date"
          value={valores.fecha_ingreso}
          onChange={(e) => actualizarCampo("fecha_ingreso", e.target.value)}
          aria-invalid={campoInvalido === "fecha_ingreso"}
          required
        />
      </div>

      <button type="submit" data-testid="empleado-guardar">
        Guardar
      </button>

      {mensajeExito && <p data-testid="mensaje-exito">{mensajeExito}</p>}
      {mensajeError && <p data-testid="mensaje-error">{mensajeError}</p>}
    </form>
  );
}
