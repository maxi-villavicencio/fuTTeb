// Capa de acceso a la API. La URL base viene de una variable de entorno
// (NEXT_PUBLIC_API_URL), NO está hardcodeada. El fallback solo evita romper si
// la variable no está definida en desarrollo.
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** GET /teams -> lista de equipos [{ id, name, short_name }]. */
export async function getEquipos() {
  let res;
  try {
    res = await fetch(`${API_URL}/teams`);
  } catch {
    throw new Error("No se pudo conectar con la API. ¿Está corriendo el backend?");
  }
  if (!res.ok) {
    throw new Error("No se pudieron cargar los equipos.");
  }
  const data = await res.json();
  return data.equipos;
}

/** POST /analyze -> resultado con los 4 mercados. */
export async function analizarPartido(homeId, awayId) {
  let res;
  try {
    res = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ home_team_id: homeId, away_team_id: awayId }),
    });
  } catch {
    throw new Error("No se pudo conectar con la API. ¿Está corriendo el backend?");
  }

  if (!res.ok) {
    // La API devuelve { detail: "mensaje en español" } en los errores 4xx/5xx.
    let detalle = "Ocurrió un error al analizar el partido.";
    try {
      const cuerpo = await res.json();
      if (cuerpo && cuerpo.detail) detalle = cuerpo.detail;
    } catch {
      /* respuesta sin JSON: se usa el mensaje por defecto */
    }
    throw new Error(detalle);
  }

  return res.json();
}
