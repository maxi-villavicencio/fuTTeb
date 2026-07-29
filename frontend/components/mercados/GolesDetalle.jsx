import Stat from "../Stat";
import ProbBarra from "../ProbBarra";
import { pct, num } from "../../lib/helpers";

/** Detalle del mercado Goles (con sus sub-mercados). */
export default function GolesDetalle({ valores }) {
  const ou = valores.over_under;
  const bt = valores.btts;

  return (
    <div className="space-y-4">
      {/* Goles esperados */}
      <div className="grid grid-cols-3 gap-2">
        <Stat etiqueta="Esp. local" valor={num(valores.goles_esperados_local)} />
        <Stat etiqueta="Esp. visitante" valor={num(valores.goles_esperados_visitante)} />
        <Stat etiqueta="Esp. total" valor={num(valores.goles_esperados_total)} resaltado />
      </div>

      {/* Over/Under y BTTS interno */}
      <div className="grid grid-cols-2 gap-2">
        <div className="rounded-md border border-slate-200 p-3">
          <div className="mb-2 text-sm font-semibold text-slate-700">
            Over/Under {ou.linea}
          </div>
          <ProbBarra etiqueta={`Over ${ou.linea}`} prob={ou.prob_over} />
          <ProbBarra etiqueta={`Under ${ou.linea}`} prob={ou.prob_under} />
        </div>
        <div className="rounded-md border border-slate-200 p-3">
          <div className="mb-2 text-sm font-semibold text-slate-700">Ambos marcan (BTTS)</div>
          <ProbBarra etiqueta="Sí" prob={bt.prob_si} />
          <ProbBarra etiqueta="No" prob={bt.prob_no} />
        </div>
      </div>

      {/* Top 5 marcadores */}
      <div>
        <div className="mb-2 text-sm font-semibold text-slate-700">
          Marcadores más probables
        </div>
        <div className="space-y-1.5">
          {valores.marcadores_top.map((m, i) => (
            <ProbBarra key={i} etiqueta={m.texto} prob={m.prob} decimales={1} />
          ))}
        </div>
      </div>

      {/* Top 5 rangos de goles */}
      <div>
        <div className="mb-2 text-sm font-semibold text-slate-700">
          Rangos de goles más probables (ancho {valores.ancho_rango})
        </div>
        <div className="space-y-1.5">
          {valores.rangos_top.map((r, i) => (
            <ProbBarra key={i} etiqueta={`${r.rango} goles`} prob={r.prob} decimales={1} />
          ))}
        </div>
      </div>
    </div>
  );
}
