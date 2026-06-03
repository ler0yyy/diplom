// Results can be viewed by teacher or anyone with session link
// For teacher-only mode, uncomment: requireAuth('teacher');
const user = getUser();
const isTeacher = user && user.role === 'teacher';

const COLORS = ['#C76E22', '#2D2D2D', '#7a7a7a', '#cfcfcf', '#000000'];

const params = new URLSearchParams(window.location.search);
const sessionId = params.get('session');

const statsList = document.getElementById('stats-list');
const questionText = document.getElementById('question-text');
const totalVotes = document.getElementById('total-votes');

// Set initial loading state
if (questionText) questionText.textContent = 'Загрузка...';
if (statsList) statsList.innerHTML = '<p class="main__subtitle">Загрузка результатов...</p>';

let lastPayload = null;
let items = [];
let chartInstance = null;
let chartType = 'bar';

function renderStats(payload) {
  document.getElementById('question-text').textContent = payload.question || '';
  document.getElementById('total-votes').textContent = `${payload.total || 0} голосов`;

  if (payload.items && payload.items.length) {
    items = payload.items.map((it) => ({
      label: it.label,
      votes: it.votes,
      percent: it.percent,
    }));

    statsList.innerHTML = items.map((item, index) => `
      <div class="stat-row">
        <div class="stat-row__head">
          <span>${item.label}</span>
          <div>
            <span style="color:var(--gray-600);margin-right:0.75rem;">${item.votes} голосов</span>
            <strong>${item.percent}%</strong>
          </div>
        </div>
        <div class="stat-bar">
          <div class="stat-bar__fill" style="width:${item.percent}%;background:${COLORS[index % COLORS.length]}"></div>
        </div>
      </div>
    `).join('');
  } else {
    // tags
    const tags = payload.tags || [];
    items = tags.map((t) => ({ label: t.word, votes: t.count, percent: 0 }));
    statsList.innerHTML = `
      <div class="card card--bordered">
        <p class="main__subtitle">Теги (топ):</p>
        <div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:0.75rem;">
          ${tags.slice(0, 30).map((t) => `
            <span style="border:1px solid var(--gray-200);background:#fff;padding:0.35rem 0.6rem;border-radius:9999px;">
              <strong style="color:var(--gray-900);">${t.word}</strong>
              <span style="color:var(--gray-600);margin-left:0.35rem;">${t.count}</span>
            </span>
          `).join('')}
        </div>
      </div>
    `;
  }

  buildChart();
}

function buildChart() {
  const ctx = document.getElementById('results-chart');
  if (!ctx) {
    console.error('Canvas not found');
    return;
  }
  if (typeof Chart === 'undefined') {
    console.error('Chart.js not loaded yet, will retry');
    // Retry after delay
    setTimeout(buildChart, 500);
    return;
  }

  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }

  // Always show chart, even with empty/default data
  const labels = items.length > 0 ? items.map((d) => d.label) : ['Нет данных'];
  const values = items.length > 0 ? items.map((d) => d.votes) : [0];

  try {
    chartInstance = new Chart(ctx, {
      type: chartType === 'bar' ? 'bar' : 'pie',
      data: {
        labels,
        datasets: [{
          label: 'Голоса',
          data: values,
          backgroundColor: COLORS,
          borderRadius: chartType === 'bar' ? 8 : 0,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: chartType === 'pie' },
          title: {
            display: items.length === 0 || values.every(v => v === 0),
            text: 'Пока нет голосов',
            font: { size: 14 }
          }
        },
        scales: chartType === 'bar' ? {
          y: { beginAtZero: true, title: { display: true, text: 'Голоса' }, max: Math.max(1, ...values) },
        } : {},
      },
    });
    console.log('Chart built successfully');
  } catch (e) {
    console.error('Chart error:', e);
  }
}

document.getElementById('chart-bar').addEventListener('click', () => {
  chartType = 'bar';
  document.getElementById('chart-bar').classList.add('active');
  document.getElementById('chart-pie').classList.remove('active');
  buildChart();
});

document.getElementById('chart-pie').addEventListener('click', () => {
  chartType = 'pie';
  document.getElementById('chart-pie').classList.add('active');
  document.getElementById('chart-bar').classList.remove('active');
  buildChart();
});

async function pollStats() {
  if (!sessionId) {
    document.getElementById('question-text').textContent = 'Нет session=...';
    statsList.innerHTML = '<p class="main__subtitle">Откройте страницу результатов с параметром session.</p>';
    return;
  }

  try {
    console.log('Polling stats for session:', sessionId);
    const payload = await apiFetch(`/api/sessions/${encodeURIComponent(sessionId)}/stats`, { auth: false });
    console.log('Stats received:', payload);

    // Don't overwrite with empty data if we already have data
    if (lastPayload && payload.total === 0 && JSON.parse(lastPayload).total > 0) {
      console.log('Skipping empty data update');
    } else {
      const key = JSON.stringify(payload);
      if (key !== lastPayload) {
        lastPayload = key;
        renderStats(payload);
      }
    }
  } catch (e) {
    console.error('Poll stats error:', e);
  }

  // Always schedule next poll
  setTimeout(pollStats, 2500);
}

// Start polling after a short delay to ensure Chart.js is loaded
setTimeout(() => {
  console.log('Chart.js loaded?', typeof Chart !== 'undefined');
  pollStats();
}, 500);
