// Minimal demo script; logs once when loaded on frontend
console.debug('[website_custom] frontend assets loaded');

document.addEventListener('DOMContentLoaded', () => {
  const el = document.querySelector('.container h1.display-5');
  if (el) {
    el.classList.add('text-primary');
  }
});

