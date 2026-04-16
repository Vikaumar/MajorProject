const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchJSON(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API ${path} returned ${res.status}`);
  return res.json();
}
