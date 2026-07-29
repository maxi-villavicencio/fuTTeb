// Utilidades de formato. El frontend NO calcula estadística: solo da formato
// a lo que ya viene de la API.

/** Formatea una probabilidad 0..1 como porcentaje. */
export function pct(x, decimales = 0) {
  return `${(Number(x) * 100).toFixed(decimales)}%`;
}

/** Formatea un número con la cantidad de decimales indicada. */
export function num(x, decimales = 2) {
  return Number(x).toFixed(decimales);
}
