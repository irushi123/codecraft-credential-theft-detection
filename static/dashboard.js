/* CodeCraft - Dashboard JS */
(function () {
    'use strict';
    const body = document.body;
    const $  = (s, r = document) => r.querySelector(s);
    const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

    /* ---------- Theme (light / dark) ---------- */
    const THEME_KEY = 'cc-theme';
    function applyTheme(t) {
        body.setAttribute('data-theme', t);
        const btn = $('#themeToggle');
        if (btn) {
            btn.innerHTML = '<i data-lucide="' + (t === 'dark' ? 'sun' : 'moon') + '"></i>';
            if (window.lucide) lucide.createIcons();
        }
    }
    applyTheme(localStorage.getItem(THEME_KEY) || 'light');

    const themeBtn = $('#themeToggle');
    if (themeBtn) themeBtn.addEventListener('click', () => {
        const next = body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        localStorage.setItem(THEME_KEY, next);
        applyTheme(next);
    });

    /* ---------- Sidebar toggle ---------- */
    const COLLAPSE_KEY = 'cc-sidebar-collapsed';
    if (localStorage.getItem(COLLAPSE_KEY) === '1') body.classList.add('sidebar-collapsed');

    const sidebarBtn = $('#sidebarToggle');
    if (sidebarBtn) sidebarBtn.addEventListener('click', () => {
        if (window.matchMedia('(max-width: 768px)').matches) {
            body.classList.toggle('sidebar-open');
        } else {
            body.classList.toggle('sidebar-collapsed');
            localStorage.setItem(COLLAPSE_KEY, body.classList.contains('sidebar-collapsed') ? '1' : '0');
        }
    });
    const overlay = $('.overlay');
    if (overlay) overlay.addEventListener('click', () => body.classList.remove('sidebar-open'));

    /* ---------- Active menu link (URL eken auto) ---------- */
    const links = $$('.sidebar nav a');
    const path = location.pathname.replace(/\/$/, '') || '/';
    let matched = false;
    links.forEach(a => {
        const href = (a.getAttribute('href') || '').replace(/\/$/, '') || '/';
        if (href === path) { a.classList.add('active'); matched = true; }
    });
    if (matched) links.forEach(a => {
        const href = (a.getAttribute('href') || '').replace(/\/$/, '') || '/';
        if (href !== path) a.classList.remove('active');
    });

    /* ---------- Menu search ( "/" or Ctrl+K ) ---------- */
    const search = $('#menuSearch');
    if (search) {
        search.addEventListener('input', () => {
            const q = search.value.trim().toLowerCase();
            links.forEach(a => {
                a.classList.toggle('hidden-by-search', q && !a.textContent.toLowerCase().includes(q));
            });
            if (q) body.classList.remove('sidebar-collapsed');
        });
        search.addEventListener('keydown', e => {
            if (e.key === 'Enter') {
                const first = links.find(a => !a.classList.contains('hidden-by-search'));
                if (first) location.href = first.getAttribute('href');
            }
            if (e.key === 'Escape') { search.value = ''; search.dispatchEvent(new Event('input')); search.blur(); }
        });
        document.addEventListener('keydown', e => {
            const typing = /input|textarea|select/i.test(document.activeElement.tagName);
            if ((e.key === '/' && !typing) || ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k')) {
                e.preventDefault(); search.focus();
            }
        });
    }

    /* ---------- Profile dropdown ---------- */
    const pBtn = $('#profileBtn'), pMenu = $('#profileDropdown');
    if (pBtn && pMenu) {
        pBtn.addEventListener('click', e => { e.stopPropagation(); pMenu.classList.toggle('open'); });
        document.addEventListener('click', () => pMenu.classList.remove('open'));
    }

    /* ---------- Avatar initials ---------- */
    $$('[data-initials]').forEach(el => {
        const name = (el.getAttribute('data-initials') || 'A').split('@')[0];
        el.textContent = name.slice(0, 2).toUpperCase();
    });

    /* ---------- Greeting ---------- */
    const greet = $('[data-greeting]');
    if (greet) {
        const h = new Date().getHours();
        greet.textContent = h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening';
    }

    /* ---------- Count-up numbers ---------- */
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    $$('[data-count]').forEach(el => {
        const target = parseFloat(el.getAttribute('data-count')) || 0;
        if (reduce || target === 0) { el.textContent = target.toLocaleString(); return; }
        const start = performance.now(), dur = 900;
        (function tick(now) {
            const p = Math.min((now - start) / dur, 1);
            const eased = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(target * eased).toLocaleString();
            if (p < 1) requestAnimationFrame(tick);
        })(start);
    });

    /* ---------- Progress bars ---------- */
    requestAnimationFrame(() => $$('.progress > div[data-percent]').forEach(bar => {
        bar.style.width = Math.min(parseFloat(bar.getAttribute('data-percent')) || 0, 100) + '%';
    }));

    /* ---------- Icons ---------- */
    if (window.lucide) lucide.createIcons();
})();