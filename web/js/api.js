const API_BASE = (window.location.origin && window.location.origin !== 'null')
  ? window.location.origin
  : 'http://localhost:5000';

const TOKEN_KEY = 'pollpoint_token';
const USER_KEY = 'pollpoint_user';

function getToken() {
  return localStorage.getItem(TOKEN_KEY) || '';
}

function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function getUser() {
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function isAuthenticated() {
  return !!getToken();
}

async function apiFetch(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let json = null;
  try { json = text ? JSON.parse(text) : null; } catch { json = { raw: text }; }

  if (!res.ok) {
    const err = new Error('API error');
    err.status = res.status;
    err.payload = json;
    throw err;
  }
  return json;
}

