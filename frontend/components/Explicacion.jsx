/** Muestra la explicación en español que devuelve la API (respeta saltos de línea). */
export default function Explicacion({ texto }) {
  if (!texto) return null;
  return (
    <div className="rounded-md bg-slate-50 p-3">
      <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">
        Explicación
      </div>
      <p className="whitespace-pre-line text-sm text-slate-600">{texto}</p>
    </div>
  );
}
