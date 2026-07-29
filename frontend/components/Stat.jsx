/** Pequeña tarjeta etiqueta/valor para mostrar números destacados. */
export default function Stat({ etiqueta, valor, resaltado = false }) {
  return (
    <div
      className={`rounded-md border p-3 text-center ${
        resaltado ? "border-emerald-200 bg-emerald-50" : "border-slate-200 bg-slate-50"
      }`}
    >
      <div className="text-xs uppercase tracking-wide text-slate-500">{etiqueta}</div>
      <div className="mt-1 text-lg font-semibold text-slate-800">{valor}</div>
    </div>
  );
}
