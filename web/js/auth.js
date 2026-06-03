// Auth helpers now backed by Python API (JWT in localStorage)

async function login(email, password, role) {
  const data = await apiFetch('/api/auth/login', {
    method: 'POST',
    auth: false,
    body: { email, password },
  });

  if (role && data.user && data.user.role !== role) {
    throw new Error('wrong_role');
  }
  setAuth(data.token, data.user);
}

async function register(email, password, name, role) {
  const data = await apiFetch('/api/auth/register', {
    method: 'POST',
    auth: false,
    body: { email, password, name, role },
  });
  setAuth(data.token, data.user);
}

function logout() {
  clearAuth();
  window.location.href = 'index.html';
}

/** Редирект, если не авторизован или неверная роль */
function requireAuth(role) {
  const user = getUser();
  if (!user || !isAuthenticated()) {
    window.location.href = 'index.html';
    return null;
  }
  if (role && user.role !== role) {
    window.location.href = 'index.html';
    return null;
  }
  return user;
}

/** Заполнить имя/email в шапке */
function fillUserHeader() {
  const user = getUser();
  if (!user) return;
  const nameEl = document.querySelector('[data-user-name]');
  const emailEl = document.querySelector('[data-user-email]');
  if (nameEl) nameEl.textContent = user.name;
  if (emailEl) emailEl.textContent = user.email;
}
