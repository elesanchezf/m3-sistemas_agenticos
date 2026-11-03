import { useEffect, useState } from "react";
import FormularioEmpleado from "./components/FormularioEmpleado";
import DirectorioEmpleados from "./components/DirectorioEmpleados";
import { obtenerEmpleados } from "./services/api";

export default function App() {
  const [empleados, setEmpleados] = useState([]);

  function cargarEmpleados() {
    obtenerEmpleados().then(setEmpleados);
  }

  useEffect(() => {
    cargarEmpleados();
  }, []);

  return (
    <main>
      <h1>Gestión de empleados</h1>
      <FormularioEmpleado onEmpleadoCreado={cargarEmpleados} />
      <DirectorioEmpleados empleados={empleados} />
    </main>
  );
}
