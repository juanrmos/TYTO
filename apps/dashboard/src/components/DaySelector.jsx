import { DayCard } from './DayCard';

export function DaySelector({ days, selectedDate, onSelect }) {
  return (
    <div
      className="day-selector"
      role="group"
      aria-label="Selecciona un día de los próximos siete días"
    >
      {days.map((day) => (
        <DayCard
          key={day.date}
          day={day}
          selected={day.date === selectedDate}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
