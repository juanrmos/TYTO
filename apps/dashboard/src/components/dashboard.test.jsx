import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { DayCard } from './DayCard';
import { Dashboard } from '../pages/Dashboard';
import { makeForecast } from '../test/fixtures';

describe('tarjetas', () => {
  it.each(['RECOMENDADO', 'PRECAUCION', 'NO_RECOMENDADO', 'SIN_DATOS'])(
    'comunica categoría %s con texto y color',
    (category) => {
      const day = makeForecast(category).days[0];
      render(<DayCard day={day} selected onSelect={() => {}} />);
      expect(screen.getByRole('button')).toHaveClass(`category-${category}`);
      expect(screen.getByText(day.convenience.category_label)).toBeVisible();
      expect(screen.getByRole('button')).toHaveAttribute('aria-pressed', 'true');
    },
  );
  it('señala la mejor opción sin seleccionarla automáticamente', () => {
    render(<DayCard day={makeForecast().days[1]} selected={false} onSelect={() => {}} />);
    expect(screen.getByText(/Mejor opción/)).toBeVisible();
    expect(screen.getByRole('button')).toHaveAttribute('aria-pressed', 'false');
  });
});

describe('dashboard', () => {
  it('selecciona hoy y cambia el detalle sin otra solicitud', async () => {
    const fetch = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue({ ok: true, json: async () => makeForecast() });
    render(<Dashboard />);
    expect(screen.getByRole('status')).toHaveTextContent('Cargando pronóstico…');
    await screen.findByRole('heading', { name: 'Martes, 6 de octubre' });
    const group = screen.getByRole('group', {
      name: 'Selecciona un día de los próximos siete días',
    });
    const cards = within(group).getAllByRole('button');
    expect(cards).toHaveLength(7);
    expect(cards[0]).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(cards[1]);
    expect(screen.getByRole('heading', { name: 'Miércoles, 7 de octubre' })).toBeVisible();
    expect(cards[0]).toHaveAttribute('aria-pressed', 'false');
    expect(fetch).toHaveBeenCalledTimes(1);
  });
  it('permite reintentar un error', async () => {
    vi.spyOn(globalThis, 'fetch')
      .mockRejectedValueOnce(new Error('offline'))
      .mockResolvedValue({ ok: true, json: async () => makeForecast() });
    render(<Dashboard />);
    fireEvent.click(await screen.findByRole('button', { name: 'Reintentar' }));
    await screen.findByRole('heading', { name: 'Martes, 6 de octubre' });
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
  it('muestra datos degradados, advertencia semanal y enlaces seguros', async () => {
    const data = makeForecast('SIN_DATOS');
    data.week_warning = 'No se dispone de pronóstico meteorológico suficiente.';
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true, json: async () => data });
    render(<Dashboard />);
    await waitFor(() =>
      expect(screen.getAllByText('Sin datos meteorológicos').length).toBeGreaterThan(0),
    );
    expect(screen.getByRole('status')).toHaveTextContent(data.week_warning);
    expect(screen.getByRole('link', { name: /Comprar entrada/ })).toHaveAttribute(
      'rel',
      'noopener noreferrer',
    );
    fireEvent.click(screen.getByText('Aviso metodológico'));
    expect(screen.getByText(data.methodology_warning)).toBeInTheDocument();
  });
  it('rechaza un horizonte incompleto', async () => {
    const data = makeForecast();
    data.days.pop();
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: true, json: async () => data });
    render(<Dashboard />);
    expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo cargar el pronóstico.');
  });
});
