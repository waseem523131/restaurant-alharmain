/**
 * مطعم الحرمين - ملف JavaScript الرئيسي
 */

document.addEventListener('DOMContentLoaded', function () {
    initNavbar();
    initMobileMenu();
    initScrollAnimations();
    initCounterAnimation();
    initAlertAutoClose();
});

/**
 * Navbar scroll effect
 */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    function handleScroll() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }

    window.addEventListener('scroll', handleScroll);
    handleScroll();
}

/**
 * Mobile menu toggle
 */
function initMobileMenu() {
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    if (!navToggle || !navLinks) return;

    navToggle.addEventListener('click', function () {
        navToggle.classList.toggle('active');
        navLinks.classList.toggle('active');
    });

    navLinks.querySelectorAll('.nav-link').forEach(function (link) {
        link.addEventListener('click', function () {
            navToggle.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });

    document.addEventListener('click', function (e) {
        if (!navToggle.contains(e.target) && !navLinks.contains(e.target)) {
            navToggle.classList.remove('active');
            navLinks.classList.remove('active');
        }
    });
}

/**
 * Scroll fade-in animations
 */
function initScrollAnimations() {
    const elements = document.querySelectorAll('.fade-in');
    if (!elements.length) return;

    const observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px',
        }
    );

    elements.forEach(function (el) {
        observer.observe(el);
    });
}

/**
 * Counter animation for statistics
 */
function initCounterAnimation() {
    const counters = document.querySelectorAll('.stat-number');
    if (!counters.length) return;

    const observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );

    counters.forEach(function (counter) {
        observer.observe(counter);
    });
}

function animateCounter(element) {
    const target = parseFloat(element.getAttribute('data-target'));
    const isDecimal = target % 1 !== 0;
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;

    function update() {
        current += step;
        if (current < target) {
            element.textContent = isDecimal ? current.toFixed(1) : Math.floor(current).toLocaleString('ar-SA');
            requestAnimationFrame(update);
        } else {
            element.textContent = isDecimal ? target.toFixed(1) : target.toLocaleString('ar-SA');
        }
    }

    update();
}

/**
 * Auto-close alert messages
 */
function initAlertAutoClose() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            alert.style.transition = 'all 0.3s ease';
            setTimeout(function () {
                alert.remove();
            }, 300);
        }, 5000);
    });
}

/**
 * Menu category filter
 */
function initMenuFilter() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const menuCards = document.querySelectorAll('.menu-card');
    if (!filterBtns.length || !menuCards.length) return;

    filterBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            filterBtns.forEach(function (b) {
                b.classList.remove('active');
            });
            btn.classList.add('active');

            const category = btn.getAttribute('data-category');

            menuCards.forEach(function (card) {
                const cardCategory = card.getAttribute('data-category');

                if (category === 'all' || cardCategory === category) {
                    card.classList.remove('hidden');
                    card.style.animation = 'none';
                    card.offsetHeight;
                    card.style.animation = 'fadeIn 0.5s ease';
                } else {
                    card.classList.add('hidden');
                }
            });
        });
    });
}

// CSS animation for filter
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);
