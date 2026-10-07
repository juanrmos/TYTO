import { bestLabels, formatDate, number } from '../utils/format';
import { WeatherSummary } from './WeatherSummary';

export function DayDetail({ day }) {
  return (
    <section
      className={`detail category-${day.convenience.category}`}
      aria-labelledby="detail-title"
    >
      <div className="detail-heading">
        <div>
          <div className="section-eyebrow">TU DÍA EN DETALLE</div>
          <h2 id="detail-title">
            {day.day_of_week}, {formatDate(day.date, { day: 'numeric', month: 'long' })}
          </h2>
        </div>
        {day.is_best && <span className="best-badge">✦ {bestLabels[day.best_label]}</span>}
      </div>
      <div className="detail-grid">
        <div className="decision-panel">
          <div className="metrics">
            <div>
              <span className="metric-label">Conveniencia de visita</span>
              <div className="metric-score">
                {number(day.convenience.score, 0)}
                <small>/100</small>
              </div>
              <span className="recommendation-pill">
                <span className="status-dot" />
                {day.convenience.category_label}
              </span>
            </div>
            <div>
              <span className="metric-label">Afluencia estimada</span>
              <div className="metric-score crowd-score">
                {number(day.affuence.score, 0)}
                <small>/100</small>
              </div>
              <span className="crowd-level">
                {day.affuence.level_label || 'Datos insuficientes'}
              </span>
              <p className="metric-help">Concurrencia relativa esperada</p>
            </div>
          </div>
          <div className="recommendation">
            <h3>Para planificar tu visita</h3>
            <p>{day.recommendation.text}</p>
          </div>
          {day.degraded_reason === 'ZERO_REPORTED_MONTH' && (
            <p className="data-note">
              El mes de referencia tiene cero visitantes reportados. Confirma las condiciones de
              acceso en los canales oficiales.
            </p>
          )}
          <div className="factors">
            <h3>Factores principales</h3>
            <ul>
              {day.active_factors.map((factor) => (
                <li key={factor}>{factor}</li>
              ))}
            </ul>
          </div>
        </div>
        <WeatherSummary weather={day.weather} />
      </div>
    </section>
  );
}
