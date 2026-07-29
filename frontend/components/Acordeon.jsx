"use client";

import { useState } from "react";

/**
 * Acordeón reutilizable para cada mercado.
 * Aparece COLAPSADO mostrando título + dato principal; al hacer clic se despliega.
 *
 * props:
 *   titulo:    nombre del mercado (ej. "Goles").
 *   resumen:   dato principal visible en estado colapsado.
 *   confiable: si es false, muestra un aviso visible en la cabecera.
 *   children:  detalle completo que se muestra al desplegar.
 */
export default function Acordeon({ titulo, resumen, confiable = true, children }) {
  const [abierto, setAbierto] = useState(false);

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={() => setAbierto((o) => !o)}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors hover:bg-slate-50"
      >
        <div className="flex items-center gap-2">
          <span className="text-base font-semibold text-slate-800">{titulo}</span>
          {!confiable && (
            <span className="rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
              ⚠ poco confiable
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-emerald-700">{resumen}</span>
          <svg
            className={`h-4 w-4 shrink-0 text-slate-400 transition-transform ${
              abierto ? "rotate-180" : ""
            }`}
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M5.23 7.21a.75.75 0 011.06.02L10 11.06l3.71-3.83a.75.75 0 111.08 1.04l-4.25 4.4a.75.75 0 01-1.08 0l-4.25-4.4a.75.75 0 01.02-1.06z"
              clipRule="evenodd"
            />
          </svg>
        </div>
      </button>

      {abierto && (
        <div className="space-y-4 border-t border-slate-100 px-4 py-4">{children}</div>
      )}
    </div>
  );
}
