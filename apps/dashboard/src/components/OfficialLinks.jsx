export function OfficialLinks({ destination }) {
  const links = [
    ['Información del parque', destination.official_url],
    ['Comprar entrada', destination.tickets_url],
    ['Cómo llegar', destination.directions_url],
  ];
  return (
    <section className="official">
      <div>
        <span className="section-eyebrow">ANTES DE SALIR</span>
        <h2>Confirma tu visita</h2>
        <p>Horarios, entradas y avisos en los canales oficiales de SERNANP.</p>
      </div>
      <nav aria-label="Enlaces oficiales">
        {links
          .filter(([, url]) => url)
          .map(([label, url]) => (
            <a key={label} href={url} target="_blank" rel="noopener noreferrer">
              {label}
              <span aria-hidden="true">↗</span>
              <span className="sr-only"> (abre en otra pestaña)</span>
            </a>
          ))}
      </nav>
    </section>
  );
}
