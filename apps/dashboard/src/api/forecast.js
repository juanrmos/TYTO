const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export async function getForecast(slug, signal) {
  const response = await fetch(`${API_BASE}/api/v1/forecast/${encodeURIComponent(slug)}`, {
    signal,
  });
  if (!response.ok) throw new Error('No se pudo cargar el pronóstico.');
  const data = await response.json();
  if (!Array.isArray(data.days) || data.days.length !== 7 || !data.destination || !data.best_day) {
    throw new Error('La respuesta del pronóstico está incompleta.');
  }
  return data;
}
