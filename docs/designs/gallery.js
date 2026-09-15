const stages = Array.from(document.querySelectorAll('.preview-stage'));
const buttons = Array.from(document.querySelectorAll('[data-device]'));
let device = 'desktop';

function resizePreviews() {
  const viewport = device === 'mobile' ? 390 : 1120;
  stages.forEach(stage => {
    if (!stage.clientWidth) return;
    const frame = stage.querySelector('iframe');
    const scale = device === 'mobile' ? Math.min(0.85, stage.clientWidth / viewport) : stage.clientWidth / viewport;
    frame.style.width = `${viewport}px`;
    frame.style.height = `${Math.ceil(stage.clientHeight / scale)}px`;
    frame.style.transform = `scale(${scale})`;
    frame.style.left = `${Math.max(0, (stage.clientWidth - viewport * scale) / 2)}px`;
  });
}

buttons.forEach(button => button.addEventListener('click', () => {
  device = button.dataset.device;
  document.body.dataset.device = device;
  buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  resizePreviews();
}));
const observer = new ResizeObserver(resizePreviews);
stages.forEach(stage => observer.observe(stage));
resizePreviews();
