const switches = Array.from(document.querySelectorAll('[data-switch]')).map(link => ({link, target: new URL(link.getAttribute('href'), location.href)}));
const sections = Array.from(document.querySelectorAll('main .section, main .project'));
let scheduled = false;

function updateLinks() {
  let current = '';
  sections.forEach(section => {
    if (section.getBoundingClientRect().top <= 180) current = `#${section.id}`;
  });
  switches.forEach(({link, target}) => {
    target.hash = current;
    link.href = target.href;
  });
  scheduled = false;
}

window.addEventListener('scroll', () => {
  if (!scheduled) {
    scheduled = true;
    requestAnimationFrame(updateLinks);
  }
}, {passive: true});
window.addEventListener('hashchange', updateLinks);
window.addEventListener('load', updateLinks);
updateLinks();
