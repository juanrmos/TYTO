export function WeatherIcon({ code, size = 28 }) {
  const sunny = code === 0 || code === 1;
  const rain = code >= 51;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {code == null ? (
        <>
          <path d="M9 12a7 7 0 0 1 14 0c0 4-7 4-7 8" />
          <path d="M16 25h.01" />
        </>
      ) : sunny ? (
        <>
          <circle cx="16" cy="16" r="6" />
          <path d="M16 2v3m0 22v3M2 16h3m22 0h3M6 6l2 2m16 16 2 2M6 26l2-2M24 8l2-2" />
        </>
      ) : (
        <>
          <path d="M8 23a6 6 0 0 1-1-12 8 8 0 0 1 15-2 7 7 0 0 1 2 14H8Z" />
          {rain && <path d="m10 26-1 3m8-3-1 3m8-3-1 3" />}
          {code >= 95 && <path d="m18 13-4 6h5l-3 6" />}
        </>
      )}
    </svg>
  );
}
