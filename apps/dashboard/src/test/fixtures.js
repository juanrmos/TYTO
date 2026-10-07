export function makeForecast(category = 'RECOMENDADO') {
  const labels = {
    RECOMENDADO: 'Recomendado',
    PRECAUCION: 'Visitable con precaución',
    NO_RECOMENDADO: 'No recomendado',
    SIN_DATOS: 'Sin datos meteorológicos',
  };
  return {
    destination: {
      slug: 'cueva-lechuzas',
      name: 'Cueva de las Lechuzas',
      official_url:
        'https://visitaareasnaturales.sernanp.gob.pe/anps/parque-nacional-de-tingo-maria/',
      tickets_url: 'https://visitaareasnaturales.sernanp.gob.pe/tuticket/',
      directions_url:
        'https://visitaareasnaturales.sernanp.gob.pe/anps/parque-nacional-de-tingo-maria/',
    },
    generated_at: '2026-10-06T10:00:00-05:00',
    weather_fetched_at: '2026-10-06T09:30:00-05:00',
    engine_version: 'ME-1.0',
    generator_version: 'SG-1.0',
    best_day: { date: '2026-10-07', label: 'MEJOR_OPCION' },
    week_warning: null,
    methodology_warning:
      'La afluencia es una estimación académica derivada de registros mensuales oficiales. No representa ocupación real ni conteo en tiempo real.',
    days: ['Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo', 'Lunes'].map(
      (name, i) => ({
        date: `2026-10-${String(i + 6).padStart(2, '0')}`,
        day_of_week: name,
        is_today: i === 0,
        is_best: i === 1,
        best_label: i === 1 ? 'MEJOR_OPCION' : null,
        calendar_note: i === 2 ? 'Feriado' : null,
        affuence: { score: 28 + i * 6, level: 'BAJA', level_label: 'Baja' },
        convenience: {
          score: category === 'SIN_DATOS' ? null : 88 - i * 3,
          category,
          category_label: labels[category],
        },
        weather:
          category === 'SIN_DATOS'
            ? null
            : {
                condition_label: 'Parcialmente nublado',
                weather_code: 2,
                temp_max_c: 28,
                temp_min_c: 20,
                apparent_temp_max_c: 30,
                rain_mm: 1.2,
                rain_probability_pct: 15,
                rain_hours: 0.5,
                wind_max_kmh: 12,
                uv_max: 7,
                sunshine_hours: 6.2,
              },
        recommendation: {
          text: 'Buen momento para visitar. Consulte horarios y disponibilidad de entradas en los canales oficiales.',
          template_key: 'RECOMENDADO_BAJA_FAVORABLE',
        },
        active_factors: ['Afluencia histórica baja para esta fecha'],
        is_degraded: category === 'SIN_DATOS',
        degraded_reason: category === 'SIN_DATOS' ? 'WEATHER_UNAVAILABLE' : null,
      }),
    ),
  };
}
