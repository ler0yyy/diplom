requireAuth('teacher');

const params = new URLSearchParams(window.location.search);
const presentationId = params.get('presentationId') || '1';
const slideId = params.get('slideId');
const isEditing = !!slideId;

if (isEditing) {
  document.getElementById('page-title').textContent = 'Редактировать слайд';
  document.getElementById('submit-btn').textContent = 'Сохранить изменения';
}

let answers = [
  { id: '1', text: '' },
  { id: '2', text: '' },
];

function getTestType() {
  const el = document.getElementById('test-type');
  return el ? el.value : 'choice';
}

function syncVisibility() {
  const type = getTestType();
  const answersBlock = document.getElementById('answers-block');
  const tagsBlock = document.getElementById('tags-preview-block');
  if (answersBlock) {
    const isChoice = type === 'choice';
    answersBlock.classList.toggle('hidden', !isChoice);
    // Toggle required on inputs
    answersBlock.querySelectorAll('input[required]').forEach((input) => {
      if (isChoice) input.setAttribute('required', 'required');
      else input.removeAttribute('required');
    });
  }
  if (tagsBlock) tagsBlock.classList.toggle('hidden', type !== 'tags');
}

async function loadSlidesList() {
  const listEl = document.getElementById('slides-list');
  if (!listEl) return;
  listEl.innerHTML = '<p class="main__subtitle">Загрузка...</p>';

  const slides = await apiFetch(`/api/presentations/${presentationId}/slides`, { auth: false });
  if (!slides.length) {
    listEl.innerHTML = '<p class="main__subtitle">Пока слайдов нет.</p>';
    return;
  }

  listEl.innerHTML = slides.map((s) => `
    <div style="border:1px solid var(--gray-200);border-radius:var(--radius);padding:0.75rem 1rem;margin-bottom:0.75rem;">
      <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start;flex-wrap:wrap;">
        <div style="flex:1;min-width:16rem;">
          <div style="font-weight:600;margin-bottom:0.25rem;">${s.question}</div>
          <div class="main__subtitle" style="font-size:0.875rem;">Тип: <strong>${s.test_type}</strong></div>
        </div>
        <div style="display:flex;gap:0.5rem;align-items:center;">
          <a class="btn btn--outline" style="padding:0.5rem 0.75rem;" href="create-slide.html?presentationId=${encodeURIComponent(presentationId)}&slideId=${encodeURIComponent(s.id)}">Редактировать</a>
          <button type="button" class="btn btn--outline-accent session-btn" data-slide="${s.id}" style="padding:0.5rem 0.75rem;">QR</button>
          <button type="button" class="btn btn--outline results-btn" data-slide="${s.id}" style="padding:0.5rem 0.75rem;">Результаты</button>
          <button type="button" class="btn btn--outline" data-del="${s.id}" style="padding:0.5rem 0.75rem;color:var(--red-600);border-color:var(--red-600);">Удалить</button>
        </div>
      </div>
    </div>
  `).join('');

  listEl.querySelectorAll('button[data-del]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const id = btn.getAttribute('data-del');
      if (!confirm('Удалить слайд?')) return;
      await apiFetch(`/api/slides/${id}`, { method: 'DELETE' });
      loadSlidesList().catch(console.error);
    });
  });

  listEl.querySelectorAll('.session-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const sid = Number(btn.dataset.slide);
      const r = await apiFetch('/api/sessions', { method: 'POST', body: { slide_id: sid } });
      window.location.href = `powerpoint-example.html?session=${encodeURIComponent(r.session_id)}`;
    });
  });

  listEl.querySelectorAll('.results-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const sid = Number(btn.dataset.slide);
      const r = await apiFetch('/api/sessions', { method: 'POST', body: { slide_id: sid } });
      window.location.href = `results.html?session=${encodeURIComponent(r.session_id)}`;
    });
  });
}

function renderAnswers() {
  const container = document.getElementById('answers-list');
  const countLabel = document.getElementById('answers-count');
  countLabel.textContent = answers.length;

  container.innerHTML = answers.map((a, index) => `
    <div class="answer-row" data-id="${a.id}">
      <div class="answer-row__letter">${String.fromCharCode(65 + index)}</div>
      <input type="text" class="answer-row__input" value="${a.text.replace(/"/g, '&quot;')}"
        placeholder="Вариант ${String.fromCharCode(65 + index)}" required data-id="${a.id}">
      ${answers.length > 2 ? `<button type="button" class="btn-icon remove-answer" style="color:var(--red-600);" title="Удалить">${Icons.trash}</button>` : ''}
    </div>
  `).join('');

  container.querySelectorAll('.answer-row__input').forEach((input) => {
    input.addEventListener('input', () => {
      const id = input.dataset.id;
      const item = answers.find((x) => x.id === id);
      if (item) item.text = input.value;
    });
  });

  container.querySelectorAll('.remove-answer').forEach((btn) => {
    btn.addEventListener('click', () => {
      const row = btn.closest('.answer-row');
      answers = answers.filter((a) => a.id !== row.dataset.id);
      renderAnswers();
    });
  });

  document.getElementById('add-answer-btn').disabled = answers.length >= 5;
}

document.getElementById('add-answer-btn').addEventListener('click', () => {
  if (answers.length < 5) {
    answers.push({ id: Date.now().toString(), text: '' });
    renderAnswers();
  }
});

document.getElementById('slide-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const question = document.getElementById('question').value.trim();
  const test_type = getTestType();

  const payload = {
    question,
    test_type,
    order_index: 0,
    options: test_type === 'choice'
      ? answers.map((a, idx) => ({ label: String.fromCharCode(65 + idx), text: (a.text || '').trim() }))
      : [],
  };

  const req = isEditing
    ? apiFetch(`/api/slides/${slideId}`, { method: 'PUT', body: payload })
    : apiFetch(`/api/presentations/${presentationId}/slides`, { method: 'POST', body: payload });

  req
    .then((r) => {
      if (isEditing) {
        loadSlidesList().catch(console.error);
        alert('Сохранено');
      } else {
        window.location.href = `create-slide.html?presentationId=${encodeURIComponent(presentationId)}&slideId=${encodeURIComponent(r.id)}`;
      }
    })
    .catch((e) => console.error(e));
});

document.getElementById('qr-btn').addEventListener('click', () => {
  // Для QR нужен реальный session_id. Создадим сессию по slide_id после сохранения.
  // Если слайд ещё не создан — сначала сохраните.
  const sid = slideId;
  if (!sid) {
    alert('Сначала сохраните слайд, затем создайте сессию/QR.');
    return;
  }
  apiFetch('/api/sessions', { method: 'POST', body: { slide_id: Number(sid) } })
    .then((r) => {
      window.location.href = `powerpoint-example.html?session=${encodeURIComponent(r.session_id)}`;
    })
    .catch((e) => console.error(e));
});

const typeEl = document.getElementById('test-type');
if (typeEl) typeEl.addEventListener('change', syncVisibility);

renderAnswers();
syncVisibility();
loadSlidesList().catch((e) => console.error(e));

async function loadEditingSlideIfAny() {
  if (!isEditing) return;
  const slides = await apiFetch(`/api/presentations/${presentationId}/slides`, { auth: false });
  const s = slides.find((x) => String(x.id) === String(slideId));
  if (!s) return;

  document.getElementById('question').value = s.question || '';
  const typeSel = document.getElementById('test-type');
  if (typeSel) typeSel.value = s.test_type || 'choice';

  if (s.test_type === 'choice') {
    answers = (s.options || []).map((o) => ({ id: String(o.id), text: o.text }));
    if (answers.length < 2) {
      answers = [{ id: '1', text: '' }, { id: '2', text: '' }];
    }
    renderAnswers();
  }
  syncVisibility();
}

loadEditingSlideIfAny().catch(console.error);
