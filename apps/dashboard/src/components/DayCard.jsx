import { bestLabels, formatDate, number } from '../utils/format';
import { WeatherIcon } from './WeatherIcon';

export function DayCard({ day, selected, onSelect }) {
  return (
    <button
      className={`day-card category-${day.convenience.category} ${selected ? 'selected' : ''}`}
      onClick={() => onSelect(day.date)}
      aria-pressed={selected}
      aria-label={`${day.day_of_week} ${formatDate(day.date, { day: 'numeric', month: 'long' })}, ${day.convenience.category_label}`}
    >
      <span className="day-top">
        <span>{day.day_of_week.slice(0, 3)}</span>
        {day.is_today && <span className="today-tag">Hoy</span>}
      </span>
      <span className="day-number">{formatDate(day.date, { day: '2-digit' })}</span>
      <span className="best-slot">
        {day.is_best ? <span>✦ {bestLabels[day.best_label]}</span> : '\u00a0'}
      </span>
      <span className="day-weather">
        <WeatherIcon code={day.weather?.weather_code} />
        <span>{day.weather ? `${number(day.weather.temp_max_c, 0)}°` : '—'}</span>
      </span>
      <span className="day-score">
        {number(day.convenience.score, 0)}
        <small> / 100</small>
      </span>
      <span className="category-label">
        <span className="status-dot" />
        {day.convenience.category_label}
      </span>
      <span className="day-crowd">
        Afluencia {number(day.affuence.score, 0)} · {day.affuence.level_label || 'Sin datos'}
      </span>
      {day.calendar_note && <span className="calendar-note">{day.calendar_note}</span>}
    </button>
  );
}
