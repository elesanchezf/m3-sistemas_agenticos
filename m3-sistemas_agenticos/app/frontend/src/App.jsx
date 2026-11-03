import { useEffect, useState } from "react";
import FormularioEmpleado from "./components/FormularioEmpleado";
import DirectorioEmpleados from "./components/DirectorioEmpleados";
import { obtenerEmpleados } from "./services/api";

export default function App() {
  const [empleados, setEmpleados] = useState([]);
  const [buscar, setBuscar] = useState("");
  const [departamento, setDepartamento] = useState("");

  function cargarEmpleados() {
    obtenerEmpleados({ buscar, departamento }).then(setEmpleados);
  }

  useEffect(() => {
    cargarEmpleados();
  }, [buscar, departamento]);

  return (
    <main>
      <h1>Gestión de empleados</h1>
      <FormularioEmpleado onEmpleadoCreado={cargarEmpleados} />
      <DirectorioEmpleados
        empleados={empleados}
        buscar={buscar}
        onBuscarCambia={setBuscar}
        departamento={departamento}
        onDepartamentoCambia={setDepartamento}
      />
    </main>
  );
}
