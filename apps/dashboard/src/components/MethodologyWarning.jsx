export function MethodologyWarning({ text }) {
  return (
    <details className="methodology">
      <summary>Aviso metodológico</summary>
      <p>{text}</p>
      <p>
        Fuente histórica: MINCETUR. Pronóstico:{' '}
        <a href="https://open-meteo.com/" target="_blank" rel="noopener noreferrer">
          Open-Meteo ↗
        </a>
        .
      </p>
    </details>
  );
}
