export function WeekWarningBanner({ warning }) {
  return warning ? (
    <div className="week-warning" role="status">
      <span aria-hidden="true">ⓘ</span>
      <p>{warning}</p>
    </div>
  ) : null;
}
