"use client";

import { useEffect, useState } from "react";

import { getEquipos, analizarPartido } from "../lib/api";
import { pct, num } from "../lib/helpers";
import Acordeon from "../components/Acordeon";
import Advertencia from "../components/Advertencia";
import Explicacion from "../components/Explicacion";
import GolesDetalle from "../components/mercados/GolesDetalle";
import CornersDetalle from "../components/mercados/CornersDetalle";
import TarjetasDetalle from "../components/mercados/TarjetasDetalle";
import BttsDetalle from "../components/mercados/BttsDetalle";

export default function Home() {
  // Equipos y selección
  const [equipos, setEquipos] = useState([]);
  const [errorEquipos, setErrorEquipos] = useState("");
  const [localId, setLocalId] = useState("");
  const [visitanteId, setVisitanteId] = useState("");

  // Análisis
  const [analizando, setAnalizando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState("");
  const [validacion, setValidacion] = useState("");

  // Cargar equipos al montar la página.
  useEffect(() => {
    getEquipos()
      .then(setEquipos)
      .catch((e) => setErrorEquipos(e.message));
  }, []);

  async function onAnalizar() {
    setValidacion("");
    setError("");

    // Validaciones en el front antes de llamar a la API.
    if (!localId || !visitanteId) {
      setValidacion("Elegí el equipo local y el visitante.");
      return;
    }
    if (localId === visitanteId) {
      setValidacion("El equipo local y el visitante deben ser distintos.");
      return;
    }

    setAnalizando(true);
    setResultado(null);
    try {
      const data = await analizarPartido(Number(localId), Number(visitanteId));
      setResultado(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setAnalizando(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      {/* Encabezado */}
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Bet Analyzer AI</h1>
        <p className="text-sm text-slate-500">
          Análisis estadístico por mercado. Elegí dos equipos y analizá el partido.
        </p>
      </header>

      {/* Controles */}
      <section className="mb-6 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        {errorEquipos ? (
          <p className="text-sm text-red-600">{errorEquipos}</p>
        ) : (
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Equipo local
              </label>
              <select
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                value={localId}
                onChange={(e) => setLocalId(e.target.value)}
              >
                <option value="">— Elegir —</option>
                {equipos.map((eq) => (
                  <option key={eq.id} value={eq.id}>
                    {eq.short_name || eq.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1">
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Equipo visitante
              </label>
              <select
                className="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none"
                value={visitanteId}
                onChange={(e) => setVisitanteId(e.target.value)}
              >
                <option value="">— Elegir —</option>
                {equipos.map((eq) => (
                  <option key={eq.id} value={eq.id}>
                    {eq.short_name || eq.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              onClick={onAnalizar}
              disabled={analizando}
              className="rounded-md bg-emerald-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {analizando ? "Analizando..." : "Analizar"}
            </button>
          </div>
        )}

        {validacion && <p className="mt-3 text-sm text-amber-700">{validacion}</p>}
      </section>

      {/* Estado de carga */}
      {analizando && (
        <p className="mb-4 text-center text-sm text-slate-500">Analizando el partido...</p>
      )}

      {/* Error de la API */}
      {error && (
        <div className="mb-4 rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Resultados */}
      {resultado && !analizando && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-800">{resultado.partido}</h2>

          <Acordeon
            titulo="Goles"
            confiable={resultado.goals.confiable}
            resumen={`Total esp. ${num(
              resultado.goals.valores.goles_esperados_total
            )} · Over ${pct(resultado.goals.valores.over_under.prob_over)}`}
          >
            <Advertencia advertencias={resultado.goals.advertencias} />
            <GolesDetalle valores={resultado.goals.valores} />
            <Explicacion texto={resultado.goals.explicacion} />
          </Acordeon>

          <Acordeon
            titulo="Córners"
            confiable={resultado.corners.confiable}
            resumen={`Total esp. ${num(
              resultado.corners.valores.corners_totales
            )} · Índice ${num(resultado.corners.indice, 0)}`}
          >
            <Advertencia advertencias={resultado.corners.advertencias} />
            <CornersDetalle valores={resultado.corners.valores} />
            <Explicacion texto={resultado.corners.explicacion} />
          </Acordeon>

          <Acordeon
            titulo="Tarjetas"
            confiable={resultado.cards.confiable}
            resumen={`Total esp. ${num(
              resultado.cards.valores.tarjetas_esperadas_total
            )}`}
          >
            <Advertencia advertencias={resultado.cards.advertencias} />
            <TarjetasDetalle valores={resultado.cards.valores} />
            <Explicacion texto={resultado.cards.explicacion} />
          </Acordeon>

          <Acordeon
            titulo="BTTS (ambos marcan)"
            confiable={resultado.btts.confiable}
            resumen={`Sí ${pct(resultado.btts.valores.prob_si)}`}
          >
            <Advertencia advertencias={resultado.btts.advertencias} />
            <BttsDetalle valores={resultado.btts.valores} />
            <Explicacion texto={resultado.btts.explicacion} />
          </Acordeon>
        </section>
      )}
    </main>
  );
}
