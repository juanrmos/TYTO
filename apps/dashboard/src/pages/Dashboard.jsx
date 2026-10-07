import { useEffect, useState } from 'react';
import { DayDetail } from '../components/DayDetail';
import { DaySelector } from '../components/DaySelector';
import { LoadingState } from '../components/LoadingState';
import { MethodologyWarning } from '../components/MethodologyWarning';
import { OfficialLinks } from '../components/OfficialLinks';
import { WeekWarningBanner } from '../components/WeekWarningBanner';
import { useForecast } from '../hooks/useForecast';
import { formatDate, formatTimestamp } from '../utils/format';

function Landscape() {
  return (
    <svg className="landscape" viewBox="0 0 380 210" fill="none" aria-hidden="true">
      <circle cx="283" cy="58" r="28" fill="#d5bd7c" />
      <path d="M0 174 72 78l53 64 80-118 77 110 43-48 55 80v44H0Z" fill="#466858" />
      <path d="m0 192 114-91 69 49 84-90 113 139v11H0Z" fill="#254c40" />
      <path d="M124 210c4-62 24-99 60-104 45-6 84 46 91 104" fill="#16382f" />
      <path d="M162 210c1-37 7-66 26-67 25-2 44 37 45 67" fill="#a5b78b" />
      <path
        d="M188 150v60M12 190l39-46m-13 5 2 9m4 7 9-1m261 20 39-61m-29 32-10-6m22-12 11 1"
        stroke="#c9d4b2"
        strokeWidth="2"
      />
      <path d="M164 210c-9-10-8-21 2-28m63 28c9-9 10-18 1-30" stroke="#d5bd7c" strokeWidth="2" />
    </svg>
  );
}

export function Dashboard() {
  const { data, loading, error, retry } = useForecast('cueva-lechuzas');
  const [selectedDate, setSelectedDate] = useState(null);
  useEffect(() => {
    if (data) setSelectedDate((data.days.find((day) => day.is_today) || data.days[0]).date);
  }, [data]);
  const selected = data?.days.find((day) => day.date === selectedDate) || data?.days[0];
  return (
    <>
      <a className="skip-link" href="#forecast">
        Ir al pronóstico
      </a>
      <header className="site-header">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            ◉
          </span>
          <span>
            tyto<span className="brand-period">.</span>
          </span>
        </div>
        <span className="header-note">Naturaleza, con un poco de previsión.</span>
        <span className="location-tag">TINGO MARÍA · PERÚ</span>
      </header>
      <main>
        <section className="hero">
          <div className="hero-copy">
            <div className="hero-eyebrow">
              <span />
              PLANIFICA TU PRÓXIMA ESCAPADA
            </div>
            <h1>{data?.destination.name || 'Cueva de las Lechuzas'}</h1>
            <p>
              Un día para conectar con la naturaleza.
              <br />
              Encuentra el momento más conveniente para tu visita.
            </p>
            <span className="park-label">Parque Nacional Tingo María · Huánuco, Perú</span>
          </div>
          <Landscape />
        </section>
        <section
          id="forecast"
          className="forecast-section"
          aria-labelledby="forecast-title"
          aria-busy={loading}
        >
          <div className="section-heading">
            <div>
              <div className="section-eyebrow">LOS PRÓXIMOS SIETE DÍAS</div>
              <h2 id="forecast-title">Elige tu día</h2>
            </div>
            {data && (
              <div className="date-range">
                {formatDate(data.days[0].date, { day: 'numeric', month: 'short' })} —{' '}
                {formatDate(data.days[6].date, { day: 'numeric', month: 'short', year: 'numeric' })}
                <small>Hora de Perú</small>
              </div>
            )}
          </div>
          {loading ? (
            <LoadingState />
          ) : error ? (
            <div className="error-panel" role="alert">
              <span aria-hidden="true">↻</span>
              <h3>No se pudo cargar el pronóstico.</h3>
              <p>El servicio puede no estar disponible temporalmente. Vuelve a intentarlo.</p>
              <button className="primary-button" onClick={retry}>
                Reintentar
              </button>
            </div>
          ) : (
            data && (
              <>
                <WeekWarningBanner warning={data.week_warning} />
                <DaySelector
                  days={data.days}
                  selectedDate={selected?.date}
                  onSelect={setSelectedDate}
                />
                <div className="forecast-meta">
                  <span>
                    <span className="live-dot" />
                    {data.weather_fetched_at
                      ? `Pronóstico actualizado: ${formatTimestamp(data.weather_fetched_at)}`
                      : 'Pronóstico meteorológico no disponible'}
                  </span>
                  <span>Selecciona una tarjeta para ver el detalle ↓</span>
                </div>
                <DayDetail day={selected} />
                <OfficialLinks destination={data.destination} />
                <MethodologyWarning text={data.methodology_warning} />
              </>
            )
          )}
        </section>
      </main>
      <footer className="site-footer">
        <span>
          tyto. <span>Explora con información.</span>
        </span>
        <span>Estimaciones académicas · Cueva de las Lechuzas</span>
      </footer>
    </>
  );
}
