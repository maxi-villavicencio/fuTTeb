import Stat from "../Stat";
import ProbBarra from "../ProbBarra";
import { num } from "../../lib/helpers";

/** Un bloque de líneas más probables (total / local / visitante). */
function BloqueLineas({ titulo, mercados }) {
  return (
    <div className="rounded-md border border-slate-200 p-3">
      <div className="mb-2 text-sm font-semibold text-slate-700">{titulo}</div>
      <div className="space-y-1.5">
        {mercados.map((m, i) => (
          <ProbBarra key={i} etiqueta={`${m.linea} (${m.descripcion})`} prob={m.prob} />
        ))}
      </div>
    </div>
  );
}

/** Detalle del mercado Tarjetas (total del partido y por equipo). */
export default function TarjetasDetalle({ valores }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-2">
        <Stat etiqueta="Esp. local" valor={num(valores.tarjetas_esperadas_local)} />
        <Stat etiqueta="Esp. visitante" valor={num(valores.tarjetas_esperadas_visitante)} />
        <Stat etiqueta="Esp. total" valor={num(valores.tarjetas_esperadas_total)} resaltado />
      </div>

      <BloqueLineas titulo="TOTAL del partido" mercados={valores.mercados_total} />
      <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
        <BloqueLineas
          titulo={`${valores.nombre_local} (local)`}
          mercados={valores.mercados_local}
        />
        <BloqueLineas
          titulo={`${valores.nombre_visitante} (visitante)`}
          mercados={valores.mercados_visitante}
        />
      </div>
    </div>
  );
}
