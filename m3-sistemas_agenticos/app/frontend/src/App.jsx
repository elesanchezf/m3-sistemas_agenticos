import { useEffect, useState } from "react";
import FormularioEmpleado from "./components/FormularioEmpleado";
import FormularioEdicion from "./components/FormularioEdicion";
import ModalBaja from "./components/ModalBaja";
import FormularioVacaciones from "./components/FormularioVacaciones";
import DirectorioEmpleados from "./components/DirectorioEmpleados";
import { obtenerDepartamentos, obtenerEmpleados } from "./services/api";

export default function App() {
  const [empleados, setEmpleados] = useState([]);
  const [buscar, setBuscar] = useState("");
  const [departamento, setDepartamento] = useState("");
  const [departamentos, setDepartamentos] = useState([]);
  const [empleadoEditando, setEmpleadoEditando] = useState(null);
  const [empleadoDandoBaja, setEmpleadoDandoBaja] = useState(null);
  const [empleadoSolicitandoVacaciones, setEmpleadoSolicitandoVacaciones] = useState(null);

  function cargarEmpleados() {
    obtenerEmpleados({ buscar, departamento }).then(setEmpleados);
  }

  useEffect(() => {
    cargarEmpleados();
  }, [buscar, departamento]);

  useEffect(() => {
    obtenerDepartamentos().then(setDepartamentos);
  }, []);

  function manejarActualizacion() {
    cargarEmpleados();
  }

  return (
    <main>
      <h1>Gestión de empleados</h1>

      {empleadoEditando ? (
        <FormularioEdicion
          empleado={empleadoEditando}
          departamentos={departamentos}
          onCancelar={() => setEmpleadoEditando(null)}
          onEmpleadoActualizado={manejarActualizacion}
        />
      ) : empleadoDandoBaja ? (
        <ModalBaja
          empleado={empleadoDandoBaja}
          onCancelar={() => setEmpleadoDandoBaja(null)}
          onEmpleadoActualizado={manejarActualizacion}
        />
      ) : empleadoSolicitandoVacaciones ? (
        <FormularioVacaciones
          empleado={empleadoSolicitandoVacaciones}
          onCancelar={() => setEmpleadoSolicitandoVacaciones(null)}
        />
      ) : (
        <FormularioEmpleado onEmpleadoCreado={cargarEmpleados} />
      )}

      <DirectorioEmpleados
        empleados={empleados}
        buscar={buscar}
        onBuscarCambia={setBuscar}
        departamento={departamento}
        onDepartamentoCambia={setDepartamento}
        onEditar={setEmpleadoEditando}
        onBaja={setEmpleadoDandoBaja}
        onVacaciones={setEmpleadoSolicitandoVacaciones}
      />
    </main>
  );
}
