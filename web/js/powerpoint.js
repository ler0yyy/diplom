const params = new URLSearchParams(window.location.search);
const sessionId = params.get('session');
const slideId = params.get('slideId') || 'demo123';
const base = `${window.location.origin}${window.location.pathname.replace('powerpoint-example.html', '')}`;
const pollUrl = sessionId
  ? `${base}poll.html?session=${encodeURIComponent(sessionId)}`
  : `${base}poll.html?id=${encodeURIComponent(slideId)}`;

document.getElementById('poll-url').textContent = pollUrl;
document.getElementById('poll-url-small').textContent = pollUrl;

function drawQr(canvasId, size) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || typeof QRCode === 'undefined') return;
  QRCode.toCanvas(canvas, pollUrl, {
    width: size,
    margin: 2,
    color: { dark: '#1F2937', light: '#FFFFFF' },
  });
}

drawQr('qr-main', 300);
drawQr('qr-print', 200);

document.getElementById('download-btn').addEventListener('click', () => {
  const canvas = document.getElementById('qr-main');
  const link = document.createElement('a');
  link.download = sessionId ? `pollpoint-qr-${sessionId}.png` : `pollpoint-qr-${slideId}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
});
