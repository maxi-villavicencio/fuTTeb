/**
 * Cartel amarillo con las advertencias que devuelve la API (ej. datos
 * insuficientes). No se muestra nada si no hay advertencias.
 */
export default function Advertencia({ advertencias }) {
  if (!advertencias || advertencias.length === 0) return null;

  return (
    <div className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800">
      <p className="font-semibold">⚠ Datos insuficientes</p>
      <ul className="mt-1 list-inside list-disc space-y-0.5">
        {advertencias.map((a, i) => (
          <li key={i}>{a}</li>
        ))}
      </ul>
    </div>
  );
}
