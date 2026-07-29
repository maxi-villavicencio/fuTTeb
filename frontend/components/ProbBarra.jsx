import { pct } from "../lib/helpers";

/**
 * Fila con etiqueta + barra proporcional + porcentaje.
 * `prob` es una probabilidad 0..1 (ya calculada por la API).
 */
export default function ProbBarra({ etiqueta, prob, decimales = 0 }) {
  const ancho = Math.max(0, Math.min(100, Number(prob) * 100));

  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="w-28 shrink-0 truncate text-slate-600">{etiqueta}</span>
      <div className="h-2 flex-1 overflow-hidden rounded bg-slate-200">
        <div className="h-2 rounded bg-emerald-500" style={{ width: `${ancho}%` }} />
      </div>
      <span className="w-14 shrink-0 text-right font-medium tabular-nums text-slate-700">
        {pct(prob, decimales)}
      </span>
    </div>
  );
}
