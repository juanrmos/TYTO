import { useCallback, useEffect, useState } from 'react';
import { getForecast } from '../api/forecast';

export function useForecast(slug) {
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const retry = useCallback(() => setAttempt((value) => value + 1), []);

  useEffect(() => {
    const controller = new AbortController();
    let active = true;
    const timeout = setTimeout(() => controller.abort(), 20000);
    setState({ data: null, loading: true, error: null });
    getForecast(slug, controller.signal)
      .then((data) => {
        if (active) setState({ data, loading: false, error: null });
      })
      .catch(() => {
        if (active)
          setState({ data: null, loading: false, error: 'No se pudo cargar el pronóstico.' });
      })
      .finally(() => clearTimeout(timeout));
    return () => {
      active = false;
      clearTimeout(timeout);
      controller.abort();
    };
  }, [slug, attempt]);

  useEffect(() => {
    // Refresh after crossing a calendar date in Lima, including a resumed browser tab.
    let current = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima' }).format(new Date());
    const timer = setInterval(() => {
      const next = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima' }).format(
        new Date(),
      );
      if (next !== current) {
        current = next;
        retry();
      }
    }, 60000);
    return () => clearInterval(timer);
  }, [retry]);
  return { ...state, retry };
}
