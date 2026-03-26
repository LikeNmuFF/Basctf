
// Auto-dismiss flash alerts
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    // Dismiss on click
    alert.addEventListener('click', () => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.3s';
      setTimeout(() => alert.remove(), 300);
    });
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.5s';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // Typing cursor effect on brand
  const brand = document.querySelector('.navbar-brand-text');
  if (brand) {
    const text = brand.textContent;
    brand.textContent = '';
    let i = 0;
    const type = () => {
      if (i < text.length) {
        brand.textContent += text[i++];
        setTimeout(type, 60);
      }
    };
    type();
  }

  // Confirm before dangerous actions
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      if (!confirm(el.dataset.confirm)) e.preventDefault();
    });
  });

  // Flag input uppercase hint
  const flagInput = document.getElementById('flag-input');
  if (flagInput) {
    flagInput.addEventListener('input', () => {
      const val = flagInput.value;
      // Highlight if looks like a flag
      if (val.match(/^[A-Za-z0-9_]+\{.+\}$/)) {
        flagInput.style.color = 'var(--green)';
      } else {
        flagInput.style.color = '';
      }
    });
  }

  // Auto-submit challenge filters on select change
  const filterForm = document.getElementById('challenge-filter-form');
  if (filterForm) {
    filterForm.querySelectorAll('select').forEach(sel => {
      sel.addEventListener('change', () => filterForm.submit());
    });
  }
});
