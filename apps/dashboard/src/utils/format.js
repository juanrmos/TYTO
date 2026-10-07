export function formatDate(value, options = {}) {
  return new Intl.DateTimeFormat('es-PE', { timeZone: 'America/Lima', ...options }).format(
    new Date(`${value}T12:00:00-05:00`),
  );
}

export function formatTimestamp(value) {
  if (!value) return 'Pronóstico meteorológico no disponible';
  return new Intl.DateTimeFormat('es-PE', {
    timeZone: 'America/Lima',
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

export function number(value, digits = 1) {
  return value == null
    ? '—'
    : new Intl.NumberFormat('es-PE', { maximumFractionDigits: digits }).format(value);
}

export const bestLabels = {
  MEJOR_OPCION: 'Mejor opción',
  MEJOR_ALTERNATIVA: 'Mejor alternativa',
  MENOR_AFLUENCIA: 'Menor afluencia estimada',
};
