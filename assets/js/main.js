// 澳門橋霍頓有限公司官網前端腳本
// 功能：手機菜單、語言下拉、tabs 切換、表單前端演示提交、滾動淡入

document.addEventListener('DOMContentLoaded', () => {
  // 手機菜單
  const toggle = document.getElementById('menu-toggle');
  const panel = document.getElementById('mobile-panel');
  const setMenuOpen = open => {
    if (!toggle || !panel) return;
    panel.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', String(open));
  };
  if (toggle && panel) {
    toggle.setAttribute('aria-controls', 'mobile-panel');
    setMenuOpen(panel.classList.contains('open'));
    toggle.addEventListener('click', () => setMenuOpen(!panel.classList.contains('open')));
  }

  // 語言下拉（頁頭 + 頁尾）
  const langSwitches = Array.from(document.querySelectorAll('.lang-switch'));
  const setLangOpen = (sw, open) => {
    sw.classList.toggle('open', open);
    const btn = sw.querySelector('button');
    if (btn) btn.setAttribute('aria-expanded', String(open));
  };
  langSwitches.forEach((sw, index) => {
    const btn = sw.querySelector('button');
    const dropdown = sw.querySelector('.dropdown');
    if (!btn) return;
    btn.setAttribute('aria-expanded', String(sw.classList.contains('open')));
    btn.removeAttribute('aria-haspopup');
    if (dropdown) {
      dropdown.id = dropdown.id || `language-options-${index + 1}`;
      btn.setAttribute('aria-controls', dropdown.id);
    }
    btn.addEventListener('click', e => {
      e.stopPropagation();
      langSwitches.forEach(other => { if (other !== sw) setLangOpen(other, false); });
      setLangOpen(sw, !sw.classList.contains('open'));
    });
  });
  document.addEventListener('click', () => {
    langSwitches.forEach(sw => setLangOpen(sw, false));
  });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    const openLang = document.querySelector('.lang-switch.open');
    if (openLang) {
      setLangOpen(openLang, false);
      const btn = openLang.querySelector('button');
      if (btn) btn.focus();
    } else if (panel && panel.classList.contains('open')) {
      setMenuOpen(false);
      toggle.focus();
    }
  });

  // Tabs（成功案例分類、聯絡表單切換）
  document.querySelectorAll('[data-tabs]').forEach((box, boxIndex) => {
    const btns = Array.from(box.querySelectorAll('[data-tab]'));
    const panes = Array.from(box.querySelectorAll('[data-pane]'));
    if (!btns.length || !panes.length) return;
    const tablist = btns[0].parentElement;
    const heading = document.querySelector('main h1');
    if (tablist) {
      tablist.setAttribute('role', 'tablist');
      if (heading) {
        heading.id = heading.id || `page-heading-${boxIndex + 1}`;
        tablist.setAttribute('aria-labelledby', heading.id);
      }
    }
    const selectTab = (btn, moveFocus = false) => {
      btns.forEach(b => {
        const selected = b === btn;
        b.classList.toggle('active', selected);
        b.setAttribute('aria-selected', String(selected));
        b.tabIndex = selected ? 0 : -1;
      });
      panes.forEach(p => {
        const selected = p.dataset.pane === btn.dataset.tab;
        p.classList.toggle('active', selected);
        p.style.display = selected ? '' : 'none';
        p.hidden = !selected;
        if (selected && !p.querySelector('a, button, input, select, textarea')) p.tabIndex = 0;
        else p.removeAttribute('tabindex');
      });
      if (moveFocus) btn.focus();
    };
    btns.forEach((btn, index) => {
      const pane = panes.find(p => p.dataset.pane === btn.dataset.tab);
      btn.id = btn.id || `tab-${boxIndex + 1}-${index + 1}`;
      btn.setAttribute('role', 'tab');
      if (pane) {
        pane.id = pane.id || `tabpanel-${boxIndex + 1}-${index + 1}`;
        pane.setAttribute('role', 'tabpanel');
        pane.setAttribute('aria-labelledby', btn.id);
      }
      btn.addEventListener('click', () => selectTab(btn));
      btn.addEventListener('keydown', e => {
        let next;
        if (e.key === 'ArrowRight') next = (index + 1) % btns.length;
        else if (e.key === 'ArrowLeft') next = (index - 1 + btns.length) % btns.length;
        else if (e.key === 'Home') next = 0;
        else if (e.key === 'End') next = btns.length - 1;
        else return;
        e.preventDefault();
        selectTab(btns[next], true);
      });
    });
    selectTab(btns.find(btn => btn.classList.contains('active')) || btns[0]);
  });

  // 表單（前端演示：驗證後顯示成功提示，不接後端）
  document.querySelectorAll('form.ajax-form').forEach((form, formIndex) => {
    const toast = form.querySelector('.form-toast');
    if (toast) {
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      toast.setAttribute('aria-atomic', 'true');
    }
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (toast) toast.classList.remove('show');
      const errRequired = form.dataset.errRequired || 'This field is required';
      const errEmail = form.dataset.errEmail || 'Invalid email format';
      let firstInvalid = null;
      form.querySelectorAll('[required]').forEach(field => {
        const group = field.closest('.form-group');
        const errEl = group && group.querySelector('.err');
        let msg = '';
        if (!field.value.trim()) msg = errRequired;
        else if (field.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value)) msg = errEmail;
        if (group) group.classList.toggle('invalid', !!msg);
        if (errEl) errEl.textContent = msg;
        if (msg) {
          field.setAttribute('aria-invalid', 'true');
          if (!firstInvalid) firstInvalid = field;
        } else field.removeAttribute('aria-invalid');
      });
      if (firstInvalid) {
        firstInvalid.focus();
        return;
      }
      const btn = form.querySelector('.form-submit');
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
    form.querySelectorAll('[required]').forEach((field, fieldIndex) => {
      const group = field.closest('.form-group');
      const errEl = group && group.querySelector('.err');
      if (errEl) {
        errEl.id = errEl.id || `form-${formIndex + 1}-error-${fieldIndex + 1}`;
        field.setAttribute('aria-describedby', errEl.id);
      }
      const clearError = () => {
        if (group) group.classList.remove('invalid');
        field.removeAttribute('aria-invalid');
        if (errEl) errEl.textContent = '';
      };
      field.addEventListener('input', clearError);
      field.addEventListener('change', clearError);
    });
    const btn = form.querySelector('.form-submit');
    if (btn) btn.dataset.label = btn.textContent;
  });

  // 滾動淡入
  const revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); } });
    }, { threshold: 0.1 });
    revealEls.forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.top < window.innerHeight && rect.bottom > 0) el.classList.add('visible');
      else {
        el.classList.add('reveal-pending');
        io.observe(el);
      }
    });
  } else revealEls.forEach(el => el.classList.add('visible'));
});
