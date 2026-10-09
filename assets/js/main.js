// 澳門橋霍頓有限公司官網前端腳本
// 功能：手機菜單、語言下拉、tabs 切換、表單前端演示提交、滾動淡入

document.addEventListener('DOMContentLoaded', () => {
  // 手機菜單
  const toggle = document.getElementById('menu-toggle');
  const panel = document.getElementById('mobile-panel');
  if (toggle && panel) {
    toggle.addEventListener('click', () => panel.classList.toggle('open'));
  }

  // 語言下拉（頁頭 + 頁尾）
  document.querySelectorAll('.lang-switch').forEach(sw => {
    const btn = sw.querySelector('button');
    btn.addEventListener('click', e => {
      e.stopPropagation();
      document.querySelectorAll('.lang-switch.open').forEach(o => o !== sw && o.classList.remove('open'));
      sw.classList.toggle('open');
    });
  });
  document.addEventListener('click', () => {
    document.querySelectorAll('.lang-switch.open').forEach(o => o.classList.remove('open'));
  });

  // Tabs（成功案例分類、聯絡表單切換）
  document.querySelectorAll('[data-tabs]').forEach(box => {
    const btns = box.querySelectorAll('[data-tab]');
    const panes = box.querySelectorAll('[data-pane]');
    btns.forEach(btn => btn.addEventListener('click', () => {
      btns.forEach(b => b.classList.toggle('active', b === btn));
      panes.forEach(p => p.classList.toggle('active', p.dataset.pane === btn.dataset.tab));
      panes.forEach(p => { p.style.display = p.classList.contains('active') ? '' : 'none'; });
    }));
    panes.forEach(p => { p.style.display = p.classList.contains('active') ? '' : 'none'; });
  });

  // 表單（前端演示：驗證後顯示成功提示，不接後端）
  document.querySelectorAll('form.ajax-form').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      const errRequired = form.dataset.errRequired || 'This field is required';
      const errEmail = form.dataset.errEmail || 'Invalid email format';
      let ok = true;
      form.querySelectorAll('[required]').forEach(field => {
        const group = field.closest('.form-group');
        const errEl = group && group.querySelector('.err');
        let msg = '';
        if (!field.value.trim()) msg = errRequired;
        else if (field.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) msg = errEmail;
        if (group) group.classList.toggle('invalid', !!msg);
        if (errEl) errEl.textContent = msg;
        if (msg) ok = false;
      });
      if (!ok) return;
      const btn = form.querySelector('.form-submit');
      const toast = form.querySelector('.form-toast');
      if (btn) { btn.disabled = true; btn.textContent = form.dataset.submitting || btn.textContent; }
      setTimeout(() => {
        form.reset();
        if (btn) { btn.disabled = false; btn.textContent = btn.dataset.label; }
        if (toast) {
          toast.classList.add('show');
          setTimeout(() => toast.classList.remove('show'), 5000);
        }
      }, 800);
    });
    form.querySelectorAll('[required]').forEach(field => {
      field.addEventListener('input', () => {
        const group = field.closest('.form-group');
        if (group) group.classList.remove('invalid');
      });
    });
    const btn = form.querySelector('.form-submit');
    if (btn) btn.dataset.label = btn.textContent;
  });

  // 滾動淡入
  const io = new IntersectionObserver(entries => {
    entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); } });
  }, { threshold: 0.1 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
});
