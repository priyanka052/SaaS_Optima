const API_ROOT = '/api';

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_ROOT}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error('Cannot reach the backend. Start the FastAPI server and try again.');
  }

  const contentType = response.headers.get('content-type') || '';
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof payload === 'object' ? payload?.detail : payload;
    throw new Error(detail || `Request failed (${response.status}).`);
  }
  return payload;
}

const query = (values) => new URLSearchParams(values).toString();

export const api = {
  health: () => request('/health'),
  tools: () => request('/tools'),
  pricing: () => request('/pricing'),
  overlap: (threshold = 0) => request(`/overlap?${query({ threshold })}`),
  compare: (toolA, toolB) => request(`/compare?${query({ tool_a: toolA, tool_b: toolB })}`),
  negotiate: (body) => request('/negotiation', { method: 'POST', body: JSON.stringify(body) }),
};

export function formatMoney(value, currency = 'INR') {
  if (value === null || value === undefined || value === '') return '—';
  try {
    return new Intl.NumberFormat(undefined, {
      style: 'currency', currency, maximumFractionDigits: 2,
    }).format(Number(value));
  } catch {
    return `${currency} ${Number(value).toLocaleString()}`;
  }
}
