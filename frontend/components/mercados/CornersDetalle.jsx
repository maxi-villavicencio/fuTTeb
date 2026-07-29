import Stat from "../Stat";
import { num } from "../../lib/helpers";

/** Detalle del mercado Córners. */
export default function CornersDetalle({ valores }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-2">
        <Stat etiqueta="Esp. local" valor={num(valores.esperados_local)} />
        <Stat etiqueta="Esp. visitante" valor={num(valores.esperados_visitante)} />
        <Stat etiqueta="Esp. total" valor={num(valores.corners_totales)} resaltado />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <Stat etiqueta={`Línea`} valor={valores.linea} />
        <Stat etiqueta="Índice" valor={`${num(valores.indice, 0)}/100`} resaltado />
      </div>
    </div>
  );
}
