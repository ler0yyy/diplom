const params = new URLSearchParams(window.location.search);
const sessionId = params.get('session');
const slideId = params.get('id') || 'demo';

const list = document.getElementById('answer-list');
const submitBtn = document.getElementById('submit-answer');
const questionEl = document.getElementById('question');

let selectedAnswer = null;
let effectiveSessionId = sessionId;

// AUTH FIRST: Must be logged in as student to see poll
function requireStudentAuth() {
  const user = getUser();
  if (!isAuthenticated() || !user) {
    // Not logged in - redirect to login with return URL
    const returnTo = encodeURIComponent(window.location.href);
    window.location.href = `index.html?returnTo=${returnTo}`;
    return null;
  }
  if (user.role !== 'student') {
    alert('Только студенты могут участвовать в опросах. Войдите как студент.');
    window.location.href = 'index.html';
    return null;
  }
  return user;
}

async function loadPoll() {
  // First check: must be authenticated as student
  const user = requireStudentAuth();
  if (!user) return; // Redirected to login

  if (!effectiveSessionId) {
    questionEl.textContent = 'Нет session ID';
    list.innerHTML = '<p class="main__subtitle">Откройте страницу по ссылке с QR-кода.</p>';
    submitBtn.classList.add('hidden');
    return;
  }

  try {
    const poll = await apiFetch(`/api/sessions/${encodeURIComponent(effectiveSessionId)}/poll`, { auth: false });
    if (poll.test_type === 'tags') {
      window.location.href = `poll-tags.html?session=${encodeURIComponent(poll.session_id)}`;
      return;
    }
    questionEl.textContent = poll.question;

    list.innerHTML = poll.options.map((answer, index) => `
      <button type="button" class="answer-btn" data-id="${answer.id}">
        <div class="answer-btn__inner">
          <div class="answer-btn__letter">${String.fromCharCode(65 + index)}</div>
          <span class="answer-btn__text">${answer.text}</span>
          <span class="check-icon hidden">${Icons.check}</span>
        </div>
      </button>
    `).join('');

    // Add click handlers
    list.querySelectorAll('.answer-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        selectedAnswer = btn.dataset.id;
        list.querySelectorAll('.answer-btn').forEach((b) => {
          const selected = b === btn;
          b.classList.toggle('answer-btn--selected', selected);
          b.querySelector('.check-icon').classList.toggle('hidden', !selected);
        });
        submitBtn.disabled = false;
      });
    });
  } catch (e) {
    console.error(e);
    questionEl.textContent = 'Ошибка загрузки опроса';
    list.innerHTML = '<p class="main__subtitle">Не удалось загрузить опрос. Проверьте ссылку.</p>';
    submitBtn.classList.add('hidden');
  }
}

submitBtn.addEventListener('click', async () => {
  if (!selectedAnswer || !effectiveSessionId) return;

  // Re-verify auth before submitting
  const user = requireStudentAuth();
  if (!user) return;

  try {
    await apiFetch('/api/responses', {
      method: 'POST',
      body: { session_id: effectiveSessionId, option_id: Number(selectedAnswer) },
    });
    window.location.href = 'vote-submitted.html';
  } catch (e) {
    console.error(e);
    alert('Не удалось отправить ответ. Попробуйте снова.');
  }
});

loadPoll().catch((e) => console.error(e));
