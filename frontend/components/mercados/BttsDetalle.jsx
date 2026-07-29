import Stat from "../Stat";
import ProbBarra from "../ProbBarra";
import { num } from "../../lib/helpers";

/** Detalle del mercado BTTS (ambos equipos marcan). */
export default function BttsDetalle({ valores }) {
  return (
    <div className="space-y-4">
      <div className="rounded-md border border-slate-200 p-3">
        <div className="mb-2 text-sm font-semibold text-slate-700">
          ¿Ambos equipos marcan?
        </div>
        <ProbBarra etiqueta="Sí" prob={valores.prob_si} />
        <ProbBarra etiqueta="No" prob={valores.prob_no} />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <ProbBarra etiqueta="Marca el local" prob={valores.prob_local_marca} />
        <ProbBarra etiqueta="Marca el visitante" prob={valores.prob_visitante_marca} />
      </div>

      <Stat etiqueta="Índice BTTS" valor={`${num(valores.indice, 0)}/100`} resaltado />
    </div>
  );
}
