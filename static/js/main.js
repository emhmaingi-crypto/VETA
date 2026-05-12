document.addEventListener('DOMContentLoaded', function () {
    /* ── Navbar: hamburger toggle ──────────────────────────────── */
    const navToggle = document.getElementById('nav-toggle');
    const navLinks  = document.getElementById('nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('open');
            navToggle.classList.toggle('open');
            navToggle.setAttribute('aria-expanded', navLinks.classList.contains('open'));
        });

        // Close when a nav link is clicked
        navLinks.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navLinks.classList.remove('open');
                navToggle.classList.remove('open');
            });
        });
    }

    /* ── Navbar: scroll shadow ────────────────────────────────── */
    const navbar = document.getElementById('navbar');
    if (navbar) {
        function handleScroll() {
            navbar.classList.toggle('scrolled', window.scrollY > 10);
        }
        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();
    }

    /* ── Message auto-dismiss ─────────────────────────────────── */
    document.querySelectorAll('.messages-wrap .msg').forEach(function (msg) {
        setTimeout(function () {
            msg.style.opacity = '0';
            setTimeout(function () { msg.remove(); }, 400);
        }, 5000);
    });

    /* ── Scroll reveal (IntersectionObserver) ─────────────────── */
    if ('IntersectionObserver' in window) {
        const revealObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        document.querySelectorAll('[data-reveal]').forEach(function (el) {
            revealObserver.observe(el);
        });
    } else {
        // Fallback: immediately reveal everything
        document.querySelectorAll('[data-reveal]').forEach(function (el) {
            el.classList.add('revealed');
        });
    }

    /* ── Counter animation ────────────────────────────────────── */
    function animateCounter(el) {
        const text   = el.textContent.trim();
        const suffix = text.replace(/[\d,]/g, '');
        const target = parseInt(text.replace(/[^\d]/g, ''), 10);
        if (isNaN(target) || target === 0) return;

        const duration = 1400;
        const start    = performance.now();

        function tick(now) {
            const elapsed  = now - start;
            const progress = Math.min(elapsed / duration, 1);
            // ease-out cubic
            const eased    = 1 - Math.pow(1 - progress, 3);
            const current  = Math.round(eased * target);
            el.textContent = current.toLocaleString() + suffix;
            if (progress < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    if ('IntersectionObserver' in window) {
        const counterObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        document.querySelectorAll(
            '.stat-num, .stats-banner .stat-block strong, .stats-grid strong'
        ).forEach(function (el) {
            counterObserver.observe(el);
        });
    }
});

