export function LoadingState() {
  return (
    <div role="status" aria-label="Cargando pronóstico…" className="loading">
      <p>Cargando pronóstico…</p>
      <div className="loading-cards" aria-hidden="true">
        {Array.from({ length: 7 }, (_, i) => (
          <div className="skeleton" key={i} />
        ))}
      </div>
      <div className="skeleton loading-detail" aria-hidden="true" />
    </div>
  );
}
