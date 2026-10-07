import { number } from '../utils/format';
import { WeatherIcon } from './WeatherIcon';

export function WeatherSummary({ weather }) {
  if (!weather)
    return (
      <section className="weather-panel">
        <h3>El clima para tu visita</h3>
        <p className="muted">Sin datos meteorológicos</p>
        <p>Consulta el pronóstico antes de planificar.</p>
      </section>
    );
  return (
    <section className="weather-panel">
      <div className="section-eyebrow">PRONÓSTICO DIARIO</div>
      <div className="weather-heading">
        <div>
          <h3>{weather.condition_label}</h3>
          <p>
            Máx. {number(weather.temp_max_c)} °C <span>·</span> Mín. {number(weather.temp_min_c)} °C
          </p>
        </div>
        <WeatherIcon code={weather.weather_code} size={46} />
      </div>
      <dl className="weather-grid">
        <div>
          <dt>Probabilidad de lluvia</dt>
          <dd>
            {number(weather.rain_probability_pct, 0)} <small>%</small>
          </dd>
        </div>
        <div>
          <dt>Precipitación</dt>
          <dd>
            {number(weather.rain_mm)} <small>mm</small>
          </dd>
        </div>
        <div>
          <dt>Horas de lluvia</dt>
          <dd>
            {number(weather.rain_hours)} <small>h</small>
          </dd>
        </div>
        <div>
          <dt>Sensación térmica</dt>
          <dd>
            {number(weather.apparent_temp_max_c)} <small>°C</small>
          </dd>
        </div>
        <div>
          <dt>Viento máximo</dt>
          <dd>
            {number(weather.wind_max_kmh)} <small>km/h</small>
          </dd>
        </div>
        <div>
          <dt>Índice UV</dt>
          <dd>{number(weather.uv_max)}</dd>
        </div>
        <div>
          <dt>Horas de sol</dt>
          <dd>
            {number(weather.sunshine_hours)} <small>h</small>
          </dd>
        </div>
      </dl>
    </section>
  );
}
